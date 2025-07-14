import pandas as pd
from colorama import init, Fore, Style
from tabulate import tabulate
import sqlite3
import csv
import yfinance as yf
import numpy as np

# Initialize colorama for cross-platform color support
init(autoreset=True)

def get_color_for_score(score):
    """Return color based on investment score"""
    if isinstance(score, (int, float)):
        if score >= 80:
            return Fore.GREEN + Style.BRIGHT
        elif score >= 65:
            return Fore.GREEN
        elif score >= 50:
            return Fore.YELLOW
        elif score >= 35:
            return Fore.RED
        else:
            return Fore.RED + Style.BRIGHT
    else:
        return Fore.WHITE  # Default color for N/A or non-numeric

def get_value_color(value, is_percentage=False):
    """Return color for positive/negative values"""
    if isinstance(value, (int, float)):
        if value > 0:
            return Fore.GREEN
        elif value < 0:
            return Fore.RED
        else:
            return Fore.WHITE
    else:
        return Fore.WHITE  # Default color for N/A or non-numeric

def format_number(value, format_type='general'):
    """Format numbers for display"""
    if pd.isna(value) or value == 'MISSING' or value == 'N/A':
        return 'N/A'
    if not isinstance(value, (int, float)):
        return 'N/A'
    if format_type == 'currency':
        if abs(value) >= 1e9:
            return f'${value/1e9:.2f}B'
        elif abs(value) >= 1e6:
            return f'${value/1e6:.2f}M'
        else:
            return f'${value:,.0f}'
    elif format_type == 'percentage':
        return f'{value*100:.2f}%'
    elif format_type == 'score':
        return f'{value:.1f}'
    else:
        return f'{value:.2f}'

def display_analysis_results(db_path='financial_analysis.db'):
    """Display analysis results in terminal with color coding"""
    print("\n" + "="*100)
    print(f"{Style.BRIGHT}FINANCIAL ANALYSIS RESULTS - DCF, CAPM & INVESTMENT SCORING")
    print("="*100 + "\n")
    conn = sqlite3.connect(db_path)
    query = '''
        SELECT 
            a.ticker,
            d.current_price,
            d.market_cap,
            d.revenue_growth,
            d.beta,
            d.pe_ratio,
            a.dcf_value,
            a.graham_value as gg_value,
            a.capm_return,
            a.sharpe_ratio,
            a.investment_score,
            a.score_category,
            a.undervalued_percent
        FROM stock_analysis a
        JOIN stock_data d ON a.ticker = d.ticker
        ORDER BY a.investment_score DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Convert 'N/A' to np.nan for numeric columns
    for col in ['investment_score', 'sharpe_ratio', 'beta']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    display_data = []
    for _, row in df.iterrows():
        score_color = get_color_for_score(row['investment_score'])
        value_color = get_value_color(row['undervalued_percent'])
        formatted_row = [
            f"{Style.BRIGHT}{row['ticker']}{Style.RESET_ALL}",
            format_number(row['current_price'], 'currency'),
            format_number(row['market_cap'], 'currency'),
            f"{get_value_color(row['revenue_growth'])}{format_number(row['revenue_growth'], 'percentage')}{Style.RESET_ALL}",
            format_number(row['beta']),
            format_number(row['pe_ratio']),
            f"{value_color}{format_number(row['dcf_value'], 'currency')}{Style.RESET_ALL}",
            format_number(row['gg_value'], 'currency'),
            format_number(row['capm_return'], 'percentage'),
            format_number(row['sharpe_ratio']),
            f"{score_color}{format_number(row['investment_score'], 'score')}{Style.RESET_ALL}",
            f"{score_color}{row['score_category']}{Style.RESET_ALL}",
            f"{value_color}{row['undervalued_percent'] if row['undervalued_percent'] != 'N/A' else 'N/A'}{Style.RESET_ALL}"
        ]
        display_data.append(formatted_row)
    headers = [
        'Ticker', 'Price', 'Mkt Cap', 'Rev Growth', 'Beta', 'P/E',
        'DCF Value', 'GG Value', 'CAPM', 'Sharpe', 'Score', 'Rating', 'Under/Over'
    ]
    print(tabulate(display_data, headers=headers, tablefmt='grid', numalign='right'))
    print(f"\n{Style.BRIGHT}PORTFOLIO SUMMARY{Style.RESET_ALL}")
    print("-" * 50)
    categories = df['score_category'].value_counts()
    print("\nInvestment Categories:")
    for category, count in categories.items():
        if category == 'STRONG BUY':
            color = Fore.GREEN + Style.BRIGHT
        elif category == 'BUY':
            color = Fore.GREEN
        elif category == 'HOLD':
            color = Fore.YELLOW
        elif category == 'SELL':
            color = Fore.RED
        else:
            color = Fore.RED + Style.BRIGHT
        print(f"  {color}{category}: {count} stocks{Style.RESET_ALL}")
    print(f"\nKey Metrics:")
    print(f"  Average Investment Score: {df['investment_score'].mean():.1f}")
    print(f"  Average Sharpe Ratio: {df['sharpe_ratio'].mean():.2f}")
    print(f"  Portfolio Average Beta: {df['beta'].mean():.2f}")
    print(f"\n{Fore.GREEN + Style.BRIGHT}TOP OPPORTUNITIES:{Style.RESET_ALL}")
    top_stocks = df.nlargest(3, 'investment_score')
    for _, stock in top_stocks.iterrows():
        print(f"  • {stock['ticker']}: Score {stock['investment_score']:.1f}, "
              f"Undervalued by {stock['undervalued_percent']:.1f}%")
    risky_stocks = df[df['investment_score'] < 35]
    if not risky_stocks.empty:
        print(f"\n{Fore.RED + Style.BRIGHT}⚠️  WARNINGS:{Style.RESET_ALL}")
        for _, stock in risky_stocks.iterrows():
            print(f"  • {stock['ticker']}: Low score ({stock['investment_score']:.1f})")
    print("\n" + "="*100)
    print(f"\n{Style.BRIGHT}COLOR LEGEND:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN + Style.BRIGHT}■{Style.RESET_ALL} Strong Buy (80-100)")
    print(f"  {Fore.GREEN}■{Style.RESET_ALL} Buy (65-79)")
    print(f"  {Fore.YELLOW}■{Style.RESET_ALL} Hold (50-64)")
    print(f"  {Fore.RED}■{Style.RESET_ALL} Sell (35-49)")
    print(f"  {Fore.RED + Style.BRIGHT}■{Style.RESET_ALL} Strong Sell (0-34)")

def ensure_tables_exist(db_path='financial_analysis.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_analysis (
            ticker TEXT PRIMARY KEY,
            dcf_value REAL,
            graham_value REAL,
            capm_return REAL,
            sharpe_ratio REAL,
            investment_score REAL,
            score_category TEXT,
            undervalued_percent REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_data (
            ticker TEXT PRIMARY KEY,
            current_price REAL,
            market_cap REAL,
            revenue_growth REAL,
            beta REAL,
            pe_ratio REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_tickers_from_csv(csv_path='tickers.csv', db_path='financial_analysis.db'):
    """
    Reads tickers from a CSV file, fetches financial data using yfinance,
    calculates analysis metrics, and inserts results into the database.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ticker = row.get('ticker') or row.get('Ticker') or row.get('TICKER')
            if not ticker:
                continue
            try:
                yf_ticker = yf.Ticker(ticker)
                info = yf_ticker.info

                def safe_get(info, key):
                    val = info.get(key)
                    return val if val is not None else 'N/A'

                price = safe_get(info, 'currentPrice')
                market_cap = safe_get(info, 'marketCap')
                revenue_growth = safe_get(info, 'revenueGrowth')
                beta = safe_get(info, 'beta')
                pe_ratio = safe_get(info, 'trailingPE')
                free_cash_flow = safe_get(info, 'freeCashflow')
                dividends = safe_get(info, 'dividendRate')
            except Exception:
                price, market_cap, revenue_growth, beta, pe_ratio = 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'
                free_cash_flow, dividends = 'N/A', 'N/A'

            # Insert/update stock_data table
            c.execute("INSERT OR REPLACE INTO stock_data VALUES (?, ?, ?, ?, ?, ?)",
                      (ticker, price, market_cap, revenue_growth, beta, pe_ratio))

            # --- Calculations ---
            # DCF Value: Discounted 5-year free cash flow at 10%
            dcf_value = free_cash_flow / ((1 + 0.1) ** 5) if isinstance(free_cash_flow, (int, float)) and free_cash_flow != 0 else 'N/A'

            # Graham (Gordon Growth) Value: Dividends / (0.1 - revenue_growth)
            if (isinstance(dividends, (int, float)) and dividends != 0 and
                isinstance(revenue_growth, (int, float)) and revenue_growth < 0.1 and revenue_growth > -10):
                try:
                    graham_value = dividends / (0.1 - revenue_growth)
                except ZeroDivisionError:
                    graham_value = 'N/A'
            else:
                graham_value = 'N/A'

            # Future Value: market_cap * (1 + revenue_growth)^5
            if (isinstance(market_cap, (int, float)) and market_cap > 0 and
                isinstance(revenue_growth, (int, float)) and revenue_growth > -1):
                try:
                    future_value = market_cap * ((1 + revenue_growth) ** 5)
                except Exception:
                    future_value = 'N/A'
            else:
                future_value = 'N/A'

            # CAPM: 0.04 + beta * (0.1 - 0.04)
            capm_return = 0.04 + beta * (0.1 - 0.04) if isinstance(beta, (int, float)) and beta != 0 else 'N/A'

            # Sharpe Ratio: (capm_return - 0.04) / 0.2
            sharpe_ratio = (capm_return - 0.04) / 0.2 if isinstance(capm_return, (int, float)) else 'N/A'

            # Undervalued percent: (DCF - Price) / Price * 100
            if (isinstance(price, (int, float)) and price > 0 and
                isinstance(dcf_value, (int, float))):
                undervalued_percent = ((dcf_value - price) / price * 100)
            else:
                undervalued_percent = 'N/A'

            # --- Composite Investment Score Calculation ---
            # Normalize metrics to 0-100, skip N/A
            norm_sharpe = min(max((sharpe_ratio / 2) * 100, 0), 100) if isinstance(sharpe_ratio, (int, float)) else 0
            norm_growth = min(max(((revenue_growth + 0.2) / 0.7) * 100, 0), 100) if isinstance(revenue_growth, (int, float)) else 0
            norm_underval = min(max((undervalued_percent + 50) / 1, 0), 100) if isinstance(undervalued_percent, (int, float)) else 0
            norm_capm = min(max((capm_return - 0.04) / 0.16 * 100, 0), 100) if isinstance(capm_return, (int, float)) else 0

            # Composite score with weights
            if all(isinstance(x, (int, float)) for x in [norm_sharpe, norm_growth, norm_underval, norm_capm]) and norm_sharpe > 0:
                investment_score = (
                    0.4 * norm_sharpe +
                    0.2 * norm_growth +
                    0.2 * norm_underval +
                    0.2 * norm_capm
                )
                investment_score = min(max(investment_score, 0), 100)
            else:
                investment_score = 'N/A'

            # Score category logic
            if not isinstance(investment_score, (int, float)):
                score_category = 'N/A'
            elif investment_score >= 80:
                score_category = 'STRONG BUY'
            elif investment_score >= 65:
                score_category = 'BUY'
            elif investment_score >= 50:
                score_category = 'HOLD'
            elif investment_score >= 35:
                score_category = 'SELL'
            else:
                score_category = 'STRONG SELL'

            # Insert/update stock_analysis table
            c.execute(
                "INSERT OR REPLACE INTO stock_analysis VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ticker, dcf_value, graham_value, capm_return, sharpe_ratio, investment_score, score_category, undervalued_percent))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    ensure_tables_exist()
    insert_tickers_from_csv('tickers.csv')
    display_analysis_results()