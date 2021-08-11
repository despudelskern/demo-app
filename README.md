# Map of Knowledge

## Official release:
https://map-of-knowledge.herokuapp.com/

## Zielsetzung
Das Erstellen eines Netzwerkes zur Wikipedia-Visualisierung

Mit Hilfe einer Wikipedia API sollen Links auf den jeweiligen Wikipediaseiten ausgelesen werden und anschließend grafisch visualisiert werden.

In diesem Zusammenhang wollen wir diese Features miteinbauen:

* Eingabe des Suchbegriffs, der Sprache und Tiefe sollen individuell erfolgen,

* zur Benutzung wollen wir eine grafische Oberfläche ,

* (nach der Wichtigkeit der Links filtern)

### Graph im Webbrowser darstellen

Um unseren Graphen auch graphisch darzustellen nutzen wir Dash. Dash ist eine Anwendung von plotly, in der in unserem Fall mit Python programmiert werden kann und

Falls ihr mehr über Dash erfahren wollt, findet ihr [hier](https://dash.plotly.com/) mehr Informationen dazu.

Dash arbeitet lokal, das bedeutet die grafische Visualisierung

Dash Cytoscape auch erwähnen?
veröffentlichen

Um das Ganze anschließend zu veröffentlichen, also auf eine Webseite zu bringen, nutzen wir Heroku. 
