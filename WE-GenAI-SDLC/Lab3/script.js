'use strict';

// ---------------------------------------------------------------------------
// Constants — declared at top so all functions can reference them
// ---------------------------------------------------------------------------
const MAX_EXPR_LENGTH   = 50;
const ALLOWED_NUMBERS   = new Set(['0','1','2','3','4','5','6','7','8','9','.']);
const ALLOWED_OPERATORS = new Set(['+', '-', '*', '/']);

// ---------------------------------------------------------------------------
// Safe recursive-descent math evaluator — no dynamic code execution.
// Supports: +  -  *  /  parentheses  decimals  operator precedence
// ---------------------------------------------------------------------------
function safeEval(expr) {
  let i = 0;

  function parseExpression() {
    let left = parseTerm();
    while (i < expr.length && (expr[i] === '+' || expr[i] === '-')) {
      const op = expr[i++];
      const right = parseTerm();
      left = op === '+' ? left + right : left - right;
    }
    return left;
  }

  function parseTerm() {
    let left = parsePrimary();
    while (i < expr.length && (expr[i] === '*' || expr[i] === '/')) {
      const op = expr[i++];
      const right = parsePrimary();
      if (op === '/') {
        if (right === 0) throw new Error('Division by zero');
        left = left / right;
      } else {
        left = left * right;
      }
    }
    return left;
  }

  function parsePrimary() {
    if (expr[i] === '(') {
      i++;                          // consume '('
      const val = parseExpression();
      if (expr[i] === ')') i++;     // consume ')'
      return val;
    }
    const start = i;
    while (i < expr.length && /[\d.]/.test(expr[i])) i++;
    if (i === start) throw new Error('Unexpected token at position ' + i);
    const num = parseFloat(expr.slice(start, i));
    if (isNaN(num)) throw new Error('Invalid number');
    return num;
  }

  const result = parseExpression();
  if (i !== expr.length) throw new Error('Unexpected token at position ' + i);
  return result;
}

// ---------------------------------------------------------------------------

const expressionEl = document.getElementById('expression');
const resultEl     = document.getElementById('result');

let currentInput  = '';
let expression    = '';
let justEvaluated = false;

function updateDisplay() {
  expressionEl.textContent = expression;
  resultEl.textContent     = currentInput || '0';
}

// Consolidated error helper — used by calculate() instead of repeating state resets
function showError() {
  expressionEl.textContent = '';
  resultEl.textContent     = 'Error';
  currentInput             = '';
  expression               = '';
  justEvaluated            = false;
}

function appendNumber(value) {
  if (justEvaluated) {
    currentInput = '';
    expression = '';
    justEvaluated = false;
  }

  // Enforce max expression length to prevent DoS via huge strings
  if (expression.length >= MAX_EXPR_LENGTH) return;

  // Prevent multiple decimals in the current number segment
  // currentInput only ever holds the segment after the last operator, so a
  // simple includes() check is sufficient — no need to split by operators.
  if (value === '.' && currentInput.includes('.')) return;

  // Prevent leading zeros (e.g. "007") — keep expression in sync
  if (value !== '.' && currentInput === '0') {
    currentInput = value;
    expression   = expression.slice(0, -1) + value;
  } else {
    currentInput += value;
    expression   += value;
  }

  updateDisplay();
}

function appendOperator(op) {
  // Enforce max expression length to prevent DoS via huge strings
  if (expression.length >= MAX_EXPR_LENGTH) return;

  if (justEvaluated) {
    // Continue from the result
    expression = currentInput + op;
    justEvaluated = false;
  } else {
    if (currentInput === '' && expression === '') return;

    // Replace trailing operator if user changes their mind
    // Reuse ALLOWED_OPERATORS Set instead of rebuilding an array
    if (ALLOWED_OPERATORS.has(expression.slice(-1))) {
      expression = expression.slice(0, -1) + op;
    } else {
      expression += op;
    }
  }

  currentInput = '';
  updateDisplay();
}

function calculate() {
  if (expression === '') return;

  // Do not evaluate if expression ends with an operator
  if (ALLOWED_OPERATORS.has(expression.slice(-1))) return;

  // Strict whitelist: only digits, operators, dots, parentheses
  if (!/^[\d+\-*/().]+$/.test(expression)) {
    showError();
    return;
  }

  try {
    const value = safeEval(expression);

    if (!isFinite(value)) {
      showError();
      return;
    }

    // Show full expression on the top line, rounded result on the bottom line
    expressionEl.textContent = expression + ' =';
    const rounded  = parseFloat(value.toPrecision(12));
    currentInput   = String(rounded);
    expression     = currentInput;
    resultEl.textContent = currentInput;
    justEvaluated  = true;
  } catch {
    showError();
  }
}

function clearAll() {
  currentInput = '';
  expression = '';
  justEvaluated = false;
  updateDisplay();
}

function deleteLast() {
  if (justEvaluated) {
    clearAll();
    return;
  }
  expression = expression.slice(0, -1);
  // Re-derive currentInput from the last number segment so it stays in sync
  // even when deleting across an operator boundary (fixes desync bug)
  const match  = expression.match(/[\d.]*$/);
  currentInput = match ? match[0] : '';
  updateDisplay();
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------

// Button clicks — use event delegation on the grid container
document.querySelector('.buttons').addEventListener('click', function (e) {
  const btn = e.target.closest('.btn');
  if (!btn) return;

  const action = btn.dataset.action;
  const value = btn.dataset.value;

  if (action === 'clear') {
    clearAll();
  } else if (action === 'delete') {
    deleteLast();
  } else if (action === 'equals') {
    calculate();
  } else if (value !== undefined) {
    // Whitelist check guards against tampered data-value attributes
    if (ALLOWED_OPERATORS.has(value)) {
      appendOperator(value);
    } else if (ALLOWED_NUMBERS.has(value)) {
      appendNumber(value);
    }
    // Unknown values are silently ignored
  }
});

// Keyboard input — reuse ALLOWED_OPERATORS Set instead of repeating the list
document.addEventListener('keydown', function (e) {
  if (e.key >= '0' && e.key <= '9') {
    appendNumber(e.key);
  } else if (e.key === '.') {
    appendNumber('.');
  } else if (ALLOWED_OPERATORS.has(e.key)) {
    appendOperator(e.key);
  } else if (e.key === 'Enter' || e.key === '=') {
    calculate();
  } else if (e.key === 'Backspace') {
    deleteLast();
  } else if (e.key === 'Escape') {
    clearAll();
  }
});
