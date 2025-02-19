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
        title="Gross Profit Margin and Operating Margin over time",
        xaxis_title="Date",
        yaxis_title="Margin",
    )

    return fig


#Create lineplot showing historic PE-ratio
def calc_hist_pe():
    #Load datasets
    income_stmt = st.session_state["financial_stmt"]
    price_data = st.session_state["ticker_object"].history(period="5y")

    #Extracting earnings from income_stmt
    earnings = income_stmt.loc["DilutedEPS"]

    #Fix index
    earnings.index = pd.to_datetime(earnings.index)
    price_data.index = price_data.index.tz_localize(None)

    #Merging datasets
    price_data["DilutedEPS"] = earnings.reindex(price_data.index, method="ffill")

    #Calculate PE-ratio
    price_data["PE-ratio"] = np.where(price_data["DilutedEPS"].notna(),
                                   price_data["Close"] / price_data["DilutedEPS"],
                                   np.nan) 
    return price_data

def plot_hist_pe():
    pe_df = st.session_state["historic_pe"]

    fig = go.Figure(data=go.Scatter(
                        x = pe_df.index,
                        y = pe_df["PE-ratio"],
                        mode="lines"))
    
    return fig






if __name__ == "__main__":
    if "financial_stmt" not in st.session_state:
        st.session_state["financial_stmt"] = pd.DataFrame()
    if "transposed_df" not in st.session_state:
        st.session_state["transposed_df"] = pd.DataFrame()
    if "historic_pe" not in st.session_state:
        st.session_state["historic_pe"] = pd.DataFrame()
    if "margins_df" not in st.session_state:
        st.session_state["margins_df"] = pd.DataFrame()
    if "margin_plot" not in st.session_state:
        st.session_state["margin_plot"] = False
    if "pe_plot" not in st.session_state:
        st.session_state["pe_plot"] = False
    if "dividends" not in st.session_state:
        st.session_state["dividends"] = pd.DataFrame()
    
    st.header("Advanced Graphs")

    #Get financial statement
    st.session_state["financial_stmt"] = get_financials() 
    st.session_state["transposed_df"] = calc_margins() 
    st.session_state["margins_df"] = calc_margins()
    st.session_state["margin_plot"] = plot_margins()
    
    #Plot graph for margins
    st.plotly_chart(st.session_state["margin_plot"], use_container_width=True)

    #Calculating historic PE-ratio
    st.session_state["historic_pe"] = calc_hist_pe()
    st.session_state["pe_plot"] = plot_hist_pe()
    #Plot graph for historic PE-ratio
    st.plotly_chart(st.session_state["pe_plot"], use_container_width=True)

    #Get historic dividends
    st.session_state["dividends"] = get_dividends()
    st.session_state["dividend_plot"] = plot_dividends()

    #Plot graph for dividends
    st.plotly_chart(st.session_state["dividend_plot"], use_container_width=True)
    

