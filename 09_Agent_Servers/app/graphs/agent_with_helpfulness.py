from __future__ import annotations

from typing import Annotated, TypedDict

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from app.models import get_chat_model
from app.tools import get_tool_belt

SYSTEM_PROMPT = (
    "You are a helpful assistant specialized in feline (cat) health. "
    "Use the retrieve_information tool for cat-health questions, web search for "
    "current information, and Arxiv for research papers. Cite tool results when "
    "they inform your answer."
)

JUDGE_PROMPT = (
    "Decide whether the answer is helpful for the question. "
    "Reply with a single character, Y if helpful or N if not.\n\n"
    "Question: {question}\n\nAnswer: {answer}"
)

RETRY_HINT = (
    "The previous answer was judged unhelpful. Answer again, more directly and "
    "completely."
)

MAX_ATTEMPTS = 3

agent = create_agent(
    model=get_chat_model(),
    tools=get_tool_belt(),
    system_prompt=SYSTEM_PROMPT,
)

judge_model = get_chat_model()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    attempts: int
    helpful: bool


def message_text(message) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block)
        for block in content
    )


def run_agent(state: State) -> dict:
    result = agent.invoke({"messages": state["messages"]})
    new_messages = result["messages"][len(state["messages"]):]
    return {"messages": new_messages, "attempts": state.get("attempts", 0) + 1}


def judge(state: State) -> dict:
    question = next(
        (message_text(m) for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        "",
    )
    answer = message_text(state["messages"][-1])
    verdict = judge_model.invoke(JUDGE_PROMPT.format(question=question, answer=answer))
    helpful = verdict.content.strip().upper().startswith("Y")
    if helpful or state["attempts"] >= MAX_ATTEMPTS:
        return {"helpful": helpful}
    return {"helpful": helpful, "messages": [HumanMessage(content=RETRY_HINT)]}


def route(state: State) -> str:
    if state.get("helpful") or state["attempts"] >= MAX_ATTEMPTS:
        return END
    return "agent"


builder = StateGraph(State)
builder.add_node("agent", run_agent)
builder.add_node("judge", judge)
builder.add_edge(START, "agent")
builder.add_edge("agent", "judge")
builder.add_conditional_edges("judge", route, {"agent": "agent", END: END})

graph = builder.compile()
