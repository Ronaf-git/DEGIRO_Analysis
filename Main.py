# ----------------------------------------------------
# -- Projet : DEGIRO_Analysis
# -- Author : Ronaf
# -- Created : 01/02/2025
# -- Usage : 
# -- Update : 20/03/2025 
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
import os
from datetime import datetime
import sys
# ----- From Files
from functions.callAllFunctions import *

# ==============================================================================================================================
# Functions
# ==============================================================================================================================
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
output_folder = os.path.join(exe_dir, OUTPUR_FOLDER)
date_folder = os.path.join(output_folder, current_date)
pdf_filepath = os.path.join(date_folder, 'Degiro Analysis.pdf')

# ==============================================================================================================================
# Init 
# ==============================================================================================================================
# Create folders
os.makedirs(source_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)
os.makedirs(date_folder, exist_ok=True)

# ===============================================================
# Create Dataset
# ===============================================================
# Create Dataset 
base_df = create_dataset(source_folder)

cumulative_df = calculation_df(base_df)
# get dataset grouped by date
grouped_df = grouped_df_by_date(cumulative_df)

#get today dataset
today = cumulative_df['Date'].max()
# Filter for the latest data
today_data = cumulative_df[cumulative_df['Date'] == today].copy()


plots = get_all_plots(cumulative_df,today_data,grouped_df)

createUI(plots,pdf_filepath,date_folder,cumulative_df)
exit()

