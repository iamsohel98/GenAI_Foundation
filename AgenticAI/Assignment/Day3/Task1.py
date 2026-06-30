from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END
# ─────────────────────────────────────────────────────────────────────────────
# TASK 1: Extend Basic Pipeline - No LLM
# ─────────────────────────────────────────────────────────────────────────────

print("TASK 1 - Basic Pipeline With Character Count and Word Count")
print("=" * 70)

# Step 1: Define State
class PipelineState(TypedDict):
    text: str
    char_count: int
    word_count: int
    summary: str


# Step 2: Define Nodes
def count_chars(state: PipelineState) -> dict:
    """
    Node 1:
    Counts number of characters in input text.
    """
    char_count = len(state["text"])
    return {"char_count": char_count}


def count_words(state: PipelineState) -> dict:
    """
    Node 2:
    Counts number of words in input text.
    """
    words = state["text"].split()
    word_count = len(words)
    return {"word_count": word_count}


def make_summary(state: PipelineState) -> dict:
    """
    Node 3:
    Creates final summary using character count and word count.
    """
    summary = (
        f"'{state['text']}' — "
        f"{state['char_count']} characters, "
        f"{state['word_count']} words."
    )
    return {"summary": summary}


# Step 3: Build Graph
builder_task1 = StateGraph(PipelineState)

builder_task1.add_node("count", count_chars)
builder_task1.add_node("word_count", count_words)
builder_task1.add_node("summarise", make_summary)

# Step 4: Add Edges
builder_task1.add_edge(START, "count")
builder_task1.add_edge("count", "word_count")
builder_task1.add_edge("word_count", "summarise")
builder_task1.add_edge("summarise", END)

# Step 5: Compile Graph
graph_task1 = builder_task1.compile()

# Step 6: Invoke Graph
input_text = "LangGraph makes stateful AI workflows easy!"

result_task1 = graph_task1.invoke({
    "text": input_text,
    "char_count": 0,
    "word_count": 0,
    "summary": ""
})

# Step 7: Print Output
print("Input Text  :", result_task1["text"])
print("Characters  :", result_task1["char_count"])
print("Words       :", result_task1["word_count"])
print("Summary     :", result_task1["summary"])