import pandas as pd


def run_risk_agent(
    symbol,
    event_date,
    anomaly_score,
    priority,
    price_change,
    volume_ratio,
    volatility,
    relative_performance
):

    symbol = symbol.upper().strip()

    observations = []
    risk_factors = []
    recommendations = []

    # -------------------------------------------------
    # PRICE MOVEMENT
    # -------------------------------------------------

    if price_change is not None:

        price_change = float(price_change)

        observations.append(
            f"Price moved {price_change:.2f}% on the event date."
        )

        if abs(price_change) >= 8:

            risk_factors.append(
                "Very large price movement"
            )

        elif abs(price_change) >= 5:

            risk_factors.append(
                "Large price movement"
            )

        elif abs(price_change) >= 3:

            risk_factors.append(
                "Elevated price movement"
            )


    # -------------------------------------------------
    # VOLUME
    # -------------------------------------------------

    if volume_ratio is not None:

        volume_ratio = float(volume_ratio)

        observations.append(
            f"Trading volume was {volume_ratio:.2f}x the recent average."
        )

        if volume_ratio >= 5:

            risk_factors.append(
                "Extremely unusual trading volume"
            )

        elif volume_ratio >= 3:

            risk_factors.append(
                "Unusually high trading volume"
            )

        elif volume_ratio >= 2:

            risk_factors.append(
                "Elevated trading volume"
            )


    # -------------------------------------------------
    # VOLATILITY
    # -------------------------------------------------

    if volatility is not None:

        volatility = float(volatility)

        observations.append(
            f"20-day volatility was {volatility:.2f}%."
        )

        if volatility >= 6:

            risk_factors.append(
                "Very high recent volatility"
            )

        elif volatility >= 4:

            risk_factors.append(
                "High recent volatility"
            )

        elif volatility >= 2:

            risk_factors.append(
                "Elevated recent volatility"
            )


    # -------------------------------------------------
    # RELATIVE PERFORMANCE
    # -------------------------------------------------

    if relative_performance is not None:

        relative_performance = float(
            relative_performance
        )

        observations.append(
            f"Stock performance differed from the broader market by "
            f"{relative_performance:.2f} percentage points."
        )

        if abs(relative_performance) >= 5:

            risk_factors.append(
                "Substantial divergence from the broader market"
            )

        elif abs(relative_performance) >= 3:

            risk_factors.append(
                "Moderate divergence from the broader market"
            )


    # -------------------------------------------------
    # PRIORITY CALCULATION
    # -------------------------------------------------

    risk_points = 0

    if price_change is not None:
        if abs(float(price_change)) >= 8:
            risk_points += 3
        elif abs(float(price_change)) >= 5:
            risk_points += 2
        elif abs(float(price_change)) >= 3:
            risk_points += 1

    if volume_ratio is not None:
        if float(volume_ratio) >= 5:
            risk_points += 3
        elif float(volume_ratio) >= 3:
            risk_points += 2
        elif float(volume_ratio) >= 2:
            risk_points += 1

    if volatility is not None:
        if float(volatility) >= 6:
            risk_points += 3
        elif float(volatility) >= 4:
            risk_points += 2
        elif float(volatility) >= 2:
            risk_points += 1

    if relative_performance is not None:
        if abs(float(relative_performance)) >= 5:
            risk_points += 2
        elif abs(float(relative_performance)) >= 3:
            risk_points += 1


    # Existing anomaly score also contributes context

    if anomaly_score is not None:

        if float(anomaly_score) >= 9:
            risk_points += 3

        elif float(anomaly_score) >= 6:
            risk_points += 2

        elif float(anomaly_score) >= 3:
            risk_points += 1


    # -------------------------------------------------
    # FINAL RISK LEVEL
    # -------------------------------------------------

    if risk_points >= 10:

        risk_level = "CRITICAL"

    elif risk_points >= 7:

        risk_level = "HIGH"

    elif risk_points >= 4:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"


    # -------------------------------------------------
    # RECOMMENDATIONS
    # -------------------------------------------------

    if risk_level in ["CRITICAL", "HIGH"]:

        recommendations.append(
            "Review relevant company and market news."
        )

        recommendations.append(
            "Compare the event with broader market movement."
        )

        recommendations.append(
            "Check whether unusual trading activity persisted "
            "after the event."
        )

    elif risk_level == "MEDIUM":

        recommendations.append(
            "Review available historical news and market context."
        )

        recommendations.append(
            "Monitor subsequent price and volume behaviour."
        )

    else:

        recommendations.append(
            "Continue monitoring the stock for repeated anomalies."
        )


    # -------------------------------------------------
    # EXPLANATION
    # -------------------------------------------------

    if risk_factors:

        explanation = (
            f"{symbol} received a {risk_level} investigation priority "
            f"based on {len(risk_factors)} identified risk factor(s)."
        )

    else:

        explanation = (
            f"{symbol} currently shows limited evidence of elevated "
            f"investigation risk."
        )


    return {

        "agent": "Risk & Priority Agent",

        "symbol": symbol,

        "event_date": str(event_date),

        "risk_level": risk_level,

        "risk_score": risk_points,

        "existing_priority": priority,

        "anomaly_score": anomaly_score,

        "explanation": explanation,

        "observations": observations,

        "risk_factors": risk_factors,

        "recommendations": recommendations

    }