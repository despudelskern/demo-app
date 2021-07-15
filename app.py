import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto

import plotly.graph_objs as go
import networkx as nx

# Wikipedia Klasse
##############################################################################


'''
Requires
pip install wikipedia
OR
pip install git+https://github.com/lucasdnd/Wikipedia.git

'''


import wikipedia as wiki

class WikipediaArticle():
	""""An Article"""

	def __init__(self, search_term, language = "en", \
		page_name = None, links = None, links_filtered = None, page = None, content = None, \
		content_filtered = None, title = None, url = None, references = None, \
		references_filtered = None, categories = None, categories_filtered = None, \
		summary = None, error = False):
		# Weird init attributes are needed to recreate article from JSON
		# Because of the "keywords arguments" (**kwargs)


		wiki.set_lang(language)

		self.search_term = search_term
		self.page_name = page_name
		self.page = page


		self.links = links
		self.links_filtered = links_filtered
		self.references = references
		self.references_filtered = references_filtered
		self.categories = categories
		self.categories_filtered = categories_filtered
		self.content = content
		self.content_filtered = content_filtered

		self.title = title
		self.url = url
		self.summary = summary

		self.error = error

	def search_and_set_page(self):
		search_results = wiki.search(self.search_term)

		self.page_name = search_results[0]
		print("LOOKING UP: ", self.page_name)

		try:
			self.set_page()

		except wiki.DisambiguationError as e:
			best_guess = e.options[1] #Take the first of the options
			print("GUESSING: ", best_guess)

			self.page_name = best_guess
			self.set_page()

		except wiki.PageError as e:
			print("ERROR! Page doesnt exist:", self.page_name)
			self.error = True
			return

		self.remove_page_attr()
		# self.page Object cannot be converted to JSON, so we have to delete it


	def set_page(self): # Can be used directly if there is no disambiguation for sure
		self.page = wiki.page(self.page_name)
		self.summary = wiki.summary(self.page_name)

	def filter(self, num): # Filter out data
		self.filter_links(num)
		self.filter_content(num)
		self.filter_references(num)
		self.filter_categories(num)

	def filter_links(self, num):
		self.links_filtered = self.links[:num] # Get first ... links

	def filter_content(self, num):
		self.content_filtered = self.content[:num]

	def filter_references(self, num):
		self.references_filtered = self.references[:num]

	def filter_categories(self, num):
		self.categories_filtered = self.categories[:num]

	def remove_page_attr(self):
		# self.page Object cannot be converted to JSON, so we have to delete it and reassign
		self.links = self.page.links
		self.content = self.page.content
		self.title = self.page.title
		self.url = self.page.url
		try:
			self.references = self.page.references
		except KeyError as e:
			print(e)
		self.categories = self.page.categories

		self.page = None


###############################################################################
# Zufälliges Netzwerk; weg damit
def generate_network(n):
    '''
    Generates a random geometric graph with n nodes. Analyzes the edges and
    nodes, so that corresponding graphs can be generated. The function returns
    the graphs.
    @param n: Anzahl der Knoten.
    '''
    G = nx.random_geometric_graph(n, 0.2)   # erzeugt einen zufälligen Graphen mit n Knoten

    edge_x = []
    edge_y = []
    for edge in G.edges():                  # hier werden Kanten aus dem Graph extrahiert
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(        # erzeugt den Plot der die Kanten darstellt
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():          # hier werden Knoten aus dem Graph extrahiert
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(         # erzeugt den Plot der die Knoten darstellt
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(                # bestimmt nur das aussehen der Knoten
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    # in diesem Teil wird bestimmt, wie viele Verbindungen jeder Knoten hat
    # das ist in den G.adjaceny() gespreichert
    node_adjacencies = []
    node_text = []
    for adjacencies in G.adjacency():
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: '+str(len(adjacencies[1])))

    # die Farbe der Knoten wird auf die Anzahl an Verbindungen gesetzt
    node_trace.marker.color = node_adjacencies

    # der Text der bei Hover angezeigt wird ist der node_text
    node_trace.text = node_text

    return [edge_trace, node_trace] #ausgegeben werden die beiden Plots / Traces


# Erzeuge den Anfangsplot
fig = go.Figure(data=generate_network(64),  # hier wird die Funktion von oben benutzt
              layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40), # ab hier nur Styling
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

##############################################################################

## Ich brauche die Variable
# fig = go.Figure(data=, layout=)


all_articles = []
all_searchTerms = []
G = nx.Graph()
title = "Barack Obam"
seite = WikipediaArticle(search_term=title)
#seite = title
seite.search_and_set_page()
all_articles.append(seite)
all_searchTerms.append(title)
G.add_node(seite)

def buildGraph(seite, tiefe):
    if tiefe == 0:
        return#void?
    seite.filter_links(3)
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
buildGraph(seite, 1)
#print(G.adj)
#for article in all_articles:
    #print(article.search_term)

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


#===============================================================================
# visualisation with dash

app = dash.Dash(__name__)


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
    }
]




# Initiate the app
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title='MoK'



# App Layout
app.layout = html.Div([
    html.H1("Map of Knowledge"),
    html.Div("Have fun with the progam!"),
    html.Div("You can enter your search term in the first box and the depth into the second box."),
    html.Br(),
    dcc.Input(id='topic', type='text', value='None', autoFocus=True),
    dcc.Input(id='depth', type='number', value=64),
    
    dcc.Input(
        id='my_txt_input',
        type='text',
        value='en',
        debounce=True,           # changes to input are sent to Dash server only on enter or losing focus
        pattern=r"^[A-Za-z].*",  # Regex: string must start with letters only
        inputMode='latin',       # provides a hint to browser on type of data that might be entered by the user.
        name='text',             # the name of the control, which is submitted with the form data
        list='options',          # identifies a list of pre-defined options to suggest to the user
    ),
    
    html.Button(id='submit-button-state', n_clicks=0, children='Start'),
    
    html.Datalist(id='options', children=[
        html.Option(value="en"),
        html.Option(value="de"),
        html.Option(value="fr")
    ]),
    
    html.Div(id='output-state'),
    html.Br(),
    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    
    cyto.Cytoscape(
        id='cytoscape-event-callbacks-2',
        layout={'name': 'cose'},
        elements=elements,
        stylesheet=default_stylesheet,
        style={'width': '100%', 'height': '450px'}
    ),
    html.P(id='cytoscape-tapNodeData-output'),
    html.P(id='cytoscape-tapEdgeData-output'),
    html.P(id='cytoscape-mouseoverNodeData-output'),
    html.P(id='cytoscape-mouseoverEdgeData-output')
])

#===============================================================================
# Callbacks - Interaktion mit der Benutzeroberfläche

# Mit @ wird ein sogenannter "Decorater" benutzt.
# Der Decorator führt dazu, dass die Funktion, die darunter deklariert wird
# (hier update_output) die Funktionalität des Decorators erhält.
# Hier werden Input, Output, State vom Paket dash.dependencies verwendet (siehe import).
# Wichtig ist, dass Inputs und Outputs mit den Argumenten und Returns der Funktion zusammenpassen!


@app.callback(Output('output-state', 'children'),
              [Input('submit-button-state', 'n_clicks'),
               Input('my_txt_input', 'value')],
              [State('topic', 'value'),
              State('depth', 'value')]
             )

def update_output(n_clicks, lang, input1, input2):
    '''
    displays the user inputs on the page
    @param n_clicks: [Integer] Anzahl, wie oft Programm gestartet wurde
    @param input1: [String] Suchbegriff
    @param input2: [Integer] Tiefe
    '''

    return u'''
        The program was started {} times,\n
        language is "{}", the topic is "{}",
        and the depth is "{}"
    '''.format(n_clicks, lang, input1, input2)



@app.callback(Output('example-graph', 'figure'),
              [Input('submit-button-state', 'n_clicks')],
              [State('topic', 'value'),
              State('depth', 'value')]
             )

def update_figure(n_klicks, topic, depth):
    '''
    generates a random network and corresponding plots
    figure is updated with the new plots.
    @param n_klicks: Wie oft wurde Button gedrückt.
    @param topic: [String] Suchbegriff
    @param depth: [Integer] Tiefe
    '''
    fig = go.Figure(data=generate_network(depth),
                    layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig

@app.callback(Output('cytoscape-tapNodeData-output', 'children'),
              Input('cytoscape-event-callbacks-2', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        return "You recently clicked/tapped the city: " + data['label']


@app.callback(Output('cytoscape-tapEdgeData-output', 'children'),
              Input('cytoscape-event-callbacks-2', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "You recently clicked/tapped the edge between " + data['source'].upper() + " and " + data['target'].upper()


@app.callback(Output('cytoscape-mouseoverNodeData-output', 'children'),
              Input('cytoscape-event-callbacks-2', 'mouseoverNodeData'))
def displayTapNodeData(data):
    if data:
        return "You recently hovered over the city: " + data['label']


@app.callback(Output('cytoscape-mouseoverEdgeData-output', 'children'),
              Input('cytoscape-event-callbacks-2', 'mouseoverEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "You recently hovered over the edge between " + data['source'].upper() + " and " + data['target'].upper()



if __name__ == '__main__':
    app.run_server()
