import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import dash_cytoscape as cyto
import networkx as nx

#%%

#import numpy # For Runtime purposes

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
])

if __name__ == '__main__':
    app.run_server(debug=False)
