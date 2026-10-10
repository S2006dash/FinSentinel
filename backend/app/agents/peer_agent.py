import pandas as pd

from app.sector_map import get_sector


def run_peer_agent(
    market_df,
    symbol,
    event_date
):

    print(
        f"Running Peer Intelligence Agent "
        f"for {symbol} on {event_date}"
    )

    symbol = symbol.upper().strip()

    event_date = pd.to_datetime(
        event_date,
        errors="coerce"
    )

    if pd.isna(event_date):

        return {
            "agent": "Peer Intelligence Agent",
            "symbol": symbol,
            "event_date": str(event_date),
            "status": "ERROR",
            "comparison": []
        }

    df = market_df.copy()

    df["TIMESTAMP"] = pd.to_datetime(
        df["TIMESTAMP"],
        errors="coerce"
    )

    event_rows = df[
        df["TIMESTAMP"].dt.normalize()
        == event_date.normalize()
    ].copy()

    if event_rows.empty:

        return {
            "agent": "Peer Intelligence Agent",
            "symbol": symbol,
            "event_date": event_date.strftime(
                "%Y-%m-%d"
            ),
            "status": "NO_DATA",
            "message": "No market data available for this date",
            "comparison": []
        }

    # -------------------------------------------------
    # DAILY RETURN
    # -------------------------------------------------

    if "daily_return" not in event_rows.columns:

        event_rows["daily_return"] = (
            (
                event_rows["CLOSE"]
                - event_rows["PREVCLOSE"]
            )
            / event_rows["PREVCLOSE"]
        ) * 100

    event_rows["SYMBOL_NORMALIZED"] = (
        event_rows["SYMBOL"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # -------------------------------------------------
    # TARGET STOCK
    # -------------------------------------------------

    target = event_rows[
        event_rows["SYMBOL_NORMALIZED"]
        == symbol
    ].copy()

    if target.empty:

        return {
            "agent": "Peer Intelligence Agent",
            "symbol": symbol,
            "event_date": event_date.strftime(
                "%Y-%m-%d"
            ),
            "status": "NO_STOCK",
            "message": (
                "Stock was not found in the market "
                "dataset for this date."
            ),
            "comparison": []
        }

    target_return = float(
        target.iloc[0]["daily_return"]
    )

    # -------------------------------------------------
    # BROADER MARKET
    # -------------------------------------------------

    valid_returns = event_rows[
        event_rows["daily_return"].notna()
    ]["daily_return"]

    if valid_returns.empty:

        return {
            "agent": "Peer Intelligence Agent",
            "symbol": symbol,
            "event_date": event_date.strftime(
                "%Y-%m-%d"
            ),
            "status": "NO_RETURN_DATA",
            "comparison": []
        }

    market_average = float(
        valid_returns.mean()
    )

    market_median = float(
        valid_returns.median()
    )

    market_std = float(
        valid_returns.std()
    )

    relative_to_market = (
        target_return
        - market_average
    )

    if market_average > 0.5:

        market_direction = "BROAD_MARKET_UP"

    elif market_average < -0.5:

        market_direction = "BROAD_MARKET_DOWN"

    else:

        market_direction = "MARKET_MIXED"

    if abs(relative_to_market) >= 5:

        interpretation = (
            "Stock movement was substantially "
            "different from the broader market."
        )

    elif abs(relative_to_market) >= 3:

        interpretation = (
            "Stock movement was moderately "
            "different from the broader market."
        )

    else:

        interpretation = (
            "Stock movement was broadly aligned "
            "with the market."
        )

    # -------------------------------------------------
    # TOP MARKET COMPARISON
    # -------------------------------------------------

    comparison_df = event_rows[
        [
            "SYMBOL_NORMALIZED",
            "CLOSE",
            "daily_return"
        ]
    ].copy()

    comparison_df = comparison_df.dropna(
        subset=["daily_return"]
    )

    comparison_df = comparison_df.sort_values(
        by="daily_return",
        key=lambda x: x.abs(),
        ascending=False
    )

    comparison_df = comparison_df.head(10)

    comparison = []

    for _, row in comparison_df.iterrows():

        comparison.append({

            "symbol": str(
                row["SYMBOL_NORMALIZED"]
            ),

            "close": float(
                row["CLOSE"]
            ),

            "daily_return": float(
                row["daily_return"]
            )
        })

    # =================================================
    # SECTOR ANALYSIS
    # =================================================

    sector = get_sector(symbol)

    sector_average = None
    sector_median = None
    relative_to_sector = None
    sector_peer_count = 0
    sector_interpretation = None
    sector_status = "SECTOR_UNAVAILABLE"

    if sector is not None:

        event_rows["SECTOR"] = (
            event_rows["SYMBOL_NORMALIZED"]
            .map(get_sector)
        )

        sector_rows = event_rows[
            event_rows["SECTOR"]
            == sector
        ].copy()

        # Exclude target stock from peer calculation.
        sector_peers = sector_rows[
            sector_rows["SYMBOL_NORMALIZED"]
            != symbol
        ].copy()

        sector_peers = sector_peers[
            sector_peers["daily_return"].notna()
        ]

        if not sector_peers.empty:

            sector_peer_count = (
                sector_peers["SYMBOL_NORMALIZED"]
                .nunique()
            )

            sector_average = float(
                sector_peers["daily_return"].mean()
            )

            sector_median = float(
                sector_peers["daily_return"].median()
            )

            relative_to_sector = (
                target_return
                - sector_average
            )

            sector_status = "SUCCESS"

            if abs(relative_to_sector) >= 5:

                sector_interpretation = (
                    "The stock moved substantially differently "
                    "from its sector peers, suggesting a "
                    "potentially stock-specific signal."
                )

            elif abs(relative_to_sector) >= 3:

                sector_interpretation = (
                    "The stock showed moderate divergence "
                    "from its sector peers."
                )

            else:

                sector_interpretation = (
                    "The stock movement was broadly aligned "
                    "with its sector peers."
                )

        else:

            sector_status = "NO_SECTOR_DATA"

            sector_interpretation = (
                "A sector classification exists, but there "
                "is not enough peer data for this date."
            )

    # -------------------------------------------------
    # EVIDENCE
    # -------------------------------------------------

    evidence = [

        {
            "type": "STOCK_RETURN",
            "status": "OBSERVED",
            "message": (
                f"{symbol} moved "
                f"{target_return:.2f}% "
                f"on the event date."
            )
        },

        {
            "type": "MARKET_AVERAGE",
            "status": "OBSERVED",
            "message": (
                f"Average stock movement across "
                f"available market data was "
                f"{market_average:.2f}%."
            )
        },

        {
            "type": "RELATIVE_PERFORMANCE",
            "status": "OBSERVED",
            "message": (
                f"{symbol} differed from the "
                f"market average by "
                f"{relative_to_market:.2f} "
                f"percentage points."
            )
        }
    ]

    if sector_status == "SUCCESS":

        evidence.append({

            "type": "SECTOR_CONTEXT",
            "status": "OBSERVED",
            "message": (
                f"{symbol} belongs to the "
                f"{sector} sector. Sector peers "
                f"averaged {sector_average:.2f}% "
                f"on the event date."
            )
        })

        evidence.append({

            "type": "SECTOR_RELATIVE_PERFORMANCE",
            "status": "OBSERVED",
            "message": (
                f"{symbol} differed from its "
                f"sector peers by "
                f"{relative_to_sector:.2f} "
                f"percentage points."
            )
        })

    # -------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------

    return {

        "agent": "Peer Intelligence Agent",

        "symbol": symbol,

        "event_date": event_date.strftime(
            "%Y-%m-%d"
        ),

        "status": "SUCCESS",

        # Market
        "market_direction": market_direction,

        "stock_return": round(
            target_return,
            2
        ),

        "market_average_return": round(
            market_average,
            2
        ),

        "market_median_return": round(
            market_median,
            2
        ),

        "market_volatility": round(
            market_std,
            2
        ),

        "relative_performance": round(
            relative_to_market,
            2
        ),

        "interpretation": interpretation,

        # Sector
        "sector_status": sector_status,

        "sector": sector,

        "sector_average_return": (
            round(sector_average, 2)
            if sector_average is not None
            else None
        ),

        "sector_median_return": (
            round(sector_median, 2)
            if sector_median is not None
            else None
        ),

        "relative_to_sector": (
            round(relative_to_sector, 2)
            if relative_to_sector is not None
            else None
        ),

        "sector_peer_count": sector_peer_count,

        "sector_interpretation":
            sector_interpretation,

        "evidence": evidence,

        "comparison": comparison
    }