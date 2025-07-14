# InvestmentScraper

A Python tool for automated financial analysis and scoring of stocks using Yahoo Finance data.  
It calculates DCF, CAPM, Sharpe ratio, and a composite investment score for a list of tickers, and displays results in a color-coded terminal table.

---

## ⚠️ DISCLAIMER

**THIS SOFTWARE IS FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY.**

- **NOT FINANCIAL ADVICE:** This tool does not provide financial, investment, or trading advice.
- **DO YOUR OWN RESEARCH:** All investment decisions should be based on your own research and risk tolerance.
- **CONSULT PROFESSIONALS:** Always consult with qualified financial advisors before making investment decisions.
- **NO WARRANTIES:** The calculations and scores are simplified models and may not reflect real market conditions.
- **USE AT YOUR OWN RISK:** The authors are not responsible for any financial losses resulting from the use of this software.

**Past performance does not guarantee future results. All investments carry risk of loss.**

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

## License

MIT License

---
