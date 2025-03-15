# ----------------------------------------------------
# -- Projet : DEGIRO_Analysis
# -- Author : Ronaf
# -- Created : 01/02/2025
# -- Usage : 
# -- Update : 
# --  
# ----------------------------------------------------


# --- If running from python : install requirements (packages)
# from Config.requirements import *

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

# ==============================================================================================================================
# Variables
# ==============================================================================================================================
# ----- Custom Files
# Const
from Config.config import *


# Get current date as a string in the format YYYY-MM-DD
current_date = datetime.now().strftime('%Y-%m-%d')



# ==============================================================================================================================
# Functions
# ==============================================================================================================================


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
    
def show_popup(title,message) :
    # Create the root window (it won't appear)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    # Show the popup message box
    messagebox.showinfo(title,message)
    # Close the tkinter instance after the popup
    root.quit()

def open_system(path):
    """
    Opens the specified folder in the default file explorer based on the operating system.

    Parameters:
    - folder_path (str): The full path to the folder to be opened.
    """
    try:
        # Check the operating system and open the folder accordingly
        if platform.system() == "Darwin":  # macOS
            os.system(f'open "{path}"')
        elif platform.system() == "Windows":  # Windows
            os.startfile(path)
        else:  # Linux and others
            os.system(f'xdg-open "{path}"')
    except Exception as e:
        print(f"An error occurred while trying to open the folder: {e}")

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
def create_table_if_not_exists(tickers_data_df):
    # Get the columns of the DataFrame
    columns = tickers_data_df.columns

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
    create_table_if_not_exists(tickers_data_df)
    
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









# Check if the code is being run as a PyInstaller executable
if hasattr(sys, '_MEIPASS'):  # This is a special attribute set by PyInstaller when running an exe
    exe_dir = sys._MEIPASS  # PyInstaller sets _MEIPASS to the temporary folder where the exe is running
else:
    try:
        exe_dir = os.path.dirname(os.path.realpath(__file__))  # For regular Python script, use the script's directory
    except NameError:
        # In Jupyter, __file__ doesn't exist, so fallback to the current working directory
        exe_dir = os.getcwd()  # Use the current working directory in Jupyter



# Define the output folder and file name
source_folder = os.path.join(exe_dir, 'source')
os.makedirs(source_folder, exist_ok=True)  # Ensure the output folder exists

output_folder = os.path.join(exe_dir, 'output')
os.makedirs(output_folder, exist_ok=True)  # Ensure the output folder exists

date_folder = os.path.join(output_folder, current_date)
os.makedirs(date_folder, exist_ok=True)

# Define the output file path inside the new subfolder
output_file = os.path.join(date_folder, 'output_file.csv')

# Connect to SQLite (You can use SQLAlchemy for other databases)
conn = sqlite3.connect(f'{date_folder}/tickers_data.db')
cursor = conn.cursor()


# Get all CSV files in the 'source' folder
csv_files = glob.glob(f'{source_folder}/*.csv')
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
    print(yahoo_ticker)
    tickers_data = yf.Ticker(yahoo_ticker).history(start=min_date, end=max_date).reset_index() 
    tickers_data['Date'] = pd.to_datetime(tickers_data['Date']).dt.tz_localize(None).dt.date
    # Store the new ticker data in DB
    store_new_tickers_data(tickers_data,yahoo_ticker,f'{date_folder}/tickers_data.db')
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

# Export the DataFrame to the CSV file in the 'output' folder
cumulative_df.to_csv(output_file, index=False)




# ===============================================================
# Create Dataset
# ===============================================================



# plots
# Set plot style
sns.set(style="whitegrid")

# Create an array to store the plot objects
plots = []

# 0. Home/KPI
# Get the most recent date
# Get the most recent date
today = cumulative_df['Date'].max()

# Filter for the latest data
today_data = cumulative_df[cumulative_df['Date'] == today].copy()
# Calculate the total row
total_row = today_data[['Buying_value', 'Actual_value']].sum()
# Convert the total row to a DataFrame (since pd.concat expects DataFrames)
total_row_df = pd.DataFrame([total_row])
# Concatenate the original DataFrame with the total row
today_data = pd.concat([today_data, total_row_df], ignore_index=True)

# Calculate the percentage difference for Actual_value vs Buying_value using .loc to avoid SettingWithCopyWarning
today_data.loc[:, 'Value_diff'] = (today_data['Actual_value'] - today_data['Buying_value'])
today_data.loc[:, 'Percentage_diff'] = ((today_data['Actual_value'] - today_data['Buying_value']) / today_data['Buying_value']) * 100
print(today_data)

exit()
# 1. KPI: Actual_value vs Buying_value (today), in percentage
# Calculate the absolute and percentage delta for today
total_actual_value = today_data['Actual_value'].sum()
total_buying_value = today_data['Buying_value'].sum()

# Absolute delta
absolute_delta = total_actual_value - total_buying_value
# Choose color based on percentage delta
colorKPI1 = 'green' if absolute_delta >= 0 else 'red'

# Percentage delta
if total_buying_value != 0 and not pd.isna(total_buying_value):
    percentage_delta = ((total_actual_value - total_buying_value) / total_buying_value) * 100
else:
    percentage_delta = 0  # Or handle as needed, maybe raise an exception

# 2. KPI: Maximum negative gap (both value and percentage)
negative_gap_df = cumulative_df[cumulative_df['Actual_value'] < cumulative_df['Buying_value']]
negative_gap_df['Gap_value'] = negative_gap_df['Buying_value'] - negative_gap_df['Actual_value']
negative_gap_df['Gap_percentage'] = (negative_gap_df['Gap_value'] / negative_gap_df['Buying_value']) * 100

# Check if there are any negative gaps; if not, set default values
if negative_gap_df.empty:
    max_negative_gap_value = 0
    max_negative_gap_percentage = 0
else:
    max_negative_gap_value = negative_gap_df['Gap_value'].max()
    max_negative_gap_percentage = negative_gap_df['Gap_percentage'].max()

# Create the grid for the KPIs and add it to the plots list
plots = []

fig0, axs = plt.subplots(2, 2, figsize=(10, 6))
# Set the title for the entire figure
fig0.suptitle("KPI Dashboard for Today's Data", fontsize=16)

# 1st plot: Actual_value vs Buying_value (aggregated for today)
axs[0, 0].barh([f'Actual vs Buying Value (Today)'], [percentage_delta], color=colorKPI1)
axs[0, 0].set_title(f'Profit and Loss (On {current_date})')
axs[0, 0].set_xlabel('% Difference')
axs[0, 0].set_ylabel('')
# Add absolute and percentage delta as text on the plot
axs[0, 0].text(0.5, 0.60, f"{absolute_delta:,.2f}€", ha='center', va='center', fontsize=26, transform=axs[0, 0].transAxes, color='black')
axs[0, 0].text(0.5, 0.30, f"{percentage_delta:,.2f}%", ha='center', va='center', fontsize=26, transform=axs[0, 0].transAxes, color='black')
axs[0, 0].axis('off')

# 2nd plot: Maximum Negative Gap (value)
axs[0, 1].barh([f'Max Negative Gap'], [max_negative_gap_value], color='tomato')
axs[0, 1].set_title(f'Max Negative Gap (Value)')
axs[0, 1].set_xlabel('Gap Value')
axs[0, 1].set_xlim([0, max_negative_gap_value + 5])
axs[0, 1].axis('off')

# 3rd plot: Placeholder (empty or some other visualization)
axs[1, 0].axis('off')
axs[1, 0].text(0.5, 0.5, 'Placeholder 1', horizontalalignment='center', verticalalignment='center', fontsize=12)

# 4th plot: Placeholder (empty or some other visualization)
axs[1, 1].axis('off')
axs[1, 1].text(0.5, 0.5, 'Placeholder 2', horizontalalignment='center', verticalalignment='center', fontsize=12)

plots.append(fig0)




# Plot 
def plot_variation(cumulative_df, plots):
    # Step 1: Convert 'Date' to datetime format
    cumulative_df['Date'] = pd.to_datetime(cumulative_df['Date'])

    # Step 2: Group by 'Date' and calculate the total Buying_value and Actual_value per date
    grouped = cumulative_df.groupby('Date').agg({
        'Buying_value': 'sum',
        'Actual_value': 'sum'
    }).reset_index()

    # Step 3: Calculate the percentage variation for each grouped date
    grouped['Variation_%'] = ((grouped['Actual_value'] - grouped['Buying_value']) / grouped['Buying_value']) * 100

    # Step 4: Create the plot
    fig, ax = plt.subplots(figsize=(10,6))
    # Step 6: Loop through the data to plot each point with the appropriate color
    for i in range(1, len(grouped)):
        if grouped['Variation_%'].iloc[i] >= 0:
            color = 'green'  # Positive or 0% variation
        else:
            color = 'red'  # Negative variation
        
        # Plot the segment between consecutive points (i-1 and i)
        ax.plot(grouped['Date'].iloc[i-1:i+1], 
                grouped['Variation_%'].iloc[i-1:i+1], 
                color=color, linestyle='-', label='All' if i == len(grouped) - 1 else "")

    # Step 5: Add labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Variation (%)')
    ax.set_title('Variation in % between Buying and Actual Values by Date')

    # Step 6: Add grid, format x-axis labels, and tight layout
    ax.grid(True)
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
    plt.tight_layout()

    # Step 7: Add a horizontal line at 0% for visual reference
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
    # Step 7: Append the figure to the plots list
    plots.append(fig)
plot_variation(cumulative_df, plots)

def plot_variation_by_isin(cumulative_df, plots):
    # Step 1: Convert 'Date' to datetime format
    cumulative_df['Date'] = pd.to_datetime(cumulative_df['Date'])

    # Step 2: Loop through each unique ISIN
    for isin in cumulative_df['ISIN'].unique():
        # Filter the data for the current ISIN
        isin_data = cumulative_df[cumulative_df['ISIN'] == isin]
        # Get the product name for the current ISIN (assuming there's only one product per ISIN)
        product_name = isin_data['Products'].unique()[0]
        
        # Step 3: Group by 'Date' and calculate the total Buying_value and Actual_value per date for this ISIN
        grouped = isin_data.groupby('Date').agg({
            'Buying_value': 'sum',
            'Actual_value': 'sum'
        }).reset_index()

        # Step 4: Calculate the percentage variation for each grouped date
        grouped['Variation_%'] = ((grouped['Actual_value'] - grouped['Buying_value']) / grouped['Buying_value']) * 100

        # Step 5: Create the plot for this ISIN
        fig, ax = plt.subplots(figsize=(10, 6))

        # Step 6: Loop through the data to plot each point with the appropriate color
        for i in range(1, len(grouped)):
            if grouped['Variation_%'].iloc[i] >= 0:
                color = 'green'  # Positive or 0% variation
            else:
                color = 'red'  # Negative variation
            
            # Plot the segment between consecutive points (i-1 and i)
            ax.plot(grouped['Date'].iloc[i-1:i+1], 
                    grouped['Variation_%'].iloc[i-1:i+1], 
                    color=color, linestyle='-', label=product_name if i == len(grouped) - 1 else "")

        # Step 7: Add labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Variation (%)')
        ax.set_title(f'Variation in % {isin} ({product_name})')


        # Step 7: Add a horizontal line at 0% for visual reference
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1)

        # Step 8: Format y-axis as percentage
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))

        # Step 9: Add grid, format x-axis labels, and tight layout
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels
        plt.tight_layout()

        # Step 10: Append the figure to the plots list
        plots.append(fig)
plot_variation_by_isin(cumulative_df, plots)



# Assuming today_data is already defined and includes the 'Date' column
df_today_data = today_data.copy()

df = today_data.copy()




# Format the values for table display
df['Buying_value'] = df['Buying_value'].apply(lambda x: f"€ {x:,.2f}")
df['Actual_value'] = df['Actual_value'].apply(lambda x: f"€ {x:,.2f}")
df['Value_diff'] = df['Value_diff'].apply(lambda x: f"€ {x:,.2f}")
df['Percentage_diff'] = df['Percentage_diff'].apply(lambda x: f"{x:,.2f}%")

'''
# Function to wrap text in cells
def wrap_text(text, width=10):
    return "\n".join(textwrap.wrap(text, width=width))

# Apply wrapping to the DataFrame content
df = df.applymap(lambda x: wrap_text(x) if isinstance(x, str) else x)
'''
# Prepare the table
fig_Table, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size (in inches)
# Hide axes
ax.axis('off')
# Create the table using the DataFrame
table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
# Adjust table aesthetics
table.auto_set_font_size(False)
table.set_fontsize(8)
table.auto_set_column_width(col=list(range(len(df.columns))))



# Show the plot
plt.title('Product Comparison with Values and Deltas', fontsize=16)
plt.tight_layout()


# Store the plot in the array
plots.append(fig_Table)









# 1. Create and store the plot for the total Montant du portefeuille by date
plt1 = plt.figure(figsize=(12, 6))
# Group the data by 'Date' and sum the 'Montant du portefeuille' for each date
grouped_data = cumulative_df.groupby('Date')[['Actual_value','Buying_value']].sum().reset_index()
# Loop through the data to plot each point with the appropriate color
for i in range(1, len(grouped_data)):
    # Check if 'Montant du portefeuille' is ahead or not for this segment
    if grouped_data['Actual_value'].iloc[i] > grouped_data['Buying_value'].iloc[i]:
        color = 'green'  # 'Montant du portefeuille' is ahead
    else:
        color = 'red'  # 'Montant du portefeuille' is not ahead
    
    # Plot the segment between consecutive points (i-1 and i)
    plt.plot(grouped_data['Date'].iloc[i-1:i+1], 
             grouped_data['Actual_value'].iloc[i-1:i+1], 
             color=color,label='Product value' if i == len(grouped_data) - 1 else "", linestyle='-')


# Plot the 'Cumulative_Montant_négocié' line in red
plt.plot(grouped_data['Date'], grouped_data['Buying_value'], color='Blue', label='Invested value', linestyle='-')

plt.title('Portfolio Progress')
plt.xlabel('Date')
plt.ylabel('Value')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
# Store the plot in the array
plots.append(plt1)



# 2. Create and store the plot for each ISIN showing its "Montant du portefeuille"
isin_list = cumulative_df['ISIN'].unique()
for isin in isin_list:
    plt_isin = plt.figure(figsize=(12, 6))
    # Filter data for the current ISIN
    isin_data = cumulative_df[cumulative_df['ISIN'] == isin]
    # Filter the rows where 'Actual_value' is 0 and drop the 'Date' column
    isin_data.loc[isin_data['Actual_value'] == 0, 'Date'] = None
    product_name = cumulative_df[cumulative_df['ISIN'] == isin]['Products'].unique()[0]
    
    # Loop through the data for the current ISIN and plot segments with different colors
    for i in range(1, len(isin_data)):
        # Check if 'Montant du portefeuille' is ahead or not for this segment
        if isin_data['Actual_value'].iloc[i] > isin_data['Buying_value'].iloc[i]:
            color = 'green'  # 'Montant du portefeuille' is ahead
        else:
            color = 'red'  # 'Montant du portefeuille' is not ahead
        
        # Plot the segment between consecutive points (i-1 and i) for 'Montant du portefeuille'
        plt.plot(isin_data['Date'].iloc[i-1:i+1], 
                 isin_data['Actual_value'].iloc[i-1:i+1], 
                 color=color,label='Product value' if i == len(grouped_data) - 1 else "", linestyle='-')

    # Plot the 'Cumulative_Montant_négocié' line in red for the current ISIN
    plt.plot(isin_data['Date'], isin_data['Buying_value'], color='blue', label=f"Invested value", linestyle='-')
    
    plt.title(f'Portfolio Value for {product_name}')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    # Store the plot in the array
    plots.append(plt_isin)

# 3. Create and store the combined plot for all tickers
plt_all_tickers = plt.figure(figsize=(12, 6))
for isin in cumulative_df['ISIN'].unique():
    # Get the ticker for the current ISIN (assuming the `get_ticker_from_isin()` function)
    #ticker = get_ticker_from_isin(isin, api_key="YOUR_API_KEY")  # Replace with your actual API key
    # Filter the data for the current ISIN
    isin_data = cumulative_df[cumulative_df['ISIN'] == isin]
    product_name = cumulative_df[cumulative_df['ISIN'] == isin]['Products'].unique()[0]
    # Plot the data for the current ticker (ISIN)
    plt.plot(isin_data['Date'], isin_data['Actual_value'], label=f"{product_name}", linestyle='-')

plt.title('Portfolio Progress By Product - Actual Values')
plt.xlabel('Date')
plt.ylabel('Value')
plt.xticks(rotation=45)
plt.legend(title='Products')
plt.tight_layout()
# Store the plot in the array
plots.append(plt_all_tickers)

# 3. Create and store the combined plot for all tickers
plt_all_tickers_bought = plt.figure(figsize=(12, 6))
for isin in cumulative_df['ISIN'].unique():
    # Filter the data for the current ISIN
    isin_data = cumulative_df[cumulative_df['ISIN'] == isin]
    product_name = cumulative_df[cumulative_df['ISIN'] == isin]['Products'].unique()[0]
    # Plot the data for the current ticker (ISIN)
    plt.plot(isin_data['Date'], isin_data['Buying_value'], label=f"{product_name}", linestyle='-')

plt.title('Portfolio Progress By Product - Buying value')
plt.xlabel('Date')
plt.ylabel('Value')
plt.xticks(rotation=45)
plt.legend(title='Products')
plt.tight_layout()
# Store the plot in the array
plots.append(plt_all_tickers_bought)


# 4. Create a pie chart of portfolio distribution by ISIN and actual value
# Calculate total value for each ISIN
Product_value = today_data.groupby('Products')['Actual_value'].sum()
# Pie chart for portfolio distribution
plt_pie = plt.figure(figsize=(12, 6))
plt.pie(Product_value, labels=Product_value.index, autopct='%1.1f%%', startangle=140)
plt.title('Portfolio Distribution By Product')
plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
# Store the pie chart in the array
plots.append(plt_pie)


# Create a PdfPages object to save all the plots into a single PDF
pdf_filepath = os.path.join(date_folder, 'Degiro Analysis.pdf')
with PdfPages(pdf_filepath) as pdf:
    # Loop through the list of plot objects and save each one to the PDF
    for idx, plot in enumerate(plots):
        # Get the plot's title (handling cases where the title might be missing or empty)
        title = plot.gca().get_title() if plot.gca().get_title() else f"plot_{idx+1}"
        plot.savefig(os.path.join(date_folder, f'{title}.png'))
        pdf.savefig(plot)  # Save the current plot to the PDF
        plt.close(plot)    # Close the plot after saving

try : 
   # show_popup("Analyse done",f"All graphs (separate and merged in PDF) have been saved to the output folder ({date_folder}). The dataset is also available. The pdf will open.")
    open_system(pdf_filepath)
except:
    print("An exception occurred")