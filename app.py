import io
import base64
from flask import Flask, render_template, request
import sympy as sp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

def safe_continuous_domain(expr, symbol):
    if not expr.has(symbol):
        return sp.Reals
    return sp.calculus.util.continuous_domain(expr, symbol, sp.Reals)

def get_endpoints(domain):
    if domain == sp.Reals:
        return []
    if isinstance(domain, sp.Interval):
        return [domain.start, domain.end]
    if isinstance(domain, sp.Union):
        pts = []
        for part in domain.args:
            if isinstance(part, sp.Interval):
                pts.extend([part.start, part.end])
        return pts
    return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    user_input = request.form.get('function_input', 'x**2')
    xo_str = request.form.get('x_point', '0')

    try:
        xo_val = float(xo_str)
    except:
        xo_val = 0.0

    x = sp.symbols('x')
    e = sp.exp(1)
    try:
        f = sp.sympify(user_input, locals={'e': e, 'x': x})
    except Exception as err:
        return render_template('index.html', error="Invalid function. Use * for multiply and ** for power.")

    # Core calculations for BACII
    domain = safe_continuous_domain(f, x)
    horiz_asymp = sp.limit(f, x, sp.oo)
    f_prime = sp.diff(f, x)
    f_double = sp.diff(f_prime, x)

    # Intercepts
    try:
        y_int = float(f.subs(x, 0))
    except:
        y_int = "undefined"
    x_ints = [float(r) for r in sp.solve(f, x) if r.is_real]

    # Critical points
    crit_points = [float(r) for r in sp.solve(f_prime, x) if r.is_real]

    # Inflection points
    inflection_points = [float(r) for r in sp.solve(f_double, x) if r.is_real]

    # Vertical asymptotes
    vert_asym = get_endpoints(domain)
    # Filter out infinities
    vert_asym = [v for v in vert_asym if v not in (sp.oo, -sp.oo, float('inf'), float('-inf'))]

    # Monotonicity summary
    mono_info = []
    sorted_crits = sorted(crit_points)
    test_points = []
    if sorted_crits:
        test_points.append(sorted_crits[0] - 1)
        for i in range(len(sorted_crits) - 1):
            test_points.append((sorted_crits[i] + sorted_crits[i+1]) / 2)
        test_points.append(sorted_crits[-1] + 1)
    for tp in test_points:
        try:
            val = float(f_prime.subs(x, tp))
            direction = "increasing ↑" if val > 0 else "decreasing ↓"
            mono_info.append(f"x={round(tp,2)}: {direction}")
        except:
            pass

    # Steps for display
    steps = [
        {
            "num": 1,
            "title": "1. Domain",
            "math": sp.latex(domain),
            "explain": "The set of all real numbers x for which f(x) is defined."
        },
        {
            "num": 2,
            "title": "2. Intercepts",
            "math": f"y\\text{{-intercept: }}{y_int}\\quad x\\text{{-intercepts: }}{x_ints}",
            "explain": "Points where the graph crosses the x-axis and y-axis."
        },
        {
            "num": 3,
            "title": "3. Asymptotes",
            "math": f"\\text{{Vertical: }}x = {vert_asym}\\quad \\text{{Horizontal: }}y = {sp.latex(horiz_asymp)}",
            "explain": "Lines that the graph approaches but never touches."
        },
        {
            "num": 4,
            "title": "4. First Derivative f'(x)",
            "math": f"f'(x) = {sp.latex(f_prime)}",
            "explain": "Used to find increasing/decreasing intervals and critical points."
        },
        {
            "num": 5,
            "title": "5. Critical Points",
            "math": f"x = {crit_points}",
            "explain": "Points where f'(x) = 0 (possible local max/min). " + (", ".join(mono_info) if mono_info else ""),
        },
        {
            "num": 6,
            "title": "6. Second Derivative f''(x)",
            "math": f"f''(x) = {sp.latex(f_double)}",
            "explain": "Used to determine concavity and inflection points."
        },
        {
            "num": 7,
            "title": "7. Inflection Points",
            "math": f"x = {inflection_points}",
            "explain": "Points where concavity changes (f''(x) = 0 changes sign)."
        }
    ]

    # Generate Plot
    fig, ax = plt.subplots(figsize=(10, 6.5))
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#1e293b')

    f_lambdified = sp.lambdify(x, f, modules=['numpy'])
    x_vals = np.linspace(-20, 20, 4000)

    for va in vert_asym:
        x_vals = x_vals[np.abs(x_vals - float(va)) > 0.05]

    y_vals = f_lambdified(x_vals)

    # Mask large jumps (discontinuities)
    y_masked = np.ma.array(y_vals)
    y_masked[np.abs(y_vals) > 50] = np.ma.masked
    diff = np.abs(np.diff(y_vals))
    jumps = np.where(diff > 30)[0]
    for j in jumps:
        y_masked[j] = np.ma.masked
        y_masked[j+1] = np.ma.masked

    ax.plot(x_vals, y_masked, color='#38bdf8', linewidth=2.5, label='f(x)', zorder=5)

    # Vertical asymptotes
    for va in vert_asym:
        ax.axvline(x=float(va), color='#f87171', linestyle='--', linewidth=1.5, label=f'VA: x={float(va):.2f}', zorder=4)

    # Horizontal asymptote
    try:
        ha = float(horiz_asymp)
        if abs(ha) < 50:
            ax.axhline(y=ha, color='#4ade80', linestyle='--', linewidth=1.5, label=f'HA: y={ha:.2f}', zorder=4)
    except:
        pass

    # Tangent line
    try:
        yo = float(f.subs(x, xo_val))
        slope = float(f_prime.subs(x, xo_val))
        ax.axline((xo_val, yo), slope=slope, color='#fb923c', linestyle='--', linewidth=2, label=f'Tangent at x={xo_val}', zorder=6)
        ax.plot(xo_val, yo, 'o', color='#fb923c', markersize=8, zorder=7)
    except:
        pass

    # Critical points
    for cp in crit_points:
        try:
            ycp = float(f.subs(x, cp))
            if abs(ycp) < 50:
                ax.plot(cp, ycp, 's', color='#facc15', markersize=8, zorder=8, label=f'CP: ({cp:.2f}, {ycp:.2f})')
        except:
            pass

    ax.set_ylim(-20, 20)
    ax.set_xlim(-20, 20)
    ax.grid(True, alpha=0.2, color='#94a3b8')
    ax.axhline(0, color='#94a3b8', linewidth=0.8, alpha=0.5)
    ax.axvline(0, color='#94a3b8', linewidth=0.8, alpha=0.5)
    ax.set_title(f'f(x) = {user_input}', fontsize=14, color='#e2e8f0', pad=12)
    ax.tick_params(colors='#94a3b8')
    for spine in ax.spines.values():
        spine.set_edgecolor('#334155')

    legend = ax.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#e2e8f0', fontsize=9)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=180, facecolor='#0f172a')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    results = {
        "function": user_input,
        "plot_url": plot_url,
        "steps": steps,
        "xo": xo_val
    }

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
