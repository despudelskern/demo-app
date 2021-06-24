import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import networkx as nx



###########

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

########### Define your variables
beers=['Chesapeake Stout', 'Snake Dog IPA', 'Imperial Porter', 'Double Dog IPA']
ibu_values=[35, 60, 85, 75]
abv_values=[5.4, 7.1, 9.2, 4.3]
color1='darkred'
color2='orange'
mytitle='Beer Comparison'
tabtitle='beer!'
myheading='Flying Dog Beers'
label1='IBU'
label2='ABV'
githublink='https://github.com/austinlasseter/flying-dog-beers'
sourceurl='https://www.flyingdog.com/beers/'

########### Set up the chart
bitterness = go.Bar(
    x=beers,
    y=ibu_values,
    name=label1,
    marker={'color':color1}
)
alcohol = go.Bar(
    x=beers,
    y=abv_values,
    name=label2,
    marker={'color':color2}
)

beer_data = [bitterness, alcohol]
beer_layout = go.Layout(
    barmode='group',
    title = mytitle
)

beer_fig = go.Figure(data=beer_data, layout=beer_layout)


########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout
app.layout = html.Div(children=[
    html.H1(myheading),
    dcc.Graph(
        id='flyingdog',
        figure=beer_fig
    ),
    html.A('Code on Github', href=githublink),
    html.Br(),
    html.A('Data Source', href=sourceurl),
    ]
)

if __name__ == '__main__':
    app.run_server()
