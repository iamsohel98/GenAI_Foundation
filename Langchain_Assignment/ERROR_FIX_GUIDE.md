# ❌ ValidationError Fix Guide

## The Error You Got:

```
ValidationError: 1 validation error for ChatAnthropic
api_key
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
```

---

## Root Causes:

### ❌ WRONG - What was causing the error:

```python
# MISTAKE 1: Wrong environment variable name
api_key = os.environ.get("KEY")  # ← Returns None!

# MISTAKE 2: Invalid custom base_url
llm = ChatAnthropic(
    model="global.anthropic.claude-haiku-4-5-20251001-v1:0",
    api_key=os.environ.get("KEY"),  # ← None!
    base_url="https://llmgw-wp.tekstac.com",  # ← Invalid endpoint!
    max_tokens=200
)
# Result: api_key=None → ValidationError!
```

---

## ✅ CORRECT - How to fix it:

### Step 1: Set the correct environment variable

```bash
# Option A: Export in terminal
export ANTHROPIC_API_KEY="sk-ant-your-actual-key-here"

# Option B: Create .env file in project directory
echo "ANTHROPIC_API_KEY=sk-ant-your-actual-key-here" > .env
```

### Step 2: Use CORRECT variable names and NO custom base_url

```python
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# Load .env file
load_dotenv(override=True)

# CORRECT: Use ANTHROPIC_API_KEY (not "KEY")
api_key = os.environ.get("ANTHROPIC_API_KEY")

# CORRECT: Validate BEFORE creating instance
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set!")

# CORRECT: DO NOT use custom base_url
llm = ChatAnthropic(
    model="global.anthropic.claude-opus-4-5-20251101-v1:0",
    api_key=api_key,  # ← Now it's a valid string!
    temperature=0.7,
    max_tokens=1024
    # NO base_url parameter!
)
print("✅ LLM initialized successfully")
```

---

## Comparison Table:

| Issue | ❌ WRONG | ✅ CORRECT |
|-------|---------|-----------|
| **Environment Variable** | `"KEY"` | `"ANTHROPIC_API_KEY"` |
| **Result** | Returns `None` | Returns valid key string |
| **base_url Parameter** | `"https://llmgw-wp.tekstac.com"` | Remove it completely |
| **Validation** | None | `if not api_key: raise ValueError(...)` |
| **Error** | ValidationError: api_key is None | ✅ Initializes successfully |

---

## Quick Fix Checklist:

- [ ] Set `export ANTHROPIC_API_KEY='your-key'` or create `.env` file
- [ ] Check environment variable is actually set: `echo $ANTHROPIC_API_KEY`
- [ ] Use correct var name: `os.environ.get("ANTHROPIC_API_KEY")`
- [ ] Remove `base_url` parameter
- [ ] Remove `"KEY"` references
- [ ] Add validation: `if not api_key: raise ValueError(...)`
- [ ] Test: `python -c "import os; print(os.environ.get('ANTHROPIC_API_KEY'))"`

---

## Debugging Commands:

```bash
# Check if env var is set
echo $ANTHROPIC_API_KEY

# Test Python import
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get('ANTHROPIC_API_KEY')
print(f'API Key Set: {bool(key)}')
print(f'Key Length: {len(key) if key else 0}')
"

# Check .env file exists
cat .env | grep ANTHROPIC_API_KEY
```

---

## Files Updated:

1. ✅ **Exercise_01_PromptTemplates_Chaining_FIXED.ipynb**
   - Correct environment variable usage
   - No custom base_url
   - Proper validation
   - All 10 blocks with correct code

---

## Running the Fixed Notebook:

```bash
# Set environment
export ANTHROPIC_API_KEY='sk-your-actual-key'

# Run notebook (if using Jupyter)
jupyter notebook Exercise_01_PromptTemplates_Chaining_FIXED.ipynb

# Or run via Python
python -m nbconvert --execute Exercise_01_PromptTemplates_Chaining_FIXED.ipynb
```

