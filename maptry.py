import pandas as pd
import geopandas as gpd
import json
import matplotlib as mpl
import pylab as plt
import numpy as np
from bokeh.io import output_file, show, output_notebook, export_png
from bokeh.models import ColumnDataSource, GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Range1d
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
with open('df_natural_gas_exporters.pickle', 'rb') as handle:
    df_gas_treemap = pickle.load(handle)
with open('df_oil_petrol_exporters.pickle', 'rb') as handle:
    df_oil_treemap = pickle.load(handle)
with open('df_solid_fuel_exporters.pickle', 'rb') as handle:
    df_solid_treemap = pickle.load(handle)
gdf.crs = {"init": "epsg:4326"}


def get_dataset(name, year=None):
    global datasetname
    if name == "Natural Gas":
        df = df_gas[df_gas['Year'] == year]
    elif name == "Oil Petrol":
        df = df_oil[df_oil['Year'] == year]
    elif name == "Solid Fuel":
        df = df_solid[df_solid['Year'] == year]
    datasetname = name
    merged = gdf.merge(df, on='Country', how='left')
    return merged


def get_dataset_exp(name, year, country='EU27_2020'):
    global datasetname
    if name == "Natural Gas":
        df = df_gas_treemap[df_gas_treemap['Country'] == country]
        df = df[df['Year'] == year]
    elif name == "Oil Petrol":
        df = df_oil_treemap[df_oil_treemap['Country'] == country]
        df = df[df['Year'] == year]
    elif name == "Solid Fuel":
        df = df_solid_treemap[df_solid_treemap['Country'] == country]
        df = df[df['Year'] == year]

    df = df[df['Import'] != 0]
    datasetname = name
    return df


def get_dataset_line(name, year, country='EU27_2020'):
    global datasetname
    if name == "Natural Gas":
        df = df_gas[df_gas['Country'] == country]
        # df = df[df['Year'] == year]
    elif name == "Oil Petrol":
        df = df_oil[df_oil['Country'] == country]
        # df = df[df['Year'] == year]
    elif name == "Solid Fuel":
        df = df_solid[df_solid['Country'] == country]
        # df = df[df['Year'] == year]

    datasetname = name
    return df


datasetname = 'Natural Gas'


def get_geodatasource(gdf):
    """Get getjsondatasource from geopandas object"""
    json_data = json.dumps(json.loads(gdf.to_json()))
    return GeoJSONDataSource(geojson=json_data)


# Define custom tick labels for color bar.
tick_labels = {'0': '0%', '20': '20%', '40': '40%', '60': '60%', '80': '80%', '100': '100%', }


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
    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette=palette, low=0, high=100)
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, height=660, width=20,
                         location=(0, 0), orientation='vertical', border_line_color=None,
                         major_label_overrides=tick_labels, background_fill_color='WhiteSmoke')

    tools = 'wheel_zoom,pan,reset,hover'
    p = figure(title=title, plot_height=400, plot_width=850, toolbar_location='right', tools=tools)
    p.xaxis.visible = False
    p.yaxis.visible = False
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.background_fill_color = (245, 245, 245)
    p.border_fill_color = (245, 245, 245)
    p.outline_line_color = (245, 245, 245)
    # Add patch renderer to figure
    p.patches('xs', 'ys', source=geosource, fill_alpha=1, line_width=0.5, line_color='black',
              fill_color={'field': column, 'transform': color_mapper})
    # Specify figure layout.
    p.add_layout(color_bar, 'right')
    p.add_tools(hover)
    return p


def plotly_plot_treemap(df, column=None, title=''):
    # Ref: https://discourse.bokeh.org/t/treemap-chart/7907/3
    p = px.treemap(df, path=['Continent', 'Partner'], values=column,
                   color='Import', hover_data=[column],
                   color_continuous_scale='Greys',
                   color_continuous_midpoint=np.average(df[column],
                                                        weights=df[column]))
    # print(df_treemap)
    p.update_layout(width=800, height=390, margin=dict(l=10, r=10, b=10, t=40, pad=2),
                    paper_bgcolor="WhiteSmoke")
    return p


def bokeh_plot_lines(df, column=None, year=None, title=''):
    global datasetname
    if datasetname == "Natural Gas":
        color = 'green'
    elif datasetname == "Oil Petrol":
        color = 'blue'
    elif datasetname == "Solid Fuel":
        color = 'orange'

    source = ColumnDataSource(df)
    p = figure(x_range=(2000, 2020))
    p.line(x='Year', y=column, line_width=2, line_color=color, source=source, legend_label=df.iloc[0]['Country'])
    p.y_range = Range1d(0, 100, max_interval=100, min_interval=0)
    p.yaxis.axis_label = 'Dependency on Russia in %'
    if year is not None:
        #df = df[df['Year'] == year]
        source = ColumnDataSource(df.loc[(df.Year == year)])
        p.vbar(x='Year', top=column, bottom=0, width=0.5, source=source, fill_color=color, fill_alpha=0.5)
    p.background_fill_color = "WhiteSmoke"
    return p


# ref.: https://stackoverflow.com/questions/57301630/trigger-event-on-mouseup-instead-of-continuosly-with-panel-slider-widget
class IntThrottledSlider(pnw.IntSlider):
    value_throttled = param.Integer(default=0)


def map_dash():
    """Map dashboard"""
    from bokeh.models.widgets import DataTable
    map_pane = pn.pane.Bokeh(width=900, height=700)
    data_select = pn.widgets.RadioButtonGroup(name='Select Dataset',
                                              options=['Natural Gas', 'Oil Petrol', 'Solid Fuel'])
    # data_select = pnw.Select(name='dataset', options=['Natural Gas', 'Oil Petrol', 'Solid Fuel'])
    year_slider = IntThrottledSlider(name='Year', start=2000, end=2020, callback_policy='mouseup')
    treemap_pane = pn.pane.plotly.Plotly(width=800, height=390)
    lines_pane = pn.pane.Bokeh(height=350, width=800)

    def update_map(event):
        df_map = get_dataset(name=data_select.value, year=year_slider.value)
        map_pane.object = bokeh_plot_map(df_map, column='Import')

        df_treemap = get_dataset_exp(name=data_select.value, year=year_slider.value)
        treemap_pane.object = plotly_plot_treemap(df_treemap, column='Import')

        df_lines = get_dataset_line(name=data_select.value, year=year_slider.value)
        lines_pane.object = bokeh_plot_lines(df_lines, column='Import', year=year_slider.value)
        return

    year_slider.param.watch(update_map, 'value_throttled')
    year_slider.param.trigger('value_throttled')
    data_select.param.watch(update_map, 'value')

    l = pn.Column(pn.Row(data_select, year_slider, background='WhiteSmoke'), map_pane, background='WhiteSmoke')
    l2 = pn.Column(treemap_pane, lines_pane, background='WhiteSmoke')
    app = pn.Row(l, l2, background='WhiteSmoke')
    app.servable()
    return app


app = map_dash()
