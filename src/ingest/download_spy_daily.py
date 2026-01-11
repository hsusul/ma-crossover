import yfinance as yf
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import sys
from pathlib import Path

RAW_DIR = Path("data/raw")
FIG_DIR = Path("reports/figures")

OUT_CSV = RAW_DIR / "SPY_daily.csv"
OUTFIG = FIG_DIR / "spy_price.png"

TICKER = "SPY"
START = "2010-01-01"


def ensure_dirs() -> None:
    """Makes sure that the folders data """
    RAW_DIR.mkdir(parents = True, exist_ok = True)
    FIG_DIR.mkdir(parents = True, exist_ok = True)

def download_spy_daily() -> pd.DataFrame:
    """creates dataframe of spy data daily"""
    df = yf.download(
        TICKER,
        start = START,
        interval = "1d",
        auto_adjust = False,
        progress = False,
        actions = True,
    )
    df.index = pd.to_datetime(df.index)
    #remove timezones if there is timezones
    try:
        df.index = df.index.tz_localize(None)
    except TypeError:
        pass

    # Sort index chronologically and drop duplicate dates
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]
    

    #Flatten MultiIndex columns 
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
        df.columns.name = None  
    return df


def sanity_check(df: pd.DataFrame) -> None:
    """Check if DataFrame has everything"""
    required = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    if df.empty:
        raise ValueError("DataFrame is empty.")

    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # index checks
    if not df.index.is_monotonic_increasing:
        raise ValueError("Index is not sorted in increasing (chronological) order.")

    dupes = df.index.duplicated().sum()
    if dupes > 0:
        raise ValueError(f"Found {dupes} duplicate dates in the index.")

    # NA checks
    na_counts = df[required].isna().sum()
    total_nas = int(na_counts.sum())

    print("\nCheck")
    print(f"Rows: {len(df):,}")
    print(f"Start: {df.index.min().date()}")
    print(f"End:   {df.index.max().date()}")
    print(f"Total missing values (required cols): {total_nas}")
    print("Missing by column:")
    print(na_counts)


def save_csv(df: pd.DataFrame) -> None:
    """Saves Dataframe to csv"""
    out = df.copy()
    out.insert(0, "date", out.index.date)
    out.to_csv(OUT_CSV, index=False)
    print(f"\nSaved CSV -> {OUT_CSV}")


def save_price_plot(df:pd.DataFrame) -> None:
    """Creates price plot and saves to png"""
    price_col = "Adj Close" if "Adj Close" in df.columns else "Close"

    plt.figure()
    plt.plot(df.index, df[price_col])
    plt.title(f"{TICKER} Daily {price_col}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.tight_layout()
    plt.savefig(OUTFIG, dpi=200)
    plt.close()
    print(f"Saved figure -> {OUTFIG}")

def main() -> int:
    ensure_dirs()
    df = download_spy_daily()
    print(df.head())
    print("\nColumns:", list(df.columns))
    sanity_check(df)
    save_csv(df)
    save_price_plot(df)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())