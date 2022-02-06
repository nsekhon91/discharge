import pandas as pd
import numpy as np
import datetime
import contextily as cx
import xlrd
import os
import glob
from IPython.display import display
from functools import reduce

def prep_index_data( parent_dir, filename, title ):
    
    '''
    Load Indices Dataset and add Quality Contorl (QC) indeces
    Returns date (as datetime), QC'd indeces as a dataframe. 
    Prepare indeces dataset.
    
    Parameters
    ---------
      
      parent_dir
        directory of indeces data are stored
        
      filename
        name of file with index data
    
      title
        column name of Index data. Not used
    
    Returns
    --------
      
      Dataframe containing monthly indeces
    '''
    
    print( 'Prep Index data' )
    
    file = os.path.join( parent_dir, f'{filename}.csv'  )
    df   = pd.read_csv( file )
    
    df.columns = [ 'Year','ssta (°C)' ]
    df['time'] = pd.DataFrame( {'time': pd.date_range('1854-01-15','2021-07-15', 
                      freq='MS').strftime('%Y-%m').tolist()} )
    df['date'] = pd.to_datetime( df['time'] )
    
    return df
    
def prep_mod_rain_data( folder ):
    
    '''
    Prepare Modern rainfall data. 
    
    Parameters
    ---------
      
      folder
        Input data file name
        
      labelname
    
    Returns
    --------
      
      Dataframe containing monthly totals. Units in mm.
      Label of rain stations
    '''
    print( 'Prep Modern data' )
    
    all_files = glob.glob( folder + '/*.xlsx' )
    
    l_df_rain = []
    l_label   = ['Date']
    rain_dic  = {}

    for filename in all_files:
        
        df = pd.read_excel( filename, header = 0 )

        df['PRCP Inch'] = df['PRCP Inch'].replace(' ',np.NaN).astype(float)
        #df['PRCP Inch'] = df['PRCP Inch'].replace(0,np.NaN).astype(float)
    
        df.replace(99.99, np.nan, inplace=True)
        df['Date'] = df.apply( lambda x: datetime.datetime( int(x['YEAR']), int(x['MONTH']), int(x['DAY']) ), axis = 1 )

        df['Prpmm'] = df['PRCP Inch'] 
        
        df_mon_sum  = df.resample('MS', on = 'Date').mean().reset_index()
        df_mon_sum.replace(0.0, np.nan, inplace = True)
        df_mon_sum.replace(0.00, np.nan, inplace = True)
        df_2        = df_mon_sum.drop( ['YEAR','MONTH','DAY', 'PRCP Inch'],axis = 1 )
        l_df_rain.append(df_2)
        
        # appending year and label
        temp_label = f"mod_{filename.split('/')[-1].split('.')[0].lower()}"
        l_label.append(temp_label)

    df_final_rain = reduce( lambda left,right: pd.merge( left,right,on='Date', how='outer' ), l_df_rain )
    df_final_rain = df_final_rain.drop(['Unnamed: 4_x','Unnamed: 4_y','Unnamed: 4'],axis = 1)
    df_final_rain.columns = l_label
   
    return df_final_rain, l_label
    
    
def prep_rain_data( filename, labelname ):
    
    '''
    Prepare historical and mid(gridded century) data.
    
    Parameters
    ---------
      
      filename
        Input data file name
        
      labelname
        Data label name. hist for historical data and mid for mid
        century data. 
    
    Returns
    --------
      
      Dataframe containing monthly totals. Units in mm.
    
    '''
    print( 'Prep Historical/Mid data' )
    
    df_p      = pd.read_csv( filename )
    
    df_p      = df_p.iloc[2:].reset_index() \
                             .drop( columns='index' ) \
                             .rename(columns = {'Unnamed: 0':'year','Unnamed: 1':'month', 'name':'day'} ) \
                             .replace('?',-999) \
                             .replace(0.0,np.nan) \
                             .astype(float)
    
    df_p.replace(-999, np.nan, inplace=True)
    #df_p.replace(0.0, np.nan, inplace = True)
    df_p.columns = [ f"{labelname}_{label.lower()}" for label in df_p.columns  ]
    df_p
    
    df_p['Date'] = df_p.apply(lambda x: datetime.datetime( int(x[f'{labelname}_year']), int(x[f'{labelname}_month']), 
                                           int(x[f'{labelname}_day'])), axis = 1 )

    df_2= df_p.resample('MS', on='Date').mean().reset_index()
    df_2.replace(0.0, np.nan, inplace = True)
    
    return df_2, df_2.columns
    
def prep_his_dis_dic( df_index,df ):

    '''
    Prepare dictionary with keys and values of location, year, data, drainage values for historical  
    drainage.
    Example: Historical_Maragayap dict_keys(['data', 'drainage'])
    Example: dic_data['Historical_Maragayap']['data'][1922]
        
    Parameters
    ---------
      
      df_index
        Raw Historical Drainage Data Files  
        
      df
        Excel Data for Historical Drainage 
    
    Returns
    --------
      
      Dictionary with Historical Drainage Data 
    
    '''
    
    dic_temp = {}
    
    for i in df_index:
        # get year
        year=df['Unnamed: 12'].loc[i]
        print( f'Prep Historical Discharge Data for {year}' )
        # slicing for days
        df_temp = df.loc[i+2:i+34].dropna(axis=1, how = 'all')
        
        # dropping column
        df_temp.drop(columns=['splice'],axis=1,inplace = True)
        
        # rename columns
        df_temp.columns = df_temp.loc[i+2]
        
        # droppings unnecessary columns
        df_temp.drop([i+2,i+3], inplace = True)
        dic_temp[year] = df_temp.reset_index()
        
    return dic_temp

def prep_mod_dis_data( folder ): 
    
    '''
        
    Parameters
    ---------
      
      folder
        Directory to where Modern Discharge data (from Ibarra et al.   
        2020) is stored 
         
  
    Returns
    --------
      
      df_final    = Table with Discharge data in mm/month. 
      hess_labels = Discharge River Names as labels 
    
    '''
    
    print( 'Prep Modern Discharge Data' ) 
    
    
    directory = folder
    all_files = glob.glob(directory + '/*.xlsx')
    
    l_df = []
    l_label = ['Year']
    hess_dic = {}
    
    for filename in all_files:

        df = pd.read_excel(filename, header=0)

        # appending year and label
        temp_label = 'hess_'+df.iat[0,1].split(sep=' River')[0].lower()
        l_label.append(temp_label)
        
        # reading only needed rows and columns
        df = df.iloc[4:-1, 0:2]
        
        # changing column to date time as soon as reading it in
        df['Major River Basin'] = pd.to_datetime( df.iloc[: , 0], yearfirst = True )
        l_df.append(df)
    
    # merging based on time
    df_final = reduce(lambda left,right: pd.merge(left,right,on='Major River Basin', how = 'outer'), l_df)

    df_final.columns = l_label
    # storing hess_labels
    hess_labels      = df_final.columns

    df_final         = df_final.sort_values(by='Year')
    
    df_final.replace( 0, np.nan, inplace = True )
    df_final = df_final.reset_index( drop=True )
    
    return df_final, hess_labels


def merge_rain_data( df_a, df_b, list_a, list_b, drop_list, mlabel): 

    '''
        
    Parameters
    ---------
      
      df_a
        dataset a
        
      df_b
        dataset b which is merged
        
      list_a
        list of stations from dataset a 
        
      list_b
        list of stations from dataset b
        
      drop_list
         list of station names that will be dropped 
    
      mlabel
         label of dataset that is being merged
         
  
    Returns
    --------
      
      Table with Discharge data and labels. Units of mm/month. 
    
    '''
    for clean_name, name in zip( 
            list_a, 
            df_a.columns[4:] 
        ):

        # Outer join data A (historical) and data B (modern) data on dates
        df_b = df_b.merge( 
            df_a[['Date',name]], 
            how      = 'outer', 
            on       = 'Date',  
            validate = '1:1' 
        )

        # Sort by date
        df_b = df_b.sort_values('Date').reset_index(drop=True)  


        if clean_name in list_b:

            # Coalesce data B (modern) and data A (historical) rain data
            df_b[clean_name] = df_b[ f'{mlabel}_{clean_name}' ].combine_first( df_b[ name ])


    df_b = df_b.drop( drop_list , axis =1 )
    
    return df_b


def prep_his_dis_data( dict_hist ):
    
    ''' 
    Parameters
    ---------
      
      dict
        Historical Daily Discharge Data. 
         
  
    Returns
    --------
      
      Table with Historical Discharge data. Units of mm/month. 
    
    '''
    
    print( 'Prep Historic Discharge Data' ) 
    dict_final = {}
    
    for k,v in dict_hist.items():
        dict_final[k] = [] 
        #dict_new_keys = 
        for year,df_daily in v['data'].items():
            # Change from l/sec (instantaneous) to mm/month
            # [ [ Q (mean discharge) / A (drainage area) ] * 3600 * 24 * n of days ] / 10^6
            dic_days = {1:31, 2:[28,29], 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
            df_discharge = df_daily.copy()
            df_discharge = ( (( ( df_discharge.mean()/v['drainage'] ) * 0.0864 * 30)).to_frame() )
            df_discharge = df_discharge.iloc[2: , :]
            df_discharge.columns = [k]
            df_discharge.index.names = ['Year']
            df_discharge.reset_index(inplace=True)
            look_up = {'JAN':1, 'FEB':2,  'MAR':3, 'APR':4,'MAY':5,
                       'JUN':6, 'JUL':7, 'AUG':8 , 'SEPT':9,'OCT':10, 'NOV':11, 'DEC':12}
            df_discharge['Year'] = df_discharge['Year'].map(lambda x: look_up[x])
            df_discharge['Year'] = df_discharge['Year'].map(lambda x: datetime.datetime(year,x,1))
            dict_final[k].append( df_discharge )

        dict_final[k] = pd.concat(dict_final[k]).reset_index(drop=True)
    
    return dict_final



