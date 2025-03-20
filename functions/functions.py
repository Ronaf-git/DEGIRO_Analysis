# ----------------------------------------------------
# -- Projet : DEGIRO_Analysis
# -- Author : Ronaf
# -- Created : 01/02/2025
# -- Usage : 
# -- Update : 
# --  
# ----------------------------------------------------
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

def show_popup(title, message):
    """
    Displays a simple popup message box with a specified title and message.

    Parameters:
    title (str): The title that will appear at the top of the popup window.
    message (str): The message content displayed in the popup.

    The function creates a hidden root Tkinter window, shows the message box, 
    and then gracefully terminates the Tkinter instance after the popup is dismissed.
    
    Example usage:
    show_popup("Information", "This is a message!")
    """
    # Create the root window (it won't appear)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    # Show the popup message box
    messagebox.showinfo(title, message)
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

def export_df_csv(OutputFolder,df):
# Define the output file path inside the new subfolder
    output_file = os.path.join(OutputFolder, 'output_file.csv')
    # Export the DataFrame to the CSV file in the 'output' folder
    df.to_csv(output_file, index=False)
    show_popup('Data exported to csv', f'Data exported to {output_file}')

def plots_saveAs_OnePDF(pdf_filepath, plots_dict):
    """
    Save multiple plots into a single PDF file.

    This function takes a dictionary of plot objects and saves each of them into a single PDF file. 
    The function can handle both individual plots as well as lists of plots.

    Parameters:
    -----------
    pdf_filepath : str
        The path where the PDF file will be saved (including the file name).
    
    plots_dict : dict
        A dictionary where the keys are titles (strings) and the values are plot objects (matplotlib figures or lists of figures).
        Each entry in the dictionary represents a plot or a list of plots that will be saved into the PDF.
    
    The function will iterate over the dictionary, and for each plot or list of plots:
    - It will save each plot to the provided PDF file.
    - It will close each plot after saving to free up memory.

    Returns:
    --------
    None
        This function does not return any values. It performs the action of saving the plots to a PDF.

    Example usage:
    --------------
    # Assuming you have a dictionary of plots
    plots_dict = {
        'Plot 1': plot1, 
        'Plot 2': [plot2a, plot2b], 
        'Plot 3': plot3
    }
    plots_saveAs_OnePDF('output_plots.pdf', plots_dict)
    
    This will save `plot1`, `plot2a`, `plot2b`, and `plot3` to the file `output_plots.pdf`.
    """
    with PdfPages(pdf_filepath) as pdf:
        # Loop through the dictionary of plots and save each one to the PDF
        for title, plot in plots_dict.items():  # title is the first element, plot is the figure object
            # Check if the plot is a list
            if isinstance(plot, list):
                # Iterate over each plot in the list and save it
                for p in plot:
                    pdf.savefig(p)  # Save each figure in the list
                    plt.close(p)    # Close the plot after saving
            else:
                pdf.savefig(plot)  # Save the current plot (figure) to the PDF
                plt.close(plot)    # Close the plot after saving
                plt.close(plot)    # Close the plot after saving
    show_popup('Report exported to pdf', f'Report exported to {pdf_filepath}')

def plots_saveAs_PNG(outputFolderPath, plots_dict):
    """
    Save multiple plots as PNG files in a specified folder.

    This function takes a dictionary of plot objects and saves each one as a PNG file in the specified output folder. 
    The function handles both individual plot objects as well as lists of plots.

    Parameters:
    -----------
    outputFolderPath : str
        The folder path where the PNG files will be saved. The folder should exist before calling this function.
    
    plots_dict : dict
        A dictionary where the keys are titles (strings) and the values are plot objects (matplotlib figures or lists of figures).
        Each entry in the dictionary represents a plot or a list of plots that will be saved as PNG files.

    The function will iterate over the dictionary and save each plot to the specified folder. If a plot has no title, 
    the function will generate a default title. After saving each plot, it will be closed to free up memory.

    Returns:
    --------
    None
        This function does not return any values. It performs the action of saving the plots as PNG files.

    Example usage:
    --------------
    # Assuming you have a dictionary of plots
    plots_dict = {
        'Plot 1': plot1, 
        'Plot 2': [plot2a, plot2b], 
        'Plot 3': plot3
    }
    plots_saveAs_PNG('outputFolderPath', plots_dict)
    
    This will save `plot1`, `plot2a`, `plot2b`, and `plot3` as PNG files in the 'outputFolderPath'.
    """
    for title, plot in plots_dict.items():  # title is the key, plot is the figure object
        if isinstance(plot, list):  # Check if the plot is a list of figures
            for idx, p in enumerate(plot):
                # Get the plot's title (handling cases where the title might be missing or empty)
                plot_title = p.gca().get_title() if p.gca().get_title() else f"{title}_plot_{idx+1}"
                p.savefig(os.path.join(outputFolderPath, f'{plot_title}.png'))
                plt.close(p)  # Close the plot after saving
        else:
            # Get the plot's title (handling cases where the title might be missing or empty)
            plot_title = plot.gca().get_title() if plot.gca().get_title() else f"{title}"
            plot.savefig(os.path.join(outputFolderPath, f'{plot_title}.png'))
            plt.close(plot)  # Close the plot after saving
    show_popup('Plots exported as PNG', f'Img exported to {outputFolderPath}')

