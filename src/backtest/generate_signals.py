from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

TICKER = "SPY"
SHORT_WINDOW = 20
LONG_WINDOW = 100

FEATURES_CSV = Path("data/processed/spy_features.csv")
OUT_DIR = Path("data/processed")
FIG_DIR = Path("reports/figures")

OUT_SIGNALS_CSV = OUT_DIR / "spy_signals.csv"
OUT_FIG = FIG_DIR / "spy_signals.png"

def ensure_dirs() -> None:
    """Makes sure that the out and fig paths exist"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def load_features() -> pd.DataFrame:
    if not FEATURES_CSV.exists():
        raise FileNotFoundError(f"Missing features file: {FEATURES_CSV}")
    df = pd.read_csv(FEATURES_CSV)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    return df


def generate_signals(df:pd.DataFrame) -> pd.DataFrame:
    """generates buy or sell signals depending on if short window moving average is greater than long window moving average"""
    short_col = f"ma_{SHORT_WINDOW}"
    long_col = f"ma_{LONG_WINDOW}"
    out = df.dropna(subset = [short_col, long_col]).copy()
    out["signal"] = (out[short_col] > out[long_col]).astype(int)
    out["position"] = out["signal"].shift(1).fillna(0).astype(int)
    return out


def print_summary(df_sig: pd.DataFrame) -> None:
    """Number of trades ~~ number of position changes"""
    pos_changes = df_sig["position"].diff().fillna(0)
    entries = (pos_changes == 1).sum()
    exits = (pos_changes == -1).sum()

    print("\n=== Signals Summary ===")
    print(f"Rows: {len(df_sig):,}")
    print(f"Start: {df_sig.index.min().date()}")
    print(f"End:   {df_sig.index.max().date()}")
    print(f"Days in market (position=1): {int(df_sig['position'].sum()):,}")
    print(f"Entries: {int(entries)}")
    print(f"Exits:   {int(exits)}")


def save_signals(df_sig: pd.DataFrame) -> None:
    """saves to csv"""
    out = df_sig.copy()
    out.insert(0, "date", out.index.date)
    out.to_csv(OUT_SIGNALS_CSV, index=False)
    print(f"Saved signals -> {OUT_SIGNALS_CSV}")


def save_signal_plot(df_sig: pd.DataFrame) -> None:
    """saves the signals for buy/sell to plot"""
    pos_changes = df_sig["position"].diff().fillna(0)
    entries = df_sig[pos_changes == 1]
    exits = df_sig[pos_changes == -1]

    plt.figure()
    plt.plot(df_sig.index, df_sig["price"], label="price")
    plt.scatter(entries.index, entries["price"], marker="^", label="entry")
    plt.scatter(exits.index, exits["price"], marker="v", label="exit")
    plt.title(f"{TICKER} MA Crossover Signals ({SHORT_WINDOW}/{LONG_WINDOW})")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_FIG, dpi=200)
    plt.close()
    print(f"Saved figure -> {OUT_FIG}")


def main() -> int:
    ensure_dirs()
    df_feat = load_features()
    df_sig = generate_signals(df_feat)

    print_summary(df_sig)
    save_signals(df_sig)
    save_signal_plot(df_sig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())