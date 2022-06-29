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
from flask import Flask, render_template, url_for, request, session
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
app.secret_key = "hello"

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

# expression_file = 'app/static/data/GSE69074_Expression.txt'
# metadata_file = 'app/static/data/GSE69074_Metadata.json'

##### 2. Data #####
# Expression
# expression_dataframe = pd.read_csv(expression_file, index_col = 0, sep='\t')

# Metadata
# with open(metadata_file) as openfile:
# 	metadata_dict = json.load(openfile)

# Get samples to conditions mapping
# samp_to_cond = {}

# for conditions_dict in metadata_dict.values():
# 	for condition, samples_list in conditions_dict.items():
# 		for sample in samples_list:
# 			samp_to_cond[sample] = condition

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

@app.route('/<geo_accession>')
def gene_explorer(geo_accession):

	# Data
	session['geo_accession'] = geo_accession
	metadata_file = 'app/static/data/' + geo_accession + '/' + geo_accession + '_Metadata.json'
	
	# Groups
	with open(metadata_file) as openfile:
		metadata_dict = json.load(openfile)

	# Return
	return render_template('index.html', metadata_dict=metadata_dict, os=os)#, sample_dataframe=sample_dataframe, conditions_dict=conditions_dict)

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
	geo_accession = session['geo_accession']
	expression_file = 'app/static/data/' + geo_accession + '/' + geo_accession + '_Expression.txt'
	expression_dataframe = pd.read_csv(expression_file, index_col = 0, sep='\t')

	genes_json = json.dumps([{'gene_symbol': x} for x in expression_dataframe.index])

	# Return
	return genes_json

#############################################
########## 2. Plot
#############################################

@app.route('/api/plot', methods=['GET', 'POST'])

def plot_api():
	"""
	Inputs:
	- expression_dataframe, a tsv file representing a matrix with rows having indices representing gene symbols and columns with indices representing Sample ID's. 
		Each entry represents the expression value for a gene in a sample.
	- metadata_dict, a JSON file with the following format: {group_name:{condition_names:[sample_name, ...]}}

	Outputs: 
	- plotly_json, a serialized JSON formatted string that represents the data for the boxplot to be plotted, used by boxplot() function in scripts.js.
	"""
	geo_accession = session['geo_accession']
	expression_file = 'app/static/data/' + geo_accession + '/' + geo_accession + '_Expression.txt'
	metadata_file = 'app/static/data/' + geo_accession + '/' + geo_accession + '_Metadata.json'
	expression_dataframe = pd.read_csv(expression_file, index_col = 0, sep='\t')
	with open(metadata_file) as openfile:
		metadata_dict = json.load(openfile)
	
	# Get samples to conditions mapping
	samp_to_cond = {}

	for conditions_dict in metadata_dict.values():
		for condition, samples_list in conditions_dict.items():
			for sample in samples_list:
				samp_to_cond[sample] = condition

	# Get data
	data = request.json
	gene_symbol = data['gene_symbol']
	# print(gene_symbol)
	conditions = data['conditions']
	# print(conditions)

	# Create a new dataframe that maps each sample to its condition
	melted_dataframe = expression_dataframe.loc[gene_symbol].rename('logcpm').rename_axis('Sample').reset_index()
	melted_dataframe['Condition'] = melted_dataframe['Sample'].map(samp_to_cond)

	# Get plot dataframe
	plot_dataframe = melted_dataframe.groupby('Condition')['logcpm'].agg([np.mean, np.std, lambda x: list(x)])#.rename(columns={'<lambda>': 'points'})#.reindex(conditions)
	plot_dataframe = plot_dataframe.rename(columns={plot_dataframe.columns[-1]: 'points'})

	# Initialize figure
	fig = go.Figure()

	# Loop
	for condition in conditions:
		fig.add_trace(go.Box(name=condition, y=plot_dataframe.loc[condition, 'points'], boxpoints='all', pointpos=0))
	
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
