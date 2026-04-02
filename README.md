# BACII Graph Sketcher

A web tool made specifically for Cambodian Grade 12 students preparing for the BACII Mathematics exam.

## Features

- Domain analysis
- x-intercepts and y-intercepts
- Vertical and horizontal asymptotes
- First derivative f'(x) with critical points
- Monotonicity (increasing/decreasing intervals)
- Second derivative f''(x) with inflection points
- Beautiful dark-themed graph with tangent line, asymptotes, and critical points marked
- Step-by-step solution format similar to BACII marking scheme

## Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

Then open http://localhost:5000 in your browser.

## Deploy (Render / Railway / Fly.io)

Use `gunicorn` as the start command:

```
gunicorn app:app
```

## Function Input Syntax

| Math notation | Input |
|---|---|
| x² | `x**2` |
| x³ | `x**3` |
| (x²−1)/(x²−4) | `(x**2-1)/(x**2-4)` |
| e^(−x²) | `e**(-x**2)` |
| sin(x) | `sin(x)` |
| ln(x) | `log(x)` |

## Tech Stack

- **Backend**: Flask + SymPy (symbolic math) + NumPy + Matplotlib
- **Frontend**: Vanilla HTML/CSS with MathJax for LaTeX rendering
- **Fonts**: Playfair Display, DM Sans, Space Mono (Google Fonts)
