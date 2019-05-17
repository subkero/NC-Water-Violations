import pandas as pd
import requests
import numpy as np

import secrets2

def wiki_uncorp_searcher(df): #df=pd.read_csv('places_inGoogleNotInCensus2.csv',header=0)
    """
    Adds a column for the population of the city, county
    Inputs: dataframe with 'Principal City Served:' column
    Output: dataframe with only 2 columns - 'Principal City Served:' & 'Population'
    """

    df_search_list=df[['Principal City Served:','Principal County Served:']].drop_duplicates().astype(str)
    
    base_url='https://en.wikipedia.org/wiki/'
    
    Wikipop=[]
    for row in df_search_list.itertuples():
        
        spot1=row[1].title() # Wiki locations are titlecase, with underscores
        spot_01=spot1+', North Carolina'
        spot1A=spot_01.replace(' ','_')
     
        spot2=(row[1]+', '+row[2]+' County, North Carolina') # some Wiki locations have 'county_name' in name
        spot_02=spot2.title()
        spot2A=spot_02.replace(' ','_')
        
        Population=np.NAN      #default values
        global inWiki
        inWiki=False

        Population=pop_get(base_url, spot=spot1A, spot_00=spot_01,    #calls pop_get function below
                               spot2A2=spot2A, spot_002=spot_02, Population=Population)
        
        # at this point inWiki, & Population values updated            
        Wikipop.append({'Principal City Served:':row[1],'Principal County Served:':row[2],
                        'Population':Population,'inWiki':inWiki})
    
    df1=pd.merge(df_search_list,pd.DataFrame(Wikipop), on=['Principal City Served:','Principal County Served:'])    
        
    return df1
     
def pop_get(base_url, spot, spot_00, spot2A2, spot_002, Population=np.NAN):
        
    def wikiPage_reader(location):
        r = requests.get((base_url+location))
        df_page=pd.read_html(r.text)
        return df_page, r.status_code  # returns the page & status code
    
    def correct_col_getter(df_wiki_tables):  # inconsistent naming conventions for columns in Wiki
        try:
            right_column_name=df_wiki_tables[0][(spot_00+'.1')]
        except:
            try:
                right_column_name=df_wiki_tables[0][(spot+'.1')]
            except:
                try:
                    right_column_name=df_wiki_tables[0][(spot2A2+'.1')]
                except:
                    try:
                        right_column_name=df_wiki_tables[0][(spot_002+'.1')]
                    except:
                        #print('--the correct column name could not be found!')
                        return pd.Series(),'N'
        #print(right_column_name)
        return right_column_name,'Y'
    
    def pop_val(right_column_name):
        for x in range(len(right_column_name.index)):      
            cell_value=right_column_name[x]
        
            if ('Population' in str(cell_value)):  
                Population=right_column_name[x+1] # actual population value in next cell
                return Population, True
           
        return np.NAN, False # otherwise no population value in wiki table
    
    #the business of pop_get function gets started here
    df_wiki_tables,page_there=wikiPage_reader(location=spot) # get the table if it's there
    
    if page_there==404:          
         df_wiki_tables,new_status=wikiPage_reader(location=spot2A2) # if not there try adding county_name to 
         if new_status==404:   
            #print('--location not found in city or county styles.')
            return np.NAN
   
    global inWiki
    inWiki=True
       
    right_column_name,col_name_found=correct_col_getter(df_wiki_tables)
    
    if col_name_found=='Y':
        Population, contains_pop=pop_val(right_column_name)
        if contains_pop:
            return Population # doesn't matter if City only, or City_county (200A / 200B)
        elif page_there==404: # ie. new_status==200
            return Population
        else: 
             # double check to make sure it's not on county_name page
             df_wiki_tables,new_status=wikiPage_reader(location=spot2A2)
             right_column_name,col_name_found=correct_col_getter(df_wiki_tables)
             return pop_val(right_column_name)[0]
        
    elif (col_name_found=='N' and page_there==404):
        #print('--county name used, yet still no population field exists.')
        return np.NAN
       
    
    else:  # if even though page exists, no matching Pop column, check county page
        #print('--This town has no population field. checking county.')
        df_wiki_tables,new_status=wikiPage_reader(location=spot2A2)
        right_column_name,col_name_found=correct_col_getter(df_wiki_tables)
        return pop_val(right_column_name)[0]

def census_unincorp_getter():
    """
    Outputs dataframe with columns:
        'POP','Principal County Served:' & 'Principal City Served:'
        for Unincorporated NC townships.
    """
    base_url=('https://api.census.gov/data/2017/acs/acs5?get=B01001_001E,NAME&for=county%20subdivision:*&in='
              'state:37&key='+secrets2.AppKey['Census'])
    r=requests.get(base_url)
    tables = pd.read_json(r.text)
    tables.columns=tables.iloc[0]
    tables.drop(tables.head(1).index, inplace=True)
    
    mid_getter=lambda x: x.split(',')[1]
    first_getter=lambda x: x.split(',')[0]
    
    def end_dropper(x):
        pieces=x.rsplit(' ', 1)
        if pieces[-1] in ['County', 'township']:
            return pieces[0].upper().strip()
        else:
            return x.upper().strip()
    tables['Principal City Served:']=tables['NAME'].apply(first_getter)
    tables['Principal City Served:']=tables['Principal City Served:'].apply(end_dropper)
    tables['Principal County Served:']=tables['NAME'].apply(mid_getter)
    tables['Principal County Served:']=tables['Principal County Served:'].apply(end_dropper)
    
    tables=tables[~tables['Principal City Served:'].str.startswith('TOWNSHIP')]
    tables.rename(columns={'B01001_001E':'POP',
                                    }, inplace=True)
    df_new_table=tables[['POP','Principal County Served:','Principal City Served:']]
    #df_new_table.to_csv('unincorpCensus04.csv', sep=',',index=False)

    return df_new_table    

def census_countyPop_getter(df): #df=pd.read_csv('pivot_table_chloro_updated.csv', header=0)
    """
    Input: dataframe with 'Principal County Served:' column
    Output: Population Data column (by county) merged to input column
    """
    base_url=('https://api.census.gov/data/2017/pep/population?get=POP,GEONAME,COUNTY&for='
              'county:*&in=state:37&key='+secrets2.AppKey['Census'])
    r=requests.get(base_url)
    tables = pd.read_json(r.text)
    tables.columns=tables.iloc[0]
    tables.drop(tables.head(1).index, inplace=True)

    # need a couple of functions to help extract county name from Census returned Geoname
    first_getter=lambda x: x.split(',')[0]

    def end_dropper(x):
        pieces=x.rsplit(' ', 1)
        if pieces[-1] in ['County', 'township']:
            return pieces[0].upper().strip()
        else:
            return x.upper().strip()
    tables['Principal County Served:']=tables['GEONAME'].apply(first_getter).apply(end_dropper)
    tables.drop(['GEONAME', 'COUNTY', 'state', 'county'], axis=1, inplace=True)
   
    tables=pd.merge(tables,df, on='Principal County Served:')
     
    return tables

def census_pop_adder():
    """
    Returns columns ['POP','Principal City Served:'] for all incorporated NC locations.
    """
    base_101_url=('https://api.census.gov/data/2017/pep/population?get=POP,GEONAME&'
                  'for=place:*&in=state:37&key='+secrets2.AppKey['Census'])

    r = requests.get(base_101_url)
    
    #drop the index column labels, replace with labels in 1st row, then drop 1st row
    tables = pd.read_json(r.text)
    tables.columns=tables.iloc[0]
    tables.drop(tables.head(1).index, inplace=True)
    tables.drop(['state', 'place'], axis=1, inplace=True)
    
    # helper functions
    end_dropper1= lambda x: x.rsplit(',', 1)[0]
    end_dropper2= lambda x: x.rsplit(' ', 1)[0]
    tables['GEONAME']=tables['GEONAME'].apply(end_dropper1).apply(end_dropper2).str.upper()
    tables.rename(columns={'GEONAME':'Principal City Served:'},inplace=True)
    
    dict_tables={}
    for row in tables.itertuples():
        dict_tables[row[2]]=row[1]
        
    return tables, dict_tables



#census_countyPop_getter().to_csv('Ginatrip01.csv',sep=',', index=False)
#census_unincorp_getter()

#test_wiki_pop=wiki_uncorp_searcher(pd.DataFrame(["Reeds", "Welcome", "Arcadia", "Potters Hill"],
#                                  columns=['Principal City Served:']))

