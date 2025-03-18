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

def create_guard_page():
# Create a plt img with text : guard page of the exported pdf
    current_date = datetime.now().strftime("%d %B %Y")  
    fig = plt.figure(figsize=(10,6))
    # Add the main text (centered)
    plt.text(0.5, 0.6, "Degiro Report", 
             ha='center', va='center', fontsize=45, fontweight='bold')
    # Add date to the right
    plt.text(0.95, 0.05, f"{current_date}", 
            ha='right', va='center', fontsize=10, fontweight='normal')
    # Add credit to the left
    plt.text(0.05, 0.05, f"{AUTHOR} - v{VERSION}", 
            ha='left', va='center', fontsize=10, fontweight='normal')
    plt.axis('off')  # Turn off axes
    return fig

def create_page_section(title):
# Create a plt img with text  
    fig = plt.figure(figsize=(10,6))
    # Add the main text (centered)
    plt.text(0.5, 0.6, title, 
             ha='center', va='center', fontsize=45, fontweight='bold')
    plt.axis('off')  # Turn off axes
    return fig

def plot_portfolio_product_percentage_by_date(df):

    df_copy = df.copy()

    # Convert the 'Date' column to datetime if it's not already
    df_copy['Date'] = pd.to_datetime(df_copy['Date'], format='%d-%m-%y')

    # Calculate total Actual_value per day
    df_copy['Total_value'] = df_copy.groupby('Date')['Actual_value'].transform('sum')

    # Calculate percentage of Actual_value per product for each day
    df_copy['Percentage'] = (df_copy['Actual_value'] / df_copy['Total_value']) * 100

     # Create a pivot table to make plotting easier
    pivot_df = df_copy.pivot_table(index='Date', columns='Products', values='Percentage', aggfunc='sum', fill_value=0)

    # Create a figure and axes object for the plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot each product's percentage as an area plot
    pivot_df.plot.area(ax=ax, colormap='tab20', alpha=0.7)

    # Set the title and labels for the axes
    ax.set_title('Percentage Contribution of Each Product to Total Actual Value per Day')
    ax.set_xlabel('Date')
    ax.set_ylabel('Percentage (%)')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)

    # Remove the grid
    ax.grid(False)

    # Place the legend at the bottom of the plot (outside)
    ax.legend(title="Products", loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5, fontsize=8)

    # Limit the y-axis to 0-100%
    ax.set_ylim(0, 100)

    # Add a legend title and adjust the layout for better spacing
    ax.legend(title="Products")
    plt.tight_layout()
    
    return fig

def plot_total_pct_by_date(cumulative_df):
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
    return fig

def plot_total_by_date(cumulative_df):
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

    return plt1

def plots_ISIN_by_date(cumulative_df):
    # List to store all the figures
    plots = []
    # 2. Create and store the plot for each ISIN showing its "Montant du portefeuille"
    isin_list = cumulative_df['ISIN'].unique()
    for isin in isin_list:
        plt_isin = plt.figure(figsize=(12, 6))
        # Filter data for the current ISIN
        isin_data = cumulative_df[cumulative_df['ISIN'] == isin]
        # Filter the rows where 'Actual_value' is 0 and drop the 'Date' column
        isin_data.loc[isin_data['Actual_value'] == 0, 'Date'] = None
        product_name = cumulative_df[cumulative_df['ISIN'] == isin]['Products'].unique()[0]
        grouped_data = cumulative_df.groupby('Date')[['Actual_value','Buying_value']].sum().reset_index()
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

     # Return the list of figures
    return plots

def plot_pivot_table(df) :
    df_copy = df.copy()

    # Format the values for table display
    df_copy['Buying_value'] = df_copy['Buying_value'].apply(lambda x: f"€ {x:,.2f}")
    df_copy['Actual_value'] = df_copy['Actual_value'].apply(lambda x: f"€ {x:,.2f}")
    df_copy['Value_diff'] = df_copy['Value_diff'].apply(lambda x: f"€ {x:,.2f}")
    df_copy['Percentage_diff'] = df_copy['Percentage_diff'].apply(lambda x: f"{x:,.2f}%")

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
    table = ax.table(cellText=df_copy.values, colLabels=df_copy.columns, loc='center', cellLoc='center')
    # Adjust table aesthetics
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.auto_set_column_width(col=list(range(len(df_copy.columns))))

    # Show the plot
    plt.title('Product Comparison with Values and Deltas', fontsize=16)
    plt.tight_layout()

    # Store the plot in the array
    return fig_Table

def plots_portfolio_by_ISIN_by_date(cumulative_df) :
    # List to store all the figures
    plots = []
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

    return plots

def plots_ISIN_pct_by_date(cumulative_df):
    # List to store all the figures
    plots = []
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
     # Return the list of figures
    return plots


def plot_pie_portfolio_by_ISIN(df):
    df_copy = df.copy()
    # 4. Create a pie chart of portfolio distribution by ISIN and actual value
    # Calculate total value for each ISIN
    Product_value = df_copy.groupby('Products')['Actual_value'].sum()
    # Pie chart for portfolio distribution
    plt_pie = plt.figure(figsize=(12, 6))
    plt.pie(Product_value, labels=Product_value.index, autopct='%1.1f%%', startangle=140)
    plt.title('Portfolio Distribution By Product')
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    # Store the pie chart in the array
    return plt_pie

def plot_KPI(cumulative_df,today_data):
    current_date = datetime.now().strftime('%Y-%m-%d')
        # 0. Home/KPI
    # Get the most recent date
    # Get the most recent date

    # Calculate the total row
    total_row = today_data[['Buying_value', 'Actual_value']].sum()
    # Convert the total row to a DataFrame (since pd.concat expects DataFrames)
    total_row_df = pd.DataFrame([total_row])
    # Concatenate the original DataFrame with the total row
    today_data = pd.concat([today_data, total_row_df], ignore_index=True)

    # add % of total actual value
    today_data['Actual_value_percentage'] = today_data['Actual_value'] / total_row['Actual_value'] * 100


    # 1. KPI: Actual_value vs Buying_value (today), in percentage
    # Calculate the absolute and percentage delta for today
    total_actual_value = total_row_df['Actual_value'].sum()
    total_buying_value = total_row_df['Buying_value'].sum()

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

    return fig0