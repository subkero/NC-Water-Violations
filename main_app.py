import requests
import pandas as pd

import coords_getters as CG
import population_getters as PG
import map_builders as MB

#Step 1) -- Get violations data
master_table = pd.DataFrame() #creates a new dataframe that's empty
START_WSYS_NUM=3500 # Can potentially start from 1
END_WSYS_NUM=3505  # At last check ends past 23900

for x in range (START_WSYS_NUM, END_WSYS_NUM):
    url=('https://www.pwss.enr.state.nc.us/NCDWW2/JSP/Violations.'
     'jsp?tinwsys_is_number={}&tinwsys_st_code=NC'.format(x))
    wsDetail={}
    try:
        #Create a handle, page, to handle the contents of the website
        page = requests.get(url, timeout=25)
        tables = pd.read_html(page.text)
        table = tables[4]
        table.columns = table.columns.droplevel(0)
        
        # parse table 2 values into a dictionary
        for row in tables[2].iterrows():
    
            wsDetail[row[1][0]]=[row[1][1]]*(tables[4].shape[0]) # values table 4's 
            wsDetail[row[1][2]]=[row[1][3]]*(tables[4].shape[0])# length's times.
            
        dftable1=pd.DataFrame(wsDetail)
        dftable2 = pd.concat([table, dftable1], axis=1)
        
        master_table=master_table.append(dftable2)
    except:
        pass
print('crawling complete')
master_table=master_table[(~master_table['Violation Type Name'].str.contains('ROUTINE|MONTHLY|YEARLY')
                           ) | (master_table['Return To Compliance(Y=Yes; N=No)'].eq('N'))] 
master_table.to_csv('filteredMasterTable.csv',sep=',')    
"""
Once we have the Violatins data, the 2 types of maps require different types of additional data.
Choropleth maps require: i) Population numbers for each County  ii) fips codes iii) Violations counts for 
each county, and finally iv) A choropleth map of results;
"""
   
df_spots=master_table[['Principal City Served:','Principal County Served:']].drop_duplicates()  

counties_table=df_spots['Principal County Served:'].drop_duplicates()

#Step 2) i) Get populations for counties
counties_table=PG.census_countyPop_getter(counties_table) 

#ii) --  Get fips codes for counties
counties_table=CG.fips_adder(counties_table)

# iii) Violations counts for each county
df_viols=pd.merge(master_table,counties_table, how='left', on='Principal County Served:')

df_viols_pivot=df_viols.pivot_table('ViolationNo.', index=['Principal County Served:','fips_county',
                                                           'POP'],aggfunc='count',)
df_viols_pivot=df_viols_pivot.reset_index()  

#iv) -- Produce 2 choropleth maps
MB.choropl_viols(values=df_viols_pivot['ViolationNo.'], fips=df_viols_pivot['fips_county'],
                 leg='Violations by County')
values4=(df_viols_pivot['ViolationNo.'].astype(int)*1000).div(df_viols_pivot['POP'].astype(int),fill_value=0)
MB.choropl_viols(values4, fips=df_viols_pivot['fips_county'].tolist(),
              leg='Violations per 1000 residents')

"""
...while  Bubble maps require: a) Latitude and Longitude data b) Populations from incorporated cities,
 towns and villages and populations from unincorporated townships and municipalities c)Violations counts 
for each 'place' and finally d) Bubble maps.
    
Functions that support each of these steps will be imported from modules included alongside 
this main file, in order to reduce clutter.
"""

#Step 3 a) -- Get Google Latitude and Longitude data for each unique place in Violations table then re-merge

df_spots=CG.lat_long_getter(df_spots) 
df_spots=df_spots.drop_duplicates(['latitude','longitude'])

# b) Get Population of cities, towns, villages, townships from Census APIs and re-merge
incorp_pop_tables, incorp_pop_dict=PG.census_pop_adder()
unincorp_pop_tables=PG.census_unincorp_getter()
df_bubblePopData=pd.merge(df_spots,incorp_pop_tables,how='left',on='Principal City Served:')

df_bubblePopData=df_bubblePopData.merge(unincorp_pop_tables, on=['Principal City Served:',
                                                    'Principal County Served:'])
df_bubblePopData['POP']=df_bubblePopData['POP_x'].combine_first(df_bubblePopData['POP_y'])

# c) -- Re-merge with original Violations data, with violations counts ready for maps
df_viols_bubble=pd.merge(master_table,df_spots, 
                         on=['Principal City Served:','Principal County Served:']) #assign coordinates to original data
df_viols_bubble=df_viols_bubble.merge(df_bubblePopData, on=['latitude','longitude'],suffixes=('', '_y')) #add pop data

df_viols_BubPivot=df_viols_bubble.pivot_table('ViolationNo.', index=['Principal City Served:',
                        'latitude','longitude','Principal County Served:','POP'],aggfunc='count',)
df_viols_BubPivot=df_viols_BubPivot.reset_index()  

# d) -- Produce 2 bubble maps
MB.bubble_mapper(df_viols_BubPivot)
MB.bubble_mapper(df_viols_BubPivot,raw_count_map=False)
           