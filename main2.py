# Required modules
import pickle
import pandas as pd
import numpy as np
import geopandas as gdp
import json
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, Slider, HoverTool, ColumnDataSource, RadioButtonGroup
from bokeh.palettes import brewer
from bokeh.layouts import widgetbox, row, column

with open('df_gas.pickle', 'rb') as handle:
    df_gas = pickle.load(handle)
with open('df_gas.pickle', 'rb') as handle:
    df_gas = pickle.load(handle)
with open('df_gas.pickle', 'rb') as handle:
    df_gas = pickle.load(handle)
with open('gdf.pickle', 'rb') as handle:
    gdf = pickle.load(handle)

# Function to match the 2 tables at the year selected in the slider
def json_data_selector(selectedYear):
    yr = selectedYear
    # CHANGE!
    df_yr = df_gas[df_gas['Year'] == yr]
    merged = gdf.merge(df_yr, on='Country')
    #merged.fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data

# Define the callback function: update_plot
def update_plot(attr, old, new):
    # The input yr is the year selected from the slider
    yr = slider.value
    new_data = json_data_selector(yr)
    
    # The input cr is the criteria selected from the select box
    cr = select.value
    input_field = format_df.loc[format_df['verbage'] == cr, 'field'].iloc[0]
    
    # Update the plot based on the changed inputs
    p = make_plot(input_field)
    
    # Update the layout, clear the old document and display the new document
    layout = column(p, widgetbox(select), widgetbox(slider))
    curdoc().clear()
    curdoc().add_root(layout)
    
    # Update the data
    geosource.geojson = new_data 

def make_plot(field_name):    
  # Set the format of the colorbar
  min_range = format_df.loc[format_df['field'] == field_name, 'min_range'].iloc[0]
  max_range = format_df.loc[format_df['field'] == field_name, 'max_range'].iloc[0]
  field_format = format_df.loc[format_df['field'] == field_name, 'format'].iloc[0]

  # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
  color_mapper = LinearColorMapper(palette = palette, low = min_range, high = max_range)

  # Create color bar.
  format_tick = NumeralTickFormatter(format=field_format)
  color_bar = ColorBar(color_mapper=color_mapper, label_standoff=18, formatter=format_tick,
  border_line_color=None, location = (0, 0))

  # Create figure object.
  verbage = format_df.loc[format_df['field'] == field_name, 'verbage'].iloc[0]

  p = figure(title = verbage + ' by Neighborhood for Single Family Homes in SF by Year - 2009 to 2018', 
             plot_height = 650, plot_width = 850,
             toolbar_location = None)
  p.xgrid.grid_line_color = None
  p.ygrid.grid_line_color = None
  p.axis.visible = False

  # Add patch renderer to figure. 
  p.patches('xs','ys', source = geosource, fill_color = {'field' : field_name, 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
  
  # Specify color bar layout.
  p.add_layout(color_bar, 'right')

  # Add the hover tool to the graph
  p.add_tools(hover)
  return p

# Input geojson source that contains features for plotting for:
# initial year 2018 and initial criteria sale_price_median
geosource = GeoJSONDataSource(geojson = json_data_selector(2011))
input_field = 'Natural Gas'

# Define a sequential multi-hue color palette.
palette = brewer['Blues'][8]

# Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]

# Add hover tool
hover = HoverTool(tooltips = [ ('Neighborhood','@neighborhood_name'),
                               ('# Sales', '@sale_price_count'),
                               ('Average Price', '$@sale_price_mean{,}'),
                               ('Median Price', '$@sale_price_median{,}'),
                               ('Average SF', '@sf_mean{,}'),
                               ('Price/SF ', '$@price_sf_mean{,}'),
                               ('Income Needed', '$@min_income{,}')])

# Call the plotting function
p = make_plot(input_field)

# Make a slider object: slider 
slider = Slider(title = 'Year',start = 2000, end = 2020, step = 1, value = 2000)
slider.on_change('value', update_plot)

# # Make a selection object: select
# select = Select(title='Select Criteria:', value='Median Sales Price', options=['Median Sales Price', 'Minimum Income Required',
#                                                                                'Average Sales Price', 'Average Price Per Square Foot',
#                                                                                'Average Square Footage', 'Number of Sales'])
# select.on_change('value', update_plot)
LABELS = ["Natural Gas", "Option 2", "Option 3"]
radio_button_group = RadioButtonGroup(labels=LABELS, active=0)
radio_button_group.on_change('active', update_plot)

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
# Display the current document
layout = column(p, widgetbox(select), widgetbox(slider))
curdoc().add_root(layout)