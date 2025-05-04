import pandas as pd

def calculation_df(df) :

    df_copy = df.copy()

    # Formatting
    df_copy['Date'] = pd.to_datetime(df_copy['Date'], format='%d-%m-%y')

    #Adjusting values
    # Handle case where Actual_value is 0 and Buying_value is not 0
    df_copy.loc[
        (df_copy['Actual_value'] == 0) &
        (df_copy['Buying_value'] != 0) &
        (df_copy['Qty'] != 0),
        'Actual_value'
    ] = df_copy['Buying_value']

    # Calculations
    # Calculate total Actual_value per day and %of product ; excluding total rows
    df_copy['Total_Actual_value_for_day'] = df_copy.groupby('Date')['Actual_value'].transform('sum')
    df_copy['Total_Buying_value_for_day'] = df_copy.groupby('Date')['Buying_value'].transform('sum')
    df_copy['Product_pct_in_portfolio_for_day'] = (df_copy['Actual_value'] / df_copy['Total_Actual_value_for_day']) * 100

    # Calculate the percentage difference for Actual_value vs Buying_value using .loc to avoid SettingWithCopyWarning
    df_copy.loc[:, 'Value_diff'] = (df_copy['Actual_value'] - df_copy['Buying_value'])
    df_copy.loc[:, 'Percentage_diff'] = ((df_copy['Actual_value'] - df_copy['Buying_value']) / df_copy['Buying_value']) * 100
    return df_copy

def grouped_df_by_date(df) :
    grouped = df.copy()
    grouped = grouped.groupby('Date').agg({
        'Buying_value': 'sum',
        'Actual_value': 'sum'
    }).reset_index()
    grouped['Variation_%'] = ((grouped['Actual_value'] - grouped['Buying_value']) / grouped['Buying_value']) * 100
    grouped.loc[:, 'Value_diff'] = (grouped['Actual_value'] - grouped['Buying_value'])
    return grouped

def create_today_df(df):
    df_copy = df.copy()


    return df_copy