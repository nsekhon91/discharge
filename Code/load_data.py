import pandas as pd
import os
import glob
from IPython.display import display


def get_his_dis( df ):
    
    '''
    Splicing Historical Data Raw Files to extract the correct columns
    
    Parameters
    ---------
      
      df
        Excel files with Historical Discharge Data
    
    Returns
    --------
      
      Daily Historical Discharge Data Table.
    
    '''
    
    df['splice'] = df.apply(lambda x: str(x['Unnamed: 12']).startswith('19') and 
                                      str(x['Unnamed: 16']).startswith('MEAN'), axis = 1)
    
    return df[df['splice']==True][['splice','Unnamed: 12']].index

def get_drainage( df ):
    
    'Getting drainage area from historical discharge excel sheets in units of sq kms'
    
    return df.iloc[9,6]

def extract_file( folder ):
    
    '''    
    Extracting folders and files with historical datas
    
    Parameters
    ---------
      
      Folder
        Folder name where historical discharge files are stored
    
    Returns
    --------
      
      Files with historical discharge data.
    
    '''
    l_files =[]
    for path, subdirs, files in os.walk(folder):
        for name in files:
            if name.startswith('Phili'):
                continue
            l_files.append( os.path.join(path, name) )
            
    return l_files

