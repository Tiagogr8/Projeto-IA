import osmnx as ox
import pandas as pd
import networkx as nx

# Configuração para utilizar a cidade de Braga
point = 41.5518, -8.4229

# Obter o grafo da região
graph = ox.graph_from_point(point, network_type="drive", dist=4000)

# Remover nós isolados manualmente
graph = nx.Graph(graph)  # Converter para um grafo não direcional se necessário
graph.remove_nodes_from(list(nx.isolates(graph)))

# Extrair nodes como GeoDataFrame
nodes = ox.graph_to_gdfs(graph, nodes=True, edges=False)

# Transformar o índice (identificador do nó) em uma coluna e renomear essa coluna
nodes.reset_index(inplace=True)
nodes.rename(columns={'index': 'osmid'}, inplace=True)

# Selecionar apenas as colunas desejadas para os nodes
selected_columns_nodes = ['osmid', 'x', 'y']
nodes_filtered = nodes[selected_columns_nodes]

# Salvar o DataFrame filtrado em um arquivo CSV, usando ';' como separador
nodes_filtered.to_csv('nodesBig.csv', sep=';', index=False)

# Preparar uma lista para armazenar os dados das arestas
edges_data = []

# Extrair as arestas e criar uma lista com os dados
for u, v, data in graph.edges(data=True):
    # Adicionar informações do nó de início, fim e outros dados da aresta
    data['u'] = u
    data['v'] = v
    edges_data.append(data)

# Criar um DataFrame com os dados das arestas
edges_df = pd.DataFrame(edges_data)

# Selecionar apenas as colunas desejadas para as edges
selected_columns_edges = ['u', 'v', 'oneway', 'length', 'geometry', 'name']
edges_filtered = edges_df[selected_columns_edges]

# Salvar o DataFrame filtrado em um arquivo CSV, usando ';' como separador
edges_filtered.to_csv('edgesBig.csv', sep=';', index=False)
