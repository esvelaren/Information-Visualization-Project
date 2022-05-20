import pandas as pd
import geopandas as gpd
import json
import matplotlib as mpl
import pylab as plt
import numpy as np
from bokeh.io import output_file, show, output_notebook, export_png
from bokeh.models import ColumnDataSource, GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool
from bokeh.plotting import figure
from bokeh.palettes import brewer
from bokeh.palettes import Category20
import panel as pn
import panel.widgets as pnw
import plotly.express as px
import pickle
import param

pn.extension('plotly')

# Loading pickles:
# Optional: We can either obtain the datasets in another python file and load them here via pickle !OR! put everything in this python file and not use pickles.
with open('df_nat_gas_ru.pickle', 'rb') as handle:
    df_gas = pickle.load(handle)
with open('df_oil_petrol_ru.pickle', 'rb') as handle:
    df_oil = pickle.load(handle)
with open('df_solid_fuel_ru.pickle', 'rb') as handle:
    df_solid = pickle.load(handle)
with open('gdf.pickle', 'rb') as handle:
    gdf = pickle.load(handle)
with open('df_sitc.pickle', 'rb') as handle:
    df_sitc = pickle.load(handle)
with open('df_natural_gas_exporters.pickle', 'rb') as handle:
    df_gas_treemap = pickle.load(handle)
with open('df_oil_petrol_exporters.pickle', 'rb') as handle:
    df_oil_treemap = pickle.load(handle)
with open('df_solid_fuel_exporters.pickle', 'rb') as handle:
    df_solid_treemap = pickle.load(handle)
gdf.crs = {"init":"epsg:4326"}

sitc = df_sitc.columns.values
df_sitc = df_sitc.reset_index()
df_sitc['date'] = df_sitc['date'].astype(str)  # to show it in the x-axis
source = ColumnDataSource(data=df_sitc)  # data for the graph
Date = source.data['date']
source = ColumnDataSource(df_sitc.reset_index())

def get_dataset(name,year=None):
    global datasetname
    if (name == "Natural Gas"):
        df = df_gas[df_gas['Year'] == year]
    elif (name == "Oil Petrol"):
        df = df_oil[df_oil['Year'] == year]
    elif (name == "Solid Fuel"):
        df = df_solid[df_solid['Year'] == year]
    datasetname = name
    merged = gdf.merge(df, on='Country', how='left')
    return merged


def get_dataset2(name, year, country='EU27_2020'):
    global datasetname
    if (name == "Natural Gas"):
        df = df_gas_treemap[df_gas_treemap['Country'] == country]
        df = df[df['Year'] == year]
    elif (name == "Oil Petrol"):
        df = df_oil_treemap[df_oil_treemap['Country'] == country]
        df = df[df['Year'] == year]
    elif (name == "Solid Fuel"):
        df = df_solid_treemap[df_solid_treemap['Country'] == country]
        df = df[df['Year'] == year]

    df = df[df['Import']!=0]
    datasetname=name
    return df

datasetname='Natural Gas'

def get_geodatasource(gdf):
    """Get getjsondatasource from geopandas object"""
    json_data = json.dumps(json.loads(gdf.to_json()))
    return GeoJSONDataSource(geojson = json_data)

# Define custom tick labels for color bar.
tick_labels = {'0': '0%', '20': '20%', '40': '40%', '60': '60%', '80': '80%', '100': '100%',}

def bokeh_plot_map(gdf, column=None, title=''):
    """Plot bokeh map from GeoJSONDataSource """
    global datasetname
    geosource = get_geodatasource(gdf)
    if datasetname == "Natural Gas":
        palette = brewer['Greens'][8]
    elif datasetname == "Oil Petrol":
        palette = brewer['Blues'][8]
    elif datasetname == "Solid Fuel":
        palette = brewer['Oranges'][8]
    palette = palette[::-1]
    vals = gdf[column]

    hover = HoverTool(tooltips=[('Country: ', '@Country'),
                                ('Russian {} Import'.format(datasetname), '@Import')])
    #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette=palette, low=0, high=100)
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, height=660, width=20,
                         location=(0, 0), orientation='vertical', border_line_color=None,
                         major_label_overrides=tick_labels, background_fill_color='WhiteSmoke')

    tools = 'wheel_zoom,pan,reset,hover'
    p = figure(title = title, plot_height=400 , plot_width=850, toolbar_location='right', tools=tools)
    p.xaxis.visible = False
    p.yaxis.visible = False
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.background_fill_color = (245,245,245)
    p.border_fill_color = (245,245,245)
    p.outline_line_color = (245,245,245)
    #Add patch renderer to figure
    p.patches('xs','ys', source=geosource, fill_alpha=1, line_width=0.5, line_color='black',
              fill_color={'field' :column , 'transform': color_mapper})
    #Specify figure layout.
    p.add_layout(color_bar, 'right')
    p.add_tools(hover)
    return p

# ref.: https://stackoverflow.com/questions/57301630/trigger-event-on-mouseup-instead-of-continuosly-with-panel-slider-widget
class IntThrottledSlider(pnw.IntSlider):
    value_throttled = param.Integer(default=0)

def map_dash():
    """Map dashboard"""
    from bokeh.models.widgets import DataTable
    map_pane = pn.pane.Bokeh(width=900, height=700)
    data_select = pn.widgets.RadioButtonGroup(name='Select Dataset', options=['Natural Gas', 'Oil Petrol', 'Solid Fuel'])
    #data_select = pnw.Select(name='dataset', options=['Natural Gas', 'Oil Petrol', 'Solid Fuel'])
    year_slider = IntThrottledSlider(name='Year', start=2000, end=2020, callback_policy='mouseup')
    figure2 = pn.pane.plotly.Plotly(width=800, height=390)
    def update_map(event):
        gdf = get_dataset(name=data_select.value,year=year_slider.value)
        map_pane.object = bokeh_plot_map(gdf, 'Import')

        df_treemap = get_dataset2(name=data_select.value, year=year_slider.value)
        # Reference Maptree: https://discourse.bokeh.org/t/treemap-chart/7907/3
        #print(df_gas_treemap)
        
        figure2.object = px.treemap(df_treemap, path=['Continent', 'Partner'], values='Import',
                             color='Import', hover_data=['Import'],
                             color_continuous_scale='RdBu',
                             color_continuous_midpoint=np.average(df_treemap['Import'], weights=df_treemap['Import']))
        print(df_treemap)
        figure2.object.update_layout(width=800, height= 390,margin=dict(l=10,r=10,b=10,t=40,pad=2), paper_bgcolor="WhiteSmoke")
        global figure2
        
        df1 = df_gas_treemap[df_gas_treemap['Year'] == 2020]
        df1 = df1[df1['Country'] =='EU27_2020' ]
        print(df1)
        figure2 = px.treemap(df1, path=['Continent', 'Partner'], values='Import',
                             color='Partner', hover_data=['Country'],
                             color_continuous_scale='RdBu',
                             color_continuous_midpoint=np.average(df1['Import'], weights=df1['Import']))

        figure2.update_layout(width=800, height= 390,margin=dict(l=10,r=10,b=10,t=40,pad=2), paper_bgcolor="WhiteSmoke")
        #figure2.update_layout(width=800, height=390, margin=dict(l=10, r=20, b=10, t=50, pad=2))
        return

    year_slider.param.watch(update_map, 'value_throttled')
    year_slider.param.trigger('value_throttled')
    data_select.param.watch(update_map, 'value')

    p4 = figure(x_range=Date, height=350, width=800, title="SITC imports by year",background='WhiteSmoke')
    p4.vbar_stack(stackers=sitc, x='date', width=0.5, source=source, color=Category20[15],
                  legend_label=["%s" % x for x in sitc])  # TODO: Problem with the label

    p4.xgrid.grid_line_color = None
    p4.axis.minor_tick_line_color = None
    p4.outline_line_color = None
    p4.legend.location = "top"
    p4.legend.orientation = "horizontal"
    p4.background_fill_color = (245,245,245)
    p4.border_fill_color = (245,245,245)
    p4.outline_line_color = (245,245,245)

    l = pn.Column(pn.Row(data_select, year_slider, background='WhiteSmoke'), map_pane, background='WhiteSmoke')
    l2 = pn.Column(figure2, p4,background='WhiteSmoke')
    app = pn.Row(l, l2, background='WhiteSmoke')
    app.servable()
    return app

app = map_dash()
