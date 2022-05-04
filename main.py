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
slider.on_change('value_throttled', update_plot)  # 'value_throttled' -> the value is updated only at the mouseup


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

#p5 = figure(height=350, title="Relative natural gas importers to the EU", toolbar_location=None,
 #           tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

#p5.annular_wedge(x=0, y=1, inner_radius=0.1, outer_radius=0.4,
 #        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
 #        line_color="white", fill_color='color', legend_field='country', source=data)
#---------------------------------------------------------------------TRY
from collections import OrderedDict
from io import StringIO
from bokeh.io import output_notebook
output_notebook()
from math import log, sqrt
from bokeh.plotting import figure, output_file, show
import numpy as np
import bokeh
import pandas as pd


from bokeh.plotting import figure, output_file, show



dataset = """
country,   oil, energy, fuel, gram
spain,      800,        509,          353,        negative
Germany,    1043,       598,          4543,     negative
UK,         3984,       100,          5,      negative
Iceland,    850,        4564,         1,        negative
Italy,      1335,       3978,         99783,     negative
France,     850,        2,            432,      negative
Portugal,   100,        93478,        32,      negative
Belgium,    1453,       9387,         3553,    negative
Poland,     870,        41,           34,      negative
Malta,      1000,       4085,         1,    positive
Greece,     156,        497,          45,      positive
Others,     400,        5565,         87654,    positive

"""

dataset_color = OrderedDict([
    ("oil",   "#0d3362"),
    ("energy", "#c64737"),
    ("fuel",     "black"  ),
])

gram_color = OrderedDict([
    ("negative", "#e69584"),
    ("positive", "#aeaeb8"),
])

df = pd.read_csv(StringIO(dataset),
                 skiprows=1,
                 skipinitialspace=True,
                 engine='python')

width = 700
height = 700
inner_radius = 90
outer_radius = 300 - 10

maxr = sqrt(log(1 * 1E4))
minr = sqrt(log(1000000 * 1E4))
a = (outer_radius - inner_radius) / (minr - maxr)
b = inner_radius - a * maxr

def rad(mic):
    return a * np.sqrt(np.log(mic * 1E4)) + b

big_angle = 2.0 * np.pi / (len(df) + 1)
small_angle = big_angle / 7

p5 = figure(plot_width=width, plot_height=height, title="",
    x_axis_type=None, y_axis_type=None,
    x_range=(-420, 420), y_range=(-420, 420),
    min_border=0, outline_line_color="black",
    background_fill_color="#f0e1d2")

p5.xgrid.grid_line_color = None
p5.ygrid.grid_line_color = None

# annular wedges
angles = np.pi/2 - big_angle/2 - df.index.to_series()*big_angle
colors = [gram_color[gram] for gram in df.gram]
p5.annular_wedge(
    0, 0, inner_radius, outer_radius, -big_angle+angles, angles, color=colors,
)

# small wedges
p5.annular_wedge(0, 0, inner_radius, rad(df.oil),
                -big_angle+angles+5*small_angle, -big_angle+angles+6*small_angle,
                color=dataset_color['oil'])
p5.annular_wedge(0, 0, inner_radius, rad(df.energy),
                -big_angle+angles+3*small_angle, -big_angle+angles+4*small_angle,
                color=dataset_color['energy'])
p5.annular_wedge(0, 0, inner_radius, rad(df.fuel),
                -big_angle+angles+1*small_angle, -big_angle+angles+2*small_angle,
                color=dataset_color['fuel'])

# circular axes and lables
labels = np.power(10.0, np.arange(0,7))
radii = a * np.sqrt(np.log(labels * 1E4)) + b
p5.circle(0, 0, radius=radii, fill_color=None, line_color="white")
p5.text(0, radii[:-1], [str(r) for r in labels[:-1]],
       text_font_size="11px", text_align="center", text_baseline="middle")

# radial axes
p5.annular_wedge(0, 0, inner_radius-10, outer_radius+10,
                -big_angle+angles, -big_angle+angles, color="black")

# Country labels
xr = radii[-1]*np.cos(np.array(-big_angle/2 + angles))
yr = radii[-1]*np.sin(np.array(-big_angle/2 + angles))
label_angle=np.array(-big_angle/2+angles)
label_angle[label_angle < -np.pi/2] += np.pi # easier to read labels on the left side
p5.text(xr, yr, df.country, angle=label_angle,
       text_font_size="12px", text_align="center", text_baseline="middle")


p5.rect([-40, -40, -40], [18, 0, -18], width=30, height=13,
       color=list(dataset_color.values()))
p5.text([-15, -15, -15], [18, 0, -18], text=list(dataset_color),
       text_font_size="12px", text_align="left", text_baseline="middle")

#show(p)
#-----------------------------------------------------------------------TRY

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
