from langgraph.graph import START, END, StateGraph
from langchain_core.runnables import Runnable
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langgraph_nodes import (
    user_input_node,
    agentA_node,
    agentB_node,
    memory_node,
    judge_node
)

#Defining the State of the graph(shared memory)
class DebateState(TypedDict):
    topic: str
    round: int
    transcript: list
    transcript_store: list
    per_agent_summary: dict
    last_agent: str
    judge_summary: str


def build_debate_graph()-> Runnable:
    builder = StateGraph(DebateState)

    #register the nodes difined in langggraph_nodes
    builder.add_node("UserInput", user_input_node,)
    builder.add_node("agentA", agentA_node,)
    builder.add_node("Memory", memory_node,)
    builder.add_node("agentB", agentB_node)
    builder.add_node("Judge", judge_node,)

    # Graph edges (START -> UserInput -> AgentA -> Memory -> AgentB -> Memory -> ... -> Judge -> END)
    #connect the nodes with the edges
    builder.add_edge(START, "UserInput")
    #First turn will go to agentA
    builder.add_edge("UserInput", "agentA")

    #memory node after each agent node
    builder.add_edge("agentA", "Memory")
    builder.add_edge("agentB", "Memory")

    #conditional edge for the debate
    def debate_router(state:dict):
        rnd = state["round"]
        if rnd>8:
            return "Judge"
        elif rnd % 2 == 1:
            return "agentA"
        else:
            return "agentB"
    
    builder.add_conditional_edges(
        "Memory",
        debate_router,
        {
            "agentA":"agentA",
            "agentB":"agentB",
            "Judge":"Judge"
        }
    )

    builder.add_edge("Judge",END)

    #Debugging the dangling node
    '''print("\n=== DEBUG: Printing Graph State ===")
    print("Registered Nodes:", list(builder.nodes.keys()))
    print("Edges:")
    for src, dst in builder.edges:
        print(f"  {src} -> {dst}")
    print("===================================\n")'''


    #compile this to a runnable
    graph = builder.compile()
    return graph