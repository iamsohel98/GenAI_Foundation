import streamlit as st
import sys
import io
import os
import subprocess
import tempfile
import traceback
import re
from contextlib import redirect_stdout, redirect_stderr
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain.agents import create_agent
load_dotenv(override=True)

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Coding Assistant",
    page_icon="烙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Main background */
  .stApp { background-color: #0e1117; }

  /* Force text inside chat bubbles only */
  .stMarkdown p, .stMarkdown li, .stMarkdown span {
    color: #f8f8f2;
  }

  /* Chat messages */
  .user-bubble {
    background: #1e3a5f;
    border-left: 4px solid #4a9eff;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 8px 0;
    color: #e8f4fd !important;
  }
  .user-bubble * { color: #e8f4fd !important; }

  .assistant-bubble {
    background: #1a1f2e;
    border-left: 4px solid #50fa7b;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 8px 0;
    color: #f8f8f2 !important;
  }
  .assistant-bubble * { color: #f8f8f2 !important; }

  .tool-bubble {
    background: #2a1f0e;
    border-left: 4px solid #ffb86c;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 4px 0 4px 20px;
    color: #ffb86c !important;
    font-size: 0.85em;
  }
  .exec-output {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 10px;
    font-family: 'Courier New', monospace;
    font-size: 0.85em;
    color: #8b949e !important;
    margin: 4px 0 4px 20px;
  }
  .exec-output * { color: inherit !important; }
  .exec-success, .exec-success * { border-left: 3px solid #50fa7b; color: #50fa7b !important; }
  .exec-error,   .exec-error *   { border-left: 3px solid #ff5555; color: #ff5555 !important; }

  /* Sidebar */
  .stat-box {
    background: #1a1f2e;
    border-radius: 8px;
    padding: 10px;
    margin: 6px 0;
    text-align: center;
  }
  .stat-number { font-size: 1.5em; font-weight: bold; color: #4a9eff !important; }
  .stat-label  { font-size: 0.75em; color: #8b949e !important; }

  /* Input area */
  .stTextArea textarea {
    background: #1a1f2e !important;
    color: #f8f8f2 !important;
    border: 1px solid #30363d !important;
    font-family: 'Courier New', monospace;
  }
  .stTextArea textarea::placeholder {
    color: #8b949e !important;
    opacity: 1 !important;
  }
  .badge {
    display: inline-block;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.75em;
    color: #8b949e !important;
    margin: 2px;
  }

  /* Sidebar text — only target specific elements, not all */
  section[data-testid="stSidebar"] .stat-number { color: #4a9eff !important; }
  section[data-testid="stSidebar"] .stat-label  { color: #8b949e !important; }
  section[data-testid="stSidebar"] h1,
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] label { color: inherit; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────────────────────────────────────
@tool
def execute_python_code(code: str) -> str:
    """
    Execute Python code and return the output (stdout + stderr).
    Use this to run, test, or validate any Python code.
    Returns the printed output or error message.
    """
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(compile(code, "<string>", "exec"), {})
        output = stdout_capture.getvalue()
        error  = stderr_capture.getvalue()
        result = ""
        if output:
            result += f"OUTPUT:\n{output}"
        if error:
            result += f"\nSTDERR:\n{error}"
        return result.strip() if result.strip() else "Code executed successfully with no output."
    except Exception as e:
        return f"ERROR:\n{traceback.format_exc()}"


@tool
def format_python_code(code: str) -> str:
    """
    Format Python code using Black to make it clean and PEP8 compliant.
    Returns the formatted code.
    """
    try:
        import black
        formatted = black.format_str(code, mode=black.Mode())
        return formatted
    except Exception as e:
        return f"Could not format code: {e}"


@tool
def save_code_to_file(filename: str, code: str) -> str:
    """
    Save code to a file in the workspace.
    Use this when the user wants to save their code.
    Returns the file path where code was saved.
    """
    save_dir = os.path.join(os.path.dirname(__file__), "workspace")
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, filename)
    with open(path, "w") as f:
        f.write(code)
    return f"Code saved to: {path}"


@tool
def read_file(filename: str) -> str:
    """
    Read the contents of a file from the workspace.
    Use this when the user wants to load or review a saved file.
    """
    save_dir = os.path.join(os.path.dirname(__file__), "workspace")
    path = os.path.join(save_dir, filename)
    if not os.path.exists(path):
        return f"File not found: {filename}. Available files: {os.listdir(save_dir) if os.path.exists(save_dir) else []}"
    with open(path) as f:
        return f.read()


@tool
def list_workspace_files() -> str:
    """
    List all files saved in the workspace directory.
    Use this to show the user what files have been saved.
    """
    save_dir = os.path.join(os.path.dirname(__file__), "workspace")
    if not os.path.exists(save_dir) or not os.listdir(save_dir):
        return "Workspace is empty. No files saved yet."
    files = os.listdir(save_dir)
    return "Files in workspace:\n" + "\n".join(f"  - {f}" for f in files)


TOOLS = [execute_python_code, format_python_code, save_code_to_file, read_file, list_workspace_files]

SYSTEM_PROMPT = """You are an expert AI Coding Assistant powered by Claude. You help users with:
- Writing clean, efficient Python code
- Debugging and fixing errors
- Explaining code clearly
- Reviewing code for best practices
- Running and testing code

You have access to tools:
- execute_python_code: Run Python code and see the output
- format_python_code: Format code with Black (PEP8)
- save_code_to_file: Save code to the workspace
- read_file: Read a saved file
- list_workspace_files: List saved files

Guidelines:
- Always write clean, well-commented code
- When generating code, offer to run it to verify it works
- For bugs, explain what was wrong and why the fix works
- Use markdown code blocks with ```python for all code
- Be concise but thorough in explanations"""

# ─────────────────────────────────────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []          # List[BaseMessage]
if "chat_display" not in st.session_state:
    st.session_state.chat_display = []      # List[dict] for rendering
if "tool_calls_count" not in st.session_state:
    st.session_state.tool_calls_count = 0
if "total_messages" not in st.session_state:
    st.session_state.total_messages = 0

# ─────────────────────────────────────────────────────────────────────────────
# LLM + Agent (cached)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_agent(model: str, temperature: float):
    llm = ChatAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"), model=model, temperature=temperature, max_tokens=4096)
    return create_agent(model=llm, tools=TOOLS, system_prompt=SYSTEM_PROMPT)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def extract_code_blocks(text: str):
    """Return list of code strings found in ```python blocks."""
    return re.findall(r"```python\n?(.*?)```", text, re.DOTALL)


def render_message_content(content: str):
    """Render message with code blocks highlighted."""
    parts = re.split(r"(```(?:python)?\n?.*?```)", content, flags=re.DOTALL)
    for part in parts:
        if part.startswith("```"):
            lang = "python" if "```python" in part else "text"
            code = re.sub(r"```(?:python)?\n?", "", part).rstrip("`").strip()
            st.code(code, language=lang)
        elif part.strip():
            st.markdown(part)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 烙 AI Coding Assistant")
    st.markdown("*Powered by Claude + LangChain*")
    st.divider()

    st.markdown("### ⚙️ Settings")
    model = st.selectbox(
        "Model",
        ["global.anthropic.claude-haiku-4-5-20251001-v1:0",
         "global.anthropic.claude-opus-4-5-20251101-v1:0",
         "global.anthropic.claude-sonnet-4-6"
         ],
        index=0,
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1,
                            help="Lower = more precise code, Higher = more creative")

    st.divider()
    st.markdown("###  Session Stats")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
          <div class="stat-number">{st.session_state.total_messages}</div>
          <div class="stat-label">Messages</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box">
          <div class="stat-number">{st.session_state.tool_calls_count}</div>
          <div class="stat-label">Tool Calls</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### ️ Available Tools")
    tools_info = [
        ("▶️", "execute_python_code", "Run Python code"),
        ("✨", "format_python_code",  "Format with Black"),
        ("", "save_code_to_file",   "Save to workspace"),
        ("", "read_file",           "Read saved file"),
        ("", "list_workspace_files","List saved files"),
    ]
    for icon, name, desc in tools_info:
        st.markdown(f"<span class='badge'>{icon} {name}</span>", unsafe_allow_html=True)

    st.divider()
    st.markdown("###  Example Prompts")
    examples = [
        "Write a binary search function and test it",
        "Create a class for a Stack with push/pop/peek",
        "Debug this code: def fib(n): return fib(n-1)+fib(n-2)",
        "Write a decorator that measures function execution time",
        "Create a simple REST API client for GitHub",
    ]
    for ex in examples:
        if st.button(ex, key=ex, use_container_width=True):
            st.session_state["prefill"] = ex

    st.divider()
    if st.button("️ Clear Conversation", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.chat_display = []
        st.session_state.tool_calls_count = 0
        st.session_state.total_messages = 0
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Main area
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## 烙 AI Coding Assistant")
st.markdown("*Ask me to write, debug, explain, or run Python code.*")
st.divider()

# Chat history
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_display:
        st.markdown("""
        <div style='text-align:center; padding: 60px 0; color: #8b949e;'>
            <h3> Welcome to the AI Coding Assistant!</h3>
            <p>Ask me anything about Python — I can write, run, debug, and explain code.</p>
            <p style='font-size:0.85em;'>Use the example prompts in the sidebar to get started.</p>
        </div>""", unsafe_allow_html=True)
    else:
        for item in st.session_state.chat_display:
            if item["role"] == "user":
                st.markdown(f"<div class='user-bubble'> **You**<br>{item['content']}</div>",
                            unsafe_allow_html=True)

            elif item["role"] == "assistant":
                with st.container():
                    st.markdown("<div class='assistant-bubble'>烙 <b>Assistant</b></div>",
                                unsafe_allow_html=True)
                    render_message_content(item["content"])

            elif item["role"] == "tool_call":
                tool_name = item["tool"]
                args = item.get("args", {})
                st.markdown(
                    f"<div class='tool-bubble'> <b>Tool called:</b> {tool_name}</div>",
                    unsafe_allow_html=True,
                )
                # Show code argument properly if present
                if "code" in args:
                    st.code(args["code"], language="python")
                elif args:
                    for k, v in args.items():
                        st.markdown(f"**{k}:** `{str(v)[:200]}`")

            elif item["role"] == "tool_result":
                content = item["content"]
                is_error = content.startswith("ERROR")
                icon  = "❌" if is_error else "✅"
                color = "#ff5555" if is_error else "#50fa7b"
                st.markdown(
                    f"<div style='border-left:3px solid {color}; padding:6px 12px; "
                    f"margin:4px 0 4px 20px; background:#0d1117; border-radius:4px;'>"
                    f"{icon} <b style='color:{color}'>Output</b></div>",
                    unsafe_allow_html=True,
                )
                st.code(content, language="text")

# ─────────────────────────────────────────────────────────────────────────────
# Input
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
prefill = st.session_state.pop("prefill", "")

with st.form("chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_area(
            "Your message",
            value=prefill,
            placeholder="Ask me to write, debug, explain, or run Python code...",
            height=80,
            label_visibility="collapsed",
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Send ▶", use_container_width=True, type="primary")

# ─────────────────────────────────────────────────────────────────────────────
# Process message
# ─────────────────────────────────────────────────────────────────────────────
if submitted and user_input.strip():
    agent = get_agent(model, temperature)

    # Add to display
    st.session_state.chat_display.append({"role": "user", "content": user_input})
    st.session_state.messages.append(HumanMessage(content=user_input))
    st.session_state.total_messages += 1

    with st.spinner("樂 Thinking..."):
        result = agent.invoke({"messages": st.session_state.messages})

    # Process all new messages returned by the agent
    new_messages = result["messages"][len(st.session_state.messages):]

    for msg in new_messages:
        st.session_state.messages.append(msg)

        # AI message with text content
        if isinstance(msg, AIMessage):
            # Tool calls embedded in AI message
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    st.session_state.chat_display.append({
                        "role": "tool_call",
                        "tool": tc.get("name", "unknown"),
                        "args": tc.get("args", {}),        # store full args
                    })
                    st.session_state.tool_calls_count += 1

            # Text content from AI
            text = msg.content if isinstance(msg.content, str) else ""
            if not text and isinstance(msg.content, list):
                text = " ".join(
                    b.get("text", "") for b in msg.content
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            if text.strip():
                st.session_state.chat_display.append({
                    "role": "assistant",
                    "content": text,
                })

        # Tool result message
        elif isinstance(msg, ToolMessage):
            st.session_state.chat_display.append({
                "role": "tool_result",
                "content": str(msg.content),
            })

    st.rerun()
