# Financial Data Analyzer

## Overview

This is a Streamlit-based financial data analysis application that provides interactive stock market visualization and analysis. The application uses Yahoo Finance data to fetch real-time stock information and presents it through interactive charts powered by Plotly. It's designed as a single-page web application with a simple, user-friendly interface for financial data exploration.

## System Architecture

The application follows a simple client-server architecture with a Python-based backend using Streamlit as the web framework:

- **Frontend**: Streamlit web interface with interactive widgets and charts
- **Backend**: Python application handling data processing and API calls
- **Data Source**: Yahoo Finance API via yfinance library
- **Visualization**: Plotly for interactive charts and graphs
- **Deployment**: Autoscale deployment on Replit infrastructure

## Key Components

### Core Libraries
- **Streamlit**: Web application framework providing the UI and server functionality
- **yfinance**: Yahoo Finance API wrapper for fetching stock market data
- **Plotly**: Interactive charting library for data visualization
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing support

### Application Structure
- **app.py**: Main application file containing the Streamlit interface and logic
- **pyproject.toml**: Project dependencies and metadata using modern Python packaging
- **uv.lock**: Dependency lock file for reproducible builds
- **.streamlit/config.toml**: Streamlit server configuration for headless deployment

### User Interface Components
- Sidebar for user inputs (stock symbol, time period, chart type selection)
- Main area for displaying charts and financial data
- Interactive controls for customizing the analysis view

## Data Flow

1. **User Input**: User enters stock symbol and selects analysis parameters via sidebar
2. **Data Fetching**: Application queries Yahoo Finance API using yfinance library
3. **Data Processing**: Raw financial data is processed using Pandas for analysis
4. **Visualization**: Processed data is rendered into interactive charts using Plotly
5. **Display**: Charts and analysis are presented in the Streamlit web interface

The application operates in real-time, fetching fresh data on each user interaction without requiring page refreshes.

## External Dependencies

### Primary Data Source
- **Yahoo Finance API**: Real-time and historical stock market data
  - Accessed via yfinance Python library
  - No API key required
  - Provides stock prices, volume, and basic financial metrics

### Visualization Dependencies
- **Plotly**: Interactive charting capabilities
- **Streamlit**: Built-in chart integration and web interface components

### Development Dependencies
- **uv**: Modern Python package manager for faster dependency resolution
- **Python 3.11+**: Runtime environment

## Deployment Strategy

The application is configured for deployment on Replit's autoscale infrastructure:

- **Runtime Environment**: Python 3.11 with Nix package management
- **Port Configuration**: Application runs on port 5000
- **Deployment Type**: Autoscale deployment for automatic scaling based on demand
- **Server Configuration**: Headless mode optimized for web deployment
- **Dependency Management**: Automated installation via uv package manager

### Deployment Commands
- Primary: `streamlit run app.py --server.port 8501`