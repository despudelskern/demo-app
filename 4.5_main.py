import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx

from WikipediaArticle import WikipediaArticle

# pip install dash_bootstrap_components

#%%

elements = []

def createElements (title, tiefe, lang):
    all_articles = []
    all_searchTerms = []
    G = nx.Graph()
    seite = WikipediaArticle(search_term=title, language=lang)
    seite.search_and_set_page()
    all_articles.append(seite)
    all_searchTerms.append(title)
    G.add_node(seite)

    def buildGraph(seite, tiefe):
        if tiefe == 0: return
        seite.filter_links(3)
        for link in seite.links_filtered:
            curr_article = WikipediaArticle(search_term=link)
            curr_article.search_and_set_page()
            if curr_article.error==False:
                G.add_edge(seite,curr_article)
                if link not in all_searchTerms:
                    all_articles.append(curr_article)
                    all_searchTerms.append(link)
                    G.add_node(curr_article)
                    buildGraph(curr_article, tiefe-1)
        return
    buildGraph(seite, tiefe)

    elements = []

    for node in G.nodes():
        label = node.search_term
        id = all_searchTerms.index(node.search_term)
        eintrag = {'data': {'id': id, 'label': label}, 'locked': False}
        elements.append(eintrag)

    for edge in G.edges():
        node0 = edge[0]
        node1 = edge[1]
        id0 = all_searchTerms.index(node0.search_term)
        id1 = all_searchTerms.index(node1.search_term)
        eintrag = {'data': {'source': id0, 'target': id1}}
        elements.append(eintrag)

    return elements

def lock_elements (elements, locked):
    # global elements
    # for element in elements: element["locked"] = locked
    # print(elements)

    for element in elements: element["locked"] = locked
    return elements

#%%
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
# app = dash.Dash(__name__)
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

#%%

controls = dbc.Card(
    [
		# search term
        dbc.FormGroup(
            [
                dbc.Label("Search term "),
				dcc.Input(id='topic', type='text', placeholder='Search term', autoFocus=True),
            ]
        ),
		# depth
        dbc.FormGroup(
            [
                dbc.Label("Depth"),
                dbc.Input(id='Depth', type='number', placeholder='Set a depth') #value=2),
            ]
        ),
		# Language
        dbc.FormGroup(
            [
                dbc.Label("Language"),

				dcc.Dropdown(
		            id='dropdown_language',
		            options=[
		                {'label': 'english',
 		                 'value': 'en'},
		                {'label': 'french',
 		                 'value': 'fr'},
		                {'label': 'german',
 		                 'value': 'de'}
		            ], #value='en'
 					placeholder='Select a language'
		        ),
            ]
        ),
		#Layout
        dbc.FormGroup(
            [
                dbc.Label("Layout"),
				dcc.Dropdown(
		            id='dropdown_layout',
		            options=[
		                #{'label': 'random',
		                # 'value': 'random'},
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
		            ], value='cose',
		        ),
		#	],
            ]
        ),

		# button
        dbc.FormGroup(
            [#dbc.Label("Button"),
            dbc.Button(
                "Start", id="start-button", outline=True, color="primary", size="lg", className="mr-2", n_clicks=0
                )
				#html.Button(id='submit-button-state', n_clicks=0, children='Start'),
            ]
        ),
    ],
    body=True,
)

graph = dbc.Card(
    dbc.FormGroup([
            cyto.Cytoscape(
                id='cytoscape',
                autolock = False,
                elements=[],
                style={
                    'height': '350px',
                    'width': '100%'},
                stylesheet=default_stylesheet
            )
    ])
)



app.layout = html.Div([
    dbc.Container([
        html.H1("Map of Knowledge"),
        html.H2("Have fun with the progam!"),
        html.Hr(),
        dbc.Row([
                dbc.Col(controls, md=4),
                dbc.Col(graph, md=8)
            ], align="center"
        )
    ]),# fluid=True),
    html.Div([
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ]),
    html.Div([
        dcc.Interval(
            id='interval-component2',
            interval=1*100, # in milliseconds
            n_intervals=0
            )
    ]),
    html.Div(id='live-update-text'),
    html.P(id='intervall'),
    html.P(id='elli2'),
    html.P(id='elli')
])



# Graph
'''
@app.callback(Output('elli', 'children'),
              [Input('submit-button-state', 'n_clicks')],
              [State('topic', 'value'),
              State('depth', 'value'),
              State('dropdown-language', 'value')])
def update_figure(n_klicks, topic, depth, lang):
    global elements
    for i in range(0,10): elements = createElements(topic, i, lang)
    return str(elements)


@app.callback(Output('cytoscape', 'elements'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    # lock_elements(True)
    # el = elements
    # lock_elements(False)
    el = lock_elements(elements, False)
    return el
'''

@app.callback(Output('cytoscape', 'elements'),
              #Output('cytoscape', 'layout'),
              [Input('start-button', 'n_clicks'),
              Input('topic', 'value'),
              Input('Depth', 'value'),
              Input('dropdown_language', 'value')])#,
             # Input('dropdown_layout', 'value')])#,
            #  [State('topic', 'value'),
             # State('depth', 'value'),
              #State('dropdown_language', 'value'),
              #State('dropdown_language', 'value')])
def update_graph(n_clicks, topic, Depth, dropdown_language):
    return createElements(topic, Depth, dropdown_language)#dbc.Card(
#def update_cytoscape_layout(dropdown_layout):
#    return {'name': layout}


# Layout
@app.callback(Output('cytoscape', 'layout'),
              [Input('dropdown_layout', 'value')])
def update_cytoscape_layout(dropdown_layout):
    return {'name': dropdown_layout}



if __name__ == '__main__':
    app.run_server(debug=False, port=8060)
