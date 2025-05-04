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
# --- Install/Create Exe
#pyinstaller --onefile --noconsole Main.py

# ==============================================================================================================================
# Imports
# ==============================================================================================================================
# Const
from Config.config import *
# ----- Standard
import os
from datetime import datetime
import sys
import queue
import threading


# ----- From Files
from functions.callAllFunctions import *

# ==============================================================================================================================
# Functions
# ==============================================================================================================================
def get_exe_dir(relative_path):
    if getattr(sys, 'frozen', False):
        # If running from a bundled .exe, sys.executable points to the .exe file
        base_path = os.path.dirname(sys.executable)  # Directory of the .exe
    else:
        # If running from the source code (not frozen), use the current working directory
        base_path = os.path.dirname(relative_path)
    # Combine base path with relative path to get the full path to the resource
    return base_path
# ==============================================================================================================================
# Variables 
# ==============================================================================================================================
# Variables
current_date = datetime.now().strftime('%Y-%m-%d')

# Source folder, output folder
exe_dir = get_exe_dir(__file__)
source_folder = os.path.join(exe_dir, SOURCE_FOLDER)
output_folder = os.path.join(exe_dir, OUTPUR_FOLDER)
date_folder = os.path.join(output_folder, current_date)
pdf_filepath = os.path.join(date_folder, 'Degiro Analysis.pdf')

# ==============================================================================================================================
# Init 
# ==============================================================================================================================

# Start the Tkinter popup in a separate thread
command_queue = queue.Queue()
popup_thread = threading.Thread(target=run_popup, args=(command_queue,))
popup_thread.start()

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

# After the loop, close the popup
command_queue.put('close')
# Wait for the popup thread to finish
popup_thread.join()

createUI(plots,pdf_filepath,date_folder,cumulative_df)
exit()

