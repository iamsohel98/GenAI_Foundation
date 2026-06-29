# LangChain Key Concepts & Takeaways

## 1. PromptTemplate — Simple text templates with variables

**What it is:**
- Basic template for simple text prompts
- Supports variable substitution using curly braces `{}`

**Example:**
```python
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["topic"],
    template="Explain {topic} in simple terms."
)
result = prompt.format(topic="machine learning")
```

---

## 2. ChatPromptTemplate — Multi-message templates with roles

**What it is:**
- Advanced template for conversational AI
- Supports multiple roles: system, human, AI
- Better for chat-based LLMs

**Example:**
```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "What is {topic}?"),
])
messages = prompt.format_messages(topic="AI")
```

---

## 3. FewShotPromptTemplate — Learning from examples

**What it is:**
- Provides examples to guide the LLM behavior
- Ensures consistent formatting and response style
- Uses examples in the prompt context

**Example:**
```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

examples = [
    {"input": "happy", "output": "sad"},
    {"input": "tall", "output": "short"},
]

example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="Input: {input}\nOutput: {output}"
)

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Input: {word}\nOutput:",
    input_variables=["word"]
)
```

---

## 4. LCEL (Pipe operator `|`) — Chain components

**What it is:**
- LangChain Expression Language (LCEL)
- Uses pipe operator `|` to chain components
- Flow: prompt → llm → parser

**Example:**
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser

chain = prompt | llm | StrOutputParser()
result = chain.invoke({"topic": "AI"})
```

**Chain Anatomy:**
```
PromptTemplate  →  ChatAnthropic  →  OutputParser
     (input)          (process)        (format output)
```

---

## 5. RunnableParallel — Execute multiple chains simultaneously

**What it is:**
- Execute multiple chains in parallel
- Combines results from different pipelines
- Useful for multi-task processing

**Example:**
```python
from langchain_core.runnables import RunnableParallel

parallel_chain = RunnableParallel(
    summary=summary_chain,
    keywords=keywords_chain,
    sentiment=sentiment_chain
)

results = parallel_chain.invoke({"text": input_text})
# Returns: {"summary": "...", "keywords": [...], "sentiment": "positive"}
```

---

## 6. Conditional Routing — Branch based on results

**What it is:**
- Execute different chains based on intermediate results
- Uses RunnableBranch for conditional logic
- Route requests to appropriate handler

**Example:**
```python
from langchain_core.runnables import RunnableBranch

route_chain = RunnableBranch(
    (lambda x: "python" in x.lower(), python_chain),
    (lambda x: "javascript" in x.lower(), js_chain),
    default_chain  # fallback
)

result = route_chain.invoke("How to print in Python?")
```

---

## 7. Output Parsers — Extract structured data

**What it is:**
- Convert LLM output into structured formats
- Supports JSON, Pydantic models, CSV, etc.
- Ensures predictable output format

**Types:**

### a) StrOutputParser
```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
chain = prompt | llm | parser
result = chain.invoke({...})  # Returns string
```

### b) JsonOutputParser
```python
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

parser = JsonOutputParser(pydantic_object=Person)
chain = prompt | llm | parser
result = chain.invoke({...})  # Returns Person object
```

### c) PydanticOutputParser
```python
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=Person)
chain = prompt | llm | parser
```

---

## Complete Example: Multi-Concept Application

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from pydantic import BaseModel

# Define output structure
class ArticleAnalysis(BaseModel):
    title: str
    summary: str
    keywords: list[str]
    sentiment: str

# Create prompts
summary_prompt = ChatPromptTemplate.from_template(
    "Summarize this article: {article}"
)

keywords_prompt = ChatPromptTemplate.from_template(
    "Extract keywords from: {article}"
)

sentiment_prompt = ChatPromptTemplate.from_template(
    "Analyze sentiment of: {article}"
)

# Initialize LLM and parser
llm = ChatAnthropic(model="claude-opus-4-5")
parser = JsonOutputParser(pydantic_object=ArticleAnalysis)

# Create chains
summary_chain = summary_prompt | llm | StrOutputParser()
keywords_chain = keywords_prompt | llm | StrOutputParser()
sentiment_chain = sentiment_prompt | llm | StrOutputParser()

# Parallel execution
parallel_chain = RunnableParallel(
    summary=summary_chain,
    keywords=keywords_chain,
    sentiment=sentiment_chain
)

# Execute
result = parallel_chain.invoke({"article": "Your article text here"})
```

---

## LangChain Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      LangChain Application                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PromptTemplate/ChatPromptTemplate/FewShotPromptTemplate       │
│           (Format user input into prompt)                       │
│                      ↓                                           │
│                   LLM Model                                      │
│            (ChatAnthropic, OpenAI, etc)                          │
│                      ↓                                           │
│                 Output Parser                                    │
│         (Extract & format structured data)                       │
│                      ↓                                           │
│              Structured Output                                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Optional: RunnableParallel, Routing, Memory, Tools, Agents   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Best Practices

1. **Always validate API keys** before making LLM calls
2. **Use FewShotPromptTemplate** for consistent output formatting
3. **Chain with pipes `|`** for clean, readable code
4. **Use Output Parsers** for structured, type-safe results
5. **Leverage RunnableParallel** for multi-task efficiency
6. **Implement error handling** in production chains
7. **Test chains** with sample inputs before deployment

---

## Quick Reference

```python
# Simple chain
result = prompt | llm | StrOutputParser()

# With structured output
result = prompt | llm | JsonOutputParser()

# Parallel execution
results = RunnableParallel(chain1=..., chain2=...).invoke({...})

# Conditional routing
chain = RunnableBranch((condition, handler), default).invoke({...})

# Format and invoke
chain.invoke({"variable": "value"})

# Batch processing
results = chain.batch([{"var": "val1"}, {"var": "val2"}])
```

