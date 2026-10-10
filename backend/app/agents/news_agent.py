import pandas as pd
from pathlib import Path
from datetime import timedelta


NEWS_FILE = (
    Path(__file__).parent.parent.parent
    / "data"
    / "raw_partner_headlines.csv"
)


# ---------------------------------------------------------
# Load the historical news dataset
# ---------------------------------------------------------

def load_news_data():

    if not NEWS_FILE.exists():
        print("News dataset not found:", NEWS_FILE)
        return pd.DataFrame()

    try:

        df = pd.read_csv(
            NEWS_FILE,
            usecols=[
                "headline",
                "url",
                "publisher",
                "date",
                "stock"
            ]
        )

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        df["stock"] = (
            df["stock"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        df["headline"] = (
            df["headline"]
            .astype(str)
            .str.strip()
        )

        df = df.dropna(
            subset=[
                "headline",
                "date",
                "stock"
            ]
        )

        return df

    except Exception as e:

        print("Error loading news dataset:", e)

        return pd.DataFrame()


# ---------------------------------------------------------
# Find relevant historical news
# ---------------------------------------------------------

def find_relevant_news(
    symbol,
    event_date,
    days_before=3,
    days_after=1
):

    df = load_news_data()

    if df.empty:
        return []

    symbol = symbol.upper().strip()

    event_date = pd.to_datetime(
        event_date,
        errors="coerce"
    )

    if pd.isna(event_date):
        return []

    start_date = event_date - timedelta(
        days=days_before
    )

    end_date = event_date + timedelta(
        days=days_after
    )

    # Only use exact stock ticker matches.
    # This prevents false matches between
    # Indian NSE symbols and unrelated US stocks.
    matches = df[
        (df["stock"] == symbol)
        &
        (df["date"] >= start_date)
        &
        (df["date"] <= end_date)
    ].copy()

    if matches.empty:
        return []

    # Put articles closest to the anomaly date first
    matches["date_difference"] = (
        matches["date"] - event_date
    ).abs()

    matches = matches.sort_values(
        by="date_difference"
    )

    # Limit results
    matches = matches.head(10)

    results = []

    for _, row in matches.iterrows():

        article_date = row["date"]

        results.append({
            "headline": str(row["headline"]),
            "publisher": str(row["publisher"]),
            "published_date": article_date.strftime(
                "%Y-%m-%d"
            ),
            "url": str(row["url"]),
            "stock": str(row["stock"]),
            "days_from_event": int(
                abs(
                    (article_date - event_date).days
                )
            )
        })

    return results


# ---------------------------------------------------------
# Classify evidence
# ---------------------------------------------------------

def classify_evidence(
    articles,
    price_change,
    volume_ratio
):

    evidence = []

    if articles:

        evidence.append({
            "type": "NEWS_COVERAGE",
            "status": "FOUND",
            "message": (
                f"{len(articles)} historical "
                "article(s) were found around "
                "the event date."
            )
        })

    else:

        evidence.append({
            "type": "NEWS_COVERAGE",
            "status": "NOT_FOUND",
            "message": (
                "No matching historical news "
                "articles were found for this "
                "stock and event date."
            )
        })

    # Market observations are facts from our dataset

    if price_change is not None:

        price_change = float(price_change)

        evidence.append({
            "type": "MARKET_FACT",
            "status": "OBSERVED",
            "message": (
                f"Price changed by "
                f"{price_change:.2f}% "
                "on the event date."
            )
        })

    if volume_ratio is not None:

        volume_ratio = float(volume_ratio)

        evidence.append({
            "type": "MARKET_FACT",
            "status": "OBSERVED",
            "message": (
                f"Trading volume was "
                f"{volume_ratio:.2f}x the "
                "recent average."
            )
        })

    return evidence


# ---------------------------------------------------------
# Generate investigation interpretation
# ---------------------------------------------------------

def generate_interpretation(
    articles,
    price_change,
    volume_ratio
):

    observations = []

    hypotheses = []

    uncertainty = []

    # ---------------------------------------------
    # Price movement
    # ---------------------------------------------

    if price_change is not None:

        price_change = float(price_change)

        if abs(price_change) >= 5:

            observations.append(
                f"Large price movement of "
                f"{price_change:.2f}% was observed."
            )

            hypotheses.append(
                "The price movement may have been "
                "associated with a significant "
                "market event or company-specific "
                "information."
            )

        elif abs(price_change) >= 3:

            observations.append(
                f"Elevated price movement of "
                f"{price_change:.2f}% was observed."
            )

    # ---------------------------------------------
    # Volume
    # ---------------------------------------------

    if volume_ratio is not None:

        volume_ratio = float(volume_ratio)

        if volume_ratio >= 3:

            observations.append(
                f"Trading volume reached "
                f"{volume_ratio:.2f}x the recent average."
            )

            hypotheses.append(
                "Unusually high trading activity "
                "may indicate increased market "
                "attention."
            )

        elif volume_ratio >= 2:

            observations.append(
                f"Trading volume was "
                f"{volume_ratio:.2f}x the recent average."
            )

    # ---------------------------------------------
    # News
    # ---------------------------------------------

    if articles:

        hypotheses.append(
            "Historical news coverage exists "
            "around the detected event window "
            "and should be reviewed as potential "
            "context."
        )

    else:

        uncertainty.append(
            "No matching historical news coverage "
            "was found in the available dataset."
        )

    # ---------------------------------------------
    # Safety / uncertainty
    # ---------------------------------------------

    uncertainty.append(
        "Temporal proximity between news and "
        "market movement does not establish "
        "causation."
    )

    uncertainty.append(
        "The historical news dataset primarily "
        "covers US-listed stocks and may not "
        "contain relevant coverage for NSE stocks."
    )

    return {
        "observations": observations,
        "hypotheses": hypotheses,
        "uncertainty": uncertainty
    }


# ---------------------------------------------------------
# Main News Intelligence Agent
# ---------------------------------------------------------

def run_news_agent(
    symbol,
    event_date,
    price_change=None,
    volume_ratio=None
):

    print(
        f"Running News Intelligence Agent "
        f"for {symbol} on {event_date}"
    )

    articles = find_relevant_news(
        symbol=symbol,
        event_date=event_date
    )

    evidence = classify_evidence(
        articles=articles,
        price_change=price_change,
        volume_ratio=volume_ratio
    )

    interpretation = generate_interpretation(
        articles=articles,
        price_change=price_change,
        volume_ratio=volume_ratio
    )

    return {
        "agent": "News Intelligence Agent",
        "symbol": symbol,
        "event_date": str(event_date),

        "articles_found": len(articles),

        "articles": articles,

        "evidence": evidence,

        "observations": interpretation[
            "observations"
        ],

        "hypotheses": interpretation[
            "hypotheses"
        ],

        "uncertainty": interpretation[
            "uncertainty"
        ]
    }