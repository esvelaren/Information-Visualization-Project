from turtle import width
import pandas as pd
import geopandas as gpd
import json
import matplotlib as mpl
import pylab as plt
import numpy as np
from bokeh.io import output_file, show, output_notebook, export_png
from bokeh.models import ColumnDataSource, GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Range1d, Selection
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

# Getting a list of countries:
countries = list(df_gas['Country'].unique())
dropdown_country = pn.widgets.Select(name='Select', options=countries, width = 130)


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

sel_country = 'EU27_2020'
year = 2000
replot = False


# Ref: https://stackoverflow.com/questions/50478223/bokeh-taptool-return-selected-index
def selected_country(attr, old, new):
    global sel_country, replot
    sel_country = gdf._get_value(new[0], 'Country')
    if sel_country in countries:
        dropdown_country.value = sel_country
    else:
        replot = True
        dropdown_country.value = 'None'  # This is here to fake the change if two consecutive countries are out of list
        dropdown_country.value = 'EU27_2020'
    # print(sel_country)

def bokeh_plot_map(gdf, column=None, title=''):
    """Plot bokeh map from GeoJSONDataSource """
    global datasetname
    geosource = get_geodatasource(gdf)
    geosource.selected.on_change('indices', selected_country)
    if replot is False:
        geosource.selected.indices = gdf.index[gdf['Country'] == sel_country].tolist()
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

    tools = 'wheel_zoom,pan,reset,hover,tap'
    p = figure(title=title, plot_height=250, plot_width=600, toolbar_location='right', tools=tools)
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
    p.update_layout( margin=dict(l=20, r=5, b=1, t=5, pad=2),
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
    p.y_range = Range1d(start=0, end=110)
    p.yaxis.axis_label = 'Dependency on Russia in %'
    if year is not None:
        # df = df[df['Year'] == year]
        source = ColumnDataSource(df.loc[(df.Year == year)])
        p.vbar(x='Year', top=column, bottom=0, width=0.5, source=source, fill_color=color, fill_alpha=0.5)
    p.background_fill_color = (245, 245, 245)
    p.border_fill_color = (245, 245, 245)
    p.outline_line_color = (245, 245, 245)
    return p


def bokeh_plot_multilines(df, column=None, year=None, title=''):
    global datasetname
    if datasetname == "Natural Gas":
        color = 'green'
        df_main = df_gas
    elif datasetname == "Oil Petrol":
        color = 'blue'
        df_main = df_oil
    elif datasetname == "Solid Fuel":
        color = 'orange'
        df_main = df_solid

    source = ColumnDataSource(df)
    p = figure(x_range=(2000, 2020))

    p.line(x='Year', y=column, line_width=2, line_color=color, source=source, legend_label=df.iloc[0]['Country'])

    p.y_range = Range1d(0, 100, max_interval=100, min_interval=0)
    p.yaxis.axis_label = 'Dependency on Russia in %'
    for country in countries:
        p.line(x='Year', y=column, line_color='gray', source=ColumnDataSource())

    if year is not None:
        # df = df[df['Year'] == year]
        source = ColumnDataSource(df.loc[(df.Year == year)])
        p.vbar(x='Year', top=column, bottom=0, width=0.5, source=source, fill_color=color, fill_alpha=0.5)
    p.background_fill_color = "WhiteSmoke"
    return p


# ref.: https://stackoverflow.com/questions/57301630/trigger-event-on-mouseup-instead-of-continuosly-with-panel-slider-widget
class IntThrottledSlider(pnw.IntSlider):
    value_throttled = param.Integer(default=0)

map_pane = None

def map_dash():
    """Map dashboard"""
    from bokeh.models.widgets import DataTable
    map_pane = pn.pane.Bokeh(width=900, height=650)
    data_select = pn.widgets.RadioButtonGroup(name='Select Dataset',
                                              options=['Natural Gas', 'Oil Petrol', 'Solid Fuel'])
    # data_select = pnw.Select(name='dataset', options=['Natural Gas', 'Oil Petrol', 'Solid Fuel'])
    year_slider = IntThrottledSlider(name='Year', start=2000, end=2020, callback_policy='mouseup')
    dropdown_country.value = sel_country
    treemap_pane = pn.pane.plotly.Plotly(width=780, height=380)
    lines_pane = pn.pane.Bokeh(height=220, width=780, margin=(0, 50, 0, 0))

    df_table = pd.DataFrame({'int': [1], 'float': [3.14], 'str': ['A'], 'bool': [True]}, index=[1])
    df_widget = pn.widgets.DataFrame(df_table, name='DataFrame')
    #table = pn.widgets.DataFrame(df_gas[0], autosize_mode='fit_columns', width=300)
    def update_map(event):
        global replot
        global df_widget
        if str(event.obj)[:6] != 'Select' or replot is True:
            df_map = get_dataset(name=data_select.value, year=year_slider.value)
            map_pane.object = bokeh_plot_map(df_map, column='Import')
            #geosource.selected = Selection(indices=gdf.index[gdf['Country'] == sel_country].tolist())
            #if replot is False:
            #    geosource.selected.indices = gdf.index[gdf['Country'] == sel_country].tolist()
            replot = False

        df_treemap = get_dataset_exp(name=data_select.value, year=year_slider.value, country=dropdown_country.value)
        treemap_pane.object = plotly_plot_treemap(df_treemap, column='Import')

        df_lines = get_dataset_line(name=data_select.value, year=year_slider.value, country=dropdown_country.value)
        lines_pane.object = bokeh_plot_lines(df_lines, column='Import', year=year_slider.value)

        country_rel = df_lines[(df_lines['Year']== year_slider.value)].iat[0,2]
        country_abs = df_treemap[(df_treemap['Partner']== 'Russia')].iat[0,4]
        # print("Selected Country: ",sel_country)
        # print("Selected Year:", year_slider.value)
        df_table = pd.DataFrame({'Country': [sel_country], 'Import Percentage (%)': [country_rel], 'Import Value (?)': [country_abs]})
        df_widget = pn.widgets.DataFrame(df_table, name='DataFrame')
        # df = df[df['Year'] == year]
        return

    year_slider.param.watch(update_map, 'value_throttled')
    year_slider.param.trigger('value_throttled')
    data_select.param.watch(update_map, 'value')
    dropdown_country.param.watch(update_map, 'value')

    treeTitle = pn.widgets.StaticText(name='Static Text', value='A string')
    lineTitle = pn.widgets.StaticText(name='Static Text', value='A string')
    mapTitle = pn.widgets.StaticText(name='Static Text', value='A string')
    tableTitle = pn.widgets.StaticText(name='Static Text', value='A string')
    mainTitle = pn.pane.Markdown('### A serif Markdown heading',  background=(245, 245, 245), style={'font-family': "serif"})

    map_pane.sizing_mode = "stretch_both"
    lines_pane.sizing_mode = "stretch_both"
    df_widget.sizing_mode = "stretch_width"
    l = pn.Column(pn.Row(data_select, pn.Spacer(width=10), year_slider, pn.Spacer(width=10),dropdown_country, background='WhiteSmoke'), map_pane, mapTitle, df_widget ,tableTitle,background='WhiteSmoke')
    l.aspect_ratio = 1.2
    l.sizing_mode = "scale_width"
    l2 = pn.Column(mainTitle, treemap_pane, treeTitle, lines_pane, lineTitle, background='WhiteSmoke')
    app = pn.Row(l, l2, background='WhiteSmoke')
    #app = pn.Column(l3, background='WhiteSmoke')

    app.sizing_mode = "stretch_height"
    app.servable()
    return app

app = map_dash()