import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import dash_cytoscape as cyto
import networkx as nx

#%%
import wikipedia as wiki
#import numpy # For Runtime purposes

class WikipediaArticle():
	"""
	-- An Wikipedia Article --
	
	initialize with 
	WikipediaArticle(ARTICLE_NAME_HERE)

	to use given PAGE_NAME call 
	search_and_set_page() 

	then all attributes seen below in __init__ are usable:
	"""

	def __init__(self, search_term, language = "en"): 
		wiki.set_lang(language) 
		self.search_term = search_term

		self.page_name = None
		self.page = None

		self.links = None
		self.links_filtered = None
		self.references = None
		self.references_filtered = None
		self.categories = None
		self.categories_filtered = None
		self.content = None
		self.content_filtered = None

		self.title = None
		self.url = None
		self.summary = None

		self.error = False

	def search_and_set_page(self):
		self.page_name = self.search_term 

		try:
			print("TRYING: ", self.page_name, end=' ')	
			self.set_page()
			print("{*} SUCCESS")

		except wiki.DisambiguationError as e:
			best_guess = e.options[1] #Take the first of the options
			print("GUESSING: ", best_guess)

			self.page_name = best_guess
			self.set_page()

		except wiki.PageError as e:
			print("ERROR! Page doesnt exist:", self.page_name)
			self.error = True
			return

	def set_page(self): # Can be used directly if there is no disambiguation for sure
		self.page = wiki.page(self.page_name, auto_suggest=False) 
		self.summary = wiki.summary(self.page_name, auto_suggest=False)
		# Auto suggestion causes weird errors. Like "Dog" turning to "Do" in the search

	def filter(self, num): # Filter out data
		self.filter_links(num)
		#self.filter_content(num)
		#self.filter_references(num)
		#self.filter_categories(num)

	def filter_links(self, num):
		self.links_filtered = self.page.links[:num] # Get first ... links

		#self.links_filtered = numpy.array(self.page.links)[:num] 
		# Using numpy should be faster but isnt ... hmmm
	
	def filter_content(self, num):
		self.content_filtered = self.page.content[:num]

	def filter_references(self, num):
		self.references_filtered = self.page.references[:num]

	def filter_categories(self, num):
		self.categories_filtered = self.page.categories[:num]

#%%
def createElements (title, tiefe, lang):    
    all_articles = []
    all_searchTerms = []
    G = nx.Graph()
    seite = WikipediaArticle(search_term=title, language=lang)
    #seite = title
    seite.search_and_set_page()
    all_articles.append(seite)
    all_searchTerms.append(title)
    G.add_node(seite)
    
    def buildGraph(seite, tiefe):
        if tiefe == 0:
            return#void?
        seite.filter_links(5)
        for link in seite.links_filtered:
            curr_article = WikipediaArticle(search_term=link)
            curr_article.search_and_set_page()
            if curr_article.error==False:
                G.add_edge(seite,curr_article)
                if link not in all_searchTerms:
                    all_articles.append(curr_article)#was passiert, wenn artikel bereits vorhanden--> doppelt?
                    all_searchTerms.append(link)
                    G.add_node(curr_article)
                    buildGraph(curr_article, tiefe-1)
        return
    buildGraph(seite, tiefe)
    
    elements = []
    
    for node in G.nodes():
        label = node.search_term
        id = all_searchTerms.index(node.search_term)
        eintrag = {'data': {'id': id, 'label': label}}
        elements.append(eintrag)
    
    for edge in G.edges():
        node0 = edge[0]
        node1 = edge[1]
        id0 = all_searchTerms.index(node0.search_term)
        id1 = all_searchTerms.index(node1.search_term)
        eintrag = {'data': {'source': id0, 'target': id1}}
        elements.append(eintrag)
        
    return elements

#%%
app = dash.Dash(__name__)
server = app.server
app.title='MoK'

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

default_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)'
        }
    },
    {
        'selector': '[id = "0"]',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }
    },
    {
        'selector': 'edge',
        'style': {
        # The default curve style does not work with certain arrows
        'curve-style': 'bezier'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'target-arrow-color': 'lightblue',
            'target-arrow-shape': 'vee',
            'line-color': 'lightblue'
        }
    }
]

# define layout
app.layout = html.Div([
    
    html.H1("Map of Knowledge"),
    html.Div("Have fun with the progam!"),
    html.Br(),    
    
    dcc.Input(id='topic', type='text', value='hallo', autoFocus=True),
    dcc.Input(id='depth', type='number', value=2),
    
    # Language Dropdown
    dcc.Dropdown(
            id='language-dropdown',
            options=[
                {'label': 'english',
                 'value': 'en'},
                {'label': 'french',
                 'value': 'fr'},
                {'label': 'german',
                 'value': 'de'}
            ], value='en'
        ),
    
    # Layout Dropdown
    dcc.Dropdown(
            id='dropdown-layout',
            options=[
                {'label': 'random',
                 'value': 'random'},
                {'label': 'grid',
                 'value': 'grid'},
                {'label': 'circle',
                 'value': 'circle'},
                {'label': 'concentric',
                 'value': 'concentric'},
                {'label': 'breadthfirst',
                 'value': 'breadthfirst'},
                {'label': 'cose',
                 'value': 'cose'}
            ], value='cose'
        ),
    
    html.Button(id='submit-button-state', n_clicks=0, children='Start'),

    # html.Div([
    cyto.Cytoscape(
            id='cytoscape',
            elements=[],
            style={
                'height': '450px',
                'width': '100%'},
            stylesheet=default_stylesheet
        )
    # ])
])

# Graph
@app.callback(Output('cytoscape', 'elements'),
              [Input('submit-button-state', 'n_clicks')],
              [State('topic', 'value'),
              State('depth', 'value'),
              State('language-dropdown', 'value')]
              )
def update_figure(n_klicks, topic, depth, lang):
    return createElements(topic, depth, lang)


# Layout
@app.callback(Output('cytoscape', 'layout'),
              [Input('dropdown-layout', 'value')])
def update_cytoscape_layout(layout):
    return {'name': layout}



if __name__ == '__main__':
    app.run_server(debug=False)
