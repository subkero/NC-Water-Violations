import numpy as np

import plotly.plotly as py
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly.io as pio
import plotly.tools as ptools

import secrets2

def choropl_viols(values, fips,leg='Violations by County'):
    """
    Inputs: values: list of values to be mapped
            fips:list of fips codes for each county mapped
            leg: Title to be used in legend
    """
    endpts = list(np.mgrid[min(values):max(values):6j])
 
    colorscale=['rgb(169,186,157)','rgb(208,240,192)','rgb(152,251,152)',
              'rgb(80,220,100)','rgb(0,168,107)','rgb(79,121,66)',
              'rgb(63,122,77)','rgb(46,139,87)','rgb(11,102,35)',
              'rgb(0,78,56)'
             ]

    fig = ff.create_choropleth(
    fips=fips, values=values, scope=['North Carolina'], show_state_data=True,
    colorscale=colorscale, binning_endpoints=endpts, round_legend_values=True,
    plot_bgcolor='rgb(229,229,229)',
    paper_bgcolor='rgb(229,229,229)',
    legend_title=leg, #legend_title='Violations by County',
    county_outline={'color': 'rgb(255,255,255)', 'width': 0.5},
    #exponent_format=True,
     
    )
    fig['layout']['legend'].update({'x': 0})
    fig['layout']['annotations'][0].update({'x': -0.12, 'xanchor': 'left'})
  
    ptools.set_credentials_file(api_key=secrets2.AppKey['Plotly'],
                                username=secrets2.uzer_name['Plotly'])

    name3=(leg.split(' ')[-1])+'LnkDNtstFri10am'
   
    py.plot(fig, filename=name3, auto_open=True)
    pio.write_image(fig, name3+'.png')
   
    return


def bubble_mapper(df,raw_count_map=True):
    """
    Inputs: df: dataframe with 'Principal City Served:' column,
            Violations counts in 'ViolationNo.' column [typically from pivot table],
            'POP' (Population) & 'Principal City Served:' columns 
    Output: Interactive Bubble map hosted on plotly
    """  
   
    colors=["rgb(0,116,217)","rgb(255,65,54)","rgb(133,20,75)","rgb(255,133,27)","lightgrey"] 
    limits = [(0,49),(50,99),(100,499),(500,999),(1000,3000)]
    
    df.rename(columns={'ViolationNo.':'Num_Viols'}, inplace=True)
    df = df[np.isfinite(df['POP'].astype(int))]
    #df['ViolsDensityPer1C']=(((df['Num_Viols'].astype(int))*100).div(df['POP'].astype(int),
    #                            fill_value=0))
    df['ViolsDensityPer1C']=(df['Num_Viols'].astype(int)*100).div(df['POP'].astype(int),fill_value=0)
    #df.to_csv('test_bubbleData3.csv', sep=',')
    if raw_count_map:
        values_column='Num_Viols'
        df['text'] = (df['Principal City Served:'] + '<br>Violations:' + (df[values_column].astype(str))  )
        header_txt='Water violations in North Carolina by location <br>'+'<sub>Click legend to toggle traces'
        legend_text='# of Violations'
        scale = 50.0
    else:
        values_column='ViolsDensityPer1C'
        df=df[df.loc[:,values_column] != np.Inf]
        limits = [(0,4.99999),(5,9.99999),(10,49.99999),(50,300)]
        colors.pop(-2)
        legend_text='Violations/100 pop'

        df['text'] = (df['Principal City Served:'] +'   [POP: '+ df['POP'].astype(str)+']'+ 
          '<br>Violation density:' + (df[values_column].astype(str)) )
        header_txt=('Water violations per 100 residents in North Carolina by location <br>'+
                    '<sub>Click legend to toggle traces')
        scale = 2
        
    cities = []

    for i in range(len(limits)):
        lim = limits[i]
        df_sub = df[(df[values_column]>=lim[0])&(df[values_column]<=lim[1])] #slice of results from tuples bins

        city = go.Scattergeo(            
            lon = df_sub['longitude'].astype(float), #df_sub['lon']
            lat = df_sub['latitude'].astype(float), #df_sub['lat']
            text = df_sub['text'],
            marker = go.scattergeo.Marker(
                size = df_sub[values_column].astype(int)/scale, # df_sub['pop']/scale,
                color = colors[i],
                line = go.scattergeo.marker.Line(
                    width=0.5, color='rgb(40,40,40)'
                ),
                sizemode = 'diameter'
            ),
            name = '{0} - {1}'.format(lim[0],lim[1]) )
        cities.append(city)
    
    layout = go.Layout(
            title = go.layout.Title(
                
                text = header_txt
            ),
            showlegend = True,
            geo = go.layout.Geo(
                resolution = 110,
                center=go.layout.geo.Center(lon=-79 , lat=35.5 ),
                
                projection = go.layout.geo.Projection(
                    type= 'albers usa',#'mercator','conic equal area',
                    
                ),
                showland = True,
                landcolor = 'rgb(217, 217, 217)',
                subunitwidth=1,
                countrywidth=1,
                subunitcolor="rgb(255, 255, 255)",
                countrycolor="rgb(255, 255, 255)",
                
                lonaxis = go.layout.geo.Lonaxis(range= [ -85.0, -75.0 ]),
                lataxis = go.layout.geo.Lataxis(range= [ 33.0, 36.0]),
                domain = go.layout.geo.Domain(x = [ 0, 1 ],y = [ 0, 1 ])
            ),
        annotations=[
        dict(
            x=1.12,
            y=1.05,
            align="right",
            valign="top",
            text=legend_text, 
            showarrow=False,
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="top"
        ),

    ],            
                
    )
    
    ptools.set_credentials_file(api_key=secrets2.AppKey['Plotly'],
                                username=secrets2.uzer_name['Plotly'])
    fig = go.Figure(data=cities, layout=layout)

    py.plot(fig, filename='d3-bubble-map-linkED01',auto_open=True)
    return



