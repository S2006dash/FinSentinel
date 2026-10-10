# Common NSE stock -> broad sector mapping.
# Unknown symbols are intentionally left unclassified
# rather than inventing a sector.

SECTOR_MAP = {

    # -------------------------
    # INFORMATION TECHNOLOGY
    # -------------------------

    "TCS": "Information Technology",
    "INFY": "Information Technology",
    "HCLTECH": "Information Technology",
    "WIPRO": "Information Technology",
    "TECHM": "Information Technology",
    "LTIM": "Information Technology",
    "LTIMINDTREE": "Information Technology",
    "MPHASIS": "Information Technology",
    "COFORGE": "Information Technology",
    "PERSISTENT": "Information Technology",
    "LTTS": "Information Technology",
    "OFSS": "Information Technology",
    "KPITTECH": "Information Technology",
    "TATAELXSI": "Information Technology",
    "CYIENT": "Information Technology",

    # -------------------------
    # FINANCIAL SERVICES
    # -------------------------

    "HDFCBANK": "Financial Services",
    "ICICIBANK": "Financial Services",
    "SBIN": "Financial Services",
    "AXISBANK": "Financial Services",
    "KOTAKBANK": "Financial Services",
    "INDUSINDBK": "Financial Services",
    "BANKBARODA": "Financial Services",
    "PNB": "Financial Services",
    "CANBK": "Financial Services",
    "IDFCFIRSTB": "Financial Services",

    "BAJFINANCE": "Financial Services",
    "BAJAJFINSV": "Financial Services",
    "SHRIRAMFIN": "Financial Services",
    "CHOLAFIN": "Financial Services",
    "MUTHOOTFIN": "Financial Services",
    "MANAPPURAM": "Financial Services",

    "HDFCLIFE": "Financial Services",
    "SBILIFE": "Financial Services",
    "ICICIPRULI": "Financial Services",
    "ICICIGI": "Financial Services",

    # -------------------------
    # OIL / GAS / ENERGY
    # -------------------------

    "RELIANCE": "Energy",
    "ONGC": "Energy",
    "BPCL": "Energy",
    "IOC": "Energy",
    "GAIL": "Energy",
    "OIL": "Energy",
    "COALINDIA": "Energy",

    # -------------------------
    # POWER / UTILITIES
    # -------------------------

    "NTPC": "Utilities",
    "POWERGRID": "Utilities",
    "TATAPOWER": "Utilities",
    "NHPC": "Utilities",
    "SJVN": "Utilities",

    # -------------------------
    # AUTOMOBILE
    # -------------------------

    "MARUTI": "Automobile",
    "TATAMOTORS": "Automobile",
    "M&M": "Automobile",
    "MOTHERSON": "Automobile",
    "BAJAJ-AUTO": "Automobile",
    "BAJAJ_AUTO": "Automobile",
    "EICHERMOT": "Automobile",
    "HEROMOTOCO": "Automobile",
    "TVSMOTOR": "Automobile",
    "ASHOKLEY": "Automobile",
    "BHARATFORG": "Automobile",

    # -------------------------
    # PHARMACEUTICALS / HEALTHCARE
    # -------------------------

    "SUNPHARMA": "Healthcare",
    "DRREDDY": "Healthcare",
    "CIPLA": "Healthcare",
    "DIVISLAB": "Healthcare",
    "LUPIN": "Healthcare",
    "AUROPHARMA": "Healthcare",
    "TORNTPHARM": "Healthcare",
    "APOLLOHOSP": "Healthcare",
    "ZYDUSLIFE": "Healthcare",
    "BIOCON": "Healthcare",
    "ALKEM": "Healthcare",
    "MAXHEALTH": "Healthcare",

    # -------------------------
    # FMCG / CONSUMER
    # -------------------------

    "ITC": "Consumer Staples",
    "HINDUNILVR": "Consumer Staples",
    "NESTLEIND": "Consumer Staples",
    "BRITANNIA": "Consumer Staples",
    "DABUR": "Consumer Staples",
    "MARICO": "Consumer Staples",
    "GODREJCP": "Consumer Staples",
    "TATACONSUM": "Consumer Staples",
    "COLPAL": "Consumer Staples",

    # -------------------------
    # METALS
    # -------------------------

    "TATASTEEL": "Metals",
    "JSWSTEEL": "Metals",
    "HINDALCO": "Metals",
    "VEDL": "Metals",
    "SAIL": "Metals",
    "NMDC": "Metals",
    "JINDALSTEL": "Metals",
    "NATIONALUM": "Metals",

    # -------------------------
    # CONSTRUCTION / INDUSTRIALS
    # -------------------------

    "LT": "Industrials",
    "SIEMENS": "Industrials",
    "ABB": "Industrials",
    "BEL": "Industrials",
    "BHEL": "Industrials",
    "HAL": "Industrials",
    "ADANIENT": "Industrials",
    "ADANIENT": "Industrials",
    "ADANIPORTS": "Industrials",
    "CUMMINSIND": "Industrials",

    # -------------------------
    # CEMENT
    # -------------------------

    "ULTRACEMCO": "Cement",
    "GRASIM": "Cement",
    "SHREECEM": "Cement",
    "AMBUJACEM": "Cement",
    "ACC": "Cement",

    # -------------------------
    # CHEMICALS
    # -------------------------

    "PIDILITIND": "Chemicals",
    "SRF": "Chemicals",
    "UPL": "Chemicals",
    "PIIND": "Chemicals",
    "DEEPAKNTR": "Chemicals",
    "AARTIIND": "Chemicals",

    # -------------------------
    # TELECOMMUNICATIONS
    # -------------------------

    "BHARTIARTL": "Telecommunications",
    "IDEA": "Telecommunications",

    # -------------------------
    # REAL ESTATE
    # -------------------------

    "DLF": "Real Estate",
    "GODREJPROP": "Real Estate",
    "PRESTIGE": "Real Estate",
    "OBEROIRLTY": "Real Estate",

    # -------------------------
    # CONSUMER DURABLES
    # -------------------------

    "TITAN": "Consumer Discretionary",
    "TRENT": "Consumer Discretionary",
    "ASIANPAINT": "Consumer Discretionary",
    "HAVELLS": "Consumer Discretionary",
    "VOLTAS": "Consumer Discretionary",
    "DIXON": "Consumer Discretionary",
}


def get_sector(symbol):

    if symbol is None:
        return None

    symbol = str(symbol).upper().strip()

    return SECTOR_MAP.get(symbol)