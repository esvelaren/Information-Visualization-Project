Instructions:

1. Make sure to use an environment with python 3.9.11

You can easily do so by installing Anaconda:
	https://docs.anaconda.com/anaconda/install/windows/
Then you can open a terminal and create the environment via:
	conda create -n py39 python=3.9
	conda activate py39
Feel free to use Visual Code or Pycharm to edit the python file.

Note: If you have python recently installed it is most likely to be 3.9,
if so you can skip the previous step and use your environment on visual code or pycharm

2. Requirements: Install the following dependencies:
+ pandas:
pip install pandas
+ plotly:
pip install plotly
+ panel
pip install panel
+ bokeh
pip install bokeh
+ geopandas: to be installed correctly, install as follows:
pip install wheel
pip install pipwin
pipwin install numpy
pipwin install pandas
pipwin install shapely
pipwin install gdal
pipwin install fiona
pipwin install pyproj
pipwin install six
pipwin install rtree
pipwin install geopandas

Note: 	You can do by typing in the terminal: pip install pandas (for example)
	Maybe you are required to install something else, if so the
	console will tell you what and you just need to do pip install...

3. From the terminal you can mount the bokeh server using the following command:
bokeh serve --show main.py

4. At this point a new tab in your browser is created with the dashboard created in the python file.