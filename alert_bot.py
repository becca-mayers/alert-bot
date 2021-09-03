  
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 15:23:03 2021

@author: beccamayers
"""

from jinja2 import Environment as JinjaEnvironment
from jinja2 import FileSystemLoader
from alert_variables import alert_variables
import plotly.express as px
from colour import Color
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def get_alert(): 
    
    (metrics,
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
    headers) = alert_variables() 
    
    extended_filter = rolling_dict[option]['extended_filter']
    exact_filter = rolling_dict[option]['filter']
    earliest_month = rolling_dict[option]['earliest_month'] 
    current_month = rolling_dict[option]['current_month'] 
    trend_label = rolling_dict[option]['trend_range'] 
    roll_integer = rolling_dict[option]['xtnd_trend_no']
           
    metric_holder = []
    for mc in metrics:
        tempdf = data[['Facility', 'Reporting Month', 'MonthYear']]
        tempdf.loc[:,'Metric'] = mc
        tempdf.loc[:,'Value'] = data[mc]
        metric_holder.append(tempdf)   
    reformatted_df = pd.concat(metric_holder)
    
    calculated_values = []
    for facility in facilities:
        for metric in final_metrics:
            fig_title = facility + ' ' + metric
            
            if metric == 'LOS Ratio':
                
                #Monthly
                tempdff = reformatted_df.loc[(reformatted_df['Facility'] == facility) & (reformatted_df['Metric'] == metric)]
                most_recent_value = tempdff.loc[tempdff['MonthYear'] == current_readable]['Value'].reset_index(drop=True)[0]
                last_month_value = tempdff.loc[tempdff['Reporting Month'] == last_month]['Value'].reset_index(drop=True)[0]
                month_series = pd.Series([last_month_value, most_recent_value])
                month_var = month_series.pct_change()[1]
                month_var = round(month_var*100)
                if month_var == np.inf:
                    month_var = 0.00
                tempdff['Month_to_Month_Variance'] = f'{month_var:,}'
                
                #FYTD
                tempdfytd = reformatted_df.loc[(reformatted_df['Facility'] == facility) & (reformatted_df['Reporting Month'].isin(fytd_list))]
                temp_los = tempdfytd.loc[tempdfytd['Metric'] == 'LOS']
                temp_gmlos = tempdfytd.loc[tempdfytd['Metric'] == 'GMLOS']
                current_fytd = temp_los['Value'].sum()/temp_gmlos['Value'].sum()
                current_fytd = round(current_fytd)
                tempdff['FYTD'] = f'{current_fytd:,}'
                
                #Prior FYTD
                tempdfx = reformatted_df.loc[(reformatted_df['Facility'] == facility) & (reformatted_df['Reporting Month'].isin(last_fytd_list))]
                temp_los = tempdfx.loc[tempdfx['Metric'] == 'LOS']
                temp_gmlos = tempdfx.loc[tempdfx['Metric'] == 'GMLOS']
                prior_fytd = temp_los['Value'].sum()/temp_gmlos['Value'].sum()
                prior_fytd = round(prior_fytd)
                tempdff['Prior FYTD'] = f'{prior_fytd:,}'
    
                #FYTD Variance
                fytd_series = pd.Series([prior_fytd, current_fytd])
                fytd_var = fytd_series.pct_change()[1]
                fytd_var = round(fytd_var*100)
                if fytd_var == np.inf:
                    fytd_var = 0.00
                tempdff['FYTD_Variance'] = f'{fytd_var:,}'
                
                #Rolling, window=1
                temp_frame = reformatted_df.loc[(reformatted_df['Facility'] == facility) & (reformatted_df['Metric'] == metric) & (reformatted_df['Reporting Month'].isin(extended_filter))]
                temp_frame_set = temp_frame.set_index(['Facility', 'Reporting Month', 'MonthYear', 'Metric'])
                temp = temp_frame_set.rolling(roll_integer, min_periods=1).mean()
                temp = temp.reset_index()
                most_recent_value = temp.loc[temp['Reporting Month'] == current_month]['Value'].reset_index(drop=True)[0]
                earliest_value = temp.loc[temp['Reporting Month'] == earliest_month]['Value'].reset_index(drop=True)[0]
                
                rolling_series = pd.Series([earliest_value, most_recent_value])
                rolling_var = rolling_series.pct_change()[1]
                rolling_var = (most_recent_value-earliest_value)/earliest_value
                rolling_var = round(rolling_var*100)
                if rolling_var == np.inf:
                    rolling_var = 0.00
                tempdff[trend_label] = f'{rolling_var:,}'
                
                fig_df = temp.loc[temp['Reporting Month'].isin(exact_filter)]
                fig_df = fig_df.rename(columns={'Value':'Rolling Sum'})
              
                fig = px.line(fig_df, x = 'MonthYear', y = 'Rolling Sum')
                fig.update_layout({
                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                    })
                fig.update_yaxes(visible=False, fixedrange=True)
                fig.update_xaxes(visible=False, fixedrange=True)
                fig.update_traces(line_color='#e63674')
                fig_save = vis_path + fig_title + '.svg'
                fig.write_image(fig_save)
                tempdff['plotted'] = fig_save
                calculated_values.append(tempdff)
            
            elif metric == 'Observation Rate':
                
                #Monthly
                tempdff = reformatted_df.loc[(reformatted_df['Facility'] == facility) & (reformatted_df['Metric'] == metric)]
                most_recent_value = tempdff.loc[tempdff['MonthYear'] == current_readable]['Value'].reset_index(drop=True)[0]
                last_month_value = tempdff.loc[tempdff['Reporting Month'] == last_month]['Value'].reset_index(drop=True)[0]
                month_series = pd.Series([last_month_value, most_recent_value])
                month_var = month_series.pct_change()[1]
                month_var = round(month_var*100)
                if month_var == np.inf:
                    month_var = 0.00
                #tempdff['Value'] = 
                tempdff['Month_to_Month_Variance'] = f'{month_var:,}' + '%'
                tempdff['Value'] = tempdff['Value'].astype(str) + '%'
                #FYTD
                tempdfytd = reformatted_df.loc[(reformatted_df['Facility'] == facility) & (reformatted_df['Reporting Month'].isin(fytd_list))]
                temp_obs_cases = tempdfytd.loc[tempdfytd['Metric'] == 'Obs_Cases']
             
                temp_obs_rate_inp = tempdfytd.loc[tempdfytd['Metric'] == 'Obs_Rate_Inp']
                current_fytd = temp_obs_cases['Value'].sum()/(temp_obs_rate_inp['Value'].sum()+temp_obs_cases['Value'].sum())
                current_fytd = round(current_fytd*100)
                tempdff['FYTD'] = f'{current_fytd:,}' + '%'
                
                #Prior FYTD
                tempdfx = reformatted_df.loc[(reformatted_df['Facility'] == facility) & (reformatted_df['Reporting Month'].isin(last_fytd_list))]
                prior_cases = tempdfx.loc[tempdfx['Metric'] == 'Obs_Cases']
                prior_inp = tempdfx.loc[tempdfx['Metric'] == 'Obs_Rate_Inp']
                prior_fytd = prior_cases['Value'].sum()/(prior_inp['Value'].sum()+prior_cases['Value'].sum())
                prior_fytd = round(prior_fytd*100)
                tempdff['Prior FYTD'] = f'{prior_fytd:,}' + '%'
                
                #FYTD Variance
                fytd_series = pd.Series([prior_fytd, current_fytd])
                fytd_var = fytd_series.pct_change()[1]
                fytd_var = round(fytd_var*100)
                if fytd_var == np.inf:
                    fytd_var = 0.00
                tempdff['FYTD_Variance'] = f'{fytd_var:,}' + '%'
                    
                #rolling, window=1
                temp_frame = reformatted_df.loc[(reformatted_df['Facility'] == facility) & (reformatted_df['Metric'] == metric) & (reformatted_df['Reporting Month'].isin(extended_filter))]
                temp_frame_set = temp_frame.set_index(['Facility', 'Reporting Month', 'MonthYear', 'Metric'])
                temp = temp_frame_set.rolling(roll_integer, min_periods=1).mean()
                temp = temp.reset_index()
                most_recent_value = temp.loc[temp['Reporting Month'] == current_month]['Value'].reset_index(drop=True)[0]
                earliest_value = temp.loc[temp['Reporting Month'] == earliest_month]['Value'].reset_index(drop=True)[0]
    
                rolling_series = pd.Series([earliest_value, most_recent_value])
                rolling_var = rolling_series.pct_change()[1]
                rolling_var = round(rolling_var*100)
                if rolling_var == np.inf:
                    rolling_var = 0.00
                tempdff[trend_label] = f'{rolling_var:,}' + '%'
    
                fig_df = temp.loc[temp['Reporting Month'].isin(exact_filter)]
                fig_df = fig_df.rename(columns={'Value':'Rolling Sum'})
                
                fig = px.line(fig_df, x = 'MonthYear', y = 'Rolling Sum')
                fig.update_layout({
                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                    })
                fig.update_yaxes(visible=False, fixedrange=True)
                fig.update_xaxes(visible=False, fixedrange=True)
                fig.update_traces(line_color='#e63674')
                fig_save = vis_path + fig_title + '.svg'
                fig.write_image(fig_save)
                tempdff['plotted'] = fig_save
                calculated_values.append(tempdff)
            
            else:
                
                #Monthly
                tempdff = reformatted_df.loc[(reformatted_df['Facility'] == facility) & (reformatted_df['Metric'] == metric)]
                most_recent_value = tempdff.loc[tempdff['MonthYear'] == current_readable]['Value'].reset_index(drop=True)[0]
                last_month_value = tempdff.loc[tempdff['Reporting Month'] == last_month]['Value'].reset_index(drop=True)[0]
                month_series = pd.Series([last_month_value, most_recent_value])
                month_var = month_series.pct_change()[1]
                month_var = round(month_var*100)
                tempdff['Month_to_Month_Variance'] = f'{month_var:,}'
                
                #FYTD
                tempdfff = tempdff.loc[tempdff['Reporting Month'].isin(fytd_list)]
                current_fytd = tempdfff['Value'].sum()
                current_fytd = int(current_fytd)
                tempdff['FYTD'] = f'{current_fytd:,}'
        
                #Prior FYTD
                tempdfx = tempdff.loc[tempdff['Reporting Month'].isin(last_fytd_list)]
                prior_fytd = tempdfx['Value'].sum()
                prior_fytd = int(prior_fytd)
                tempdff['Prior FYTD'] = f'{prior_fytd:,}'
                
                #FYTD Variance
                fytd_series = pd.Series([prior_fytd, current_fytd])
                fytd_var = fytd_series.pct_change()[1]
                fytd_var = round(fytd_var*100)
                tempdff['FYTD_Variance'] = f'{fytd_var:,}'
                
                #Rolling, window=1
                temp_frame = reformatted_df.loc[(reformatted_df['Facility'] == facility) & (reformatted_df['Metric'] == metric) & (reformatted_df['Reporting Month'].isin(extended_filter))]
                temp_frame_set = temp_frame.set_index(['Facility', 'Reporting Month', 'MonthYear', 'Metric'])
                temp = temp_frame_set.rolling(roll_integer, min_periods=1).mean()
                temp = temp.reset_index()
                most_recent_value = temp.loc[temp['Reporting Month'] == current_month]['Value'].reset_index(drop=True)[0]
                earliest_value = temp.loc[temp['Reporting Month'] == earliest_month]['Value'].reset_index(drop=True)[0]
                
                rolling_series = pd.Series([earliest_value, most_recent_value])
                rolling_var = rolling_series.pct_change()[1]
                rolling_var = round(rolling_var*100)
                tempdff[trend_label] = f'{rolling_var:,}'
    
                fig_df = temp.loc[temp['Reporting Month'].isin(exact_filter)]
                fig_df = fig_df.rename(columns={'Value':'Rolling Sum'})
               
                fig = px.line(fig_df, x = 'MonthYear', y = 'Rolling Sum')
                fig.update_layout({
                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                    })
                fig.update_yaxes(visible=False, fixedrange=True)
                fig.update_xaxes(visible=False, fixedrange=True)
                fig.update_traces(line_color='#e63674')
                fig_save = vis_path + fig_title + '.svg'
                fig.write_image(fig_save)
                tempdff['plotted'] = fig_save
                calculated_values.append(tempdff)
     
    dfff = pd.concat(calculated_values)
    dfff = dfff.replace(np.inf, 0.000)
    
    #Clean up the data
    dfff = dfff.replace({'Metric': metric_renamer})
    dff = dfff.loc[dfff['MonthYear'] == current_readable]
    dff = dff.rename(columns={trend_label: 'months_trend'})
    
    three_df = dfff.loc[dfff['Reporting Month'].isin(three_month_filter)]
    three_df['type'] = 'monthly value'
    
    #%%Find the discerning variances
    monthly_dff = dff.sort_values(by='Month_to_Month_Variance', ascending=False)[:version_slicer]
    monthly_dff['alert'] = 'Month Variance'
    
    fytd_dff = dff.sort_values(by='FYTD_Variance', ascending=False)[:version_slicer]
    fytd_dff['alert'] = 'FYTD Variance'
    
    trend_dff = dff.sort_values(by='months_trend', ascending=False)[:version_slicer]
    trend_dff['alert'] = trend_label
    
    dff_quant = pd.concat([monthly_dff, fytd_dff, trend_dff])
    dff_quant = dff_quant.reset_index().drop('index', axis=1)
    
    #%% watchlist facility deets
    
    watchlist_facilities = dff_quant['Facility'].drop_duplicates().tolist()
    facility_length = len(watchlist_facilities)
    
    watchlist_dict = {}
    for f in range(0, facility_length):
    
        facility = watchlist_facilities[f]
    
        mo_alert = dff_quant.loc[(dff_quant['Facility'] == facility) & (dff_quant['alert'] == 'Month Variance')]['Metric'].reset_index(drop=True).tolist()
        fytd_alert = dff_quant.loc[(dff_quant['Facility'] == facility) & (dff_quant['alert'] == 'FYTD Variance')]['Metric'].reset_index(drop=True).tolist()
        trend_alert = dff_quant.loc[(dff_quant['Facility'] == facility) & (dff_quant['alert'] == trend_label)]['Metric'].reset_index(drop=True).tolist()
       
        fac_df = data.loc[(data['Facility'] == facility) & (data['MonthYear'] == current_readable)]
        fytd_df = data.loc[(data['Facility'] == facility) & (data['Reporting Month'].isin(fytd_list))]
        trend_df = data.loc[(data['Facility'] == facility) & (data['Reporting Month'].isin(extended_filter))]
    
        ''' Opp Days '''
        opp_days = int(fac_df['OppDays'].sum())
        fytd_opp_days = int(fytd_df['OppDays'].sum())
    
        opp_trend_df = trend_df[['Facility', 'Reporting Month', 'MonthYear', 'OppDays']].set_index(['Facility', 'Reporting Month', 'MonthYear'])
        trend = opp_trend_df.rolling(roll_integer, min_periods=1).mean()
        trend = trend.reset_index()
        most_recent_value = trend.loc[trend['Reporting Month'] == current_month]['OppDays'].sum() #reset_index(drop=True)[0]
        earliest_value = trend.loc[trend['Reporting Month'] == earliest_month]['OppDays'].sum() #['Value'].reset_index(drop=True)[0]
        
        trend_series = pd.Series([earliest_value, most_recent_value])
        trend_opp_days = trend_series.pct_change()[1]
        trend_opp_days = round(trend_opp_days*100)
        
        opp_days_dict = {'metric':'<b> Opportunity <br> Days </b>', 
                         'monthly_value': f'{opp_days:,}', #'<b>' + str(opp_days) + '</b>' 
                         'fytd_value': f'{fytd_opp_days:,}', #'<b>' + str(fytd_opp_days) + '</b>'
                         'trend_value': f'{trend_opp_days:,}',
                         'trend_type': trend_label} #'<b>' + str(trend_opp_days) + '</b>'
        
        if 'Opportunity Days' in mo_alert:
            opp_days_dict['monthly_class'] = 'text-rose strong'
        else:
            opp_days_dict['monthly_class'] = 'text-secondary'
        
        if 'Opportunity Days' in fytd_alert:
            opp_days_dict['fytd_class'] = 'text-rose strong'
        else:
            opp_days_dict['fytd_class'] = 'text-secondary'
      
        if 'Opportunity Days' in trend_alert:
            opp_days_dict['trend_class'] = 'text-rose strong'
        else:
            opp_days_dict['trend_class'] = 'text-secondary'
    
        ''' Cases > 48 H '''
        cases_48h = int(fac_df['Obs_Hours_48'].sum())
        fytd_cases_48h = int(fytd_df['Obs_Hours_48'].sum())
        
        cases48_trend_df = trend_df[['Facility', 'Reporting Month', 'MonthYear', 'Obs_Hours_48']].set_index(['Facility', 'Reporting Month', 'MonthYear'])
        trend = cases48_trend_df.rolling(roll_integer, min_periods=1).mean()
        trend = trend.reset_index()
        
        most_recent_value = trend.loc[trend['Reporting Month'] == current_month]['Obs_Hours_48'].sum() #reset_index(drop=True)[0]
        earliest_value = trend.loc[trend['Reporting Month'] == earliest_month]['Obs_Hours_48'].sum() #['Value'].reset_index(drop=True)[0]
        cases_series = pd.Series([earliest_value, most_recent_value])
        trend_cases_48h = cases_series.pct_change()[1]
        trend_cases_48h = round(trend_cases_48h*100)
        if trend_cases_48h == np.inf:
            trend_cases_48h = 0
        else:
            trend_cases_48h = int(trend_cases_48h)
        
        cases48_dict = {'metric':'<b> Observation <br> Cases > 48H </b>', 
                        'monthly_value': f'{cases_48h:,}', #'<b>' + str(cases_48h) + '</b>'
                        'fytd_value': f'{fytd_cases_48h:,}', #'<b>' + str(fytd_cases_48h) + '</b>'
                        'trend_value': f'{trend_cases_48h:,}',
                        'trend_type': trend_label} #'<b>' + str(int(trend_cases_48h)) + '</b>'
        
        if 'Observation Cases > 48 Hours' in mo_alert:
            cases48_dict['monthly_class'] = 'text-rose strong'
        else:
            cases48_dict['monthly_class'] = 'text-secondary'
            
        if 'Observation Cases > 48 Hours' in fytd_alert:
            cases48_dict['fytd_class'] = 'text-rose strong'
        else:
            cases48_dict['fytd_class'] = 'text-secondary'
        
        if 'Observation Cases > 48 Hours' in trend_alert:
            cases48_dict['trend_class'] = 'text-rose strong'
        else:
            cases48_dict['trend_class'] = 'text-secondary'
    
        '''Obs Rate'''
        obs_cases = fac_df['Obs_Cases'].sum()
        obs_rate_inp = fac_df['Obs_Rate_Inp'].sum()
        obs_rate = obs_cases/(obs_rate_inp+obs_cases)
        obs_rate = round(obs_rate*100)
        obs_rate_dict = {'metric':'<b> Observation <br> Rate </b>', 
                         'monthly_value': f'{obs_rate:,}' + '%'} 
        
        obs_cases = fytd_df['Obs_Cases'].sum()
        obs_rate_inp = fytd_df['Obs_Rate_Inp'].sum()
        obs_rate = obs_cases/(obs_rate_inp+obs_cases)
        obs_rate = round(obs_rate*100)
        obs_rate_dict['fytd_value'] = f'{obs_rate:,}' + '%'
        
        obs_rate_trend_df = trend_df[['Facility', 'Reporting Month', 'MonthYear', 'Obs_Cases', 'Obs_Rate_Inp']].set_index(['Facility', 'Reporting Month', 'MonthYear'])
        obs_cases_trend = obs_rate_trend_df.rolling(4, min_periods=1).mean()
        obs_cases_trend = obs_cases_trend.reset_index()
        
        most_recent_cases_value = obs_cases_trend.loc[obs_cases_trend['Reporting Month'] == current_month]['Obs_Cases'].sum() #reset_index(drop=True)[0]
        most_recent_inp_value = obs_cases_trend.loc[obs_cases_trend['Reporting Month'] == current_month]['Obs_Rate_Inp'].sum() #reset_index(drop=True)[0]
        most_recent_obs_rate = most_recent_cases_value/(most_recent_inp_value+most_recent_cases_value)
        
        two_mo_ago_cases_value = obs_cases_trend.loc[obs_cases_trend['Reporting Month'] == earliest_month]['Obs_Cases'].sum() #['Value'].reset_index(drop=True)[0]
        two_mo_ago_inp_value = obs_cases_trend.loc[obs_cases_trend['Reporting Month'] == earliest_month]['Obs_Rate_Inp'].sum() #['Value'].reset_index(drop=True)[0]
        two_mo_ago_obs_rate = two_mo_ago_cases_value/(two_mo_ago_inp_value+two_mo_ago_cases_value)
        
        obs_series = pd.Series([two_mo_ago_obs_rate, most_recent_obs_rate])
        trend_obs_rate = obs_series.pct_change()[1]
        trend_obs_rate = round(trend_obs_rate*100)
        obs_rate_dict['trend_value'] = f'{trend_obs_rate:,}' + '%'
        obs_rate_dict['trend_type'] = trend_label
        
        if 'Observation Rate' in mo_alert:
            obs_rate_dict['monthly_class'] = 'text-rose strong'
        else:
            obs_rate_dict['monthly_class'] = 'text-secondary'
    
        if 'Observation Rate' in fytd_alert:
            obs_rate_dict['fytd_class'] = 'text-rose strong'
        else:
            obs_rate_dict['fytd_class'] = 'text-secondary'
            
        if 'Observation Rate' in trend_alert:
            obs_rate_dict['trend_class'] = 'text-rose strong'
        else:
            obs_rate_dict['trend_class'] = 'text-secondary'
    
        '''LOS Ratio'''
        los = fac_df['LOS'].sum()
        gmlos = fac_df['GMLOS'].sum()
        los_ratio = los/gmlos
        los_ratio = round(los_ratio)
        los_dict = {'metric':'<b> LOS Ratio </b>', 
                    'monthly_value': f'{los_ratio:,}'} #'<b>' + str(los_ratio) + '</b>'
        
        los = fytd_df['LOS'].sum()
        gmlos = fytd_df['GMLOS'].sum()
        los_ratio = los/gmlos
        los_ratio = round(los_ratio)
        los_dict['fytd_value'] = f'{los_ratio:,}'
        
        los_trend_df = trend_df[['Facility', 'Reporting Month', 'MonthYear', 'LOS', 'GMLOS']].set_index(['Facility', 'Reporting Month', 'MonthYear'])
        los_trend = los_trend_df.rolling(roll_integer, min_periods=1).mean()
        los_trend = los_trend.reset_index()
        
        most_recent_los_value = los_trend.loc[los_trend['Reporting Month'] == current_month]['LOS'].sum() #reset_index(drop=True)[0]
        most_recent_gmlos_value = los_trend.loc[los_trend['Reporting Month'] == current_month]['GMLOS'].sum() #reset_index(drop=True)[0]
        most_recent_los = most_recent_los_value/most_recent_gmlos_value
        
        two_mo_ago_los_value = los_trend.loc[los_trend['Reporting Month'] == earliest_month]['LOS'].sum() #reset_index(drop=True)[0]
        two_mo_ago_gmlos_value = los_trend.loc[los_trend['Reporting Month'] == earliest_month]['GMLOS'].sum() #reset_index(drop=True)[0]
        two_mo_ago_los = two_mo_ago_los_value/two_mo_ago_gmlos_value
        
        los_series = pd.Series([two_mo_ago_los, most_recent_los])
        trend_los = los_series.pct_change()[1]
        trend_los = round(trend_los*100)
        los_dict['trend_value'] = f'{trend_los:,}'
        los_dict['trend_type'] = trend_label
        
        if 'LOS Ratio' in mo_alert:
            los_dict['monthly_class'] = 'text-rose strong'
        else:
            los_dict['monthly_class'] = 'text-secondary'   
      
        if 'LOS Ratio' in fytd_alert:
            los_dict['fytd_class'] = 'text-rose strong'
        else:
            los_dict['fytd_class'] = 'text-secondary' 
     
        if 'LOS Ratio' in trend_alert:
            los_dict['trend_class'] = 'text-rose strong'
        else:
            los_dict['trend_class'] = 'text-secondary' 
    
            
        watchlist_dict[f] = {}
        watchlist_dict[f] = [facility, los_dict, opp_days_dict, obs_rate_dict, cases48_dict]
    
    #%% Make the color map
    
    if len(watchlist_facilities) < 7:
        #go with the pre-set color shade list
        color_df = pd.DataFrame(red_hex_shades, columns=['colors'])
    else:
        #generate a color shade list
        rose = Color('#e60250')
        white = Color('#ffffff')
        red_hex_shade_list = list(rose.range_to(white, len(watchlist_facilities)))
        red_hex_shades = []
        for i in red_hex_shade_list:
            red_hex_shades.append('bgcolor:' + red_hex_shade_list[i].hex_l)
        color_df = pd.DataFrame(red_hex_shades, columns=['colors'])
    
    color_df['colors'] = color_df['colors'] + "; color:#ffffff; text-align:center; font-size:14px; font-weight:bolder;"
    
    dff_columns = dff_quant.columns.values
    monthly_variance = dff_quant.loc[dff_quant['alert'] == 'Month Variance']
    monthly_variance = monthly_variance.sort_values(by='Month_to_Month_Variance', ascending=False)
    monthly_variance = monthly_variance.reset_index().drop('index', axis=1)
    monthly_variance = monthly_variance.merge(color_df, left_index=True, right_index=True, how='left')
    monthly_variance['Month_to_Month_Variance'] = monthly_variance['colors']
    monthly_variance = monthly_variance.drop('colors', axis=1)
    monthly_columns = [x for x in dff_columns if x != 'Month_to_Month_Variance']
    for c in monthly_columns:
        monthly_variance[c] = "background-color:#ffffff; color:#6c757d; text-align:center; font-size:14px;"
    
    fytd_variance = dff_quant.loc[dff_quant['alert'] == 'FYTD Variance']
    fytd_variance = fytd_variance.sort_values(by='FYTD_Variance', ascending=False)
    fytd_variance = fytd_variance.reset_index().drop('index', axis=1)
    fytd_variance = fytd_variance.merge(color_df, left_index=True, right_index=True, how='left')
    fytd_variance['FYTD_Variance'] = fytd_variance['colors']
    fytd_variance = fytd_variance.drop('colors', axis=1)
    fytd_columns = [x for x in dff_columns if x != 'FYTD_Variance']
    for c in fytd_columns:
        fytd_variance[c] = "background-color:#ffffff; color:#6c757d; text-align:center; font-size:14px;"
    
    three_month = dff_quant.loc[dff_quant['alert'] == trend_label]
    three_month = three_month.sort_values(by='months_trend', ascending=False)
    three_month = three_month.reset_index().drop('index', axis=1)
    three_month = three_month.merge(color_df, left_index=True, right_index=True, how='left')
    three_month['months_trend'] = three_month['colors']
    three_month = three_month.drop('colors', axis=1)
    three_columns = [x for x in dff_columns if x != 'months_trend']
    for c in three_columns:
        three_month[c] = "background-color:#ffffff; color:#6c757d; text-align:center; font-size:14px;"
            
    color_map = pd.concat([monthly_variance, fytd_variance, three_month])
    dff_quant = dff_quant.drop('alert', axis=1)
    
    #wrap metric labels
    dff_quant.loc[dff_quant['Metric'] == 'Observation Cases > 48 Hours', 'Metric'] = 'Observation Cases <br> > 48 Hours'
    dff_quant.loc[dff_quant['Metric'] == 'Observation Rate', 'Metric'] = 'Observation <br> Rate'
    dff_quant.loc[dff_quant['Metric'] == 'Opportunity Days', 'Metric'] = 'Opportunity Days'
    dff_quant.loc[dff_quant['Metric'] == 'LOS Ratio', 'Metric'] = 'LOS <br> Ratio'
    
    
    #%%Templating & rendering
    
    data_dict = dff_quant.to_dict('records')
    color_dict = color_map.to_dict('records')
    final_dict = zip(data_dict, color_dict)   
    
    env = JinjaEnvironment(loader=FileSystemLoader('templates/'))
    
    template = env.get_template('alert_template.html')
    html = template.render(version = version,
                            current_readable = current_readable,
                            trend_label = trend_label,
                            headers = headers,
                            data = final_dict,
                            watchlist_data = watchlist_dict,
                            facilities = watchlist_facilities,
                            css_file = css_file,
                            icon_integers = ['', 'one', 'two', '3', '4'])
                            #icon_path = icon_path)
    #return html
    with open("html/alert.html", "w") as h:
        h.write(html)
        h.close() 
            
