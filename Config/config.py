# ----------------------------------------------------
# -- Projet : DEGIRO_ANALYSIS
# -- Author : Ronaf
# -- Created : 02/03/2025
# -- Usage : Store const
# -- Update : 
# --  
# ----------------------------------------------------
AUTHOR = 'Ronaf'
VERSION = 0.1
# Dictionary to map exchanges to Yahoo Finance suffix
EXCHANGES_SUFFIXES = {
    "EAM": ".AS",      # Euronext Amsterdam (Netherlands)
    "XETR": ".DE",    # Frankfurt Stock Exchange (Germany)
    "NYS": ".N",      # New York Stock Exchange (NYSE)
    "TSE": ".T",      # Tokyo Stock Exchange (Japan)
    "TDG": ".DE",      
    "EPA": ".PA",     # Euronext Paris (France)
    "BVMF": ".SA",    # B3 - São Paulo Stock Exchange (Brazil)
    "SSE": ".SS",     # Shanghai Stock Exchange (China)
    "SZSE": ".SZ",    # Shenzhen Stock Exchange (China)
    "HKEX": ".HK",    # Hong Kong Stock Exchange (Hong Kong)
    "LSE": ".L",      # London Stock Exchange (UK)
    "ASX": ".AX",     # Australian Securities Exchange (Australia)
    "TSX": ".TO",     # Toronto Stock Exchange (Canada)
    "MEXBOL": ".MX",  # Bolsa Mexicana de Valores (Mexico)
    "BME": ".MC",     # Bolsas y Mercados Españoles (Spain)
    "JSE": ".J",      # Johannesburg Stock Exchange (South Africa)
    "NSE": ".NS",     # National Stock Exchange of India (NSE)
    "BSE": ".BO",     # Bombay Stock Exchange (India)
    "SGX": ".SI",     # Singapore Exchange (Singapore)
    "ISE": ".IE",     # Irish Stock Exchange (Ireland)
    "WSE": ".WA",     # Warsaw Stock Exchange (Poland)
    "SWX": ".SW",     # Swiss Exchange (Switzerland)
    "KOSDAQ": ".KQ",  # KOSDAQ (South Korea)
    "KSE": ".KS",     # Korea Stock Exchange (South Korea)
    "CSE": ".CN",     # Colombo Stock Exchange (Sri Lanka)
    "TASE": ".TA",    # Tel Aviv Stock Exchange (Israel)
    "BSE": ".BR",     # Bahrain Stock Exchange (Bahrain)
    "ASE": ".AT",     # Athens Stock Exchange (Greece)
    "NZX": ".NZ",     # New Zealand Stock Exchange (New Zealand)
    "VSE": ".VN",     # Vietnam Stock Exchange (Vietnam)
    "PSE": ".PH",     # Philippine Stock Exchange (Philippines)
    "EGX": ".CA",     # Egyptian Stock Exchange (Egypt)
    "BVB": ".RO",     # Bucharest Stock Exchange (Romania)
    "IDX": ".JK",     # Indonesia Stock Exchange (Indonesia)
    "MSE": ".MN",     # Mongolian Stock Exchange (Mongolia)
    "QSE": ".QA",     # Qatar Stock Exchange (Qatar)
    "DSE": ".BD",     # Dhaka Stock Exchange (Bangladesh)
    "MOEX": ".ME",    # Moscow Exchange (Russia)
    "TASE": ".TL",    # Turkish Stock Exchange (Turkey)
    "LSE": ".L",      # London Stock Exchange (UK)
    "AMEX": ".A",     # American Stock Exchange (formerly, now merged with NYSE)
    "BATS": ".B",     # BATS Global Markets (U.S. exchange)
    "CBOE": ".C",     # Chicago Board Options Exchange (CBOE)
    "OTC": ".OTC",    # Over-the-counter market (generic)
    "FRA": ".F",      # Frankfurt Stock Exchange (Germany)
    "MEX": ".MX",     # Mexican Stock Exchange
    "TA": ".T",       # Tel Aviv Stock Exchange
    "NZX": ".NZ",     # New Zealand Stock Exchange
    "BMO": ".BR",     # Brazilian Stock Market
    "SO": ".SO",      # Santiago Stock Exchange (Chile)
    "MCX": ".MC",     # Mumbai Stock Exchange (India)
    "BME": ".MC",     # Spanish Stock Exchange (BME)
    "LSE": ".L",      # London Stock Exchange (UK)
    "SSE": ".SS",     # Shanghai Stock Exchange (China)
    "XETRA": ".DE",   # Xetra Frankfurt (Germany)
    "TSE": ".T",      # Tokyo Stock Exchange (Japan)
    "SINGEX": ".SG",  # Singapore Exchange (Singapore)
    "NSE": ".NS",     # National Stock Exchange of India (NSE)
    "BSE": ".BO",     # Bombay Stock Exchange (India)
    "VSE": ".VN",     # Vietnam Stock Exchange (Vietnam)
    "MOEX": ".RU",    # Moscow Exchange (Russia)
    "CSE": ".CN",     # Colombo Stock Exchange (Sri Lanka)
    "MAD": ".MC",     # Bolsa de Madrid (Spain)
    "QSE": ".QA",     # Qatar Stock Exchange (Qatar)
    "ASE": ".AT",     # Athens Stock Exchange (Greece)
    "EGX": ".EG",     # Egyptian Stock Exchange (Egypt)
    "TASE": ".TA",    # Tel Aviv Stock Exchange (Israel)
    "DSE": ".BD",     # Dhaka Stock Exchange (Bangladesh)
    "PSE": ".PH",     # Philippine Stock Exchange (Philippines)
    "JSE": ".J",      # Johannesburg Stock Exchange (South Africa)
    "PSE": ".PH",     # Philippine Stock Exchange
    "SHSE": ".SS",    # Shanghai Stock Exchange (China)
    "SZSE": ".SZ",    # Shenzhen Stock Exchange (China)
    "BSE": ".IN",     # Bombay Stock Exchange (India)
    "DAX": ".DE",     # Frankfurt (Germany)
    "EGX": ".EG",     # Egyptian Stock Exchange (Egypt)
    "MEX": ".MX",     # Mexican Stock Exchange (Mexico)
    "IDEX": ".ID",    # Indonesia Stock Exchange (Indonesia)
    "FTSE": ".FT",    # FTSE 100 Index (UK)
}
SOURCE_FOLDER = 'source'
OUTPUR_FOLDER = 'output'

print("config.py loaded successfully")