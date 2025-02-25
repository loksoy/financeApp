import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import streamlit as st

if "income_stmt" not in st.session_state:
    st.session_state["income_stmt"] = pd.DataFrame()
if "balance_sheet" not in st.session_state:
    st.session_state["balance_sheet"] = pd.DataFrame()


@st.cache_data
def fetch_income_stmt():
    stock_data = st.session_state["ticker_object"]
    income_stmt = stock_data.get_income_stmt(freq="yearly")
    return income_stmt  

@st.cache_data
def fetch_balance_sheet():
    stock_data = st.session_state["ticker_object"]
    balance_sheet = stock_data.get_balance_sheet(freq="yearly")
    return balance_sheet

if __name__ == "__main__":
    st.write(f"Stock name: {st.session_state["stock_name"]}")
    #st.write(f"Stock: {st.session_state["stock_name"]}")
    st.session_state["income_stmt"] = fetch_income_stmt()
    st.session_state["balance_sheet"] = fetch_balance_sheet()


    # Clear cache if stock selection has changed
    if "last_selected_ticker" in st.session_state and st.session_state["last_selected_ticker"] != st.session_state["selected_ticker"]:
        st.cache_data.clear()  # Clears the cached data when the selection changes

    st.write(f"### Currency: {st.session_state["currency"]}")
    st.header("Income Statement & Balance Sheet")
    
    with st.expander("Yearly Income Statement"):
        st.write(st.session_state["income_stmt"])


    st.header("Balance Sheet")
    with st.expander("Yearly Balance Sheet"):
        st.write(st.session_state["balance_sheet"])
    