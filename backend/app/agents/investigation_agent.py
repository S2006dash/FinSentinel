def run_investigation_agent(
    symbol,
    event_date,
    event,
    news,
    peer,
    risk
):

    symbol = symbol.upper().strip()

    observations = []
    evidence = []
    hypotheses = []
    limitations = []

    # -------------------------------------------------
    # MARKET EVENT
    # -------------------------------------------------

    if event:

        price_change = event.get(
            "daily_return"
        )

        volume_ratio = event.get(
            "volume_ratio"
        )

        volatility = event.get(
            "volatility_20"
        )

        anomaly_score = event.get(
            "anomaly_score"
        )

        if price_change is not None:

            observations.append(
                f"{symbol} moved "
                f"{float(price_change):.2f}% "
                f"on {event_date}."
            )

            evidence.append(
                f"Observed price movement: "
                f"{float(price_change):.2f}%"
            )

        if volume_ratio is not None:

            observations.append(
                f"Trading volume was "
                f"{float(volume_ratio):.2f}x "
                f"the recent average."
            )

            evidence.append(
                f"Volume ratio: "
                f"{float(volume_ratio):.2f}x"
            )

        if volatility is not None:

            observations.append(
                f"20-day volatility was "
                f"{float(volatility):.2f}%."
            )

        if anomaly_score is not None:

            evidence.append(
                f"Anomaly score: "
                f"{int(anomaly_score)}"
            )

    # -------------------------------------------------
    # MARKET + SECTOR CONTEXT
    # -------------------------------------------------

    relative_performance = None
    relative_to_sector = None
    sector = None

    if peer:

        relative_performance = peer.get(
            "relative_performance"
        )

        if relative_performance is not None:

            observations.append(
                f"The stock differed from the broader market "
                f"by {float(relative_performance):.2f} "
                f"percentage points."
            )

            evidence.append(
                f"Relative market performance: "
                f"{float(relative_performance):.2f} "
                f"percentage points"
            )

        interpretation = peer.get(
            "interpretation"
        )

        if interpretation:

            observations.append(
                interpretation
            )

        # -------------------------------------------------
        # SECTOR
        # -------------------------------------------------

        sector = peer.get(
            "sector"
        )

        sector_status = peer.get(
            "sector_status"
        )

        relative_to_sector = peer.get(
            "relative_to_sector"
        )

        sector_average_return = peer.get(
            "sector_average_return"
        )

        sector_peer_count = peer.get(
            "sector_peer_count",
            0
        )

        sector_interpretation = peer.get(
            "sector_interpretation"
        )

        if (
            sector_status == "SUCCESS"
            and sector is not None
            and relative_to_sector is not None
        ):

            observations.append(
                f"{symbol} belongs to the "
                f"{sector} sector, where "
                f"{sector_peer_count} peer stock(s) "
                f"averaged "
                f"{float(sector_average_return):.2f}%."
            )

            evidence.append(
                f"Sector relative performance: "
                f"{float(relative_to_sector):.2f} "
                f"percentage points"
            )

            if sector_interpretation:

                observations.append(
                    sector_interpretation
                )

        elif sector_status == "SECTOR_UNAVAILABLE":

            limitations.append(
                "Sector classification was not available "
                "for this stock in the built-in NSE sector map."
            )

        elif sector_status == "NO_SECTOR_DATA":

            limitations.append(
                "Sector classification was available, but "
                "insufficient sector peer data existed for "
                "the event date."
            )

    # -------------------------------------------------
    # NEWS
    # -------------------------------------------------

    articles_found = 0

    if news:

        articles_found = news.get(
            "articles_found",
            0
        )

        if articles_found > 0:

            observations.append(
                f"{articles_found} historical news article(s) "
                f"were found around the event window."
            )

            evidence.append(
                f"Historical news coverage found: "
                f"{articles_found} article(s)"
            )

            hypotheses.append(
                "Historical news coverage may provide "
                "context for the observed market movement."
            )

        else:

            observations.append(
                "No matching historical news coverage "
                "was found in the available dataset."
            )

            limitations.append(
                "No matching historical news evidence "
                "was available."
            )

    # -------------------------------------------------
    # RISK
    # -------------------------------------------------

    risk_level = "UNKNOWN"
    risk_score = 0

    if risk:

        risk_level = risk.get(
            "risk_level",
            "UNKNOWN"
        )

        risk_score = risk.get(
            "risk_score",
            0
        )

        risk_factors = risk.get(
            "risk_factors",
            []
        )

        for factor in risk_factors:

            evidence.append(
                f"Risk factor: {factor}"
            )

    # -------------------------------------------------
    # ASSESSMENT
    # -------------------------------------------------

    if risk_level == "CRITICAL":

        assessment = (
            f"{symbol} requires immediate investigation priority. "
            f"The event combines multiple elevated market signals "
            f"and should be reviewed for company-specific or "
            f"market-wide explanations."
        )

    elif risk_level == "HIGH":

        assessment = (
            f"{symbol} shows a high-priority market anomaly. "
            f"The combination of unusual market behaviour and "
            f"additional risk signals warrants further investigation."
        )

    elif risk_level == "MEDIUM":

        assessment = (
            f"{symbol} shows moderate abnormal market behaviour. "
            f"The event should be reviewed against available news, "
            f"sector context, and subsequent market activity."
        )

    else:

        assessment = (
            f"{symbol} shows a relatively limited anomaly signal. "
            f"Continued monitoring is appropriate."
        )

    # -------------------------------------------------
    # HYPOTHESES
    # -------------------------------------------------

    if (
        relative_performance is not None
        and abs(float(relative_performance)) >= 3
    ):

        hypotheses.append(
            "The divergence from broader market behaviour "
            "may indicate a stock-specific factor."
        )

    if (
        relative_to_sector is not None
        and abs(float(relative_to_sector)) >= 3
    ):

        hypotheses.append(
            "The divergence from sector peers may indicate "
            "a company-specific catalyst rather than a "
            "sector-wide movement."
        )

    if (
        event
        and event.get("volume_ratio") is not None
        and float(event["volume_ratio"]) >= 3
    ):

        hypotheses.append(
            "Elevated trading activity may indicate increased "
            "market attention around the event."
        )

    # -------------------------------------------------
    # LIMITATIONS
    # -------------------------------------------------

    limitations.append(
        "Temporal proximity between news and price movement "
        "does not establish causation."
    )

    limitations.append(
        "The analysis depends on the historical datasets "
        "available to FinSentinel."
    )

    # -------------------------------------------------
    # NEXT ACTIONS
    # -------------------------------------------------

    next_actions = [

        "Review company-specific announcements around "
        "the event date.",

        "Compare the event with broader market and "
        "sector behaviour.",

        "Monitor subsequent price and volume activity.",

    ]

    if articles_found == 0:

        next_actions.append(
            "Obtain additional news sources for stronger "
            "event context."
        )

    # -------------------------------------------------
    # RESULT
    # -------------------------------------------------

    return {

        "agent":
            "Investigation Intelligence Agent",

        "symbol":
            symbol,

        "event_date":
            str(event_date),

        "risk_level":
            risk_level,

        "risk_score":
            risk_score,

        "headline":
            (
                f"{symbol} investigation classified as "
                f"{risk_level} priority."
            ),

        "assessment":
            assessment,

        "observations":
            observations,

        "evidence":
            evidence,

        "hypotheses":
            hypotheses,

        "limitations":
            limitations,

        "next_actions":
            next_actions
    }