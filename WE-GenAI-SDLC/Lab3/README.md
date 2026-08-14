# Calculator Web Application

A clean, responsive calculator built with plain HTML, CSS, and JavaScript — no frameworks or dependencies required.

---

## Features

- **Basic Operations** — Addition (`+`), Subtraction (`−`), Multiplication (`×`), Division (`÷`)
- **Decimal Input** — Supports floating-point numbers (`.`)
- **Chained Expressions** — Two-line display: expression on top, result below
- **Clear (AC)** — Resets the entire calculation
- **Delete (⌫)** — Removes the last entered character
- **Keyboard Support** — Full keyboard input for fast use
- **Error Handling** — Displays `Error` for invalid expressions or division by zero

---

## Project Structure

```
Lab3/
├── index.html   # Calculator layout and button structure
├── style.css    # Styling, colors, and responsive layout
├── script.js    # Calculator logic and event handling
└── README.md    # Project documentation
```

---

## Getting Started

No installation or build step needed.

1. Download or clone the project folder.
2. Open `index.html` in any modern web browser.

```
Double-click index.html   →   Opens in your default browser
```

---

## How to Use

| Action | Button | Keyboard |
|---|---|---|
| Enter a number | `0` – `9` | `0` – `9` |
| Decimal point | `.` | `.` |
| Add | `+` | `+` |
| Subtract | `−` | `-` |
| Multiply | `×` | `*` |
| Divide | `÷` | `/` |
| Calculate result | `=` | `Enter` or `=` |
| Delete last character | `⌫` | `Backspace` |
| Clear all | `AC` | `Escape` |

---

## Button Layout

```
┌─────┬──────────┬─────┐
│  ÷  │    AC    │  ⌫  │
├─────┼─────┬────┴─────┤
│  ×  │  7  │  8  │  9 │
├─────┼─────┼─────┼────┤
│  −  │  4  │  5  │  6 │
├─────┼─────┼─────┼────┤
│  +  │  1  │  2  │  3 │
├─────┼──────────┬─────┤
│  =  │    0     │  .  │
└─────┴──────────┴─────┘
```

---

## Color Scheme

| Element | Color |
|---|---|
| Background | Dark navy (`#1a1a2e`) |
| Display | Pink (`#ffb6c1`) |
| Expression text | Dark pink (`#a0003a`) |
| Operator buttons (`÷ × − +`) | Yellow (`#ffd700`) |
| Number buttons (`0–9`, `.`) | Sky blue (`#87ceeb`) |
| AC button | Red (`#e74c3c`) |
| Delete button | Sky blue (`#87ceeb`) |
| Equals button | Sky blue (`#87ceeb`) |

---

## File Details

### `index.html`
Defines the structure using semantic HTML. Each button uses `data-value` or `data-action` attributes that JavaScript reads to determine what to do when clicked.

### `style.css`
Styles the calculator using CSS Grid for the button layout. The `btn-wide` class spans a button across 2 columns (used for `AC` and `0`).

### `script.js`
Handles all calculator logic:
- Tracks `expression` (full input string) and `currentInput` (current number segment)
- Uses `Function()` for safe expression evaluation (only digits, operators, and `.` are allowed through a regex guard)
- Supports chained operations and operator replacement (pressing `+` then `−` replaces the operator)

---

## Browser Support

Works in all modern browsers that support ES6+:

- Google Chrome
- Mozilla Firefox
- Microsoft Edge
- Safari

---

## License

This project is for educational purposes.
