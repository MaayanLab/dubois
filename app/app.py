#################################################################
#################################################################
############### Dubois RNA-seq Analysis #########################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#######################################################
#######################################################
########## 1. App Configuration
#######################################################
#######################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. Flask modules #####
from flask import Flask, render_template, url_for, request
from flask_basicauth import BasicAuth
import os
import json
import plotly
import plotly.graph_objects as go
import pandas as pd
import numpy as np
# import numpy as np

# Maybe make entry point / to get into a home page; can redirect to 'dubois'-- OR can take advantage of URL's and the data that can be stored in them?-- I need a home page anyways, dynamic
# urls seem like a pain for now. Actually, URL's that hold information sound better. 1. Make 'dubois' the index page, and 2. Make subpages that are dynamically generated that can host the plots.

# Change entry point
entry_point = os.environ.get('DUBOIS_ENTRYPOINT', '/dubois')
app = Flask(__name__, static_url_path=os.path.join('/app/static'))

##### 2. Authentication #####
if json.loads(os.environ.get('AUTHENTICATION', 'false')):
	for key in ['BASIC_AUTH_USERNAME', 'BASIC_AUTH_PASSWORD']:
		app.config[key] = os.environ.get(key)
	app.config['BASIC_AUTH_FORCE'] = True
	basic_auth = BasicAuth(app)

##### 3. Prefix middleware #####
class PrefixMiddleware(object):

	def __init__(self, app, prefix=''):
		self.app = app
		self.prefix = prefix

	def __call__(self, environ, start_response):
		if environ['PATH_INFO'].startswith(self.prefix):
			environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
			environ['SCRIPT_NAME'] = self.prefix
			return self.app(environ, start_response)
		else:
			start_response('404', [('Content-Type', 'text/plain')])
			return ["This url does not belong to the app.".encode()]
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=entry_point)

#############################################
########## 2. Data
#############################################ow toow
##### 1. Files #####
##### Make these variable dependent
###


def general_plot_api(expression_file, groups_file):
	"""
	Inputs:
	- expression_file, a string filename referencing a tsv file representing a matrix with rows representing gene symbols and columns with the Sample ID's
	- groups_file, a string filename referencing a JSON file representing the groups, where each group contains the names of conditions.
	- metadata_file, a string filename referencing a tsv file with two columns: one with sample ID's, and the other with the names of the conditions. Column names are 'sample_name'
	and 'Condition', respectively.
	Outputs: 
	"""
	expression_dataframe = pd.read_csv(expression_file, index_col='gene_symbol', sep='\t')
	metadata_dataframe = pd.read_csv(metadata_file, sep='\t')
	with open(groups_file) as openfile:
		group_dict = json.load(openfile)
	
	### Actual plotting
	data = request.json
	gene_symbol = data['gene_symbol']
	conditions = data['conditions']

	### Melt data
	melted_dataframe = expression_dataframe.loc[gene_symbol].rename('logcpm').rename_axis('sample_name').reset_index().merge(metadata_dataframe, on='sample_name')

	### Get plot dataframe
	plot_dataframe = melted_dataframe.groupby('Condition')['logcpm'].agg([np.mean, np.std, lambda x: list(x)])#.rename(columns={'<lambda>': 'points'})#.reindex(conditions)
	plot_dataframe = plot_dataframe.rename(columns={plot_dataframe.columns[-1]: 'points'})

	# Initialize figure
	fig = go.Figure()

	# Loop
	for condition in conditions:
		fig.add_trace(go.Box(name=rename_dict[condition], y=plot_dataframe.loc[condition, 'points'], boxpoints='all', pointpos=0))
	
	# Layout
	fig.update_layout(
		title = {'text': gene_symbol+' gene expression', 'x': 0.5, 'y': 0.85, 'xanchor': 'center', 'yanchor': 'top'},
		xaxis_title = 'Condition',
		yaxis_title = 'Expression<br>(log10 counts per million)',
		showlegend = False
	)

	# Return
	return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)




	


expression_file = 'app/static/data/kallisto-logcpm.txt'
metadata_file = 'app/static/data/dubois-metadata.txt'
groups_file = 'app/static/data/dubois-groups.json'

##### 2. Data #####
# Expression
expression_dataframe = pd.read_csv(expression_file, index_col='gene_symbol', sep='\t')

# Metadata
metadata_dataframe = pd.read_csv(metadata_file, sep='\t')
metadata_dataframe['sample_name'] = metadata_dataframe['Sample']
# Have the same label names as logcpm columns.
metadata_dataframe['sample_name'] = ['sample_'+str(x).replace('.', '_') for x in metadata_dataframe['Sample']]
### Note that, for metadata, only useful columns are 'sample_name' (even this is kind of useless) and 'Condition' (which can be hard coded-- tell me what samples go w/ what condition.)
### ^^ At least for now. Later, we can think about how to more 'systematically' get this info from GEO.

# Groups
with open(groups_file) as openfile:
	group_dict = json.load(openfile)

#######################################################
#######################################################
########## 2. Routes
#######################################################
#######################################################

##################################################
########## 2.1 Webpages
##################################################

#############################################
########## 1. Home
#############################################
### Landing page for the website.

@app.route('/')
def index():

	# Groups
	with open(groups_file) as openfile:
		group_dict = json.load(openfile)

	# Return
	return render_template('index.html', group_dict=group_dict, os=os)#, sample_dataframe=sample_dataframe, conditions_dict=conditions_dict)

##################################################
########## 2.2 APIs
##################################################

#############################################
########## 1. Genes
#############################################

@app.route('/api/genes')

# this will likely stay the same.
def genes_api():

	# Get genes json
	genes_json = json.dumps([{'gene_symbol': x} for x in expression_dataframe.index])

	# Return
	return genes_json

#############################################
########## 2. Plot
#############################################

@app.route('/api/plot', methods=['GET', 'POST'])

def plot_api():

	# Get data
	data = request.json
	gene_symbol = data['gene_symbol']
	# print(gene_symbol)
	conditions = data['conditions']
	# print(conditions)
	
	# Melt data
	melted_dataframe = expression_dataframe.loc[gene_symbol].rename('logcpm').rename_axis('sample_name').reset_index().merge(metadata_dataframe, on='sample_name')

	# Get plot dataframe
	plot_dataframe = melted_dataframe.groupby('Condition')['logcpm'].agg([np.mean, np.std, lambda x: list(x)])#.rename(columns={'<lambda>': 'points'})#.reindex(conditions)
	plot_dataframe = plot_dataframe.rename(columns={plot_dataframe.columns[-1]: 'points'})
	
	# Rename groups-- create a mapping from group strings to labels
	rename_dict = pd.DataFrame([x for key, value in group_dict.items() for x in value]).set_index('group_string').to_dict()['group_label']

	# Initialize figure
	fig = go.Figure()

	# Loop
	for condition in conditions:
		fig.add_trace(go.Box(name=rename_dict[condition], y=plot_dataframe.loc[condition, 'points'], boxpoints='all', pointpos=0))
	
	# Layout
	fig.update_layout(
		title = {'text': gene_symbol+' gene expression', 'x': 0.5, 'y': 0.85, 'xanchor': 'center', 'yanchor': 'top'},
		xaxis_title = 'Condition',
		yaxis_title = 'Expression<br>(log10 counts per million)',
		showlegend = False
	)

	# Return
	return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#######################################################
#######################################################
########## 3. Run App
#######################################################
#######################################################
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')
