import pandas as pd
from pathlib import Path


DATA_FOLDER = Path(__file__).parent.parent / "data"


def find_market_csv():
    """
    Find the CSV containing the NSE market dataset.

    We identify it by checking for the expected
    market-data columns instead of relying on filename
    or alphabetical order.
    """

    csv_files = list(DATA_FOLDER.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV file found inside backend/data"
        )

    required_columns = {
        "SYMBOL",
        "TIMESTAMP",
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "TOTTRDQTY"
    }

    for csv_file in csv_files:

        try:

            sample = pd.read_csv(
                csv_file,
                nrows=2
            )

            columns = set(
                sample.columns
            )

            if required_columns.issubset(columns):

                return csv_file

        except Exception as e:

            print(
                f"Could not inspect {csv_file.name}: {e}"
            )

    raise FileNotFoundError(
        "Could not find the NSE market CSV. "
        "Make sure FINAL_FROM_DF.csv is inside backend/data."
    )


def load_stock_data():

    csv_file = find_market_csv()

    print(
        f"Loading market dataset: {csv_file.name}"
    )

    df = pd.read_csv(
        csv_file
    )

    return df