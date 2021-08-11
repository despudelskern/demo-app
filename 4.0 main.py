import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import dash_cytoscape as cyto
import networkx as nx

from WikipediaArticle import WikipediaArticle

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

    html.P(id='tapNodeData'),
    html.P(id='tapEdgeData'),
    html.P(id='mouseoverNodeData'),
    html.P(id='mouseoverEdgeData'),

    # html.Div([
    cyto.Cytoscape(
            id='cytoscape',
            elements=[],
            style={
                'height': '350px',
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
              State('language-dropdown', 'value')])
def update_figure(n_klicks, topic, depth, lang):
    return createElements(topic, depth, lang)

# Layout
@app.callback(Output('cytoscape', 'layout'),
              [Input('dropdown-layout', 'value')])
def update_cytoscape_layout(layout):
    return {'name': layout}


# Text Output
@app.callback(Output('tapNodeData', 'children'),
              Input('cytoscape', 'tapNodeData'))
def displayTapNodeData(data):
    if data: return "You recently clicked/tapped the article: " + data['label']


@app.callback(Output('tapEdgeData', 'children'),
              Input('cytoscape', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data: return "You recently clicked/tapped the edge between " + data['source'].upper() + " and " + data['target'].upper()

@app.callback(Output('mouseoverNodeData', 'children'),
              Input('cytoscape', 'mouseoverNodeData'))
def displayHoverNodeData(data):
    if data: return data['label']

@app.callback(Output('mouseoverEdgeData', 'children'),
              Input('cytoscape', 'mouseoverEdgeData'))
def displayHoverEdgeData(data):
    if data: return "You recently hovered over the edge between " + data['source'].upper() + " and " + data['target'].upper()


if __name__ == '__main__':
    app.run_server(debug=False)