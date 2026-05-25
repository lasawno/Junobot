import os
from datetime import datetime, timezone
from decimal import Decimal

import streamlit as st

from junobot.brokers.base import OrderSide
from junobot.config import ConfigError, load_broker

st.set_page_config(page_title="JUNOBOT TERMINAL", page_icon="📈", layout="wide")


# --- Terminal aesthetic CSS -------------------------------------------------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Major+Mono+Display&display=swap');

:root {
  --bg: #0a0e0d;
  --bg-card: #11181a;
  --border: #1d2a25;
  --border-bright: #2a3f35;
  --text: #d4d4d4;
  --text-dim: #6a7a72;
  --green: #00ff88;
  --green-dim: #00b362;
  --amber: #ffa724;
  --red: #ff3866;
  --shadow-green: 0 0 12px rgba(0,255,136,0.35);
  --shadow-amber: 0 0 12px rgba(255,167,36,0.35);
}

.stApp, .main, body {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'IBM Plex Mono', ui-monospace, Menlo, monospace !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }

h1, h2, h3, h4, h5 {
  font-family: 'IBM Plex Mono', monospace !important;
  color: var(--text) !important;
  letter-spacing: 0.02em;
}

/* Top status bar */
.term-statusbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: linear-gradient(180deg, #0e1614 0%, #0a0e0d 100%);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}
.term-statusbar .left { display: flex; gap: 18px; align-items: center; }
.term-statusbar .right { display: flex; gap: 18px; align-items: center; color: var(--text-dim); }
.term-statusbar .brand { color: var(--green); text-shadow: var(--shadow-green); font-weight: 700; }
.term-statusbar .pill {
  padding: 2px 8px;
  border: 1px solid var(--border-bright);
  border-radius: 2px;
  font-size: 10px;
}
.term-statusbar .pill.paper { color: var(--amber); border-color: var(--amber); }
.term-statusbar .pill.live { color: var(--red); border-color: var(--red); }
.term-statusbar .pill.market-open { color: var(--green); border-color: var(--green); }
.term-statusbar .pill.market-closed { color: var(--text-dim); }
.term-statusbar .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.term-statusbar .dot.green { background: var(--green); box-shadow: var(--shadow-green); }
.term-statusbar .dot.red { background: var(--red); }
.term-statusbar .dot.amber { background: var(--amber); box-shadow: var(--shadow-amber); }

/* Cards */
.term-card {
  border: 1px solid var(--border);
  background: var(--bg-card);
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 8px;
}
.term-card .card-title {
  font-size: 10px;
  color: var(--text-dim);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 6px;
  display: flex;
  justify-content: space-between;
}
.term-card .card-title .status {
  color: var(--green);
  text-shadow: var(--shadow-green);
}

/* Giant LCD-style number for headline PNL/equity */
.term-lcd {
  font-family: 'Major Mono Display', 'IBM Plex Mono', monospace;
  font-size: 56px;
  color: var(--green);
  text-shadow: var(--shadow-green);
  line-height: 1.0;
  letter-spacing: 0.02em;
  margin: 4px 0 6px 0;
}
.term-lcd.amber { color: var(--amber); text-shadow: var(--shadow-amber); }
.term-lcd.red { color: var(--red); }

.term-lcd-sub {
  display: flex;
  gap: 18px;
  color: var(--text-dim);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.term-lcd-sub b { color: var(--text); margin-left: 6px; }

/* Account row metrics */
.term-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  margin-top: 6px;
}
.term-metrics .cell {
  border-top: 1px solid var(--border);
  padding-top: 8px;
}
.term-metrics .label {
  font-size: 10px;
  color: var(--text-dim);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.term-metrics .value {
  font-size: 18px;
  color: var(--text);
  font-weight: 600;
  margin-top: 2px;
}

/* Streamlit-specific overrides for inputs and buttons */
.stTextInput input, .stNumberInput input {
  background: var(--bg) !important;
  color: var(--green) !important;
  border: 1px solid var(--border-bright) !important;
  font-family: 'IBM Plex Mono', monospace !important;
}
.stButton button {
  background: var(--bg-card) !important;
  color: var(--green) !important;
  border: 1px solid var(--green-dim) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
  font-size: 12px !important;
}
.stButton button:hover {
  border-color: var(--green) !important;
  box-shadow: var(--shadow-green);
}
.stButton button:disabled { opacity: 0.4; }

[data-testid="stDataFrame"] { background: var(--bg-card) !important; }
[data-testid="stDataFrame"] div { color: var(--text) !important; }

[data-testid="stMarkdownContainer"] code {
  background: var(--bg) !important;
  color: var(--amber) !important;
  border: 1px solid var(--border-bright);
  padding: 1px 6px;
}
hr { border-color: var(--border) !important; }
</style>
"""


@st.cache_resource
def get_broker():
    return load_broker()


def _password_gate() -> bool:
    expected = os.environ.get("JUNOBOT_DASHBOARD_PASSWORD")
    if not expected:
        return True
    if st.session_state.get("authed"):
        return True
    st.markdown("## 🔒 Junobot Terminal")
    pw = st.text_input("Password", type="password")
    if st.button("Unlock"):
        if pw == expected:
            st.session_state["authed"] = True
            st.rerun()
        else:
            st.error("Wrong password.")
    return False


def _status_bar(broker, paper: bool, market_open: bool) -> str:
    mode_pill = (
        '<span class="pill paper"><span class="dot amber"></span>PAPER</span>'
        if paper
        else '<span class="pill live"><span class="dot red"></span>LIVE</span>'
    )
    market_pill = (
        '<span class="pill market-open"><span class="dot green"></span>MARKET OPEN</span>'
        if market_open
        else '<span class="pill market-closed"><span class="dot"></span>MARKET CLOSED</span>'
    )
    now_utc = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return f"""
<div class="term-statusbar">
  <div class="left">
    <span class="brand">JUNOBOT TERMINAL</span>
    <span style="color: var(--text-dim);">v0.1 · {broker.name.upper()}</span>
    {mode_pill}
    {market_pill}
  </div>
  <div class="right">
    <span>SESSION · LIVE</span>
    <span style="color: var(--green);">{now_utc}</span>
  </div>
</div>
"""


def _wallet_card(acct, paper: bool) -> str:
    color = "amber" if paper else ""
    return f"""
<div class="term-card">
  <div class="card-title">
    <span>WALLET · ALPACA · {'PAPER' if paper else 'LIVE'}</span>
    <span class="status">● ACTIVE</span>
  </div>
  <div style="font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px;">
    ACCOUNT EQUITY · USD
  </div>
  <div class="term-lcd {color}">
    ${acct.equity:,.2f}
  </div>
  <div class="term-lcd-sub">
    <span>CASH<b>${acct.cash:,.0f}</b></span>
    <span>BUYING PWR<b>${acct.buying_power:,.0f}</b></span>
  </div>
</div>
"""


def _quote_card(symbol: str, bid: Decimal, ask: Decimal) -> str:
    spread = ask - bid
    return f"""
<div class="term-card">
  <div class="card-title">
    <span>QUOTE · {symbol}</span>
    <span class="status">● LIVE</span>
  </div>
  <div class="term-metrics" style="grid-template-columns: repeat(3, 1fr);">
    <div class="cell"><div class="label">BID</div><div class="value">${bid}</div></div>
    <div class="cell"><div class="label">ASK</div><div class="value">${ask}</div></div>
    <div class="cell"><div class="label">SPREAD</div><div class="value">${spread:.4f}</div></div>
  </div>
</div>
"""


def main():
    st.markdown(CSS, unsafe_allow_html=True)

    if not _password_gate():
        return

    try:
        broker = get_broker()
    except ConfigError as e:
        st.error(f"Config error: {e}")
        st.stop()
        return

    paper = getattr(broker, "paper", False)
    market_open = broker.is_market_open()

    st.markdown(_status_bar(broker, paper, market_open), unsafe_allow_html=True)

    acct = broker.get_account()

    # Top row: wallet card (3/5 width) + refresh button area (2/5)
    left, right = st.columns([3, 2])
    with left:
        st.markdown(_wallet_card(acct, paper), unsafe_allow_html=True)
    with right:
        st.markdown(
            f"""
<div class="term-card" style="height: 100%;">
  <div class="card-title">
    <span>SESSION</span>
    <span class="status">●</span>
  </div>
  <div class="term-metrics">
    <div class="cell"><div class="label">CURRENCY</div><div class="value">{acct.currency}</div></div>
    <div class="cell"><div class="label">BROKER</div><div class="value">{broker.name}</div></div>
  </div>
  <div style="margin-top: 14px;"></div>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("⟳ REFRESH", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

    # Positions
    st.markdown(
        '<div class="term-card" style="margin-top: 10px;"><div class="card-title">'
        '<span>POSITIONS</span><span class="status">●</span></div></div>',
        unsafe_allow_html=True,
    )
    positions = broker.get_positions()
    if not positions:
        st.markdown(
            '<div style="color: var(--text-dim); padding: 0 0 10px 4px; font-size: 12px; '
            'text-transform: uppercase; letter-spacing: 0.08em;">▒ NO OPEN POSITIONS</div>',
            unsafe_allow_html=True,
        )
    else:
        st.dataframe(
            [
                {
                    "SYMBOL": p.symbol,
                    "QTY": float(p.qty),
                    "AVG ENTRY": float(p.avg_entry_price),
                    "MARKET VALUE": float(p.market_value),
                    "UNREALIZED P/L": float(p.unrealized_pl),
                }
                for p in positions
            ],
            use_container_width=True,
            hide_index=True,
        )

    # Quote + order side-by-side
    left, right = st.columns(2)

    with left:
        st.markdown(
            '<div class="term-card"><div class="card-title">'
            '<span>QUOTE LOOKUP</span><span class="status">●</span></div></div>',
            unsafe_allow_html=True,
        )
        symbol_q = st.text_input("Symbol", value="AAPL", key="quote_symbol").upper().strip()
        if st.button("◉ GET QUOTE", key="quote_btn"):
            try:
                q = broker.get_quote(symbol_q)
                st.markdown(_quote_card(symbol_q, q.bid, q.ask), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Quote failed: {e}")

    with right:
        st.markdown(
            '<div class="term-card"><div class="card-title">'
            f'<span>PLACE MARKET ORDER</span><span class="status">{"●" if paper else "▲ LIVE"}</span>'
            "</div></div>",
            unsafe_allow_html=True,
        )
        if not paper:
            st.warning("⚠️ LIVE mode — orders use real money.")
        symbol_o = st.text_input("Symbol", value="AAPL", key="order_symbol").upper().strip()
        qty = st.number_input("Qty", min_value=0.0, value=1.0, step=1.0, key="order_qty")
        side = st.radio("Side", ["BUY", "SELL"], horizontal=True, key="order_side")
        confirm = st.checkbox("Confirm order", key="order_confirm")
        if st.button("► SUBMIT ORDER", key="order_btn", disabled=not confirm):
            try:
                order_side = OrderSide.BUY if side == "BUY" else OrderSide.SELL
                order = broker.submit_market_order(symbol_o, Decimal(str(qty)), order_side)
                st.success(f"Order submitted: `{order.id}` — status `{order.status}`")
            except Exception as e:
                st.error(f"Order failed: {e}")


main()
