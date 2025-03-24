# ==============================================================================================================================
# Imports
# ==============================================================================================================================
# ----- Standard
from matplotlib.ticker import PercentFormatter
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms  # Import necessary transforms
# Const
from Config.config import *

def create_ReadMe():
    # Create a figure and axis
    fig = plt.figure(figsize=(10, 6))
    plt.axis('off')
    text_content = f"""
    Author : {AUTHOR}
    Version : {VERSION}

    Tab 2: KPI
    Plot: "KPI Plot"
    Description: This dashboard contains key performance indicators (KPIs) to evaluate the portfolio’s performance, including profit/loss percentage and other relevant metrics for today’s data.

    Tab 3: Pivot Table
    Plot: "Pivot Table"
    Description: This plot displays a table summarizing the portfolio data, showing values like buying value, actual value, value differences, and percentage differences for each product. 
    This helps in detailed analysis and comparison of each product.

    Tab 4: Overview
    1. Plot: "Total Percentage by Date"
       Description: A line chart that shows the percentage variation between the actual value and the buying value over time.
    2. Plot: "Total by Date"
       Description: A line chart tracking the total actual and invested value of the portfolio over time. The color coding indicates whether the portfolio’s value is ahead or behind the invested value.
    3. Plot: "Portfolio Product Percentage"
       Description: A stacked area chart displaying how each product’s percentage contributes to the total portfolio value over time.
    4. Plot: "Pie Portfolio by ISIN"
       Description: A pie chart showing the distribution of portfolio value by different ISINs (products), making it easy to see which products have the largest share.

    Tab 5: Appendixes
    1. Plot: "ISIN Percentage by Date"
       Description: This line plot shows the percentage variation between actual and buying values for each ISIN, color-coded to highlight positive and negative variations.
    2. Plot: "ISIN by Date"
       Description: A line chart showing portfolio values over time for each ISIN, displaying whether the actual value is above or below the invested value at each point.
    3. Plot: "Portfolio by ISIN by Date"
       Description: A line plot showing the performance of the portfolio over time for all ISINs, indicating how each product performs relative to the invested value.
    
    Tab 6: Export
   - Export all plots in a single PDF Report
   - Export all plots as PNG individually
   - Export dataset as CSV
   - Export stocks data as sqlite3 DB and as CSV

    For more information, visit: https://github.com/Ronaf-git/DEGIRO_Analysis
    """
    # Adding text to the plot
    plt.text(0, 1, text_content, transform=fig.transFigure, fontsize=12, verticalalignment='top')

    return fig

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
    plt.axis('off')  
    return fig

def create_page_section(title):
# Create a plt img with text  
    fig = plt.figure(figsize=(10,6))
    # Add the main text (centered)
    plt.text(0.5, 0.6, title, 
             ha='center', va='center', fontsize=45, fontweight='bold')
    plt.axis('off') 
    return fig

def plot_portfolio_product_percentage_by_date(df):
    """
    Plots the percentage contribution of each product in a portfolio over time.

    This function takes a DataFrame containing portfolio data, processes the data by creating 
    a pivot table, and then generates an area plot showing the percentage contribution of 
    each product in the portfolio for each date.

    Args:
    - df (pandas.DataFrame): A DataFrame containing the portfolio data with the following columns:
        - 'Date': The date of the portfolio snapshot.
        - 'Products': The product names or identifiers.
        - 'Product_pct_in_portfolio_for_day': The percentage of the portfolio attributed to each product on that day.

    Returns:
    - matplotlib.figure.Figure: A Matplotlib figure object containing the plot.

    Example:
    --------
    df = pd.DataFrame({
        'Date': ['2025-01-01', '2025-01-01', '2025-01-02', '2025-01-02'],
        'Products': ['Product A', 'Product B', 'Product A', 'Product B'],
        'Product_pct_in_portfolio_for_day': [30, 70, 40, 60]
    })

    fig = plot_portfolio_product_percentage_by_date(df)
    plt.show()

    This will produce an area plot displaying the percentage contribution of 'Product A' and 
    'Product B' to the portfolio for each day in the dataset.
    """
    
    # Create a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()

    # Create a pivot table to make plotting easier
    pivot_df = df_copy.pivot_table(
        index='Date', 
        columns='Products', 
        values='Product_pct_in_portfolio_for_day', 
        aggfunc='sum', 
        fill_value=0
    )

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

def plot_total_pct_by_date(df):
    """
    Plots the variation percentage between buying and actual values over time, 
    with positive variations shown in green and negative variations in red.
    
    Parameters:
    df (pd.DataFrame): A pandas DataFrame containing the data to be plotted. The DataFrame must include:
        - 'Date' (pd.Series): A series of dates (should be in datetime format).
        - 'Variation_%' (pd.Series): A series of percentage values representing the variation between buying and actual values.
    
    Returns:
    fig (matplotlib.figure.Figure): The matplotlib figure object containing the plot.
    
    The plot will display:
        - A line plot of the percentage variation, where:
            - Positive or 0% variation is shown in green.
            - Negative variation is shown in red.
        - A horizontal dashed line at 0% variation for reference.
        - X-axis labels rotated for better visibility.
        - Y-axis formatted to show percentage values.
    """
    # Create a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()

    # Create the plot with a specific figure size
    fig, ax = plt.subplots(figsize=(10,6))
    
    # Loop through the data to plot each segment of the variation with the appropriate color
    for i in range(1, len(df_copy)):
        if df_copy['Variation_%'].iloc[i] >= 0:
            color = 'green'  # Positive or 0% variation
        else:
            color = 'red'  # Negative variation
        
        # Plot the segment between consecutive points (i-1 and i)
        ax.plot(df_copy['Date'].iloc[i-1:i+1], 
                df_copy['Variation_%'].iloc[i-1:i+1], 
                color=color, linestyle='-', label='All' if i == len(df_copy) - 1 else "")

    # Add labels for x and y axes and set the plot title
    ax.set_xlabel('Date')
    ax.set_ylabel('Variation (%)')
    ax.set_title('Variation in % between Buying and Actual Values by Date')

    # Add grid lines, rotate x-axis labels for better readability, and format the y-axis as a percentage
    ax.grid(True)
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))  # Format y-axis as percentage
    plt.tight_layout()

    # Add a horizontal line at 0% for visual reference
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
    
    # Return the figure object containing the plot
    return fig

import matplotlib.pyplot as plt

def plot_total_by_date(df, start_date=None, end_date=None):
    """
    Plots the total portfolio value over time, comparing the actual value ('Actual_value') 
    with the invested value ('Buying_value'), and highlights the progress of the portfolio.
    
    Args:
        df (pd.DataFrame): The input dataframe containing portfolio data. The dataframe must have the following columns:
            - 'Date': A datetime or string column representing the dates of each observation.
            - 'Actual_value': A numerical column representing the actual value of the portfolio at each date.
            - 'Buying_value': A numerical column representing the invested value of the portfolio at each date.
        start_date (str or datetime, optional): The start date for filtering the data (inclusive).
        end_date (str or datetime, optional): The end date for filtering the data (inclusive).
        
    Returns:
        plt.Figure: A matplotlib figure object containing the plot.

    The function creates a plot where:
    - Green segments represent periods where the 'Actual_value' is higher than the 'Buying_value'.
    - Red segments represent periods where the 'Actual_value' is lower than the 'Buying_value'.
    - A blue line represents the 'Buying_value' (invested value) throughout the time period.
    """
    # Convert 'Date' column to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'])

    # Filter the dataframe based on the start_date and end_date (if provided)
    if start_date is not None:
        df = df[df['Date'] >= pd.to_datetime(start_date)]
    if end_date is not None:
        df = df[df['Date'] <= pd.to_datetime(end_date)]
    
    # Create a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Create and store the plot for the total Actual_value by date
    fig = plt.figure(figsize=(12, 6))
    
    # Loop through the data to plot each point with the appropriate color
    for i in range(1, len(df_copy)):
        # Check if 'Actual_value' is ahead or not for this segment
        if df_copy['Actual_value'].iloc[i] > df_copy['Buying_value'].iloc[i]:
            color = 'green'  # 'Actual_value' is ahead
        else:
            color = 'red'  # 'Actual_value' is not ahead
        
        # Plot the segment between consecutive points (i-1 and i)
        plt.plot(df_copy['Date'].iloc[i-1:i+1], 
                 df_copy['Actual_value'].iloc[i-1:i+1], 
                 color=color, label='Product value' if i == len(df_copy) - 1 else "", linestyle='-')

    # Plot the 'Buying_value' line in blue
    plt.plot(df_copy['Date'], df_copy['Buying_value'], color='Blue', label='Invested value', linestyle='-')

    plt.title('Portfolio Progress')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    return fig


def plots_ISIN_by_date(df):
    """
    Generates a series of line plots for each ISIN in the given DataFrame showing the portfolio value 
    over time. The plots are designed to show the comparison between the actual portfolio value 
    and the invested value, highlighting whether the portfolio is ahead or behind the invested value 
    at different points in time.

    The function generates a separate plot for each unique ISIN in the dataframe. The plot displays:
    - A line for the portfolio value ('Actual_value') with color-coded segments: green if the portfolio 
      value is ahead of the invested value ('Buying_value'), and red if it is behind.
    - A line for the invested value ('Buying_value') in blue.

    Additionally:
    - The x-axis represents the dates, and the y-axis represents the monetary values.
    - Each plot is titled with the product name associated with the ISIN.
    - Legends are provided to differentiate between the 'Portfolio Value' and 'Invested Value' lines.
    - The plot for each ISIN is returned in a list.

    Args:
        df (pandas.DataFrame): A DataFrame containing the following columns:
            - 'ISIN' (str): Unique identifier for each financial instrument (e.g., stock, bond, or mutual fund).
            - 'Date' (datetime): The date for each record, representing the date of a portfolio value observation.
            - 'Actual_value' (float): The current portfolio value on a given date, representing the performance 
              of the investment.
            - 'Buying_value' (float): The invested value (cumulative value invested in the portfolio), which can 
              be used to compare the portfolio's growth.
            - 'Products' (str): The name of the product associated with each ISIN, which will be used as the 
              title of the plot.

    Returns:
        list: A list of Matplotlib figure objects, each representing a plot for a specific ISIN. Each plot contains:
            - A color-coded line for the portfolio's actual value over time, with green for when the portfolio 
              is ahead of the invested value and red when it is behind.
            - A line for the invested value (blue) over time.
            - A title containing the name of the product corresponding to the ISIN.
            - A legend to differentiate between the portfolio value and invested value lines.

       Example:
        >>> df = pd.DataFrame({
        >>>     'ISIN': ['ISIN1', 'ISIN1', 'ISIN2', 'ISIN2'],
        >>>     'Date': pd.to_datetime(['2021-01-01', '2021-01-02', '2021-01-01', '2021-01-02']),
        >>>     'Actual_value': [100, 120, 200, 220],
        >>>     'Buying_value': [90, 110, 190, 210],
        >>>     'Products': ['Product A', 'Product A', 'Product B', 'Product B']
        >>> })
        >>> plots = plots_ISIN_by_date(df)
        >>> # This will return a list of Matplotlib figure objects, which can be displayed or saved.
    """
    # Create a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    # List to store all the figures
    plots = []
    # Create and store the plot for each ISIN showing its Actual_value
    isin_list = df_copy['ISIN'].unique()
    for isin in isin_list:
        plt_isin = plt.figure(figsize=(12, 6))
        # Filter data for the current ISIN
        isin_data = df_copy[df_copy['ISIN'] == isin]
        # Filter the rows where 'Actual_value' is 0 and drop the 'Date' column
        isin_data.loc[isin_data['Actual_value'] == 0, 'Date'] = None
        product_name = df_copy[df_copy['ISIN'] == isin]['Products'].unique()[0]
        grouped_data = df_copy.groupby('Date')[['Actual_value','Buying_value']].sum().reset_index()
        # Loop through the data for the current ISIN and plot segments with different colors
        for i in range(1, len(isin_data)):
            # Check if Actual_value is ahead or not for this segment
            if isin_data['Actual_value'].iloc[i] > isin_data['Buying_value'].iloc[i]:
                color = 'green'  # Actual_value is ahead
            else:
                color = 'red'  # Actual_value is not ahead
            
            # Plot the segment between consecutive points (i-1 and i) for Actual_value
            plt.plot(isin_data['Date'].iloc[i-1:i+1], 
                    isin_data['Actual_value'].iloc[i-1:i+1], 
                    color=color,label='Product value' if i == len(grouped_data) - 1 else "", linestyle='-')

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

def plot_pivot_table(df):
    """
    Generates a pivot table plot from the given DataFrame, displaying key financial data such as
    'Product % in Portfolio', 'Investment Value', 'Portfolio Value', and their corresponding 
    delta values (in both € and percentage). The plot is a table that shows this information in 
    a clean and formatted manner.

    Parameters:
    -----------
    df : pandas.DataFrame
        A DataFrame containing financial data with at least the following columns:
        - 'Date': The date of the portfolio entry.
        - 'Product_pct_in_portfolio_for_day': The percentage of the product in the portfolio.
        - 'Buying_value': The investment value.
        - 'Actual_value': The actual portfolio value.
        - 'Value_diff': The difference in the value (between expected and actual).
        - 'Percentage_diff': The percentage difference in value.

    Returns:
    --------
    matplotlib.figure.Figure
        A matplotlib figure object containing the table plot with the financial data and its deltas.

    Process:
    --------
    1. Creates a copy of the input DataFrame and removes the 'Total_value_for_day' column if it exists.
    2. Formats the columns for better readability:
        - 'Date' column is converted to a datetime format.
        - The 'Product_pct_in_portfolio_for_day' column is formatted as a percentage with two decimal places.
        - 'Buying_value', 'Actual_value', 'Value_diff', and 'Percentage_diff' columns are formatted in euros and percentages respectively.
    3. Renames the columns for improved readability.
    4. Generates a matplotlib figure with a table displaying the formatted DataFrame.
    5. Hides the axes for a cleaner table view and adjusts the aesthetics like font size, column width, and title.
    
    Example:
    --------
    df = pd.DataFrame({
        'Date': ['01-03-25', '02-03-25'],
        'Product_pct_in_portfolio_for_day': [25.0, 30.5],
        'Buying_value': [1000, 1500],
        'Actual_value': [1050, 1550],
        'Value_diff': [50, 50],
        'Percentage_diff': [5.0, 3.33],
        'Total_value_for_day': [1050, 1550]
    })
    
    fig = plot_pivot_table(df)
    plt.show()
    """
    
    # Step 1: Create a copy of the DataFrame and drop 'Total_value_for_day' column
    df_copy = df.copy()
    df_copy = df.drop(columns=['Total_Actual_value_for_day','Place','Exec Place','Total_Buying_value_for_day']).copy()
    
    total_row = df_copy[['Buying_value', 'Actual_value','Value_diff']].sum()
    # Convert the total row to a DataFrame
    total_row = pd.DataFrame([total_row])
    # Convert the total row to a DataFrame (since pd.concat expects DataFrames)
    total_row['Products'] = 'Total'  # Label it as 'Total' or something unique
    total_row['Percentage_diff'] = (total_row['Value_diff'].sum() / total_row['Buying_value'].sum())*100
    df_copy = pd.concat([df_copy, total_row], ignore_index=True)

    # Step 2: Format the values for table display
    df_copy['Date'] = df_copy['Date'].dt.strftime('%d/%m/%Y')
    df_copy['Product_pct_in_portfolio_for_day'] = df_copy['Product_pct_in_portfolio_for_day'].apply(lambda x: f"{x:,.2f}%")
    df_copy['Buying_value'] = df_copy['Buying_value'].apply(lambda x: f"€ {x:,.2f}")
    df_copy['Actual_value'] = df_copy['Actual_value'].apply(lambda x: f"€ {x:,.2f}")
    df_copy['Value_diff'] = df_copy['Value_diff'].apply(lambda x: f"€ {x:,.2f}")
    df_copy['Percentage_diff'] = df_copy['Percentage_diff'].apply(lambda x: f"{x:,.2f}%")
    
    # Step 3: Rename columns for better readability
    df_copy = df_copy.rename(columns={
        'Product_pct_in_portfolio_for_day': 'Product % in Portfolio',
        'Buying_value': 'Investment Value',
        'Actual_value': 'Portfolio Value',
        'Value_diff': 'Delta €',
        'Percentage_diff': 'Delta %'
    })
    
    # Step 4: Prepare the table plot
    fig, ax = plt.subplots(figsize=(12, 6))  # Set figure size (A4 landscape size)
    # Hide axes for a cleaner table view
    ax.axis('off')
    # Create the table using the DataFrame
    table = ax.table(cellText=df_copy.values, colLabels=df_copy.columns, loc='center', cellLoc='center')
    # Adjust table aesthetics: font size, column width
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.auto_set_column_width(col=list(range(len(df_copy.columns))))
    # Add a title to the plot
    plt.title('Product Comparison with Values and Deltas', fontsize=16)

    return fig

def plots_portfolio_by_ISIN_by_date(df):
    """
    This function generates two plots visualizing the portfolio progress based on ISIN and date:
    1. The first plot shows the portfolio progress by product with actual values over time.
    2. The second plot shows the portfolio progress by product with buying values over time.

    Args:
    df (pd.DataFrame): A DataFrame containing the portfolio data with columns: 'ISIN', 'Products', 
                        'Date', 'Actual_value', and 'Buying_value'.

    Returns:
    list: A list containing two matplotlib figure objects with the generated plots.
    """
    
    # Create a copy of the DataFrame to avoid modifying the original data
    df_copy = df.copy()
    
    # List to store the generated plots
    generated_plots = []
    
    # List of value types to loop through
    value_types = ['Actual_value', 'Buying_value']
    
    # Loop through the value types (Actual_value and Buying_value)
    for value_type in value_types:
        # Create a new figure for the plot
        plot = plt.figure(figsize=(12, 6))
        
        # Loop through each unique ISIN in the DataFrame to plot the data
        for isin in df_copy['ISIN'].unique():
            # Filter data for the current ISIN
            isin_data = df_copy[df_copy['ISIN'] == isin]
            
            # Get the product name for the current ISIN
            product_name = isin_data['Products'].unique()[0]
            
            # Plot the specified value (Actual_value or Buying_value) for the current ISIN
            plt.plot(isin_data['Date'], isin_data[value_type], label=f"{product_name}", linestyle='-')

        # Set the title and labels based on the value type
        plt.title(f'Portfolio Progress by Product - {value_type.replace("_", " ").title()}')
        plt.xlabel('Date')
        plt.ylabel(f'{value_type.replace("_", " ").title()}')
        plt.xticks(rotation=45)
        plt.legend(title='Products')
        plt.tight_layout()
        
        # Store the plot in the generated plots list
        generated_plots.append(plot)

    return generated_plots

def plots_ISIN_pct_by_date(df):
    """
    This function generates a series of plots showing the percentage variation between 'Actual_value' and 'Buying_value'
    for each ISIN in the given DataFrame. Each plot represents the percentage change over time, with positive changes 
    shown in green and negative changes shown in red.

    Parameters:
    df (DataFrame): A pandas DataFrame containing the data. It must include the columns 'ISIN', 'Products', 
                    'Date', 'Buying_value', and 'Actual_value'.
    
    Returns:
    List: A list of matplotlib figure objects, each corresponding to a plot for one ISIN.
    """
    
    # Create a copy of the DataFrame to avoid modifying the original data
    df_copy = df.copy()
    
    # List to store all the plot figures
    plots = []
    
    # Loop through each unique ISIN in the DataFrame
    for isin in df_copy['ISIN'].unique():
        # Filter the data for the current ISIN
        isin_data = df_copy[df_copy['ISIN'] == isin]
        
        # Get the product name for the current ISIN (assuming one product per ISIN)
        product_name = isin_data['Products'].unique()[0]
        
        # Group by 'Date' and calculate the total Buying_value and Actual_value per date for this ISIN
        grouped_data = isin_data.groupby('Date').agg({
            'Buying_value': 'sum',
            'Actual_value': 'sum'
        }).reset_index()

        # Calculate the percentage variation for each grouped date
        grouped_data['Variation_%'] = ((grouped_data['Actual_value'] - grouped_data['Buying_value']) / 
                                       grouped_data['Buying_value']) * 100

        # Create the plot for this ISIN
        fig, ax = plt.subplots(figsize=(10, 6))

        # Loop through the data to plot each point with the appropriate color (green for positive or 0%, red for negative)
        for i in range(1, len(grouped_data)):
            color = 'green' if grouped_data['Variation_%'].iloc[i] >= 0 else 'red'
            
            # Plot the segment between consecutive points (i-1 and i)
            ax.plot(grouped_data['Date'].iloc[i-1:i+1], 
                    grouped_data['Variation_%'].iloc[i-1:i+1], 
                    color=color, linestyle='-', label=product_name if i == len(grouped_data) - 1 else "")
        
        # Add labels and title to the plot
        ax.set_xlabel('Date')
        ax.set_ylabel('Variation (%)')
        ax.set_title(f'Variation in % for ISIN {isin} ({product_name})')
        
        # Add a horizontal line at 0% for visual reference
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
        
        # Format y-axis as percentage
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
        
        # Add grid, rotate x-axis labels for readability, and adjust layout
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels for better readability
        plt.tight_layout()

        # Append the generated plot to the list of plots
        plots.append(fig)
    
    # Return the list of plots
    return plots

def plot_pie_portfolio_by_ISIN(df):
    """
    Plots a pie chart showing the distribution of a portfolio by ISIN and its corresponding actual value.

    Parameters:
    df (pandas.DataFrame): A pandas DataFrame containing the portfolio data.
                           The DataFrame should include at least two columns:
                           - 'Products' (the ISIN or product identifier),
                           - 'Actual_value' (the value associated with each product).

    Returns:
    matplotlib.figure.Figure: The pie chart figure displaying the portfolio distribution by ISIN.
    
    Process:
    1. A copy of the input DataFrame is created to avoid modifying the original data.
    2. The total value for each ISIN (or product) is calculated by summing the 'Actual_value' column grouped by the 'Products' column.
    3. A pie chart is created to visualize the portfolio distribution, with each slice representing the proportion of each ISIN's total value.
    4. The pie chart is displayed with percentages shown on the slices, and the chart is configured to have an equal aspect ratio to ensure the pie is circular.

    Example:
    >>> df = pd.DataFrame({
    >>>     'Products': ['ISIN001', 'ISIN002', 'ISIN003', 'ISIN001', 'ISIN002'],
    >>>     'Actual_value': [100, 200, 150, 300, 50]
    >>> })
    >>> plot_pie_portfolio_by_ISIN(df)
    """
    # Create a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    current_date = df_copy['Date'].max().strftime('%d/%m/%Y')
    # Calculate total value for each ISIN
    Product_value = df_copy.groupby('Products')['Actual_value'].sum()
    # Pie chart for portfolio distribution
    fig = plt.figure(figsize=(12, 6))
    plt.pie(Product_value, labels=Product_value.index, autopct='%1.1f%%', startangle=140)
    plt.title(f'Portfolio Distribution By Product - {current_date}')
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.

    return fig

def plot_KPI(df):
    """
    Generate a KPI dashboard for today's data, including various visualizations. 
    This function creates a figure with multiple subplots displaying key performance indicators (KPIs) for a given dataset.

    Parameters:
    -----------
    df : pandas.DataFrame
        A pandas DataFrame containing the dataset with at least the following columns:
        - 'Date': A column containing the date of the data entries.
        - 'Value_diff': A column containing the difference in values (e.g., profit or loss) between two values (actual vs buying).
        - 'Buying_value': A column containing the buying value for each entry.

    Returns:
    --------
    fig : matplotlib.figure.Figure
        A matplotlib figure object containing the KPI dashboard with 4 subplots:
        1. A bar plot showing the percentage difference between the actual and buying values for today.
        2. Three placeholders for future visualizations.
    
    Details:
    --------
    - The first plot shows the profit and loss for today, comparing the 'Actual_value' with the 'Buying_value' as a percentage difference.
    - The color of the bar in the first plot depends on the sign of the absolute delta, where green indicates a positive value and red indicates a negative value.
    - The second, third, and fourth plots are placeholders and can be replaced with additional visualizations.
    - The function does not modify the original DataFrame but works with a copy.

    Example:
    --------
    fig = plot_KPI(df)
    plt.show()  # Display the generated figure
    """
    
    # Create a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()

    # 1. KPI: Actual_value vs Buying_value (today), in percentage
    # Calculate the absolute and percentage delta for today
    current_date = df_copy['Date'].max().strftime('%d/%m/%Y')
    absolute_delta = df_copy['Value_diff'].sum()
    percentage_delta = (df_copy['Value_diff'].sum() / df_copy['Buying_value'].sum())*100

    # Choose color based on percentage delta
    colorKPI1 = 'green' if absolute_delta >= 0 else 'red'

    fig, axs = plt.subplots(2, 2, figsize=(10, 6))
    # Set the title for the entire figure
    fig.suptitle("KPI Dashboard for Today's Data", fontsize=16)

    # 1st plot: Actual_value vs Buying_value (aggregated for today)
    axs[0, 0].barh([f'Actual vs Buying Value (Today)'], [percentage_delta], color=colorKPI1)
    axs[0, 0].set_title(f'Profit and Loss (On {current_date})')
    axs[0, 0].set_xlabel('% Difference')
    axs[0, 0].set_ylabel('')

    # Add absolute and percentage delta as text on the plot
    axs[0, 0].text(0.5, 0.60, f"{absolute_delta:,.2f}€", ha='center', va='center', fontsize=26, transform=axs[0, 0].transAxes, color='black')
    axs[0, 0].text(0.5, 0.30, f"{percentage_delta:,.2f}%", ha='center', va='center', fontsize=26, transform=axs[0, 0].transAxes, color='black')
    axs[0, 0].axis('off')

    # 2nd plot: Placeholder (empty or some other visualization)
    axs[0, 1].axis('off')
    axs[0, 1].text(0.5, 0.5, 'Placeholder 0.1', horizontalalignment='center', verticalalignment='center', fontsize=12)

    # 3rd plot: Placeholder (empty or some other visualization)
    axs[1, 0].axis('off')
    axs[1, 0].text(0.5, 0.5, 'Placeholder 1.0', horizontalalignment='center', verticalalignment='center', fontsize=12)

    # 4th plot: Placeholder (empty or some other visualization)
    axs[1, 1].axis('off')
    axs[1, 1].text(0.5, 0.5, 'Placeholder 1.1', horizontalalignment='center', verticalalignment='center', fontsize=12)

    return fig


def get_all_plots(cumulative_df, today_data,grouped_df, start_date=None, end_date=None):
    """
    Generates and returns a dictionary of various plot objects for visualization.

    The function creates multiple plots from the provided data and stores them in a dictionary. 
    Each plot is associated with a meaningful key for easy reference. The function includes plots 
    related to KPI, portfolio performance, and other key metrics, as well as pages for additional 
    documentation like "ReadMe" and "Appendixes".

    Args:
        cumulative_df (pandas.DataFrame): A DataFrame containing cumulative data, typically used 
                                           for calculating portfolio product percentages and ISIN-based metrics.
        today_data (pandas.DataFrame): A DataFrame containing the latest data, used for generating 
                                       KPI and other time-sensitive visualizations.
        grouped_df (pandas.DataFrame): A DataFrame with grouped data, primarily used for plotting 
                                       totals and percentage breakdowns by date.

    Returns:
        dict: A dictionary where the keys are strings representing plot titles (e.g., "Guard Page", 
              "ReadMe", "KPI Plot", etc.), and the values are plot objects generated by the respective 
              plot functions.
              
    Notes:
        - The function assumes that the helper functions (e.g., `create_guard_page`, `plot_KPI`, etc.) 
          are defined elsewhere and return valid plot objects or sections.
        - The dictionary returned can be used for dynamically generating reports or visualizations.
    """
    # Create a dictionary to store the plot objects
    plots = {}
    
    # Add plots to the dictionary with meaningful keys
    plots["Guard Page"] = create_guard_page()
    plots["ReadMe"] = create_ReadMe()
    plots["KPI Plot"] = plot_KPI(today_data)
    plots["Pivot Table"] = plot_pivot_table(today_data)
    plots["Total by Date"] = plot_total_by_date(grouped_df, start_date, end_date)
    plots["Total Pct by Date"] = plot_total_pct_by_date(grouped_df)
    plots["Portfolio Product Percentage"] = plot_portfolio_product_percentage_by_date(cumulative_df)
    plots["Pie Portfolio by ISIN"] = plot_pie_portfolio_by_ISIN(today_data)
    plots["Appendixes"] = create_page_section('Appendixes')
    
    # Extend with additional plots from the functions that return lists
    plots["ISIN Percentage by Date"] = plots_ISIN_pct_by_date(cumulative_df)
    plots["ISIN by Date"] = plots_ISIN_by_date(cumulative_df)
    plots["Portfolio by ISIN by Date"] = plots_portfolio_by_ISIN_by_date(cumulative_df)
    
    return plots