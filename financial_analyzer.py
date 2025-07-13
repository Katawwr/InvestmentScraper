import pandas as pd
from colorama import init, Fore, Style
from tabulate import tabulate
import sqlite3
import csv

# Initialize colorama for cross-platform color support
init(autoreset=True)

def get_color_for_score(score):
    """Return color based on investment score"""
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

def get_value_color(value, is_percentage=False):
    """Return color for positive/negative values"""
    if value > 0:
        return Fore.GREEN
    elif value < 0:
        return Fore.RED
    else:
        return Fore.WHITE

def format_number(value, format_type='general'):
    """Format numbers for display"""
    if pd.isna(value) or value == 'MISSING':
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
    if df.empty:
        print("No analysis data found. Run analysis first.")
        return
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
            f"{value_color}{row['undervalued_percent']:.1f}%{Style.RESET_ALL}"
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
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ticker = row.get('ticker') or row.get('Ticker') or row.get('TICKER')
            if not ticker:
                continue  # skip rows without a ticker
            # Insert with placeholder/demo values for other columns
            c.execute("INSERT OR IGNORE INTO stock_data VALUES (?, ?, ?, ?, ?, ?)",
                      (ticker, 10.0, 100000000, 0.1, 1.0, 20.0))
            c.execute("INSERT OR IGNORE INTO stock_analysis VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (ticker, 12.0, 11.0, 0.08, 1.05, 60.0, 'HOLD', 10.0))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    ensure_tables_exist()
    insert_tickers_from_csv('tickers.csv')
    display_analysis_results()