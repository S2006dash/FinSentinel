from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from app.data_loader import load_stock_data
from app.feature_engineering import prepare_market_data
from app.anomaly_detector import detect_anomalies

from app.agents.news_agent import run_news_agent
from app.agents.peer_agent import run_peer_agent
from app.agents.risk_agent import run_risk_agent
from app.agents.investigation_agent import run_investigation_agent


app = FastAPI(
    title="FinSentinel API",
    description="AI Financial Early-Warning and Decision Intelligence Platform",
    version="1.0.0"
)


# -------------------------------------------------
# CORS
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

print("Loading market dataset...")
raw_df = load_stock_data()

print("Preparing market features...")
market_df = prepare_market_data(raw_df)

print("Detecting anomalies...")
anomaly_df = detect_anomalies(market_df)

print("FinSentinel backend ready.")


# -------------------------------------------------
# HELPER
# -------------------------------------------------

def clean_value(value):

    if pd.isna(value):
        return None

    if hasattr(value, "item"):

        try:
            return value.item()

        except Exception:
            pass

    return value


# -------------------------------------------------
# ROOT
# -------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "FinSentinel API is running",
        "version": "1.0.0"
    }


# -------------------------------------------------
# HEALTH
# -------------------------------------------------

@app.get("/api/health")
def health():

    return {
        "status": "healthy",
        "market_rows": len(market_df),
        "anomaly_rows": len(anomaly_df)
    }


# -------------------------------------------------
# RAW DATA PREVIEW
# -------------------------------------------------

@app.get("/api/data-preview")
def data_preview():

    preview = raw_df.head(10).copy()

    preview = preview.where(
        pd.notna(preview),
        None
    )

    return {
        "rows": len(raw_df),
        "columns": raw_df.columns.tolist(),
        "data": preview.to_dict(
            orient="records"
        )
    }


# -------------------------------------------------
# FEATURES PREVIEW
# -------------------------------------------------

@app.get("/api/features-preview")
def features_preview():

    columns = [
        "SYMBOL",
        "TIMESTAMP",
        "CLOSE",
        "TOTTRDQTY",
        "daily_return",
        "price_range_pct",
        "ma_5",
        "ma_20",
        "ma20_distance_pct",
        "volatility_20",
        "volume_ratio",
        "trade_count_ratio"
    ]

    available_columns = [
        column
        for column in columns
        if column in market_df.columns
    ]

    preview = market_df[
        available_columns
    ].head(20).copy()

    preview = preview.where(
        pd.notna(preview),
        None
    )

    return {
        "data": preview.to_dict(
            orient="records"
        )
    }


# -------------------------------------------------
# ANOMALIES
# -------------------------------------------------

@app.get("/api/anomalies")
def get_anomalies():

    columns = [
        "SYMBOL",
        "TIMESTAMP",
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "TOTTRDQTY",
        "daily_return",
        "volume_ratio",
        "volatility_20",
        "ma20_distance_pct",
        "anomaly_score",
        "priority",
        "reason"
    ]

    available_columns = [
        column
        for column in columns
        if column in anomaly_df.columns
    ]

    result = anomaly_df[
        anomaly_df["anomaly_score"] > 0
    ][available_columns].copy()

    priority_order = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "NORMAL": 1
    }

    result["_priority_order"] = (
        result["priority"]
        .map(priority_order)
        .fillna(0)
    )

    result = result.sort_values(
        by=[
            "_priority_order",
            "anomaly_score"
        ],
        ascending=[
            False,
            False
        ]
    )

    result = result.drop(
        columns=["_priority_order"]
    )

    result = result.head(500)

    result = result.where(
        pd.notna(result),
        None
    )

    return {
        "count": len(result),
        "anomalies": result.to_dict(
            orient="records"
        )
    }


# -------------------------------------------------
# STOCK HISTORY
# -------------------------------------------------

@app.get("/api/stock-history/{symbol}")
def stock_history(
    symbol: str,
    event_date=None
):

    symbol = symbol.upper().strip()

    stock_df = market_df[
        market_df["SYMBOL"]
        .astype(str)
        .str.upper()
        .str.strip()
        == symbol
    ].copy()

    if stock_df.empty:

        return {
            "symbol": symbol,
            "history": []
        }

    if event_date:

        event_date_parsed = pd.to_datetime(
            event_date,
            errors="coerce"
        )

        if not pd.isna(event_date_parsed):

            stock_df["date_only"] = (
                stock_df["TIMESTAMP"]
                .dt.normalize()
            )

            start_date = (
                event_date_parsed
                - pd.Timedelta(days=15)
            )

            end_date = (
                event_date_parsed
                + pd.Timedelta(days=15)
            )

            stock_df = stock_df[
                (
                    stock_df["date_only"]
                    >= start_date
                )
                &
                (
                    stock_df["date_only"]
                    <= end_date
                )
            ]

    history = []

    for _, row in stock_df.iterrows():

        history.append({

            "date": row["TIMESTAMP"].strftime(
                "%Y-%m-%d"
            ),

            "open": clean_value(
                row.get("OPEN")
            ),

            "high": clean_value(
                row.get("HIGH")
            ),

            "low": clean_value(
                row.get("LOW")
            ),

            "close": clean_value(
                row.get("CLOSE")
            ),

            "volume": clean_value(
                row.get("TOTTRDQTY")
            ),

            "daily_return": clean_value(
                row.get("daily_return")
            ),

            "volume_ratio": clean_value(
                row.get("volume_ratio")
            ),

            "volatility_20": clean_value(
                row.get("volatility_20")
            )
        })

    return {
        "symbol": symbol,
        "history": history
    }


# -------------------------------------------------
# NEWS INTELLIGENCE
# -------------------------------------------------

@app.get("/api/news-intelligence/{symbol}")
def news_intelligence(
    symbol: str,
    event_date=None
):

    symbol = symbol.upper().strip()

    actual_event_date = event_date

    price_change = None
    volume_ratio = None

    # ---------------------------------------------
    # Find highest anomaly if date not provided
    # ---------------------------------------------

    if actual_event_date is None:

        stock_anomalies = anomaly_df[
            anomaly_df["SYMBOL"]
            .astype(str)
            .str.upper()
            .str.strip()
            == symbol
        ].copy()

        if not stock_anomalies.empty:

            stock_anomalies = stock_anomalies.sort_values(
                by="anomaly_score",
                ascending=False
            )

            selected_event = stock_anomalies.iloc[0]

            actual_event_date = (
                selected_event["TIMESTAMP"]
                .strftime("%Y-%m-%d")
            )

            price_change = clean_value(
                selected_event.get(
                    "daily_return"
                )
            )

            volume_ratio = clean_value(
                selected_event.get(
                    "volume_ratio"
                )
            )

    # ---------------------------------------------
    # Date provided
    # ---------------------------------------------

    else:

        event_date_parsed = pd.to_datetime(
            actual_event_date,
            errors="coerce"
        )

        if not pd.isna(event_date_parsed):

            matching_rows = anomaly_df[
                (
                    anomaly_df["SYMBOL"]
                    .astype(str)
                    .str.upper()
                    .str.strip()
                    == symbol
                )
                &
                (
                    anomaly_df["TIMESTAMP"]
                    .dt.normalize()
                    == event_date_parsed.normalize()
                )
            ]

            if not matching_rows.empty:

                selected_event = (
                    matching_rows
                    .sort_values(
                        by="anomaly_score",
                        ascending=False
                    )
                    .iloc[0]
                )

                price_change = clean_value(
                    selected_event.get(
                        "daily_return"
                    )
                )

                volume_ratio = clean_value(
                    selected_event.get(
                        "volume_ratio"
                    )
                )

    # ---------------------------------------------
    # No event
    # ---------------------------------------------

    if actual_event_date is None:

        return {
            "agent": "News Intelligence Agent",
            "symbol": symbol,
            "event_date": None,
            "articles_found": 0,
            "articles": [],
            "evidence": [],
            "observations": [],
            "hypotheses": [],
            "uncertainty": [
                "No anomaly event was found for this stock."
            ]
        }

    # ---------------------------------------------
    # Run News Agent
    # ---------------------------------------------

    result = run_news_agent(
        symbol=symbol,
        event_date=actual_event_date,
        price_change=price_change,
        volume_ratio=volume_ratio
    )

    return result


# -------------------------------------------------
# PEER INTELLIGENCE
# -------------------------------------------------

@app.get("/api/peer-intelligence/{symbol}")
def peer_intelligence(
    symbol: str,
    event_date=None
):

    symbol = symbol.upper().strip()

    actual_event_date = event_date

    # ---------------------------------------------
    # Find highest anomaly if date not provided
    # ---------------------------------------------

    if actual_event_date is None:

        stock_anomalies = anomaly_df[
            anomaly_df["SYMBOL"]
            .astype(str)
            .str.upper()
            .str.strip()
            == symbol
        ].copy()

        if not stock_anomalies.empty:

            stock_anomalies = stock_anomalies.sort_values(
                by="anomaly_score",
                ascending=False
            )

            selected_event = stock_anomalies.iloc[0]

            actual_event_date = (
                selected_event["TIMESTAMP"]
                .strftime("%Y-%m-%d")
            )

    # ---------------------------------------------
    # No event
    # ---------------------------------------------

    if actual_event_date is None:

        return {
            "agent": "Peer Intelligence Agent",
            "symbol": symbol,
            "event_date": None,
            "status": "NO_EVENT",
            "comparison": []
        }

    # ---------------------------------------------
    # Run Peer Agent
    # ---------------------------------------------

    result = run_peer_agent(
        market_df=market_df,
        symbol=symbol,
        event_date=actual_event_date
    )

    return result


# -------------------------------------------------
# RISK INTELLIGENCE
# -------------------------------------------------

@app.get("/api/risk-intelligence/{symbol}")
def risk_intelligence(
    symbol: str,
    event_date=None
):

    symbol = symbol.upper().strip()

    actual_event_date = event_date

    selected_event = None

    # ---------------------------------------------
    # Find highest anomaly if date not provided
    # ---------------------------------------------

    if actual_event_date is None:

        stock_anomalies = anomaly_df[
            anomaly_df["SYMBOL"]
            .astype(str)
            .str.upper()
            .str.strip()
            == symbol
        ].copy()

        if not stock_anomalies.empty:

            stock_anomalies = stock_anomalies.sort_values(
                by="anomaly_score",
                ascending=False
            )

            selected_event = stock_anomalies.iloc[0]

            actual_event_date = (
                selected_event["TIMESTAMP"]
                .strftime("%Y-%m-%d")
            )

    # ---------------------------------------------
    # Date provided
    # ---------------------------------------------

    else:

        event_date_parsed = pd.to_datetime(
            actual_event_date,
            errors="coerce"
        )

        if not pd.isna(event_date_parsed):

            matching_rows = anomaly_df[
                (
                    anomaly_df["SYMBOL"]
                    .astype(str)
                    .str.upper()
                    .str.strip()
                    == symbol
                )
                &
                (
                    anomaly_df["TIMESTAMP"]
                    .dt.normalize()
                    == event_date_parsed.normalize()
                )
            ].copy()

            if not matching_rows.empty:

                matching_rows = matching_rows.sort_values(
                    by="anomaly_score",
                    ascending=False
                )

                selected_event = matching_rows.iloc[0]

                actual_event_date = (
                    selected_event["TIMESTAMP"]
                    .strftime("%Y-%m-%d")
                )

    # ---------------------------------------------
    # No event
    # ---------------------------------------------

    if selected_event is None:

        return {
            "agent": "Risk & Priority Agent",
            "symbol": symbol,
            "event_date": actual_event_date,
            "status": "NO_EVENT"
        }

    # ---------------------------------------------
    # Get peer context
    # ---------------------------------------------

    peer_result = run_peer_agent(
        market_df=market_df,
        symbol=symbol,
        event_date=actual_event_date
    )

    relative_performance = peer_result.get(
        "relative_performance"
    )

    # ---------------------------------------------
    # Run Risk Agent
    # ---------------------------------------------

    result = run_risk_agent(

        symbol=symbol,

        event_date=actual_event_date,

        anomaly_score=clean_value(
            selected_event.get(
                "anomaly_score"
            )
        ),

        priority=str(
            selected_event.get(
                "priority"
            )
        ),

        price_change=clean_value(
            selected_event.get(
                "daily_return"
            )
        ),

        volume_ratio=clean_value(
            selected_event.get(
                "volume_ratio"
            )
        ),

        volatility=clean_value(
            selected_event.get(
                "volatility_20"
            )
        ),

        relative_performance=relative_performance
    )

    return result


# -------------------------------------------------
# INVESTIGATION INTELLIGENCE
# -------------------------------------------------

@app.get("/api/investigation/{symbol}")
def investigation(
    symbol: str,
    event_date=None
):

    symbol = symbol.upper().strip()

    actual_event_date = event_date

    selected_event = None

    # ---------------------------------------------
    # Find highest anomaly if date not provided
    # ---------------------------------------------

    if actual_event_date is None:

        stock_anomalies = anomaly_df[
            anomaly_df["SYMBOL"]
            .astype(str)
            .str.upper()
            .str.strip()
            == symbol
        ].copy()

        if not stock_anomalies.empty:

            stock_anomalies = stock_anomalies.sort_values(
                by="anomaly_score",
                ascending=False
            )

            selected_event = stock_anomalies.iloc[0]

            actual_event_date = (
                selected_event["TIMESTAMP"]
                .strftime("%Y-%m-%d")
            )

    # ---------------------------------------------
    # Date provided
    # ---------------------------------------------

    else:

        event_date_parsed = pd.to_datetime(
            actual_event_date,
            errors="coerce"
        )

        if not pd.isna(event_date_parsed):

            matching_rows = anomaly_df[
                (
                    anomaly_df["SYMBOL"]
                    .astype(str)
                    .str.upper()
                    .str.strip()
                    == symbol
                )
                &
                (
                    anomaly_df["TIMESTAMP"]
                    .dt.normalize()
                    == event_date_parsed.normalize()
                )
            ].copy()

            if not matching_rows.empty:

                matching_rows = matching_rows.sort_values(
                    by="anomaly_score",
                    ascending=False
                )

                selected_event = matching_rows.iloc[0]

                actual_event_date = (
                    selected_event["TIMESTAMP"]
                    .strftime("%Y-%m-%d")
                )

    # ---------------------------------------------
    # No event
    # ---------------------------------------------

    if selected_event is None:

        return {
            "agent": "Investigation Intelligence Agent",
            "symbol": symbol,
            "event_date": actual_event_date,
            "status": "NO_EVENT"
        }

    # ---------------------------------------------
    # Build event information
    # ---------------------------------------------

    event = {

        "symbol": symbol,

        "daily_return": clean_value(
            selected_event.get(
                "daily_return"
            )
        ),

        "volume_ratio": clean_value(
            selected_event.get(
                "volume_ratio"
            )
        ),

        "volatility_20": clean_value(
            selected_event.get(
                "volatility_20"
            )
        ),

        "anomaly_score": clean_value(
            selected_event.get(
                "anomaly_score"
            )
        ),

        "priority": str(
            selected_event.get(
                "priority"
            )
        )
    }

    # ---------------------------------------------
    # Run News Agent
    # ---------------------------------------------

    news = run_news_agent(

        symbol=symbol,

        event_date=actual_event_date,

        price_change=event["daily_return"],

        volume_ratio=event["volume_ratio"]
    )

    # ---------------------------------------------
    # Run Peer Agent
    # ---------------------------------------------

    peer = run_peer_agent(

        market_df=market_df,

        symbol=symbol,

        event_date=actual_event_date
    )

    # ---------------------------------------------
    # Run Risk Agent
    # ---------------------------------------------

    risk = run_risk_agent(

        symbol=symbol,

        event_date=actual_event_date,

        anomaly_score=event["anomaly_score"],

        priority=event["priority"],

        price_change=event["daily_return"],

        volume_ratio=event["volume_ratio"],

        volatility=event["volatility_20"],

        relative_performance=peer.get(
            "relative_performance"
        )
    )

    # ---------------------------------------------
    # Run Investigation Intelligence Agent
    # ---------------------------------------------

    result = run_investigation_agent(

        symbol=symbol,

        event_date=actual_event_date,

        event=event,

        news=news,

        peer=peer,

        risk=risk
    )

    return result