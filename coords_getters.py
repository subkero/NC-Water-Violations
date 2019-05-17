import requests
import pandas as pd

from geopy import geocoders
import certifi
import ssl

import secrets2

ctx = ssl.create_default_context(cafile=certifi.where())
geocoders.options.default_ssl_context = ctx

# use locations from viols data to get a list of json objects which contain the longs & lats for each 'spot'.
def lat_long_getter(df, state='NC'):
    """
    Input: dataframe with columns: 'Principal City Served:' only, or also 'Principal County Served:'  
    Output: input dataframe merged with latitude,longitude & fips data
    """
    g = geocoders.GoogleV3(api_key=secrets2.AppKey['Google'])
    
    m=['latitude', 'longitude', 'address']   
    nc_json_lst_dicts=[]        
    one_row=False
    
    if df.shape[1]==1:
        on_col=['Principal City Served:']
        one_row=True
    else:
        on_col=['Principal City Served:','Principal County Served:']
    
    df.rename(columns={list(df)[0]:'Principal City Served:'}, inplace=True)
   
    for row in df.itertuples():
        if one_row:
            spot=row[1]
        else: 
            spot=(str(row[1])+', '+str(row[2])+' County')
     
        inputAddress=spot+', '+state
     
        try:
            location = g.geocode(inputAddress, timeout=10)
            lll=[location.latitude, location.longitude, location.address]
 
            """
            #for each input location add to list, a dictionary with values corresponding to keys in 
            lll plus original location. Later add fips code for 
            """
            right_dict={m[x]: lll[x] for x in range(len(m))}
            right_dict.update({'Principal City Served:':row[1]})
            if one_row==False:
                right_dict.update({'Principal County Served:':row[2]}) 

            nc_json_lst_dicts.append(right_dict) 
           
        except:
            pass

    df_json=fips_adder(pd.DataFrame(nc_json_lst_dicts))  # call fips adder        
    
    df1=pd.merge(df,df_json, on=on_col) # merge with original 
       
    return df1

def fips_adder(df):
    """
    Input: dataframe with 'Principal County Served:' column 
    Output: Dataframe with fips column merged on 'Principal County Served:' column 
    """
    url='https://www.lib.ncsu.edu/gis/countfips'
    page=requests.get(url)
    tables=pd.read_html(page.text)  
    df_nc_fips=tables[0]
   
    df_nc_fips.rename(columns={0:'Principal County Served:', 1:'fips_county'},inplace=True)
     
    df_nc_fips['Principal County Served:']=df_nc_fips['Principal County Served:'].apply(lambda x: x.upper().strip())
    df['Principal County Served:']=df['Principal County Served:'].apply(lambda x: x.upper().strip())
    
    df1=pd.merge(df,df_nc_fips, how='left', on='Principal County Served:')

    return df1

#test_locations=pd.DataFrame(['Emerald Isle', 'Enfield','Erwin','Eureka','Everetts', 'Fair Bluff', 'Fairmont' ,
#'Fairview' , 'Faison' , 'Faith' , 'Falcon' , 'Falkland' , 'Fallston' ,], columns=['Area00 Name'])
