from typing import Any
from langgraph.graph import RunnableConfig
import logging

logger = logging.getLogger("debate")

def user_input_node(state:dict)->dict:
    # expects a state[topic]
    topic = state.get("topic","").strip()
    logger.info(f"[UserNode] topic: {topic}")
    return {"topic":topic, "round": 1, "transcipt": [], "per_agent_summary": {"agentA": [], "agentB": []}, "last_agent": "", "judge_summary": ""}

def agentA_node(state:dict)->dict:
    #this agent will speak on odd turns
    rnd = state.get("round", 1)
    if rnd > 8:
        return {}
    if rnd % 2 == 0: #not an odd turn
        return {}
    
    prompt = (
        f"You are a Scientist. Topic: {state['topic']}. Round {rnd}.\n"
        f"Visible memory (agentA): {state['per_agent_summary'].get('agentA')}\n"
        "Produce a concise argument (1-2 sentences)."
    )

    text = "" #llm_generate(prompt) # llm generation to be added later
    entry = {"round": rnd, "agent": "agentA", "text": text} #add_message will add this

    #updating the per_agent_summary for the opponent
    state["per_agent_summary"]["agentA"].append(f"R{rnd} agentA: {text.split('.')[0]}")

    #update the last speaker
    return {"transcript": entry, "last_agent": "agentA", "round": rnd+1, "per_agent_summary": state["per_agent_summary"]}


def agentB_node(state:dict)->dict:
    #this agent will speak on even turns
    rnd = state.get("round", 1)
    if rnd > 8:
        return {}
    if rnd % 2 == 1: #not an even turn
        return {}
    
    prompt = (
        f"You are a Philosopher. Topic: {state['topic']}. Round {rnd}.\n"
        f"Visible memory (agentB): {state['per_agent_summary'].get('agentB')}\n"
        "Produce a concise argument (1-2 sentences)."
    )

    text = "" #llm_generate(prompt) # llm generation to be added later
    entry = {"round": rnd, "agent": "agentB", "text": text} #add_message will add this

    #updating the per_agent_summary for the opponent
    state["per_agent_summary"]["agentB"].append(f"R{rnd} agentB: {text.split('.')[0]}")

    #update the last speaker
    return {"transcript": entry, "last_agent": "agentB", "round": rnd+1, "per_agent_summary": state["per_agent_summary"]}