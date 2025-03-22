# DEGIRO_Analysis

DEGIRO_Analysis is a Python-based project designed to help users track their investments using the transaction data exported from Degiro, a popular online investment platform. By processing the transactions in CSV format, it provides users with insights into their investment performance.

## Features

- Process and clean transaction data from Degiro's CSV export.
- Analyze investment history and performance.
- Visualize investment data for better understanding.
- Dedicated Windows Interface
![My cool features](./Docs/pictures/Example.gif)
- Outputs, like a [PDF Report](./Docs/Output_example/Date/Degiro%20Analysis.pdf), Stock Data DB, ...


## How to 
### Running Executable on Windows
1. Download the latest release from the [Releases page](https://github.com/Ronaf-git/DEGIRO_Analysis/releases).
2. Extract the archive into a dedicated folder
3. Drop your Degiro export "transaction.csv" into the "source" folder (Dont forget to delete the sample)
4. Run the executable to see your reports. 

Note: Exported files will be saved in the "output" folder.

## Running python script (advanced)
### Requirements

- Python 3.x
- Required libraries: `pandas`, `matplotlib`, `numpy`, `seaborn`.
- Internet connection (to fetch data from the [OpenFIGI API](https://api.openfigi.com/v3/mapping) and [yfinance](https://github.com/ranaroussi/yfinance)).


### Files Overview

- `Main.py`: The entry point that runs the full analysis.
- `config/requirements.py`: Python script to install required dependencies.
- `config/config.py`: Config File

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Ronaf-git/DEGIRO_Analysis.git
   ```

2. Navigate to the project directory:

   ```bash
   cd DEGIRO_Analysis
   ```

3. Install the required dependencies by running the `requirements.py` script located in the `config` directory:

   ```bash
   python config/requirements.py
   ```

4. Place your Degiro transaction CSV file in the source folder, as stated by SOURCE_FOLDER variable in the config file. Create folder if not existing.

### Usage

Run the `Main.py` script to start the analysis:

```bash
python Main.py
```

This will fetch and process your CSV file, analyze the data, and provide relevant visualizations and reports.

## Coming Next

- Portfolio Analysis by sector
- Portfolio Analysis by asset type
- Date/Stock/... selectors

## Note

- Datas may not be 100% accurate
- The dictionary linking Exchange to Yahoo Finance suffix may be inaccurate
- APIs can be broken

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
