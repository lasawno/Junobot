from decimal import Decimal

import streamlit as st

from junobot.brokers.base import OrderSide
from junobot.config import ConfigError, load_broker

st.set_page_config(page_title="Junobot", page_icon="📈", layout="wide")


@st.cache_resource
def get_broker():
    return load_broker()


def main():
    st.title("📈 Junobot")

    try:
        broker = get_broker()
    except ConfigError as e:
        st.error(f"Config error: {e}")
        st.stop()
        return

    paper = getattr(broker, "paper", False)
    mode_badge = "🧪 PAPER" if paper else "🔴 LIVE"
    market_open = broker.is_market_open()
    market_badge = "🟢 Market open" if market_open else "🔴 Market closed"

    c1, c2, c3 = st.columns([2, 2, 6])
    c1.markdown(f"**Broker:** `{broker.name}` &nbsp; {mode_badge}")
    c2.markdown(market_badge)
    c3.button("🔄 Refresh", on_click=st.cache_resource.clear)

    st.divider()

    # Account summary
    acct = broker.get_account()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Cash", f"${acct.cash:,.2f}")
    m2.metric("Equity", f"${acct.equity:,.2f}")
    m3.metric("Buying power", f"${acct.buying_power:,.2f}")
    m4.metric("Currency", acct.currency)

    st.divider()

    # Positions
    st.subheader("Positions")
    positions = broker.get_positions()
    if not positions:
        st.caption("No open positions.")
    else:
        st.dataframe(
            [
                {
                    "Symbol": p.symbol,
                    "Qty": float(p.qty),
                    "Avg entry": float(p.avg_entry_price),
                    "Market value": float(p.market_value),
                    "Unrealized P/L": float(p.unrealized_pl),
                }
                for p in positions
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # Quote + order side-by-side
    left, right = st.columns(2)

    with left:
        st.subheader("Quote lookup")
        symbol_q = st.text_input("Symbol", value="AAPL", key="quote_symbol").upper().strip()
        if st.button("Get quote", key="quote_btn"):
            try:
                q = broker.get_quote(symbol_q)
                qc1, qc2 = st.columns(2)
                qc1.metric("Bid", f"${q.bid}")
                qc2.metric("Ask", f"${q.ask}")
            except Exception as e:
                st.error(f"Quote failed: {e}")

    with right:
        st.subheader("Place market order")
        if not paper:
            st.warning("⚠️ LIVE mode — orders use real money.")
        symbol_o = st.text_input("Symbol", value="AAPL", key="order_symbol").upper().strip()
        qty = st.number_input("Qty", min_value=0.0, value=1.0, step=1.0, key="order_qty")
        side = st.radio("Side", ["BUY", "SELL"], horizontal=True, key="order_side")
        confirm = st.checkbox("I confirm this order", key="order_confirm")
        if st.button("Submit order", key="order_btn", disabled=not confirm):
            try:
                order_side = OrderSide.BUY if side == "BUY" else OrderSide.SELL
                order = broker.submit_market_order(symbol_o, Decimal(str(qty)), order_side)
                st.success(f"Order submitted: `{order.id}` — status `{order.status}`")
            except Exception as e:
                st.error(f"Order failed: {e}")


main()
