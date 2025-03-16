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
# Const
from Config.config import *
# ----- Standard
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
# ----- From Files
from Data_Fetching_Cleaning import *
from vizualisations import *

# ==============================================================================================================================
# Functions
# ==============================================================================================================================

    
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

def get_exe_dir():
    # Check if the code is being run as a PyInstaller executable
    if hasattr(sys, '_MEIPASS'):  # PyInstaller sets _MEIPASS when running as an exe
        return sys._MEIPASS  # Return the temporary folder where the exe is running
    else:
        try:
            # For regular Python script, use the script's directory
            return os.path.dirname(os.path.realpath(__file__))
        except NameError:
            # In Jupyter or interactive mode, __file__ doesn't exist, so fallback to the current working directory
            return os.getcwd()  # Return the current working directory in Jupyter or interactive mode



# ==============================================================================================================================
# Variables 
# ==============================================================================================================================


# Variables
current_date = datetime.now().strftime('%Y-%m-%d')

# Source folder, output folder
exe_dir = get_exe_dir()
source_folder = os.path.join(exe_dir, SOURCE_FOLDER)
  # Ensure the output folder exists

output_folder = os.path.join(exe_dir, OUTPUR_FOLDER)
  # Ensure the output folder exists

date_folder = os.path.join(output_folder, current_date)





# Create folders
os.makedirs(source_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)
os.makedirs(date_folder, exist_ok=True)

# Create Dataset and export it, aswell as Financial data
cumulative_df = create_dataset(source_folder,date_folder)






# ===============================================================
# Create Dataset
# ===============================================================



# plots
# Set plot style
sns.set(style="whitegrid")

# Create an array to store the plot objects
plots = []

create_guard_page(plots)

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

# add % of total actual value
today_data['Actual_value_percentage'] = today_data['Actual_value'] / total_row['Actual_value'] * 100

# Calculate the percentage difference for Actual_value vs Buying_value using .loc to avoid SettingWithCopyWarning
today_data.loc[:, 'Value_diff'] = (today_data['Actual_value'] - today_data['Buying_value'])
today_data.loc[:, 'Percentage_diff'] = ((today_data['Actual_value'] - today_data['Buying_value']) / today_data['Buying_value']) * 100
print(today_data)

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





plot_product_percentage(cumulative_df, plots)

# Plot 

plot_variation(cumulative_df, plots)


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