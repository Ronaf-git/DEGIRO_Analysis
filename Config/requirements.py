# ----------------------------------------------------
# -- Projet : DEGIRO_Analysis
# -- Author : Ronaf
# -- Created : 02/03/2025
# -- Usage : Install/Update needed packages to run the uncompilled code 
# -- Update : 
# --  
# ----------------------------------------------------

# ------------------ Install Package -------------
import subprocess
import sys

# Function to install packages
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print('''============================================
Start Install/Updates needed Python Packages
============================================''')

# List of packages to install
packages = ["pandas", "matplotlib", "seaborn","yfinance"]

# Installing each package
for package in packages:
    print(f"Installing {package}...")
    install(package)

print('''============================================
Packages Installed/Updated
============================================''')

