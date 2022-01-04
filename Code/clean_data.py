import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns
import scipy.stats as stats
import datetime

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr


def clean_data(df,crit_data,crit_label,crit_name, crit_number,date_name, index_qc):
    
    'input is the merged data tables for either rainfall / discharge. output is qcd dataframe based on climate criterias used for plotting'
    '''
    Splicing Historical Data Raw Files to extract the correct columns
    
    Parameters
    ---------
      
      df
        Merged dataset as monthly means
      
      crit_data
        File with Climate Types 
    
      crit_label
        River = River Discharge; Rainfall = Station Name
        
      crit_name
        Climate Type or CPE
        
      crit_number
        Categories of Climate type or CPE
        
      date_name
        Column Name of date
        
      index_qc
        Index of interest data
    
    Returns
    --------
      
      Detrended data based on criterias
    
    '''
    
    temp_df = df

    #display( temp_df )
    df_select  = crit_data[(crit_data[crit_name] == crit_number) ]
    #print(df_select)
    df_name    = list(df_select[crit_label])
    print(df_name)
    print()
    print(f'n={len(df_name)}')
    
    # Mean of the data that meet criteria
    df_mean         = pd.DataFrame( temp_df[df_name].mean(axis=1) )
    df_mean.columns = ['data_mean']
    df_mean['date'] = temp_df[date_name]
    df_mean = df_mean.dropna().reset_index( drop=True )
    
    # log scale of mean values
    df_mean['data_log']    = pd.DataFrame( (np.log10(df_mean['data_mean'])) )
    
    # scale data 
    scaler = StandardScaler()
    df_mean['data_scaled']      = scaler.fit_transform( df_mean['data_log'].values.reshape(-1,1) )

    
    # detrend mean values  using fit and substract 
    X = [i for i in range( 0, len(df_mean['data_log']) ) ]
    X = np.reshape( X, (len(X), 1) )
    y = df_mean['data_scaled'].values
    pf = PolynomialFeatures(degree=3)
    Xp = pf.fit_transform(X)
    
    model = LinearRegression()
    model.fit(X, y)
    
    md2 = LinearRegression()
    md2.fit(Xp, y)
    
    trend = model.predict(X)
    trendp = md2.predict(Xp)
    
    plt.plot(y)
    plt.plot(trendp)
    plt.ylabel('Scaled Data')
    plt.title('Polynomial Trend')
    plt.show()
    
    df_mean['data_detrend_P'] = [y[i] - trendp[i] for i in range(0, len(df_mean['data_log']) )]
    
    plt.plot(df_mean['data_detrend_P'])
    plt.ylabel('Scaled Data')
    plt.title('Residual:Trend substracted from data')
    plt.show()
    
    # REMOVE SEASONALITY 
    df_mean['data_deseason'] = df_mean['data_detrend_P'].rolling(window=6, center=True).mean()[3:-3]
    df_mean['data_deseason12'] = df_mean['data_detrend_P'].rolling(window=12, center=True).mean()[6:-6]
    
    # merge with ENSO 3.4arel index 
    df_final = df_mean.merge(index_qc, how = 'outer', on = 'date', validate = '1:1' )
    df_final = df_final.sort_values( 'date' ).reset_index(drop=True)
    df_final = df_final.dropna().reset_index(drop=True)
    df_final['month'] = df_final['date'].dt.month #getting monthly column
    
    #df_final.to_csv(f'../discharge/Data/Images/Nov18/{crit_name}_{crit_number}_{crit_label}', encoding='utf-8', index=False)
    
    return df_final