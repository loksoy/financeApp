import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import streamlit as st

@st.cache_data
def retrieve_stock_lookup():
    #Loads lookup table containing Exchange, Stock Name and Ticker
    st.session_state["df_lookup"] = pd.read_csv("data/exchange_lookup.csv")
    return st.session_state["df_lookup"]

def update_stock_selection(df_lookup):
    #Filters stock based on selected Exchange and returns names of available stocks
    selected_exchange = st.session_state["selected_exchange"]
    if selected_exchange:
        st.session_state["filtered_stocks"] = df_lookup[df_lookup["Market"] == st.session_state.selected_exchange]
    else:
        st.session_state["filtered_stocks"] = pd.DataFrame()  # Empty DataFrame
    return st.session_state.filtered_stocks

def get_selected_symbol(df_lookup):
    #Filters list of stocks based on selected exchange and stock name and returns selected stock ticker
    selected_row = df_lookup[(df_lookup["Market"] == st.session_state.selected_exchange) & 
                            (df_lookup["Name"] == st.session_state.selected_stock)]
    st.session_state["selected_ticker"] = selected_row["Symbol"].iloc[0]
    return st.session_state["selected_ticker"]

@st.cache_resource
def retrieve_ticker_object(stock_ticker):
    #Retrieves the stock ticker object based on the selected stock_ticker
    ticker_object = yf.Ticker(stock_ticker)
    return ticker_object

@st.cache_data
def retrieve_price_data(date_range):
    #Retrieves stock data based on the stock_ticker and the date_range
    trade_data = st.session_state["ticker_object"].history(period=date_range)
    return trade_data


@st.cache_data
def create_graph(input_df):
    #Creates a grap_object that shows the price and volume of traded stocks for the selected range
    #Range selctor is added to the plot. 
    st.session_state["price_plot"] = make_subplots(specs=[[{"secondary_y":True}]])

    st.session_state["price_plot"].add_trace(go.Scatter(x=input_df.index,
                  y=input_df["Close"],
                  mode="lines"),
                  secondary_y=True)
    
    st.session_state["price_plot"].add_trace(go.Bar(x=input_df.index,
                         y=input_df["Volume"], 
                         marker={"color":"gray"}),
                         secondary_y=False)
    
    st.session_state["price_plot"].layout.xaxis.rangeslider.visible=True
    st.session_state["price_plot"].layout.yaxis2.showgrid=False
    st.session_state["price_plot"].layout.showlegend=False

    return st.session_state["price_plot"]

@st.cache_data
def retrieve_stock_info():
    #Retrieves and return stock_info and stock_name based on the selected ticker_object
    stock_data = st.session_state["ticker_object"]
    stock_info = stock_data.info
    st.session_state["stock_name"] = stock_data.info["longName"]
    return stock_info, stock_info.get("longName", "Unknown Stock")

@st.cache_data
def retrieve_price_targets():
    #Retrieves and returns analyst_price_targets based on the ticker_object
    stock_data = st.session_state["ticker_object"]
    price_targets = stock_data.analyst_price_targets
    return price_targets


if __name__ == "__main__":
    #Initializing session_states
    if "df_lookup" not in st.session_state:
        st.session_state["df_lookup"] = retrieve_stock_lookup()
    if "selected_exchange" not in st.session_state:
        st.session_state["selected_exchange"] = None
    if "filtered_stocks" not in st.session_state:
        st.session_state["filtered_stocks"] = pd.DataFrame()
    if "selected_stock" not in st.session_state:
        st.session_state["selected_stock"] = None
    if "stock_name" not in st.session_state:
        st.session_state["stock_name"] = ""
    if "selected_ticker" not in st.session_state:
        st.session_state["selected_ticker"] = ""
    if "last_selected_ticker" not in st.session_state:
        st.session_state["last_selected_ticker"] = ""
    if "submit_button" not in st.session_state:
        st.session_state["submit_ubtton"] = False
    if "ticker_object" not in st.session_state:
        st.session_state["ticker_object"] = None
    if "stock_data" not in st.session_state:
        st.session_state["stock_data"] = ""
    if "price_plt" not in st.session_state:
        st.session_state["price_plot"] = False
    if "stock_info" not in st.session_state:
        st.session_state["stock_info"] = ""
    
    
    # Select exchange 
    selected_exchange = st.selectbox(
        "Select Exchange", st.session_state.df_lookup["Market"].unique(), key="selected_exchange",
        on_change=update_stock_selection, args=(st.session_state.df_lookup, )
    )
    
    # Select Stock
    # If selection is not empty, new dropdown will appear
    if len(st.session_state["filtered_stocks"])!=0:
        st.selectbox("Select Stock", st.session_state.filtered_stocks["Name"].unique(), key="selected_stock")
    else:
        st.write("Please select an exchange to see available stocks.")
    
    if st.session_state["selected_stock"] !="":
        st.radio("Select the lenght of data to be displayed", ["1d", "5d", "1mo", "3mo", "ytd", "1y", "5y", "10y", "max"],
                 index=5, horizontal=True, key="radio_range")
    else:
        st.write("Please select a date range")


    # Submit stock to get the selected ticker
    submit_button = st.button("Get data", key="submit_button", 
                              on_click=get_selected_symbol, args=(st.session_state.df_lookup, ))
    
                                 

    #If the submit_button is pressed, retrieve data & plot graph, else write "Not submitted"
    if submit_button and st.session_state["selected_exchange"] and st.session_state["selected_stock"] != None:
        #Retrieving key info
        st.session_state["ticker_object"] = retrieve_ticker_object(st.session_state["selected_ticker"])

        # Clear cache if stock selection has changed
        if "last_selected_ticker" in st.session_state and st.session_state["last_selected_ticker"] != st.session_state["selected_ticker"]:
            st.cache_data.clear()  # Clears the cached data when the selection changes
    
        # Store the new selection for future reference
        st.session_state["last_selected_ticker"] = st.session_state["selected_ticker"]

        #Store stock_info (dictionary of info) and stock_name in cache
        st.session_state["stock_info"], st.session_state["stock_name"] = retrieve_stock_info()
        st.session_state["price_targets"] = retrieve_price_targets()

        st.header("About the company")
        st.write(st.session_state.stock_info['longBusinessSummary'])
        col1, col2 = st.columns(2)

        with col1:
            st.header("Key metrics")
            st.write(f"P/B: {st.session_state.stock_info['priceToBook']}")
            st.write(f"Dividend Yield: {st.session_state.stock_info['dividendYield']}")
            st.write(f"Trailing P/E: {st.session_state.stock_info['trailingPE']}")

        with col2:
            st.header("Analyst price targets")
            try:
                st.write(f"High: {st.session_state.price_targets['high']}")
                st.write(f"Low: {st.session_state.price_targets['low']}")
                st.write(f"Mean: {st.session_state.price_targets['mean']}")
            except:
                st.write(f"No analyst price targets available")
            

        #Retrieving price data and creating graph
        st.session_state["stock_data"] = retrieve_price_data(st.session_state["radio_range"])
        st.session_state["price_plot"] = create_graph(st.session_state["stock_data"])
        st.plotly_chart(st.session_state["price_plot"], use_container_width=True)

    else:
        st.write("Select Exchange, Stock and Date Lenght before pressing 'Get data'")
    

    #Helping functions
    st.write(f"Selected exhcange: {st.session_state['selected_exchange']}")
    st.write(f"Selected stock: {st.session_state['selected_stock']}")  
    st.write(f"Stock name: {st.session_state['stock_name']}")  
    st.write(f"Submitted: {st.session_state['selected_ticker']}")
    
