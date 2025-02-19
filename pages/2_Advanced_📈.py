import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import streamlit as st
import numpy as np

  

#Create bbar plot showing dividens
@st.cache_data
def get_dividends():
   ticker_obj = st.session_state["ticker_object"]
   dividends = ticker_obj.dividends
   dividends_df = pd.DataFrame(dividends, columns=["Dividends"])

   return dividends_df

def plot_dividends():
    dividends_df = st.session_state["dividends"]

    fig = go.Figure(data=go.Bar(x=dividends_df.index,
                                y=dividends_df["Dividends"]))

    fig.update_layout(title="Historical dividends",
                      xaxis_title="Date",
                      yaxis_title="Dividends")
    return fig


#Create linegraph showing gross-profit margin & Operating margin
#First, get financial statement
@st.cache_data
def get_financials():
    ticker_obj = st.session_state["ticker_object"]
    financial_stmt = ticker_obj.get_income_stmt(freq="yearly")
    return financial_stmt

def calc_margins():
    financial_df = st.session_state["financial_stmt"]
    #Transposing df
    df_T = financial_df.T
    # Calculate Gross Profit Margin
    df_T["GrossProfitMargin"] = np.where(
                                (df_T["GrossProfit"].notna()) & (df_T["TotalRevenue"].notna()),
                                df_T["GrossProfit"] / df_T["TotalRevenue"],
                                np.nan)

    # Calculate Operating Margin
    df_T["OperatingMargin"] = np.where(
                                (df_T["OperatingIncome"].notna()) & (df_T["TotalRevenue"].notna()),
                                df_T["OperatingIncome"] / df_T["TotalRevenue"],
                                np.nan)
    return df_T

def plot_margins():
    df_margins = st.session_state["margins_df"]
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
                x=df_margins.index,
                y=df_margins["GrossProfitMargin"],
                mode="lines+markers",
                name="Gross Profit Margin",
                line=dict(color="blue")
                ))
    
    fig.add_trace(go.Scatter(
                x=df_margins.index,
                y=df_margins["OperatingMargin"],
                mode="lines+markers",
                name="Operating Margin",
                line=dict(color="red")
    ))

    fig.update_layout(
        showlegend=False,
        xaxis_title="Date",
        yaxis_title="Margin",
    )
    return fig


#Create lineplot showing historic PE-ratio
def plot_eps_history():
    financial_df = st.session_state["financial_stmt"]

    df_T = financial_df.T
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
                x=df_T.index,
                y=df_T["DilutedEPS"],
                mode="lines+markers",
                name="EPS"
                ))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="EPS"
    )
    return fig
    
def get_pe_ratios():
    market_tickers = {"Dow Jones": "DIA",
                 "NASDAQ": "QQQ",
                 "S&P 500" : "SPY",
                 "Technology": "XLK",
                 "Financials" : "XLF",
                 "Energy" : "XLE",
                 "Healthcare": "XLV",
                 "Real Estate": "XLRE"
                 }
    
    market_pe = {}

    for key, val in market_tickers.items():
        market_obj = yf.Ticker(val)
        pe_market = market_obj.info.get("trailingPE")
        market_pe[key] = pe_market
    return market_pe

    
    



if __name__ == "__main__":
    if "market_pe" not in st.session_state:
        st.session_state["market_pe"] = ""
    if "financial_stmt" not in st.session_state:
        st.session_state["financial_stmt"] = pd.DataFrame()
    if "transposed_df" not in st.session_state:
        st.session_state["transposed_df"] = pd.DataFrame()
    if "margins_df" not in st.session_state:
        st.session_state["margins_df"] = pd.DataFrame()
    if "margin_plot" not in st.session_state:
        st.session_state["margin_plot"] = False
    if "dividends" not in st.session_state:
        st.session_state["dividends"] = pd.DataFrame()
    if "EPS_plot" not in st.session_state:
        st.session_state["EPS_plot"] = False

    
    st.header("Advanced Information 📈")
    st.write(f"### {st.session_state["stock_name"]}")
    st.write(f"PE-ratio: {st.session_state.stock_info['trailingPE']}")
    
    st.session_state["market_pe"] = get_pe_ratios()

    st.write("### Market PE-ratios")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Dow Jones: {st.session_state.market_pe["Dow Jones"]}")
        st.write(f"NASDAQ: {st.session_state.market_pe["NASDAQ"]}")
        st.write(f"S&P 500: {st.session_state.market_pe["S&P 500"]}")
        st.write(f"Technology: {st.session_state.market_pe["Technology"]}")
    with col2:
        st.write(f"Financials: {st.session_state.market_pe["Financials"]}")
        st.write(f"Energy: {st.session_state.market_pe["Energy"]}")
        st.write(f"Healthcare: {st.session_state.market_pe["Healthcare"]}")
        st.write(f"Real Estate: {st.session_state.market_pe["Real Estate"]}")

    #Get financial statement
    st.session_state["financial_stmt"] = get_financials() 
    st.session_state["transposed_df"] = calc_margins() 
    st.session_state["margins_df"] = calc_margins()
    st.session_state["margin_plot"] = plot_margins()
    st.session_state["EPS_plot"] = plot_eps_history()
    
  
    #Plot graph for margins
    st.write("#### Gross Profit & Operating Margin")
    st.plotly_chart(st.session_state["margin_plot"], use_container_width=True)


    #Plot historic EPS
    st.write("#### EPS History")
    st.plotly_chart(st.session_state["EPS_plot"], use_container_width=True)


    #Get historic dividends
    st.session_state["dividends"] = get_dividends()
    st.session_state["dividend_plot"] = plot_dividends()

    #Plot graph for dividends
    st.plotly_chart(st.session_state["dividend_plot"], use_container_width=True)
    

