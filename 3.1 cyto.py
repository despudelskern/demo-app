import networkx as nx
import plotly.graph_objects as go
from WikipediaArticle import WikipediaArticle

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output


all_articles = []
all_searchTerms = []
G = nx.Graph()
title = "Barack Obama"
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
buildGraph(seite, 3)
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
#,
#    {
#            'selector': 'Barack Obama',
#            'style': {
#                'background-color': 'red',
#                'line-color': 'red'
#            }
#        }
#'''
]


app.layout = html.Div([
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


#anpassen
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
    app.run_server(debug=True)
