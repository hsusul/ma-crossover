import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

TICKER = "SPY"
SHORT_WINDOW = 20
LONG_WINDOW = 100

RAW_CSV = Path("data/raw/SPY_daily.csv")

OUT_DIR = Path("data/processed")
FIG_DIR = Path("reports/figures")

OUT_FEATURES_CSV = OUT_DIR / "spy_features.csv"
OUT_FIG = FIG_DIR / "spy_ma_overlay.png"



def ensure_dirs() -> None:
    """Makes sure that the out and fig paths exist"""
    OUT_DIR.mkdir(parents = True, exist_ok = True)
    FIG_DIR.mkdir(parents = True, exist_ok = True)

def load_raw() -> pd.DataFrame:
    """Loads csv and sets date as index"""
    if RAW_CSV.exists():
        path = RAW_CSV
    else:
        raise FileNotFoundError("Could not find raw CSV.")
    
    df = pd.read_csv(path)

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")

    return df

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """builds long and short term features"""
    price_col = "Adj Close" 
    out = df.copy()
    out["price"] = out[price_col].astype(float)
    out["ret_1d"] = out["price"].pct_change()
    out[f"ma_{SHORT_WINDOW}"] = out["price"].rolling(SHORT_WINDOW).mean()
    out[f"ma_{LONG_WINDOW}"] = out["price"].rolling(LONG_WINDOW).mean()
    out["log_ret_1d"] = np.log(out["price"]).diff()

    return out

def save_features(df_feat: pd.DataFrame) -> None:
    """saves new features to csv"""
    df_out = df_feat.copy()
    df_out.insert(0, "date", df_out.index.date)
    df_out.to_csv(OUT_FEATURES_CSV, index = False)
    print(f"Saved features -> {OUT_FEATURES_CSV}")

def save_ma_plot(df_feat: pd.DataFrame) -> None:
    """prints moving averages on plot"""
    short_col = f"ma_{SHORT_WINDOW}"
    long_col = f"ma_{LONG_WINDOW}"
    plt.figure()
    plt.plot(df_feat.index, df_feat["price"], label = "Adj Close")
    plt.plot(df_feat.index, df_feat[short_col], label = short_col)
    plt.plot(df_feat.index, df_feat[long_col], label = long_col)
    plt.title(f"{TICKER} Price + Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_FIG, dpi = 200)
    plt.close()
    print(f"Saved figure -> {OUT_FIG}")

def main() -> int:
    ensure_dirs()
    df_raw = load_raw()
    df_feat = build_features(df_raw)
    print(df_feat[["price", f"ma_{SHORT_WINDOW}", f"ma_{LONG_WINDOW}", "ret_1d"]].tail(5))
    save_features(df_feat)
    save_ma_plot(df_feat)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())


