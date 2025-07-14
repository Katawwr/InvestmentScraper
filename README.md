# InvestmentScraper

A Python tool for automated financial analysis and scoring of stocks using Yahoo Finance data.  
It calculates DCF, CAPM, Sharpe ratio, and a composite investment score for a list of tickers, and displays results in a color-coded terminal table.

---

## Features

- **Reads tickers from `tickers.csv`** (one per line, header: `ticker`)
- **Fetches financial data** using [yfinance](https://github.com/ranaroussi/yfinance)
- **Calculates key metrics:**  
  - Discounted Cash Flow (DCF)
  - Graham (Gordon Growth) Value
  - CAPM expected return
  - Sharpe Ratio (risk-adjusted return)
  - Composite Investment Score (customizable weighting)
- **Color-coded terminal output** with summary stats and top opportunities
- **Handles missing data gracefully** (shows `N/A`)

---

## Getting Started

### 1. **Install Requirements**

```bash
pip install yfinance pandas tabulate colorama
```

### 2. **Edit Your Ticker List**

- Open `tickers.csv` and add/remove tickers (one per line, header must be `ticker`).
- Example:
  ```
  ticker
  AAPL
  MSFT
  TSLA
  ```

### 3. **Run the Analyzer**

```bash
python financial_analyzer.py
```

---

## Adjusting the Scoring System

The composite investment score is calculated as a weighted sum of normalized metrics:

```python
investment_score = (
    0.4 * norm_sharpe +
    0.2 * norm_growth +
    0.2 * norm_underval +
    0.2 * norm_capm
)
```

- **To adjust weights:**  
  Edit the weights in the `insert_tickers_from_csv` function.  
  Make sure the weights sum to 1.0 (or 100%).

- **To add/remove metrics:**  
  - Add your normalization logic for the new metric.
  - Add it to the weighted sum.
  - Adjust the weights accordingly.

---

## Notes & Tips

- **Ticker symbols must match Yahoo Finance.**  
  Some international or special tickers may not be supported.
- **Missing data:**  
  If a stock is missing key data, its score and rating will show as `N/A`.
- **Error 404:**  
  This means Yahoo Finance could not find the ticker. Check for typos or delisted stocks.
- **Customize further:**  
  You can add more metrics (e.g., P/E, PEG, FCF margin) or filters (e.g., minimum market cap) as desired.
- **For best results:**  
  Use a mix of value, growth, and risk metrics, and test your weights on historical data.

---

## License

MIT License

---
