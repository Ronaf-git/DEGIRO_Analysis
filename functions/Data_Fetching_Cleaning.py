# ----------------------------------------------------
# -- Projet : DEGIRO_Analysis
# -- Author : Ronaf
# -- Created : 15/03/2025
# -- Usage : Fetch and store data online
# -- Update : 
# --  
# ----------------------------------------------------
# ==============================================================================================================================
# Imports
# ==============================================================================================================================
import yfinance as yf #https://github.com/ranaroussi/yfinance
import pandas as pd
import requests
import glob
import tkinter as tk
from tkinter import messagebox
import csv
import sys
import sqlite3  # Use SQLite or replace with SQLAlchemy for other databases
import socket
import os

# Const
from Config.config import *
  
def show_popup(title,message) :
    """
    Display a simple popup message box with the given title and message.

    This function creates a hidden tkinter root window, shows a message box with 
    the specified title and message, and then quits the tkinter instance.

    Parameters:
        title (str): The title of the popup message box.
        message (str): The message to display in the popup.

    Returns:
        None
    """
    # Create the root window (it won't appear)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    # Show the popup message box
    messagebox.showinfo(title, message)
    # Close the tkinter instance after the popup
    root.quit()

def get_yahoo_ticker(ticker, exchange) -> None:
    """
    Generates a Yahoo Finance ticker symbol based on the provided stock ticker and exchange.

    Args:
        ticker (str): The stock ticker symbol, typically the company symbol like 'AAPL', 'GOOG', etc.
        exchange (str): The stock exchange where the ticker is listed. Should be a string, such as 'NASDAQ', 'LSE', etc.

    Returns:
        str or None: The constructed Yahoo Finance ticker symbol (e.g., 'AAPL', 'GOOG', etc.) with the appropriate suffix for the exchange.
        Returns None if no suffix mapping is found for the provided exchange.

    Notes:
        - The function expects that the exchange is passed in as a string. If not, it will not proceed.
        - The exchange string is converted to uppercase before checking for the corresponding suffix.
        - The function uses a predefined mapping (`EXCHANGES_SUFFIXES`) for suffixes based on the exchange.

    Example:
        >>> get_yahoo_ticker('AAPL', 'NASDAQ')
        'AAPL'  # Assuming the suffix for NASDAQ is empty or non-existent.

        >>> get_yahoo_ticker('GOOG', 'LSE')
        'GOOG.L'  # Assuming the suffix for LSE is '.L'
    """
    # Ensure exchange is a string before applying .upper()
    if isinstance(exchange, str):
        exchange = exchange.upper()
    
    # Get the suffix for the exchange
    suffix = EXCHANGES_SUFFIXES.get(exchange, "")
    
    if suffix:
        yahoo_ticker = ticker + suffix
        return yahoo_ticker
    else:
        return None  # No mapping found for that exchange
    
def is_internet_up():
    """
    Function to test if the internet is up by attempting to connect to Google's DNS server (8.8.8.8).
    
    Returns:
    bool: True if the internet is reachable, False otherwise.
    """
    try:
        # Try to establish a socket connection to a reliable DNS server (8.8.8.8)
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except (socket.timeout, socket.error):
        # If unable to connect, return False
        return False
    
def detect_delimiter(file_path):
    """
    Detects the delimiter used in a CSV file by inspecting a sample of its contents.

    Args:
        file_path (str): The path to the CSV file whose delimiter is to be detected.

    Returns:
        str: The delimiter character used in the CSV file (e.g., ',', ';', '\t').
        
    Raises:
        csv.Error: If the delimiter cannot be determined from the file's sample.

    Notes:
        - This function reads a sample of the first 10,000 characters from the file to guess the delimiter.
        - It uses the `csv.Sniffer` class from the Python `csv` module to detect the delimiter.
        - The function may raise a `csv.Error` if the sample is insufficient or the file format is irregular.

    Example:
        >>> detect_delimiter('data.csv')
        ','  # Returns the delimiter used in the CSV file (e.g., comma, tab, etc.)
    """
    with open(file_path, 'r', newline='') as file:
        sample = file.read(10000)  # Read a sample of the file
        dialect = csv.Sniffer().sniff(sample)  # Sniff the dialect
        return dialect.delimiter

def IsDEGIROexport(df2):
    """
    Verifies whether a given DataFrame matches the expected column data types for a DEGIRO export.

    Args:
        df2 (pandas.DataFrame): The DataFrame to be checked. It represents the exported data from DEGIRO.

    Returns:
        bool: True if the DataFrame matches the expected column data types and structure, False otherwise.

    Notes:
        - The function checks that the number of columns in the DataFrame matches the expected number.
        - It verifies that each column's data type corresponds to a predefined type in the `spec_dtypes` list.
        - The `spec_dtypes` list defines the expected data types for the columns by index, where:
          - "object" represents string columns.
          - "int64", "float64" represent integer and floating-point numeric columns respectively.
        - If any column does not match the expected data type, the function returns False.
        - If the column count does not match, the function also returns False.

    Example:
        >>> IsDEGIROexport(df)
        True  # If df matches the expected data types and structure.
        
        >>> IsDEGIROexport(df_invalid)
        False  # If df_invalid does not match the expected structure or data types.
    """
    
    # Define the expected data types by column index
    spec_dtypes = [
        "object", "object", "object", "object", "object", "object", "int64", "float64", 
        "object", "float64", "object", "float64", "object", "float64", "float64", "object", 
        "float64", "object", "object"
    ]

    # Check if the number of columns match
    if len(spec_dtypes) == len(df2.columns):
        # Check data types by index
        for i in range(len(spec_dtypes)):
            # Check if the column is of type 'object' (string)
            if pd.api.types.is_string_dtype(df2.iloc[:, i]) and spec_dtypes[i] != 'object':
                return False
            # Check if the column is of numeric type
            elif pd.api.types.is_numeric_dtype(df2.iloc[:, i]) and str(df2.iloc[:, i].dtype) != spec_dtypes[i]:
                return False
        else:
            return True
    else:
        return False

def get_ticker_from_isin(isin, api_key=None):
    """
    Given an ISIN and an OpenFIGI API key, fetches the corresponding ticker symbol.

    Parameters:
    - isin (str): The ISIN of the security.
    - api_key (str): The OpenFIGI API key.

    Returns:
    - str: The corresponding ticker symbol, or an error message if not found.
    """
    url = "https://api.openfigi.com/v3/mapping"

    # Prepare the headers with API key for authentication
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers |= {"X-OPENFIGI-APIKEY": api_key}
        
    # Prepare the payload for the request
    payload = [{
        "idType": "ID_ISIN",
        "idValue": isin
    }]

    # Make the request to OpenFIGI API
    response = requests.post(url, headers=headers, json=payload)

    # Check if the response was successful
    if response.status_code == 200:
        data = response.json()
        if data:
            # Extract the ticker symbols from the response (if available)
            tickers = [item.get("data", [{}])[0].get("ticker", None) for item in data if item.get("data")] [0]
            
            # If there are multiple tickers, return all of them
            if tickers:
                return tickers
            else:
                return "No tickers found for the given ISIN."
        else:
            return "No mapping found."
    else:
        return f"Error: {response.status_code} - {response.text}"

def export_sqlite_to_csv(db_name, table_name, output_csv):
    """
    Extract data from a SQLite3 database and export it to a CSV file.

    Parameters:
    db_name (str): The name of the SQLite database file.
    table_name (str): The name of the table to export.
    output_csv (str): The name of the output CSV file.

    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Execute a query to fetch all data from the table
    cursor.execute(f"SELECT * FROM {table_name}")

    # Fetch all rows from the result of the query
    rows = cursor.fetchall()

    # Open a CSV file for writing
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)

        # Write the column headers (optional)
        column_names = [description[0] for description in cursor.description]  # Get column names
        csv_writer.writerow(column_names)

        # Write the data rows
        csv_writer.writerows(rows)

    # Close the cursor and the connection
    cursor.close()
    conn.close()

    show_popup('DB (CSV) Saved', f'DB saved as CSV to {output_csv}')

def create_table_if_not_exists(tickers_data_df, db_name):
    """
    Creates a table in the specified SQLite database if it doesn't already exist, 
    based on the structure of the provided DataFrame.

    Args:
        tickers_data_df (pandas.DataFrame): The DataFrame containing the data. Its column names and data types are used to 
                                             dynamically define the table structure.
        db_name (str): The name of the SQLite database in which the table will be created.

    Returns:
        None: The function does not return any value. It modifies the database by creating the table if needed.

    Notes:
        - The table is named `tickers_data` and consists of columns derived from the DataFrame's column names.
        - The function assumes that the `Date` and `Ticker` columns are always present and are used as the composite primary key.
        - Columns of type `float64` are stored as `FLOAT`, columns of type `int64` as `INTEGER`, and other columns are stored as `TEXT`.
        - If the table already exists, the function does nothing.

    Example:
        >>> create_table_if_not_exists(df, 'stocks.db')
        # Creates a table named 'tickers_data' in the 'stocks.db' database based on the columns in df.
    """
    
    # Get the columns of the DataFrame
    columns = tickers_data_df.columns

    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Prepare the SQL for table creation dynamically
    sql = 'CREATE TABLE IF NOT EXISTS tickers_data ('
    sql += 'Date DATE, '
    sql += 'Ticker TEXT, '
    
    # Adding columns dynamically based on DataFrame's column names (excluding 'Date' and 'Ticker')
    for col in columns:
        if col not in ['Date', 'Ticker']:  # Exclude 'Date' and 'Ticker' columns
            if tickers_data_df[col].dtype == 'float64':
                column_type = 'FLOAT'
            elif tickers_data_df[col].dtype == 'int64':
                column_type = 'INTEGER'
            else:
                column_type = 'TEXT'  # Default to TEXT for other data types
            sql += f'{col} {column_type}, '

    # Remove the trailing comma and space, and add the PRIMARY KEY for the 'Date' and 'Ticker' combination
    sql = sql.rstrip(', ') + ', PRIMARY KEY (Date, Ticker))'
    
    # Execute the SQL to create the table
    cursor.execute(sql)
    conn.commit()
    conn.close()

# Function to alter the table if new columns are present
def get_columns_from_db(conn, table_name):
    """
    Get the column names from the existing table in the database.
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]  # Fetch column names
    return columns

def alter_table_for_new_columns(conn, df_columns, table_name):
    """
    Alter the table to add columns that are missing in the database.
    """
    existing_columns = get_columns_from_db(conn, table_name)

    # Determine which columns are not present in the existing table
    missing_columns = [col for col in df_columns if col not in existing_columns]
    
    for column in missing_columns:
        # Dynamically add the missing columns (we assume all are TEXT for simplicity)
        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN `{column}` TEXT"
        cursor = conn.cursor()
        cursor.execute(alter_sql)
        print(f"Added new column: {column}")
    
    conn.commit()

def store_new_tickers_data(tickers_data, yahoo_ticker, db_path="tickers_data.db"):
    """
    Store the new ticker data in the database with dynamic columns handling.
    """
    conn = sqlite3.connect(db_path)
    
    # Get the DataFrame and columns from Yahoo Finance data
    tickers_data_df = tickers_data.copy()
    
    # Add 'Ticker' column dynamically if it doesn't exist in the DataFrame
    tickers_data_df['Ticker'] = yahoo_ticker

    # Create the table if it doesn't exist
    create_table_if_not_exists(tickers_data_df,db_path)
    
    # Dynamically adjust the table to match the DataFrame columns
    alter_table_for_new_columns(conn, tickers_data_df.columns, 'tickers_data')
    
    # Create the dynamic SQL insert query
    placeholders = ", ".join(["?"] * len(tickers_data_df.columns))
    
    # Escape column names by wrapping them in backticks
    columns = ", ".join([f"`{col}`" for col in tickers_data_df.columns])
    
    insert_query = f"INSERT OR IGNORE INTO tickers_data ({columns}) VALUES ({placeholders})"
    
    # Insert data into the table
    for _, row in tickers_data_df.iterrows():
        conn.execute(insert_query, tuple(row))
    
    conn.commit()
    print(f"Data for {yahoo_ticker} stored successfully!")
    conn.close()

def create_dataset(SourceFolder):
    """
    This function processes a folder containing CSV files of Degiro exports, detects the delimiter, reads the data into 
    a pandas DataFrame, and calculates cumulative quantities and values for each product (identified by ISIN) 
    based on historical stock prices fetched from Yahoo Finance.

    The function performs the following tasks:
    1. Retrieves all CSV files from the specified 'SourceFolder'.
    2. Validates that the folder contains files and that the internet connection is active.
    3. Reads each CSV file, checking if it conforms to Degiro's export format.
    4. Converts the 'Date' column to a pandas datetime format.
    5. Calculates cumulative quantities and values for each product (based on ISIN) across all dates in the data range.
    6. Fetches historical stock price data for each product from Yahoo Finance.
    7. Returns a DataFrame with the cumulative values for each product on each date in the data range.

    Args:
        SourceFolder (str): The path to the folder containing the CSV files for Degiro exports.

    Returns:
        pd.DataFrame: A DataFrame containing the cumulative quantities and values for each product across the date range.
        The columns include:
            - 'Date': The date of the data.
            - 'Products': The name of the product (from the Degiro export).
            - 'ISIN': The ISIN code of the product.
            - 'Place': The exchange where the product is traded.
            - 'Exec Place': The execution place (trading venue).
            - 'Qty': The cumulative quantity of the product as of that date.
            - 'Buying_value': The cumulative value of the product based on quantity.
            - 'Actual_value': The cumulative value of the product based on the stock's closing price on that date.

    Raises:
        SystemExit: If the source folder is empty, if no internet connection is detected, or if the CSV file does not conform to Degiro's export format.

    Notes:
        - The function assumes that the first column in the CSV files represents the 'Date' field.
        - It assumes the third column represents the 'Produit' field (product name), the fourth column represents the 'ISIN', 
          the fifth column represents the 'Place boursiè' (exchange), and the sixth column represents the 'Lieu d'exécution' 
          (execution place).
        - The function uses the Yahoo Finance API to fetch historical stock data based on the product's ISIN and exchange.
        - If there is no internet connection or if no stock price data is available for the requested dates, the function will 
          handle these cases by skipping or using the closest available date.

    Example:
        df = create_dataset('path_to_your_csv_folder')
        print(df.head())
    """
    os.makedirs(SourceFolder, exist_ok=True)

    # Get all CSV files in the 'source' folder
    csv_files = glob.glob(f'{SourceFolder}/*.csv')
    if not csv_files :
        show_popup("Source Folder Empty", F"Please fill source folder ({SourceFolder})  with your Degiro export. End of process.")
        sys.exit()

    # check if internet is up. if not, close it
    if not is_internet_up() :
        show_popup("No Internet", "Please connect to Internet. End of process.")
        sys.exit()

    # Iterate over files, detect the delimiter, and read them into DataFrame
    dfs = []
    for file in csv_files:
        delim = detect_delimiter(file)
        df = pd.read_csv(file, delimiter=delim)  # Use detected delimiter
        # Check if Df is based on Degiro standards
        if not IsDEGIROexport(df) :
            show_popup("Export Not Ok", f"File {file} is not a supported DEGIRO export format. Please format it proprely. End of process.")
            sys.exit() 
        dfs.append(df)
    # Concatenate all DataFrames
    df = pd.concat(dfs, ignore_index=True)

    # Convert 'Date' column to datetime format ; Index: 0, Column Title: Date
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format='%d-%m-%Y')
    # Get today's date
    today = pd.to_datetime('today')
    # Create a date range from the first date in the data to today
    date_range = pd.date_range(df.iloc[:, 0].min(), today, freq='D')
    # Separate into min and max
    min_date = date_range.min()  # The minimum date
    max_date = date_range.max()  # The maximum date

    # Initialize a list to hold cumulative values for each product and each column
    cumulative_values = []

    # Iterate through each product in the DataFrame
    '''
    Index: 2, Column Title: Produit
    Index: 3, Column Title: Code ISIN
    Index: 4, Column Title: Place boursiè
    Index: 5, Column Title: Lieu d'exécution
    Index: 6, Column Title: Quantité
    Index: 16, Column Title: Montant négocié
    '''

    for ISIN in df.iloc[:, 3].unique():
        # Filter data for the current product
        product_df = df[df.iloc[:, 3] == ISIN]

        # Initialize variables to store the running totals 
        running_quantity = 0
        running_montant = 0
        running_value = 0

        # Find My tickers values
        ticker = get_ticker_from_isin(ISIN)
        exchange = df[df.iloc[:, 3] == ISIN].iloc[:, 4].unique()[0]
        yahoo_ticker = get_yahoo_ticker(ticker, exchange)
        tickers_data = yf.Ticker(yahoo_ticker).history(start=min_date, end=max_date).reset_index() 
        tickers_data['Date'] = pd.to_datetime(tickers_data['Date']).dt.tz_localize(None).dt.date

        # Create a dictionary with 'Date' as key and 'Close' as value (using Date as the index)
        tickers_data_dict = dict(zip(tickers_data['Date'], tickers_data['Close']))
        if not tickers_data_dict:
            continue

        # Iterate through the date range and calculate cumulative quantities and amounts for the current product
        for single_date in date_range:
            
            # Get the quantities and montant for the current date and product
            daily_quantity = product_df[product_df.iloc[:, 0] == single_date].iloc[:, 6].sum()
            daily_montant =- product_df[product_df.iloc[:, 0] == single_date].iloc[:, 16].sum()
        # Lookup the stock price for the given date, handle missing dates
            single_date = pd.to_datetime(single_date).tz_localize(None).date()
            if single_date in tickers_data_dict:
                daily_value = tickers_data_dict[single_date]
            else:
            # If the date is missing, use the closest available date (previous day)
                # Find the closest date less than or equal to the single_date
                # Check if the iterable is not empty before calling max()
                filtered_dates = [date for date in tickers_data_dict if date <= single_date]
                if filtered_dates:
                    closest_date = max(filtered_dates)
                    daily_value = tickers_data_dict[closest_date]
                else:
                    # Handle the case where no valid dates are found
                    closest_date = None  # or any other default value you prefer
                    daily_value = 0
            # Update running totals
            running_quantity += daily_quantity
            running_montant += daily_montant
            running_value = (daily_value * running_quantity)

            # Add Metadata
            product = df[df.iloc[:, 3] == ISIN].iloc[:, 2].iloc[0]  # Get the first value for 'Produit' corresponding to ISIN
            place = df[df.iloc[:, 3] == ISIN].iloc[:, 4].iloc[0]  # Get the first value for 'Place boursiè'
            exec_place = df[df.iloc[:, 3] == ISIN].iloc[:, 5].iloc[0]  # Get the first value for 'Lieu d'exécution'
            
            # Append the result for the current date, product, and cumulative values
            cumulative_values.append([single_date, product,ISIN,place,exec_place, running_quantity, running_montant,running_value])

    # Create a DataFrame with the date, product, cumulative quantity, and cumulative 'Montant négocié'
    cumulative_df = pd.DataFrame(cumulative_values, columns=['Date', 'Products','ISIN','Place','Exec Place', 'Qty', 'Buying_value','Actual_value'])
    
    return cumulative_df


def store_tickers_data_sqlite3_DB(df, output_folder):
    """
    This function stores stock data for unique ISIN values in a SQLite database.
    
    Parameters:
    df (pandas.DataFrame): A DataFrame containing stock data with columns like 'ISIN', 'Place', 'Date', etc.
    output_folder (str): The directory where the SQLite database ('tickers_data.db') will be saved.

    Process:
    - Iterates over unique ISIN values in the DataFrame.
    - Retrieves the corresponding stock ticker and Yahoo Finance ticker symbol.
    - Fetches historical stock data from Yahoo Finance.
    - Stores the stock data in an SQLite database.
    """
    
    # Initialize SQLite connection to store data
    conn = sqlite3.connect(f'{output_folder}/tickers_data.db')
    cursor = conn.cursor()

    # Iterate over each unique ISIN in the DataFrame to store its data
    for isin in df['ISIN'].unique():
        # Filter the DataFrame for the current ISIN to extract relevant information
        ISIN = df[df['ISIN'] == isin]['ISIN'].unique()[0]
        exchange = df[df['ISIN'] == isin]['Place'].unique()[0]

        # Get the stock ticker symbol using the ISIN and exchange
        ticker = get_ticker_from_isin(ISIN)
        yahoo_ticker = get_yahoo_ticker(ticker, exchange)

        # Retrieve the historical stock data from Yahoo Finance
        min_date = pd.to_datetime(df['Date'].min())  # Start date for stock data
        max_date = pd.to_datetime(df['Date'].max())  # End date for stock data
        tickers_data = yf.Ticker(yahoo_ticker).history(start=min_date, end=max_date).reset_index()
        
        # Clean and format the 'Date' column to remove timezone info and convert to date only
        tickers_data['Date'] = pd.to_datetime(tickers_data['Date']).dt.tz_localize(None).dt.date

        # Store the fetched stock data in the SQLite database
        store_new_tickers_data(tickers_data, yahoo_ticker, f'{output_folder}/tickers_data.db')

    # Commit the changes to the database and close the connection
    conn.commit()
    conn.close()

    # Show a popup message indicating the data has been saved
    show_popup('DB Saved', f'DB saved to {output_folder}')