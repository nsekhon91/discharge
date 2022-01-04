import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import geopandas as gpd
import contextily as cx
import seaborn as sns
from matplotlib.pyplot import cm
from IPython.display import display

def logscaled_plot(df_final):
    
    '''
    FIGURE OF MEAN, LOG, SCALED data
    Splicing Historical Data Raw Files to extract the correct columns
    
    Parameters
    ---------
      
      df
        Excel files with Historical Discharge Data
    
    Returns
    --------
      
      Daily Historical Discharge Data Table.
    '''
    
    fig = plt.figure(figsize=(15,7))
    plt.subplot(1,3,1)
    plt.plot(df_final['date'], df_final['data_mean'], label = 'x')
    mean_mean = np.nanmean(df_final['data_mean'])
    
    plt.title(f'Mean of Subset Data,{mean_mean}')
    plt.ylabel('mm/month')
    plt.xlabel('Time')
    plt.subplot(1,3,2)
    plt.plot(df_final['date'], df_final['data_log'])
    mean_log = np.nanmean(df_final['data_log'])
    
    plt.title(f'Log of Subset Data (Mean), {mean_log}')
    plt.ylabel('Log of Data')
    plt.xlabel('Time')
    plt.subplot(1,3,3)
    plt.plot(df_final['date'], df_final['data_scaled'])
    mean_scale = np.nanmean(df_final['data_scaled'])
    
    plt.title(f'Scale of Subset Data (Log), {mean_scale}')
    plt.ylabel('Scaled Data')
    plt.xlabel('Time')
    #plt.savefig(f'../discharge/Data/Images/Dec17/raw_{criteria_name}_{criteria_number}_{crit_label}.eps', dpi = 600)
    plt.show()
    
def detrend_plot(df_final):
    '''
    FIGURE OF DETREND AND DESEASONED data
    Splicing Historical Data Raw Files to extract the correct columns
    
    Parameters
    ---------
      
      df
        Excel files with Historical Discharge Data
    
    Returns
    --------
      
      Daily Historical Discharge Data Table.
    '''
    fig = plt.figure(figsize=(15,5))
    plt.plot(df_final['date'], df_final['data_scaled'], label = 'data_scaled')
    plt.plot(df_final['date'], df_final['data_detrend_P'], label = 'data_detrend_P' )
    plt.plot(df_final['date'], df_final['data_deseason'],label = 'data_deseason_6')
    plt.plot(df_final['date'], df_final['data_deseason12'],label = 'data_deseason_12')
    plt.ylim(-3,3)
    plt.ylabel('Scaled De-Trend and De-Season Discharge (monthly)')
    plt.xlabel('Time')
    plt.legend(loc=4)
    #plt.savefig(f'../discharge/Data/Images/Dec17/detrend_{criteria_name}_{criteria_number}_{crit_label}.eps', dpi = 600)
    plt.show()
    
def data_enso_plot(df_final,crit_label,crit_name, crit_number, color_plot):
    '''
    CLEAN DATA FIGURES with ENSO
    Splicing Historical Data Raw Files to extract the correct columns
    
    Parameters
    ---------
      
      df
        Excel files with Historical Discharge Data
    
    Returns
    --------
      
      Daily Historical Discharge Data Table.
    '''
    fig, ax1 = plt.subplots(figsize=(15,7))
    ax2 = ax1.twinx()
    ax1.plot(df_final['date'],df_final['data_deseason12'],
         color=color_plot,linewidth = 1,label = f'{crit_name} {crit_number} (± 6 months) ({crit_label})') ######
    ax1.plot(df_final['date'],df_final['data_deseason'],
         color=color_plot,linestyle='dashed',linewidth = 1, alpha = 0.5,label = f'{crit_name}  {crit_number} (± 3 months) ({crit_label})') ######
    ax1.set_ylabel(f'Scaled Logged De-Trend and De-Season {crit_label} (monthly)')
    ax1.set_ylim(-3,3)
    ax1.set_xlabel('Time (CE)')
    ax2.bar(df_final['date'],df_final['ssta (°C)']
        , width = 30,color=(df_final['ssta (°C)'] > 0).map({True: 'r',False: 'b'}),alpha = 0.7)
    ax2.set_xlim(pd.Timestamp('1900-02-15'), pd.Timestamp('2019-07-01'))
    ax2.set_ylim(-3,3)
    ax2.set_ylabel('Nino 3.4 rel (°C)', color='k')
    ax2.set_xlabel('Time (CE)')
    ax1.legend(loc='best')
    #plt.savefig(f'../discharge/Data/Images/Dec5/{criteria_name}_{criteria_number}_{crit_label}.eps', dpi = 600)
    plt.show()

    
def climatology_plot(df_final,crit_name, crit_number):
    ''' 
    Climatologies as box plots
    Splicing Historical Data Raw Files to extract the correct columns
    
    Parameters
    ---------
      
      df
        Excel files with Historical Discharge Data
    
    Returns
    --------
      
      Daily Historical Discharge Data Table.
    ''' 
    month_list = [ i for i in range(1,13) ]
    print(month_list)
    month_group  = []

    for  group in df_final.groupby( df_final['month'] ):
        month_group.append( list(group[1]['data_mean']) ) 

    fig, ax = plt.subplots(figsize=(15,7), nrows = 1, ncols =2 )
    ax[0].boxplot( list(month_group), whis=True, positions=month_list, notch=1, autorange=True, showfliers=True )
    plt.xlabel('Months')
    plt.ylabel('(mm/month)')
    ax[1].boxplot( list(month_group), whis=True, positions=month_list, notch=1, autorange=True, showfliers=False )
    plt.title(f'{crit_name} {crit_number}')
    plt.ylim( [0,1200] )
    #plt.savefig(f'../discharge/Data/Images/Dec17/BoxPlot_Discharge_CT IV.eps', dpi = 600)
    plt.show()