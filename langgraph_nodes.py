from typing import Any
import logging
from utils import llm_generater
import json
from helper import extract_json

logger = logging.getLogger("debate")

def user_input_node(state:dict)->dict:
    # expects a state[topic]
    topic = state.get("topic","").strip()
    logger.info(f"[UserNode] topic: {topic}")
    return {
        "topic":topic,
        "round": 1,
        "transcript": [],
        "transcript_store": [],
        "per_agent_summary": {"agentA": [], "agentB": []},
        "last_agent": "",
        "judge_summary": ""}

def agentA_node(state:dict)->dict:
    #this agent will speak on odd turns
    rnd = state.get("round", 1)
    if rnd > 8:
        return {}
    if rnd % 2 == 0: #not an odd turn
        return {}
    
    prompt = (
        f"You are a Scientist. Debate for the Topic: {state['topic']}. Round {rnd}.\n"
        f"Visible memory (agentA): {state['per_agent_summary'].get('agentA')}\n"
        "Produce a concise argument (1-2 sentences)."
    )

    text = llm_generater(prompt) # llm generation to be added later
    entry = {"round": rnd, "agent": "agentA", "text": text} #add_message will add this
    #logging the output
    logger.info(f"[AgentA] R{rnd} -> {text[:20]}...")

    #updating the per_agent_summary for the opponent
    state["per_agent_summary"]["agentA"].append(f"R{rnd} agentA: {text}")

    #update the last speaker
    return {"transcript": [entry],
            "last_agent": "agentA",
            "round": rnd+1,
            "per_agent_summary": state["per_agent_summary"]
            }


def agentB_node(state:dict)->dict:
    #this agent will speak on even turns
    rnd = state.get("round", 1)
    if rnd > 8:
        return {}
    if rnd % 2 == 1: #not an even turn
        return {}
    
    prompt = (
        f"You are a Philosopher. Debate against the Topic: {state['topic']}. Round {rnd}.\n"
        f"Visible memory (agentB): {state['per_agent_summary'].get('agentB')}\n"
        "Produce a concise argument (1-2 sentences)."
    )

    text = llm_generater(prompt) # llm generation to be added later
    entry = {"round": rnd, "agent": "agentB", "text": text} #add_message will add this
    #logging the output
    logger.info(f"[AgentB] R{rnd} -> {text[:20]}...")

    #updating the per_agent_summary for the opponent
    state["per_agent_summary"]["agentB"].append(f"R{rnd} agentB: {text}")

    #update the last speaker
    return {"transcript": [entry],
            "last_agent": "agentB",
            "round": rnd+1,
            "per_agent_summary": state["per_agent_summary"]
            }

def memory_node(state: dict)-> dict:
    #gets the new entries from transcipt and added them to store
    new_entry = state.get("transcript",[])
    stored = state.get("transcript_store", [])

    existing_entries = {(x['agent'],x['text'].strip().lower()) for x in stored}
    
    if new_entry:
        for e in new_entry:
            # detecting for repetation
            key = (e['agent'],e['text'].strip().lower())
            if key in existing_entries:
                #repetation detected
                print("repetation")
            stored.append(e)
            #logging each memory
            logger.info(f"[Memory] Appended R{e['round']} {e['agent']}")
    
    state_update = {"transcript_store": stored, "transcript": []}
    return state_update

def judge_node(state:dict)->dict:
    #called for the final evaluation
    stored = state.get("transcript_store",[])
    topic = state.get("topic","")
    logger.info(f"[Judge] Received {len(stored)} transcript entries for evaluation")

    #----- 1. HEURISTIC SCORING ------
    #perform heuristic keyword scoring comparision
    keywords = {
        "risk": ["risk","safety","danger","harm"],
        "benefit": ["benefit","advantage","improve","progress"],
        "ethics": ["ethic","autonomy","consent","rights"],
        "evidence": ["study","data","evidence","research","statistic"],
    }

    heuristic = {"agentA":0, "agentB":0}
    for e in stored:
        t = e['text'].lower()
        for k,words in keywords.items():
            for w in words:
                if w in t:
                    heuristic[e['agent']] += 1
    
    #----- 2. LLM SCORING (optional) -----
    debate_text = "\n".join(
        f"Round {e['round']} - {e['agent']}: {e['text']}"
        for e in stored
    )
    llm_prompt = f"""
    You are a debate judge.

    Debate Topic: {topic}

    Here is the full transcript:
    {debate_text}

    Evaluate the arguments for:
    - Clarity
    - Logic
    - Evidence
    - Rebuttal strength
    - Originality

    Return STRICT JSON:
    {{
      "agentA": <score 0-10>,
      "agentB": <score 0-10>,
      "winner": "agentA" | "agentB" | "draw",
      "justification": "<1-2 sentence justification>"
    }}
    """
    try:
        llm_result_raw = llm_generater(llm_prompt)
        llm_result = extract_json(llm_result_raw)
    except Exception as e:
        print(f"Error: {e}")
        llm_result = {
            "agentA": 0,
            "agentB": 0,
            "winner": "draw",
            "justification": "LLM scoring unavailable. Using heuristic only."
        }
    
    #----- 3. COMBINE SCORES -----
    alpha = 0.4   # 40% heuristic, 60% LLM — adjustable
    final_scores = {
        "agentA": (heuristic["agentA"] * alpha) + (llm_result["agentA"] * (1-alpha)),
        "agentB": (heuristic["agentB"] * alpha) + (llm_result["agentB"] * (1-alpha)),
    }

    #pick the winner
    if final_scores["agentA"] > final_scores["agentB"]:
        winner = "agentA"
    elif final_scores["agentA"] < final_scores["agentB"]:
        winner = "agentB"
    else:
        winner = "Draw"
    
    #Printing the results on console
    print("Results of the Debate:")
    print(f"Scores: {final_scores}")
    print(f"Winner: {winner}")
    print(f"Justification: {llm_result.get('justification', 'No justification produced.')}")

    #----- 4. BUILD THE STRICT SUMMARY -----
    summary = {
        "topic": topic,
        "heuristic_scores": heuristic,
        "llm_scores": {"agentA": llm_result.get("agentA"), "agentB": llm_result.get("agentB")},
        "final_scores": final_scores,
        "winner": winner,
        "justification": llm_result.get("justification", "No justification produced."),
        "full_transcript": stored,
    }
    
    # logger.info(f"[Judge] {summary}")
    return {"judge_summary": summary}


