

def calculation_df(cumulative_df) :
    # Calculate the percentage difference for Actual_value vs Buying_value using .loc to avoid SettingWithCopyWarning
    cumulative_df.loc[:, 'Value_diff'] = (cumulative_df['Actual_value'] - cumulative_df['Buying_value'])
    cumulative_df.loc[:, 'Percentage_diff'] = ((cumulative_df['Actual_value'] - cumulative_df['Buying_value']) / cumulative_df['Buying_value']) * 100
    return cumulative_df