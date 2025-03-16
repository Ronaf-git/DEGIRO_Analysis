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

def create_guard_page(plots):
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
    plots.append(fig)

def plot_product_percentage(df, plots):
    # Convert the 'Date' column to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%y')

    # Calculate total Actual_value per day
    df['Total_value'] = df.groupby('Date')['Actual_value'].transform('sum')

    # Calculate percentage of Actual_value per product for each day
    df['Percentage'] = (df['Actual_value'] / df['Total_value']) * 100

     # Create a pivot table to make plotting easier
    pivot_df = df.pivot_table(index='Date', columns='Products', values='Percentage', aggfunc='sum', fill_value=0)

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
    
    plots.append(fig)

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