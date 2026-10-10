import pandas as pd
import numpy as np


def prepare_market_data(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # -------------------------------------------------
    # DATE
    # -------------------------------------------------

    df["TIMESTAMP"] = pd.to_datetime(
        df["TIMESTAMP"],
        errors="coerce"
    )

    # -------------------------------------------------
    # NUMERIC COLUMNS
    # -------------------------------------------------

    numeric_columns = [
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "PREVCLOSE",
        "TOTTRDQTY",
        "TOTTRDVAL",
        "TOTALTRADES",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # -------------------------------------------------
    # CLEAN SYMBOL
    # -------------------------------------------------

    df["SYMBOL"] = (
        df["SYMBOL"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # -------------------------------------------------
    # SORT
    # -------------------------------------------------

    df = df.dropna(
        subset=[
            "SYMBOL",
            "TIMESTAMP",
            "CLOSE"
        ]
    )

    df = df.sort_values(
        by=[
            "SYMBOL",
            "TIMESTAMP"
        ]
    ).reset_index(
        drop=True
    )

    # -------------------------------------------------
    # DAILY RETURN
    # -------------------------------------------------

    previous_close = (
        df["PREVCLOSE"]
        .replace(0, np.nan)
    )

    df["daily_return"] = (
        (
            df["CLOSE"]
            - previous_close
        )
        / previous_close
    ) * 100

    # -------------------------------------------------
    # PRICE RANGE
    # -------------------------------------------------

    low_price = (
        df["LOW"]
        .replace(0, np.nan)
    )

    df["price_range_pct"] = (
        (
            df["HIGH"]
            - df["LOW"]
        )
        / low_price
    ) * 100

    # -------------------------------------------------
    # MOVING AVERAGES
    # -------------------------------------------------

    df["ma_5"] = (
        df.groupby("SYMBOL")["CLOSE"]
        .transform(
            lambda x:
            x.rolling(
                5,
                min_periods=1
            ).mean()
        )
    )

    df["ma_20"] = (
        df.groupby("SYMBOL")["CLOSE"]
        .transform(
            lambda x:
            x.rolling(
                20,
                min_periods=1
            ).mean()
        )
    )

    # -------------------------------------------------
    # DISTANCE FROM MA20
    # -------------------------------------------------

    safe_ma20 = (
        df["ma_20"]
        .replace(0, np.nan)
    )

    df["ma20_distance_pct"] = (
        (
            df["CLOSE"]
            - safe_ma20
        )
        / safe_ma20
    ) * 100

    # -------------------------------------------------
    # 20 DAY VOLATILITY
    # -------------------------------------------------

    df["volatility_20"] = (
        df.groupby("SYMBOL")["daily_return"]
        .transform(
            lambda x:
            x.rolling(
                20,
                min_periods=5
            ).std()
        )
    )

    # -------------------------------------------------
    # VOLUME
    # -------------------------------------------------

    df["avg_volume_5"] = (
        df.groupby("SYMBOL")["TOTTRDQTY"]
        .transform(
            lambda x:
            x.rolling(
                5,
                min_periods=1
            ).mean()
        )
    )

    safe_avg_volume = (
        df["avg_volume_5"]
        .replace(0, np.nan)
    )

    df["volume_ratio"] = (
        df["TOTTRDQTY"]
        / safe_avg_volume
    )

    # -------------------------------------------------
    # TRADE COUNT
    # -------------------------------------------------

    df["avg_trades_5"] = (
        df.groupby("SYMBOL")["TOTALTRADES"]
        .transform(
            lambda x:
            x.rolling(
                5,
                min_periods=1
            ).mean()
        )
    )

    safe_avg_trades = (
        df["avg_trades_5"]
        .replace(0, np.nan)
    )

    df["trade_count_ratio"] = (
        df["TOTALTRADES"]
        / safe_avg_trades
    )

    # -------------------------------------------------
    # REMOVE INF VALUES
    # -------------------------------------------------

    df = df.replace(
        [
            np.inf,
            -np.inf
        ],
        np.nan
    )

    # -------------------------------------------------
    # REQUIRED DATA
    # -------------------------------------------------

    df = df.dropna(
        subset=[
            "CLOSE",
            "daily_return",
            "volume_ratio"
        ]
    )

    return df.reset_index(
        drop=True
    )