# Required modules
import pickle
import pandas as pd
import numpy as np
import geopandas as gdp
import json
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, Slider, HoverTool, ColumnDataSource, \
    RadioButtonGroup
from bokeh.palettes import brewer
from bokeh.palettes import Category20
from bokeh.layouts import widgetbox, row, column

# HOLA THIS IS A TEST!

# Loading pickles: 
# TODO: Add the rest of datasets. 
# Optional: We can either obtain the datasets in another python file and load them here via pickle !OR! put everything in this python file and not use pickles.
with open('df_nat_gas_ru.pickle', 'rb') as handle:
    df_gas = pickle.load(handle)
with open('gdf.pickle', 'rb') as handle:
    gdf = pickle.load(handle)
with open('df_sitc.pickle', 'rb') as handle:
    df_sitc = pickle.load(handle)


# with open('df_gas.pickle', 'rb') as handle:
#    df_gas2 = pickle.load(handle)

# Function to match the 2 tables at the year selected in the slider
def json_data_selector(selectedYear):
    yr = selectedYear
    df_yr = df_gas[df_gas['Year'] == yr]
    merged = gdf.merge(df_yr, on='Country', how='left')  # how='left'
    # merged.fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data


# Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson=json_data_selector(2000))
# Define a sequential multi-hue color palette.
palette = brewer['Greens'][8]
# Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
# TODO Change High Range
color_mapper = LinearColorMapper(palette=palette, low=0.00, high=100.000, nan_color='#d9d9d9')
# Define custom tick labels for color bar.
tick_labels = {'5000': '5000', }
# Add hover tool
hover = HoverTool(tooltips=[('Country: ', '@Country'),
                            ('Russian Natural Gas Import', '@Import')])
# Create color bar.
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=20, height=660,
                     border_line_color=None, location=(0, 0), orientation='vertical', major_label_overrides=tick_labels)
# Create figure object.
p = figure(title='Russian export influence over Europe: Natural Gas', plot_height=700, plot_width=850,
           toolbar_location=None, tools=[hover])
p.xaxis.visible = False
p.yaxis.visible = False
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

# Add patch renderer to figure (for the map)
p.patches('xs', 'ys', source=geosource, fill_color={'field': 'Import', 'transform': color_mapper},
          line_color='black', line_width=0.5, fill_alpha=1)
# Specify layout
p.add_layout(color_bar, 'right')
p.add_tools(hover)

option = "Natural Gas"


def update_plot(attr, old, new):
    yr = slider.value
    new_data = json_data_selector(yr)
    geosource.geojson = new_data
    # p.title.text = 'Russian export influence over Europe: Natural Gas, %d' %yr
    p.title.text = 'Russian export influence over Europe: {}, year {}'.format(option, yr)


# Make a slider object: slider
slider = Slider(title='Year', start=2000, end=2020, step=1, value=2000)
# callback.args['']
slider.on_change('value', update_plot)


def update(attr, old, new):
    global option
    option = LABELS[radio_button_group.active]
    update_plot('value', slider.value, slider.value)


LABELS = ["Natural Gas", "Oil Petrol", "Solid Fuel"]
radio_button_group = RadioButtonGroup(labels=LABELS, active=0)
radio_button_group.on_change('active', update)

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
l0 = column(widgetbox(radio_button_group), p)
l = column(l0, widgetbox(slider))

# --------------------------------------- SCATTER PLOT (TODO Replace by one of our graphs)
import random

count = 10
x = range(count)
y = random.sample(range(0, 101), count)
p2 = figure(plot_width=400, plot_height=400)  # figure is a type of plot
# using various glyph methods to create scatter
# plots of different marker shapes
p2.circle(x, y, size=30, color='red', legend_label='circle')
p2.line(x, y, width=2, color='blue', legend_label='line')
p2.triangle(x, y, size=10, color='gold', legend_label='triangle')

# df_gas2 = df_gas2[df_gas2['Year'] == 2020]
# df_gas2.reset_index(drop=True, inplace=True)
# df_gas2 = df_gas2.drop(['Year'], axis=1)
# df_gas2 = df_gas2.drop([0, 2, 9, 13, 21, 28, 29, 32, 36, 40, 41, 42, 43])
# df_gas2.reset_index(drop=True, inplace=True)
# df_gas2
"""
x = {
    'Germany': 157,
    'Poland': 93,
    'Italy': 89,
    'France': 63,
    'Sweden': 44,
    'Finland': 42,
    'Greece': 40,
    'Spain': 35,
    'Czech Republic': 32,
    'Bulgaria': 31,
    'Romania': 31,
    'Other': 29
}
"""
x = {
    'Russia': 157,
    'Norway': 93,
    'Algeria': 89,
    'Libya': 63,
    'Saudi Arabia': 44,
    'Egypt': 42,
    'Kuwait': 40,
    'United Arab Emirates': 35,
    'Iran': 32,
    'Iraq': 31,
    'Kazakhstan': 31,
    'Other': 29
}

data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'country'})
data['angle'] = data['value'] / data['value'].sum() * 2 * np.pi
data['color'] = Category20[len(x)]

p5 = figure(height=350, title="Relative natural gas importers to the EU", toolbar_location=None,
            tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

p5.wedge(x=0, y=1, radius=0.4,
         start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
         line_color="white", fill_color='color', legend_field='country', source=data)

p5.axis.axis_label = None
p5.axis.visible = False
p5.grid.grid_line_color = None

# l2 = row(l, p5)
# --------------------------------------- STACKED BAR CHART (TODO Replace by one of our graphs)
sitc = df_sitc.columns.values
df_sitc = df_sitc.reset_index()
df_sitc['date'] = df_sitc['date'].astype(str)  # to show it in the x-axis
source = ColumnDataSource(data=df_sitc)  # data for the graph
Date = source.data['date']

source = ColumnDataSource(df_sitc.reset_index())

p4 = figure(x_range=Date, height=400, title="SITC imports by year")

#p4.vbar_stack(stackers=sitc, x='date', width=0.5, source=source, color=Category20[15],
#              legend_label=str(sitc))  # TODO: Problem with the label
p4.vbar_stack(stackers=sitc, x='date', width=0.5, source=source, color=Category20[15],
              legend_label=["%s" % x for x in sitc])  # TODO: Problem with the label

# p4.y_range.start = 0
# p4.x_range.range_padding = 0.1
p4.xgrid.grid_line_color = None
p4.axis.minor_tick_line_color = None
p4.outline_line_color = None
#p4.legend.location = "top_left"
p4.legend.location = "right"
p4.legend.orientation = "vertical"
# -----


# create a Pandas dataframe
df = pd.DataFrame(dict(
    x=[1, 2, 3, 4, 5],
    y=random.sample(range(1, 11), 5),
))
# create a ColumnDataSource obj using a dataframe
src = ColumnDataSource(data=df)
p3 = figure(plot_width=400, plot_height=400)
p3.vbar(x='x',
        top='y',
        source=src,
        width=0.5,
        bottom=0,
        color='lightgreen')

l3 = column(p5, p4)
l2 = row(l, l3)
# ------------------------------------------
curdoc().add_root(l2)

# Display plot inline in Jupyter notebook
# output_notebook()
# =show(l)
