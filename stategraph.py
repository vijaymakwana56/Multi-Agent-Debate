from langgraph.graph import START, END, state
from langgraph.graph import Runnable
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
# from langgraph_nodes import 

#Defining the State of the graph(shared memory)
class DebateState(TypedDict):
    topic: str
    round: int
    transcipt: Annotated[list,add_messages]
    per_agent_summary: str
    last_agent: str
    judge_summary: str