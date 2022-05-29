## Instructions:

1. Recommended to use an environment with python 3.9

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
+ plotly express:
pip install plotly_express==0.4.0
+ panel
pip install panel
+ bokeh
pip install bokeh
+ geopandas:
pip install geopandas

Note: 	You can do by typing in the terminal: pip install pandas (for example)
	Maybe you are required to install something else, if so the
	console will tell you what and you just need to do pip install...

3. From the terminal you can mount the bokeh server using the following command:
bokeh serve --show main.py

This needs to be called from the code's root folder. All the datasets are zipped are handled by the code in main.py.
If for any reason the pickle files needs to be rewriting, this can be done by the preprocessing code in
dataframes.ipynb jupyter notebook.

4. At this point a new tab in your browser is created with the dashboard created in the python file.