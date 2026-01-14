from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

TICKER = "SPY"
SIGNALS_CSV = Path("data/processed/spy_signals.csv")

FIG_DIR = Path("reports/figures")
OUT_EQUITY_FIG = FIG_DIR / "equity_curve.png"
OUT_DD_FIG = FIG_DIR / "drawdown.png"

TCOST = 0.0005

TRADING_DAYS = 252

def ensure_dirs() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def load_signals() -> pd.DataFrame:
    df = pd.read_csv(SIGNALS_CSV)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    df["price"] = df["price"].astype(float)
    df["ret_1d"] = df["ret_1d"].astype(float)
    df["position"] = df["position"].astype(int)

    return df

def compute_equity(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["bh_ret"] = out["ret_1d"].fillna(0.0)
    out["strat_ret_gross"] = out["position"] * out["bh_ret"]
    out["trade"] = out["position"].diff().abs().fillna(0).astype(int)
    out["strat_ret_net"] = out["strat_ret_gross"] - (out["trade"] * TCOST)
    out["equity_bh"] = (1.0 + out["bh_ret"]).cumprod()
    out["equity_strat"] = (1.0 + out["strat_ret_net"]).cumprod()

    return out    


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def cagr(equity: pd.Series) -> float:
    n = len(equity)
    years = n / TRADING_DAYS
    if years <= 0:
        return 0.0
    return float(equity.iloc[-1] ** (1.0 / years) - 1.0)


def plot_equity(out: pd.DataFrame) -> None:
    plt.figure()
    plt.plot(out.index, out["equity_bh"], label="Buy & Hold")
    plt.plot(out.index, out["equity_strat"], label="MA Crossover (net)")
    plt.title(f"{TICKER} Equity Curve (TCOST={TCOST:.4f})")
    plt.xlabel("Date")
    plt.ylabel("Equity (start=1.0)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_EQUITY_FIG, dpi=200)
    plt.close()
    print(f"Saved figure -> {OUT_EQUITY_FIG}")


def plot_drawdown(out: pd.DataFrame) -> None:
    peak = out["equity_strat"].cummax()
    dd = out["equity_strat"] / peak - 1.0
    plt.figure()
    plt.plot(out.index, dd, label="Drawdown")
    plt.title(f"{TICKER} Strategy Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.tight_layout()
    plt.savefig(OUT_DD_FIG, dpi=200)
    plt.close()
    print(f"Saved figure -> {OUT_DD_FIG}")


def print_metrics(out: pd.DataFrame) -> None:
    pos_changes = out["position"].diff().fillna(0)
    entries = int((pos_changes == 1).sum())
    exits = int((pos_changes == -1).sum())
    bh_total = float(out["equity_bh"].iloc[-1] - 1.0)
    strat_total = float(out["equity_strat"].iloc[-1] - 1.0)
    bh_cagr = cagr(out["equity_bh"])
    strat_cagr = cagr(out["equity_strat"])
    bh_mdd = max_drawdown(out["equity_bh"])
    strat_mdd = max_drawdown(out["equity_strat"])
    print("\n=== Backtest Metrics ===")
    print(f"Period: {out.index.min().date()} -> {out.index.max().date()}")
    print(f"Rows: {len(out):,}")
    print(f"Entries: {entries} | Exits: {exits} | Trade events: {int(out['trade'].sum())}")
    print(f"Buy&Hold Total Return: {bh_total:.2%} | CAGR: {bh_cagr:.2%} | Max DD: {bh_mdd:.2%}")
    print(f"Strategy Total Return: {strat_total:.2%} | CAGR: {strat_cagr:.2%} | Max DD: {strat_mdd:.2%}")


def main() -> int:
    ensure_dirs()
    df = load_signals()
    out = compute_equity(df)
    print_metrics(out)
    plot_equity(out)
    plot_drawdown(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())