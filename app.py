import streamlit as st         # Imports Streamlit for building the web app UI
import yfinance as yf          # Imports yfinance for fetching stock data from Yahoo Finance
import pandas as pd            # Imports pandas for data manipulation and analysis
import plotly.graph_objects as go  # Imports Plotly's graph objects for advanced charting
import plotly.express as px        # Imports Plotly Express for quick charting (not used here)
from plotly.subplots import make_subplots  # For combining multiple plots (not used here)
import numpy as np             # Imports numpy for numerical operations
from datetime import datetime, timedelta  # Imports datetime utilities for date/time handling
import io                      # Imports io for in-memory file operations (used for CSV download)

# Set page configuration
st.set_page_config(
    page_title="Financial Data Analyzer",  # Sets the browser tab title
    page_icon="📈",                        # Sets the browser tab icon
    layout="wide"                          # Uses the full width of the browser window
)

# Title and description
st.title("📈 Financial Data Analyzer")  # Displays the main title at the top of the app
st.markdown("Enter a stock symbol to analyze financial data from Yahoo Finance")  # Adds a description below the title

# Sidebar for user inputs
st.sidebar.header("Stock Analysis Settings")  # Adds a header to the sidebar

# Stock symbol input
stock_symbol = st.sidebar.text_input(
    "Enter Stock Symbol (e.g., AAPL, GOOGL, TSLA):",  # Label for the input box
    value="AAPL",                                     # Default value
    help="Enter a valid stock ticker symbol"           # Tooltip help text
).upper()                                             # Converts input to uppercase

# Time period selection
time_periods = {  # Dictionary mapping display names to yfinance codes
    "1 Day": "1d",
    "1 Week": "1wk",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
    "Max": "max"
}

selected_period = st.sidebar.selectbox(
    "Select Time Period:",           # Label for the dropdown
    options=list(time_periods.keys()),  # List of options
    index=2  # Default to "1 Month"
)

# Chart type selection
chart_type = st.sidebar.selectbox(
    "Select Chart Type:",                # Label for the dropdown
    options=["Line Chart", "Candlestick Chart"],  # Chart type options
    index=0                             # Default to "Line Chart"
)

# Analyze button
analyze_button = st.sidebar.button("Analyze Stock", type="primary")  # Button to trigger analysis

def get_stock_info(symbol):
    """Fetch stock information and historical data"""
    try:
        ticker = yf.Ticker(symbol)  # Create a yfinance Ticker object for the symbol
        info = ticker.info          # Fetch company info (dict)
        period = time_periods[selected_period]  # Get the period code from the selected period
        hist_data = ticker.history(period=period)  # Fetch historical price data
        if hist_data.empty:         # If no data is returned
            return None, None, "No historical data found for this symbol"
        return info, hist_data, None  # Return info, data, and no error
    except Exception as e:          # If any error occurs
        return None, None, f"Error fetching data: {str(e)}"  # Return error message

def format_large_number(num):
    """Format large numbers with appropriate suffixes"""
    if pd.isna(num) or num is None:  # If the number is missing or NaN
        return "N/A"
    if abs(num) >= 1e12:             # Trillions
        return f"${num/1e12:.2f}T"
    elif abs(num) >= 1e9:            # Billions
        return f"${num/1e9:.2f}B"
    elif abs(num) >= 1e6:            # Millions
        return f"${num/1e6:.2f}M"
    elif abs(num) >= 1e3:            # Thousands
        return f"${num/1e3:.2f}K"
    else:                            # Less than a thousand
        return f"${num:.2f}"

def create_summary_table(info):
    """Create a summary table of key financial metrics"""
    summary_data = {
        "Metric": [
            "Current Price",
            "Previous Close",
            "Day's Range",
            "52 Week Range",
            "Volume",
            "Average Volume",
            "Market Cap",
            "P/E Ratio",
            "EPS",
            "Dividend Yield",
            "Beta"
        ],
        "Value": [
            f"${info.get('currentPrice', 'N/A'):.2f}" if info.get('currentPrice') else "N/A",  # Current price
            f"${info.get('previousClose', 'N/A'):.2f}" if info.get('previousClose') else "N/A",  # Previous close
            f"${info.get('dayLow', 'N/A'):.2f} - ${info.get('dayHigh', 'N/A'):.2f}" if info.get('dayLow') and info.get('dayHigh') else "N/A",  # Day's range
            f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f} - ${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if info.get('fiftyTwoWeekLow') and info.get('fiftyTwoWeekHigh') else "N/A",  # 52 week range
            f"{info.get('volume', 'N/A'):,}" if info.get('volume') else "N/A",  # Volume
            f"{info.get('averageVolume', 'N/A'):,}" if info.get('averageVolume') else "N/A",  # Average volume
            format_large_number(info.get('marketCap')),  # Market cap
            f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A",  # P/E ratio
            f"${info.get('trailingEps', 'N/A'):.2f}" if info.get('trailingEps') else "N/A",  # EPS
            f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "N/A",  # Dividend yield
            f"{info.get('beta', 'N/A'):.2f}" if info.get('beta') else "N/A"  # Beta
        ]
    }
    return pd.DataFrame(summary_data)  # Return as a pandas DataFrame

def create_line_chart(hist_data, symbol):
    """Create an interactive line chart"""
    fig = go.Figure()  # Create a new Plotly figure
    fig.add_trace(go.Scatter(
        x=hist_data.index,         # Dates on the x-axis
        y=hist_data['Close'],      # Closing prices on the y-axis
        mode='lines',              # Draw as a line
        name='Close Price',        # Legend name
        line=dict(color='#1f77b4', width=2),  # Line color and width
        hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: $%{y:.2f}<extra></extra>'  # Tooltip format
    ))
    fig.update_layout(
        title=f'{symbol} Stock Price Over Time',  # Chart title
        xaxis_title='Date',                       # X-axis label
        yaxis_title='Price ($)',                  # Y-axis label
        hovermode='x unified',                    # Unified hover
        showlegend=True,                          # Show legend
        height=500                                # Chart height
    )
    return fig  # Return the figure

def create_candlestick_chart(hist_data, symbol):
    """Create an interactive candlestick chart"""
    fig = go.Figure(data=go.Candlestick(
        x=hist_data.index,           # Dates
        open=hist_data['Open'],      # Opening prices
        high=hist_data['High'],      # High prices
        low=hist_data['Low'],        # Low prices
        close=hist_data['Close'],    # Closing prices
        name='OHLC'                  # Legend name
    ))
    fig.update_layout(
        title=f'{symbol} Candlestick Chart',  # Chart title
        xaxis_title='Date',                   # X-axis label
        yaxis_title='Price ($)',              # Y-axis label
        height=500,                           # Chart height
        xaxis_rangeslider_visible=False       # Hide range slider
    )
    return fig

def create_volume_chart(hist_data, symbol):
    """Create a volume chart"""
    fig = go.Figure()  # New figure
    fig.add_trace(go.Bar(
        x=hist_data.index,           # Dates
        y=hist_data['Volume'],       # Volume values
        name='Volume',               # Legend name
        marker_color='rgba(0, 150, 255, 0.6)',  # Bar color
        hovertemplate='<b>Date</b>: %{x}<br><b>Volume</b>: %{y:,}<extra></extra>'  # Tooltip
    ))
    fig.update_layout(
        title=f'{symbol} Trading Volume',  # Chart title
        xaxis_title='Date',                # X-axis label
        yaxis_title='Volume',              # Y-axis label
        height=300,                        # Chart height
        showlegend=False                   # Hide legend
    )
    return fig

def prepare_csv_data(info, hist_data, symbol):
    """Prepare data for CSV download"""
    summary_df = create_summary_table(info)  # Create summary table
    hist_df = hist_data.copy()               # Copy historical data
    hist_df.index.name = 'Date'              # Name the index
    hist_df = hist_df.round(2)               # Round values to 2 decimals
    buffer = io.StringIO()                   # Create in-memory text buffer
    buffer.write(f"Stock Symbol: {symbol}\n")  # Write stock symbol
    buffer.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")  # Write date
    buffer.write(f"Time Period: {selected_period}\n\n")  # Write period
    buffer.write("SUMMARY METRICS\n")        # Section header
    summary_df.to_csv(buffer, index=False)   # Write summary table
    buffer.write("\n\nHISTORICAL DATA\n")    # Section header
    hist_df.to_csv(buffer)                   # Write historical data
    return buffer.getvalue()                 # Return CSV as string

# Main application logic
if analyze_button or stock_symbol:  # If the user clicks "Analyze" or enters a symbol
    if stock_symbol:                # If a symbol is provided
        with st.spinner(f'Fetching data for {stock_symbol}...'):  # Show loading spinner
            info, hist_data, error = get_stock_info(stock_symbol)  # Fetch data
        if error:  # If there was an error
            st.error(f"❌ {error}")  # Show error message
            st.info("Please check the stock symbol and try again.")  # Suggest retry
        elif info is None or hist_data is None:  # If no data found
            st.error(f"❌ No data found for symbol: {stock_symbol}")
            st.info("Please enter a valid stock ticker symbol.")
        else:  # If data is found
            company_name = info.get('shortName', info.get('longName', stock_symbol))  # Get company name
            st.header(f"{company_name} ({stock_symbol})")  # Show company name and symbol
            col1, col2 = st.columns([1, 1])  # Create two columns
            with col1:
                st.subheader("📊 Key Financial Metrics")  # Subheader
                summary_df = create_summary_table(info)   # Create summary table
                st.dataframe(summary_df, use_container_width=True, hide_index=True)  # Show table
            with col2:
                st.subheader("📈 Price Performance")  # Subheader
                current_price = info.get('currentPrice', 0)  # Get current price
                previous_close = info.get('previousClose', 0)  # Get previous close
                if current_price and previous_close:  # If both are available
                    price_change = current_price - previous_close  # Calculate change
                    price_change_percent = (price_change / previous_close) * 100  # Calculate percent change
                    st.metric(
                        label="Current Price",
                        value=f"${current_price:.2f}",
                        delta=f"{price_change_percent:+.2f}%"
                    )  # Show metric with delta
                if info.get('marketCap'):
                    st.metric("Market Cap", format_large_number(info.get('marketCap')))  # Show market cap
                if info.get('volume'):
                    st.metric("Volume", f"{info.get('volume'):,}")  # Show volume
            st.subheader("📈 Interactive Charts")  # Charts section
            if chart_type == "Line Chart":
                price_fig = create_line_chart(hist_data, stock_symbol)  # Create line chart
            else:
                price_fig = create_candlestick_chart(hist_data, stock_symbol)  # Create candlestick chart
                st.plotly_chart(price_fig, use_container_width=True)  # Show price chart
                volume_fig = create_volume_chart(hist_data, stock_symbol)  # Create volume chart
                st.plotly_chart(volume_fig, use_container_width=True)  # Show volume chart
                st.subheader("📋 Historical Data")  # Historical data section
                st.write("Recent Historical Data (Last 10 Trading Days):")  # Section description
                recent_data = hist_data.tail(10).round(2)  # Get last 10 rows
                st.dataframe(recent_data, use_container_width=True)  # Show table
                st.subheader("💾 Download Data")  # Download section
                csv_data = prepare_csv_data(info, hist_data, stock_symbol)  # Prepare CSV
                st.download_button(
                    label="📥 Download Complete Data as CSV",
                    data=csv_data,
                    file_name=f"{stock_symbol}_financial_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    help="Download all financial data and historical prices as CSV file"
            )  # Download button
            with st.expander("📊 Additional Statistics"):  # Expandable section
                col1, col2, col3 = st.columns(3)  # Three columns
                with col1:
                    st.metric("Period High", f"${hist_data['High'].max():.2f}")  # Highest price
                    st.metric("Period Low", f"${hist_data['Low'].min():.2f}")    # Lowest price
                with col2:
                    avg_volume = hist_data['Volume'].mean()  # Average volume
                    st.metric("Average Volume", f"{avg_volume:,.0f}")
                    volatility = hist_data['Close'].pct_change().std() * np.sqrt(252) * 100  # Annualized volatility
                    st.metric("Volatility (Annualized)", f"{volatility:.2f}%")
                with col3:
                    total_return = ((hist_data['Close'].iloc[-1] / hist_data['Close'].iloc[0]) - 1) * 100  # Total return
                    st.metric("Total Return", f"{total_return:+.2f}%")
                    avg_daily_return = hist_data['Close'].pct_change().mean() * 100  # Average daily return
                    st.metric("Avg Daily Return", f"{avg_daily_return:+.3f}%")
    else:
        st.info("👆 Please enter a stock symbol in the sidebar to begin analysis.")  # Prompt user to enter symbol

# Footer
st.markdown("---")  # Horizontal line
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>📊 Financial Data Analyzer | Data provided by Yahoo Finance via yfinance library</p>
        <small>Disclaimer: This tool is for informational purposes only and should not be considered as financial advice.</small>
    </div>
    """,
    unsafe_allow_html=True  # Allows HTML rendering
)