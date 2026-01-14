<!-- README.md -->

# ma-crossover

A **dual moving-average crossover (trend-following)** trading strategy on **SPY** with a small, reproducible pipeline:

1) **Ingest**: download SPY daily data  
2) **Features**: returns + moving averages (MA20/MA100)  
3) **Signals**: crossover signal + position (shifted 1 day)  
4) **Backtest**: strategy vs buy-and-hold, equity curve + drawdown

---

## Strategy

- **Fast MA**: MA(20)
- **Slow MA**: MA(100)
- **Signal**: `1` when `MA20 > MA100`, else `0`
- **Position**: `signal.shift(1)` (trade next day to avoid look-ahead bias)

---

## Repo structure

- `src/ingest/` — download and save raw data
- `src/features/` — compute indicators/features
- `src/backtest/` — generate signals + run backtest
- `data/raw/` — raw CSV output (ignored by git)
- `data/processed/` — processed CSV outputs (ignored by git)
- `reports/figures/` — plots

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
