#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 29 13:51:27 2021

@author: beccamayers
"""

from datetime import datetime
import pandas as pd
import numpy as np
import random

def generate_data():
    
    #list of military alphabet values
    locations = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet', 'Kilo', 'Lima', 
                 'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Rome', 'Sierra', 'Tango', 'Uniform', 'Victor', 
                 'Whiskey', 'Xray', 'Yankee', 'Zulu']
    
    a_tier = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel']
    b_tier = ['India', 'Juliet', 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa', 'Quebec']
    c_tier = ['Rome', 'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'Xray', 'Yankee', 'Zulu']
    
    tiers = {'A': a_tier,
             'B': b_tier,
             'C': c_tier}
    
    tiered_locations = list(np.append(b_tier, c_tier))
    
    #generate date range
    date_range = list(pd.date_range(datetime(2019, 7, 1), datetime.today(), freq='M'))
    date_len = len(date_range)
    
    #generate fiscal date range lists
    last_last_fiscal_range = list(pd.date_range(datetime(2019,7,1), datetime(2020,6,30), freq='M'))
    last_fiscal_range = list(pd.date_range(datetime(2020,7,1), datetime(2021,6,30), freq='M'))
    this_fiscal_range = list(pd.date_range(datetime(2021,7,1), datetime.today(), freq='M'))
    
    base = []
    for location in locations:
        #generate random values for each metric
        los_values = [random.uniform(0, 11100) for _ in range(date_len)]
        gmlos_values = [random.uniform(0, 10000) for _ in range(date_len)]
        oppday_values = [random.randint(-128, 3750) for _ in range(date_len)] 
        cases_values = [random.uniform(0, 800) for _ in range(date_len)]
        cases48_values = [random.randint(0, 195) for _ in range(date_len)] 
        rate_inp_values = [random.uniform(0, 2800) for _ in range(date_len)] 
        
        #generate dataframe
        temp_df = pd.DataFrame({'Facility': location, 
                                'Reporting Month': date_range,
                                'LOS': los_values,
                                'GMLOS': gmlos_values,
                                'OppDays': oppday_values,
                                'Obs_Cases': cases_values,
                                'Obs_Hours_48': cases48_values,
                                'Obs_Rate_Inp': rate_inp_values})
        
        #set fiscal year labels
        temp_df.loc[temp_df['Reporting Month'].isin(last_last_fiscal_range), 'Fiscal Year'] = 'FY2020'
        temp_df.loc[temp_df['Reporting Month'].isin(last_fiscal_range), 'Fiscal Year'] = 'FY2021'
        temp_df.loc[temp_df['Reporting Month'].isin(this_fiscal_range), 'Fiscal Year'] = 'FY2022'
        
        base.append(temp_df)
    
    base_df = pd.concat(base)
    
    #assign tiers
    for key, value in tiers.items():
        base_df.loc[base_df['Facility'].isin(value), 'Tiers'] = key
        
    los_cols = ['LOS', 'GMLOS', 'OppDays', 'Facility', 'Fiscal Year', 'Reporting Month', 'Tiers']
    obs_cols = ['Obs_Cases', 'Obs_Hours_48', 'Obs_Rate_Inp', 'Facility', 'Fiscal Year', 'Reporting Month', 'Tiers']
    
    los_df = base_df[los_cols]
    obs_df = base_df[obs_cols]
    
    return los_df, obs_df, tiers, locations, tiered_locations
    
