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

def plots_saveAs_OnePDF(pdf_filepath,plots) :
    with PdfPages(pdf_filepath) as pdf:
        # Loop through the list of plot objects and save each one to the PDF
        for idx, plot in enumerate(plots):
            pdf.savefig(plot)  # Save the current plot to the PDF
            plt.close(plot)    # Close the plot after saving

def plots_saveAs_PNG(outputFolderPath,plots) :
    for idx, plot in enumerate(plots):
        # Get the plot's title (handling cases where the title might be missing or empty)
        title = plot.gca().get_title() if plot.gca().get_title() else f"plot_{idx+1}"
        plot.savefig(os.path.join(outputFolderPath, f'{title}.png'))
        plt.close(plot)    # Close the plot after saving