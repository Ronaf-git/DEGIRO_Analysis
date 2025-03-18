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
from functions import *
from analysis import *

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
cumulative_df = calculation_df(cumulative_df)

today = cumulative_df['Date'].max()
# Filter for the latest data
today_data = cumulative_df[cumulative_df['Date'] == today].copy()


# ===============================================================
# Create Dataset
# ===============================================================



# plots
# Set plot style
#sns.set(style="whitegrid")

# Create an array to store the plot objects
# extend : add one value ; Extend : add all individual value from a list to another list
plots = []


plots.append(create_guard_page())
plots.append(plot_KPI(cumulative_df,today_data))
plots.append(plot_pivot_table(today_data))
plots.append(plot_total_by_date(cumulative_df))
plots.append(plot_total_pct_by_date(cumulative_df))
plots.append(plot_portfolio_product_percentage_by_date(cumulative_df))
print(today_data)
plots.append(plot_pie_portfolio_by_ISIN(today_data))

plots.append(create_page_section('Appendixes'))
plots.extend(plots_ISIN_pct_by_date(cumulative_df))
plots.extend(plots_ISIN_by_date(cumulative_df))
plots.extend(plots_portfolio_by_ISIN_by_date(cumulative_df))




# Create a PdfPages object to save all the plots into a single PDF
pdf_filepath = os.path.join(date_folder, 'Degiro Analysis.pdf')
plots_saveAs_OnePDF(pdf_filepath,plots)
plots_saveAs_PNG(date_folder,plots)


try : 
   # show_popup("Analyse done",f"All graphs (separate and merged in PDF) have been saved to the output folder ({date_folder}). The dataset is also available. The pdf will open.")
    open_system(pdf_filepath)
except:
    print("An exception occurred")