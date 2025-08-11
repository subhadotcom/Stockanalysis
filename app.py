"""
Financial Data Analyzer - A Streamlit application for stock market analysis
Provides interactive charts, financial metrics, and data download capabilities
using Yahoo Finance data via the yfinance library.
"""

# Standard library imports
import io
from datetime import datetime, timedelta

# Third-party imports
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Financial Data Analyzer",
    page_icon="📈",
    layout="wide"
)

# APPLICATION HEADER
st.title("📈 Financial Data Analyzer")
st.markdown(
    "Enter a stock symbol to analyze financial data from Yahoo Finance. "
    "Get real-time stock prices, historical charts, and key financial metrics."
)

# SIDEBAR CONFIGURATION
st.sidebar.header("Stock Analysis Settings")

# Stock symbol input with validation
stock_symbol = st.sidebar.text_input(
    "Enter Stock Symbol (e.g., AAPL, GOOGL, TSLA):",
    value="AAPL",
    help="Enter a valid stock ticker symbol from any major exchange"
).upper().strip()

# Time period selection for historical data
time_periods = {
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
    "Select Time Period:",
    options=list(time_periods.keys()),
    index=5,  # Default to "1 Year"
    help="Choose the time range for historical data analysis"
)

# Chart type selection
chart_type = st.sidebar.selectbox(
    "Select Chart Type:",
    options=["Line Chart", "Candlestick Chart"],
    index=0,
    help="Line charts show price trends, candlestick charts show OHLC data"
)

# Analysis trigger button
analyze_button = st.sidebar.button("Analyze Stock", type="primary")

# DATA FETCHING FUNCTIONS
def get_stock_info(symbol):
    """
    Fetch comprehensive stock information and historical data from Yahoo Finance.
    
    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        
    Returns:
        tuple: (info_dict, hist_dataframe, error_message)
            - info_dict: Company information and current metrics
            - hist_dataframe: Historical price and volume data
            - error_message: Error description if fetch fails, None if successful
    """
    try:
        # Create yfinance Ticker object and fetch data
        ticker = yf.Ticker(symbol)
        info = ticker.info
        period_code = time_periods[selected_period]
        hist_data = ticker.history(period=period_code)
        
        # Validate data availability
        if hist_data.empty:
            return None, None, "No historical data found for this symbol"
            
        return info, hist_data, None
        
    except Exception as e:
        return None, None, f"Error fetching data: {str(e)}"


def format_large_number(num):
    """
    Format large numbers with appropriate suffixes (K, M, B, T) for better readability.
    
    Args:
        num (float/int): Number to format
        
    Returns:
        str: Formatted number with suffix (e.g., "$1.23B", "$456.78K")
    """
    if pd.isna(num) or num is None:
        return "N/A"
        
    abs_num = abs(num)
    if abs_num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif abs_num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif abs_num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif abs_num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"


# DATA PRESENTATION FUNCTIONS
def create_summary_table(info):
    """
    Create a comprehensive summary table of key financial metrics.
    
    Args:
        info (dict): Stock information dictionary from yfinance
        
    Returns:
        pd.DataFrame: Formatted summary table with metrics and values
    """
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
            f"${info.get('currentPrice', 'N/A'):.2f}" if info.get('currentPrice') else "N/A",
            f"${info.get('previousClose', 'N/A'):.2f}" if info.get('previousClose') else "N/A",
            f"${info.get('dayLow', 'N/A'):.2f} - ${info.get('dayHigh', 'N/A'):.2f}" 
                if info.get('dayLow') and info.get('dayHigh') else "N/A",
            f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f} - ${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}"
                if info.get('fiftyTwoWeekLow') and info.get('fiftyTwoWeekHigh') else "N/A",
            f"{info.get('volume', 'N/A'):,}" if info.get('volume') else "N/A",
            f"{info.get('averageVolume', 'N/A'):,}" if info.get('averageVolume') else "N/A",
            format_large_number(info.get('marketCap')),
            f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A",
            f"${info.get('trailingEps', 'N/A'):.2f}" if info.get('trailingEps') else "N/A",
            f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "N/A",
            f"{info.get('beta', 'N/A'):.2f}" if info.get('beta') else "N/A"
        ]
    }
    return pd.DataFrame(summary_data)


# CHART CREATION FUNCTIONS
def create_line_chart(hist_data, symbol):
    """
    Create an interactive line chart showing stock price trends.
    
    Args:
        hist_data (pd.DataFrame): Historical price data
        symbol (str): Stock symbol for chart title
        
    Returns:
        go.Figure: Interactive Plotly line chart
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: $%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'{symbol} Stock Price Over Time',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        hovermode='x unified',
        showlegend=True,
        height=500,
        template='plotly_white'
    )
    
    return fig


def create_candlestick_chart(hist_data, symbol):
    """
    Create an interactive candlestick chart showing OHLC data.
    
    Args:
        hist_data (pd.DataFrame): Historical OHLC data
        symbol (str): Stock symbol for chart title
        
    Returns:
        go.Figure: Interactive Plotly candlestick chart
    """
    fig = go.Figure(data=go.Candlestick(
        x=hist_data.index,
        open=hist_data['Open'],
        high=hist_data['High'],
        low=hist_data['Low'],
        close=hist_data['Close'],
        name='OHLC'
    ))
    
    fig.update_layout(
        title=f'{symbol} Candlestick Chart',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        height=500,
        xaxis_rangeslider_visible=False,
        template='plotly_white'
    )
    
    return fig


def create_volume_chart(hist_data, symbol):
    """
    Create a bar chart showing trading volume over time.
    
    Args:
        hist_data (pd.DataFrame): Historical volume data
        symbol (str): Stock symbol for chart title
        
    Returns:
        go.Figure: Interactive Plotly bar chart
    """
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=hist_data.index,
        y=hist_data['Volume'],
        name='Volume',
        marker_color='rgba(0, 150, 255, 0.6)',
        hovertemplate='<b>Date</b>: %{x}<br><b>Volume</b>: %{y:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'{symbol} Trading Volume',
        xaxis_title='Date',
        yaxis_title='Volume',
        height=300,
        showlegend=False,
        template='plotly_white'
    )
    
    return fig

# DATA EXPORT FUNCTIONS
def prepare_csv_data(info, hist_data, symbol):
    """
    Prepare comprehensive data for CSV download including summary and historical data.
    
    Args:
        info (dict): Stock information
        hist_data (pd.DataFrame): Historical price data
        symbol (str): Stock symbol
        
    Returns:
        str: Formatted CSV data as string
    """
    # Create summary table
    summary_df = create_summary_table(info)
    
    # Prepare historical data
    hist_df = hist_data.copy()
    hist_df.index.name = 'Date'
    hist_df = hist_df.round(2)
    
    # Create CSV buffer
    buffer = io.StringIO()
    
    # Write header information
    buffer.write(f"Stock Symbol: {symbol}\n")
    buffer.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    buffer.write(f"Time Period: {selected_period}\n\n")
    
    # Write summary metrics
    buffer.write("SUMMARY METRICS\n")
    buffer.write("=" * 50 + "\n")
    summary_df.to_csv(buffer, index=False)
    
    # Write historical data
    buffer.write("\n\nHISTORICAL DATA\n")
    buffer.write("=" * 50 + "\n")
    hist_df.to_csv(buffer)
    
    return buffer.getvalue()

# MAIN APPLICATION LOGIC
if analyze_button or stock_symbol:
    if stock_symbol:
        # Show loading indicator while fetching data
        with st.spinner(f'Fetching data for {stock_symbol}...'):
            info, hist_data, error = get_stock_info(stock_symbol)
        
        # Handle errors and missing data
        if error:
            st.error(f"❌ {error}")
            st.info("💡 Please check the stock symbol and try again. "
                   "Make sure the symbol is valid and actively traded.")
        elif info is None or hist_data is None:
            st.error(f"❌ No data found for symbol: {stock_symbol}")
            st.info("💡 Please enter a valid stock ticker symbol from a major exchange.")
        else:
            # Display company information
            company_name = info.get('shortName', info.get('longName', stock_symbol))
            st.header(f"{company_name} ({stock_symbol})")
            
            # Create two-column layout for metrics
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📊 Key Financial Metrics")
                summary_df = create_summary_table(info)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("📈 Price Performance")
                
                # Display current price with change
                current_price = info.get('currentPrice', 0)
                previous_close = info.get('previousClose', 0)
                
                if current_price and previous_close:
                    price_change = current_price - previous_close
                    price_change_percent = (price_change / previous_close) * 100
                    
                    st.metric(
                        label="Current Price",
                        value=f"${current_price:.2f}",
                        delta=f"{price_change_percent:+.2f}%"
                    )
                
                # Display additional metrics
                if info.get('marketCap'):
                    st.metric("Market Cap", format_large_number(info.get('marketCap')))
                if info.get('volume'):
                    st.metric("Volume", f"{info.get('volume'):,}")
            
            # Display interactive charts
            st.subheader("📈 Interactive Charts")
            
            if chart_type == "Line Chart":
                price_fig = create_line_chart(hist_data, stock_symbol)
                st.plotly_chart(price_fig, use_container_width=True)
            else:
                # Candlestick chart with volume
                price_fig = create_candlestick_chart(hist_data, stock_symbol)
                st.plotly_chart(price_fig, use_container_width=True)
                
                volume_fig = create_volume_chart(hist_data, stock_symbol)
                st.plotly_chart(volume_fig, use_container_width=True)
            
            # Display historical data table
            st.subheader("📋 Historical Data")
            st.write("Recent Historical Data (Last 10 Trading Days):")
            recent_data = hist_data.tail(10).round(2)
            st.dataframe(recent_data, use_container_width=True)
            
            # Data download section
            st.subheader("💾 Download Data")
            csv_data = prepare_csv_data(info, hist_data, stock_symbol)
            st.download_button(
                label="📥 Download Complete Data as CSV",
                data=csv_data,
                file_name=f"{stock_symbol}_financial_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Download all financial data and historical prices as CSV file"
            )
            
            # Additional statistics in expandable section
            with st.expander("📊 Additional Statistics"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Period High", f"${hist_data['High'].max():.2f}")
                    st.metric("Period Low", f"${hist_data['Low'].min():.2f}")
                
                with col2:
                    avg_volume = hist_data['Volume'].mean()
                    st.metric("Average Volume", f"{avg_volume:,.0f}")
                    
                    # Calculate annualized volatility
                    volatility = hist_data['Close'].pct_change().std() * np.sqrt(252) * 100
                    st.metric("Volatility (Annualized)", f"{volatility:.2f}%")
                
                with col3:
                    # Calculate total return for the period
                    total_return = ((hist_data['Close'].iloc[-1] / hist_data['Close'].iloc[0]) - 1) * 100
                    st.metric("Total Return", f"{total_return:+.2f}%")
                    
                    # Calculate average daily return
                    avg_daily_return = hist_data['Close'].pct_change().mean() * 100
                    st.metric("Avg Daily Return", f"{avg_daily_return:+.3f}%")
    else:
        st.info("👆 Please enter a stock symbol in the sidebar to begin analysis.")

# FOOTER
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>📊 Financial Data Analyzer | Data provided by Yahoo Finance via yfinance library</p>
        <small>
            ⚠️ Disclaimer: This tool is for informational purposes only and should not be 
            considered as financial advice. Always conduct your own research before making 
            investment decisions.
        </small>
    </div>
    """,
    unsafe_allow_html=True
)