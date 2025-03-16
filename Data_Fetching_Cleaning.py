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
from matplotlib.ticker import PercentFormatter
import yfinance as yf #https://github.com/ranaroussi/yfinance
import pandas as pd
import requests
import json
import glob
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk
from tkinter import messagebox
import csv
import sys
import platform
import numpy as np
from datetime import timedelta
import textwrap
import sqlite3  # Use SQLite or replace with SQLAlchemy for other databases


# Const
from Config.config import *


  
def show_popup(title,message) :
    # Create the root window (it won't appear)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    # Show the popup message box
    messagebox.showinfo(title,message)
    # Close the tkinter instance after the popup
    root.quit()

# Function to dynamically create Yahoo Finance tickers based on ISIN and exchange
def get_yahoo_ticker(ticker, exchange) -> None:
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
    

def detect_delimiter(file_path):
    with open(file_path, 'r', newline='') as file:
        sample = file.read(10000)  # Read a sample of the file
        dialect = csv.Sniffer().sniff(sample)  # Sniff the dialect
        return dialect.delimiter

def IsDEGIROexport(df2):
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

    print(f"Data has been extracted to '{output_csv}'.")



# Function to create the table if not exists
def create_table_if_not_exists(tickers_data_df,db_name):
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

def create_dataset(SourceFolder,OutputFolder) :
        
    # Connect to SQLite (You can use SQLAlchemy for other databases)
    conn = sqlite3.connect(f'{OutputFolder}/tickers_data.db')
    cursor = conn.cursor()


    # Get all CSV files in the 'source' folder
    csv_files = glob.glob(f'{SourceFolder}/*.csv')
    if not csv_files :
        show_popup("Source Folder Empty", "Please fill source folder with your Degiro export. End of process.")
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
        # Store the new ticker data in DB
        store_new_tickers_data(tickers_data,yahoo_ticker,f'{OutputFolder}/tickers_data.db')
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

    # for debug
    # export_sqlite_to_csv(f'{date_folder}/tickers_data.db', 'tickers_data', 'dboutput.csv')

    # Create a DataFrame with the date, product, cumulative quantity, and cumulative 'Montant négocié'
    cumulative_df = pd.DataFrame(cumulative_values, columns=['Date', 'Products','ISIN','Place','Exec Place', 'Qty', 'Buying_value','Actual_value'])

    # Define the output file path inside the new subfolder
    output_file = os.path.join(OutputFolder, 'output_file.csv')
    # Export the DataFrame to the CSV file in the 'output' folder
    cumulative_df.to_csv(output_file, index=False)
    
    return cumulative_df