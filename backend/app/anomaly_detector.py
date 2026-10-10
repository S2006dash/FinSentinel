import pandas as pd
import numpy as np


def safe_quantile(
    series,
    quantile,
    fallback
):

    values = pd.to_numeric(
        series,
        errors="coerce"
    ).dropna()

    if values.empty:
        return fallback

    value = float(
        values.quantile(quantile)
    )

    if not np.isfinite(value):
        return fallback

    return value


def detect_anomalies(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    # -------------------------------------------------
    # BASIC CLEANING
    # -------------------------------------------------

    df["SYMBOL"] = (
        df["SYMBOL"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    numeric_columns = [
        "daily_return",
        "volume_ratio",
        "volatility_20",
        "ma20_distance_pct",
        "CLOSE",
        "OPEN",
        "HIGH",
        "LOW",
        "TOTTRDQTY",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    df = df.replace(
        [
            np.inf,
            -np.inf
        ],
        np.nan
    )

    # -------------------------------------------------
    # ABSOLUTE FEATURES
    # -------------------------------------------------

    df["abs_return"] = (
        df["daily_return"]
        .abs()
    )

    df["abs_ma_distance"] = (
        df["ma20_distance_pct"]
        .abs()
    )

    # -------------------------------------------------
    # DATA-DRIVEN THRESHOLDS
    #
    # This makes the detector adapt to the dataset.
    # -------------------------------------------------

    return_95 = safe_quantile(
        df["abs_return"],
        0.95,
        3.0
    )

    return_99 = safe_quantile(
        df["abs_return"],
        0.99,
        5.0
    )

    return_999 = safe_quantile(
        df["abs_return"],
        0.999,
        8.0
    )

    volume_90 = safe_quantile(
        df["volume_ratio"],
        0.90,
        2.0
    )

    volume_97 = safe_quantile(
        df["volume_ratio"],
        0.97,
        3.0
    )

    volume_99 = safe_quantile(
        df["volume_ratio"],
        0.99,
        5.0
    )

    volatility_90 = safe_quantile(
        df["volatility_20"],
        0.90,
        2.0
    )

    volatility_97 = safe_quantile(
        df["volatility_20"],
        0.97,
        4.0
    )

    volatility_99 = safe_quantile(
        df["volatility_20"],
        0.99,
        6.0
    )

    ma_90 = safe_quantile(
        df["abs_ma_distance"],
        0.90,
        5.0
    )

    ma_97 = safe_quantile(
        df["abs_ma_distance"],
        0.97,
        10.0
    )

    ma_99 = safe_quantile(
        df["abs_ma_distance"],
        0.99,
        15.0
    )

    # -------------------------------------------------
    # KEEP MINIMUM FINANCIAL THRESHOLDS
    # -------------------------------------------------

    price_threshold_1 = max(
        3.0,
        return_95
    )

    price_threshold_2 = max(
        5.0,
        return_99
    )

    price_threshold_3 = max(
        8.0,
        return_999
    )

    volume_threshold_1 = max(
        2.0,
        volume_90
    )

    volume_threshold_2 = max(
        3.0,
        volume_97
    )

    volume_threshold_3 = max(
        5.0,
        volume_99
    )

    volatility_threshold_1 = max(
        2.0,
        volatility_90
    )

    volatility_threshold_2 = max(
        4.0,
        volatility_97
    )

    volatility_threshold_3 = max(
        6.0,
        volatility_99
    )

    ma_threshold_1 = max(
        5.0,
        ma_90
    )

    ma_threshold_2 = max(
        10.0,
        ma_97
    )

    ma_threshold_3 = max(
        15.0,
        ma_99
    )

    # -------------------------------------------------
    # PRICE SIGNAL
    # -------------------------------------------------

    df["price_signal"] = 0

    df.loc[
        df["abs_return"]
        >= price_threshold_1,
        "price_signal"
    ] = 1

    df.loc[
        df["abs_return"]
        >= price_threshold_2,
        "price_signal"
    ] = 2

    df.loc[
        df["abs_return"]
        >= price_threshold_3,
        "price_signal"
    ] = 3

    # -------------------------------------------------
    # VOLUME SIGNAL
    # -------------------------------------------------

    df["volume_signal"] = 0

    df.loc[
        df["volume_ratio"]
        >= volume_threshold_1,
        "volume_signal"
    ] = 1

    df.loc[
        df["volume_ratio"]
        >= volume_threshold_2,
        "volume_signal"
    ] = 2

    df.loc[
        df["volume_ratio"]
        >= volume_threshold_3,
        "volume_signal"
    ] = 3

    # -------------------------------------------------
    # VOLATILITY SIGNAL
    # -------------------------------------------------

    df["volatility_signal"] = 0

    df.loc[
        df["volatility_20"]
        >= volatility_threshold_1,
        "volatility_signal"
    ] = 1

    df.loc[
        df["volatility_20"]
        >= volatility_threshold_2,
        "volatility_signal"
    ] = 2

    df.loc[
        df["volatility_20"]
        >= volatility_threshold_3,
        "volatility_signal"
    ] = 3

    # -------------------------------------------------
    # MOVING AVERAGE SIGNAL
    # -------------------------------------------------

    df["ma_signal"] = 0

    df.loc[
        df["abs_ma_distance"]
        >= ma_threshold_1,
        "ma_signal"
    ] = 1

    df.loc[
        df["abs_ma_distance"]
        >= ma_threshold_2,
        "ma_signal"
    ] = 2

    df.loc[
        df["abs_ma_distance"]
        >= ma_threshold_3,
        "ma_signal"
    ] = 3

    # -------------------------------------------------
    # ANOMALY SCORE
    # -------------------------------------------------

    df["anomaly_score"] = (
        df["price_signal"]
        + df["volume_signal"]
        + df["volatility_signal"]
        + df["ma_signal"]
    )

    # -------------------------------------------------
    # PRIORITY
    # -------------------------------------------------

    df["priority"] = "NORMAL"

    df.loc[
        df["anomaly_score"] >= 3,
        "priority"
    ] = "MEDIUM"

    df.loc[
        df["anomaly_score"] >= 6,
        "priority"
    ] = "HIGH"

    df.loc[
        df["anomaly_score"] >= 9,
        "priority"
    ] = "CRITICAL"

    # -------------------------------------------------
    # REASON
    # -------------------------------------------------

    def create_reason(row):

        reasons = []

        if row["price_signal"] > 0:

            reasons.append(
                f"Price movement "
                f"{row['daily_return']:.2f}%"
            )

        if row["volume_signal"] > 0:

            reasons.append(
                f"Volume "
                f"{row['volume_ratio']:.2f}x average"
            )

        if (
            pd.notna(row["volatility_20"])
            and row["volatility_signal"] > 0
        ):

            reasons.append(
                f"Volatility "
                f"{row['volatility_20']:.2f}%"
            )

        if (
            pd.notna(row["ma20_distance_pct"])
            and row["ma_signal"] > 0
        ):

            reasons.append(
                f"Price "
                f"{row['ma20_distance_pct']:.2f}% "
                f"from MA20"
            )

        if not reasons:

            return (
                "No significant anomaly detected"
            )

        return " | ".join(reasons)

    df["reason"] = df.apply(
        create_reason,
        axis=1
    )

    # -------------------------------------------------
    # DEBUG INFORMATION
    # -------------------------------------------------

    anomaly_count = int(
        (df["anomaly_score"] > 0).sum()
    )

    critical_count = int(
        (
            df["priority"]
            == "CRITICAL"
        ).sum()
    )

    high_count = int(
        (
            df["priority"]
            == "HIGH"
        ).sum()
    )

    medium_count = int(
        (
            df["priority"]
            == "MEDIUM"
        ).sum()
    )

    print(
        "Anomaly detection complete:"
    )

    print(
        f"Total rows: {len(df)}"
    )

    print(
        f"Anomalies: {anomaly_count}"
    )

    print(
        f"Medium: {medium_count}"
    )

    print(
        f"High: {high_count}"
    )

    print(
        f"Critical: {critical_count}"
    )

    print(
        "Thresholds:"
    )

    print(
        f"Price: "
        f"{price_threshold_1:.2f} / "
        f"{price_threshold_2:.2f} / "
        f"{price_threshold_3:.2f}"
    )

    print(
        f"Volume: "
        f"{volume_threshold_1:.2f} / "
        f"{volume_threshold_2:.2f} / "
        f"{volume_threshold_3:.2f}"
    )

    return df