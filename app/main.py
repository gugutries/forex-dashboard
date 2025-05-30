from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app import forex_utils
import plotly.graph_objects as go
from plotly.io import to_html

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        usd_inr, inr_usd, updated = forex_utils.fetch_usd_inr_rate()
        forex_utils.store_rates(usd_inr, inr_usd)
        df = forex_utils.get_last_forex_rates()
    except Exception as e:
        return f"<h1 style='color:red;'>Error: {e}</h1>"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["usd_to_inr"], mode="lines+markers", name="USD→INR"))
    fig.update_layout(template="plotly_dark", title="USD → INR Trend", xaxis_title="Time", yaxis_title="Rate")

    plot_html = to_html(fig, include_plotlyjs="cdn", full_html=False)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "usd_inr": usd_inr,
        "inr_usd": inr_usd,
        "updated": updated,
        "plot_html": plot_html
    })
    # HTML
    return f"""
    <html>
        <head>
            <meta charset='utf-8'>
            <title>💱 Forex Rates Live</title>
            <style>
                body {{
                    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
                    font-family: 'Segoe UI', sans-serif;
                    color: #fff;
                    padding: 20px;
                    text-align: center;
                }}
                h1 {{ font-size: 3em; margin-bottom: 0; }}
                h2 {{ color: #FFD700; margin-top: 0.2em; }}
                .glow {{
                    text-shadow: 0 0 10px #FFD700, 0 0 20px #FFA500;
                }}
            </style>
        </head>
        <body>
            <h1 class="glow">💸 USD → INR = ₹{usd_inr}</h1>
            <h2>INR → USD = ${inr_usd}</h2>
            <p><small>Updated: {updated}</small></p>
            {to_html(fig, include_plotlyjs='cdn', full_html=False)}
        </body>
    </html>
    """

