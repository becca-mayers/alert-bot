# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 10:57:45 2021

@author: beccamayers
"""

from dateutil.relativedelta import relativedelta
from data_generator import generate_data
from datetime import datetime
import pandas as pd
import pathlib

def alert_variables():
    
    base_folder_path = str(pathlib.Path(__file__).parent.absolute())
    
    templates_path = base_folder_path + '\\templates\\'
    vis_path = base_folder_path + '/visualizations/'
    css_file = base_folder_path + '/templates/material-dashboard.css'

    los_df, obs_df, tiers, facilities, tiered_locations = generate_data()
    
    los_df['LOS Ratio'] = round(los_df['LOS']/los_df['GMLOS'],3)
    obs_df['Observation Rate'] = round((obs_df['Obs_Cases']/(obs_df['Obs_Cases'] + obs_df['Obs_Rate_Inp']))*100) 

    metrics = ['LOS', 'GMLOS', 'OppDays', 'LOS Ratio','Obs_Cases', 'Obs_Hours_48', 'Obs_Rate_Inp', 'Observation Rate']
    final_metrics = ['OppDays', 'LOS Ratio', 'Obs_Hours_48', 'Observation Rate']

    
    metric_renamer = {'OppDays': 'Opportunity Days', 
                      'Obs_Hours': 'Observation Hours', 
                      'Obs_Hours_48': 'Observation Cases > 48 Hours', 
                      'Obs_Rate_Inp': 'Inpatient Observation Rates', 
                      'ObservationRate': 'Observation Rate'}
    
    round_these = ['Value', 
                   'Month_to_Month_Variance', 
                   'FYTD', 
                   'FYTD_Variance', 
                   'months_trend']
    
    #%%date handling
    most_recent_date = max(los_df['Reporting Month'])
    three_months_ago = most_recent_date + relativedelta(months=-3)
    two_months_ago = most_recent_date + relativedelta(months=-2)
    last_month = most_recent_date + relativedelta(months=-1)
    next_month = most_recent_date + relativedelta(months=+1)
    
    #make date strings for matching purposes
    current_readable = most_recent_date.strftime('%b %y')

    #filter for most recent three or four months
    three_month_filter = [two_months_ago, last_month, most_recent_date]  
    four_month_filter = [three_months_ago, two_months_ago, last_month, most_recent_date] 

    #%%calculations
    data = los_df.merge(obs_df, on = ['Facility','Reporting Month', 'Tiers', 'Fiscal Year'])
    data['MonthYear'] = data['Reporting Month'].dt.strftime('%b %y')
    
    julys = data[['Reporting Month']]
    julys['Month'] = julys['Reporting Month'].dt.strftime('%B')
    julys['Year'] = julys['Reporting Month'].dt.year
    julys = julys.loc[julys['Month'] == 'July']
    july_year_max = max(julys['Year'])
    first_date = datetime(july_year_max,7,1)
    prior_first_date = datetime(july_year_max-1,7,1)
     
    fytd_dates = pd.date_range(start=first_date, end=next_month, freq='M')
    fytd_list = fytd_dates.tolist()
    
    last_fytd_dates = pd.date_range(start=prior_first_date, end=first_date, freq='M')
    last_fytd_list = last_fytd_dates.tolist()

    #colors
    red_hex_shades = ['background-color:#e60250','background-color:#e63674','background-color:#e85185', 'background-color:#e86b96', 'background-color:#e68eac', 'background-color:#e8cad5', 'background-color:#ede8ea', 'background-color:#ffffff']

    version = 'top 2'
    option = 3
    version_slicer = 2
    
    headers = ['Facility', 
               'Metric', 
               'Month', 
               'Month Variance', 
               'FYTD', 
               'FYTD Variance', 
               '3-Month Trend',
               'Trend Plot']

    #rollings
    rolling_dict = {}
    rolling_dict[3] = {}
    rolling_dict[3]['current_month'] = most_recent_date
    rolling_dict[3]['earliest_month'] = two_months_ago
    rolling_dict[3]['trend_range'] = '3-Month Trend'
    rolling_dict[3]['xtnd_trend_no'] = 4
    rolling_dict[3]['trend_number'] = 3
    rolling_dict[3]['extended_filter'] = four_month_filter
    rolling_dict[3]['filter'] = three_month_filter

    return (metrics,
            final_metrics,
            current_readable,
            last_month,
            four_month_filter,
            three_month_filter,
            fytd_list,
            last_fytd_list,
            metric_renamer,
            round_these,
            data,
            red_hex_shades,
            version,
            option,
            templates_path,
            vis_path,
            version_slicer,
            rolling_dict,
            css_file,
            facilities,
            headers)

