import math
import heapq
from queue import Queue
import plotly.graph_objects as go
import re
import time
import random


class Edge:
    def __init__(self, u, v, oneway, length, geometry, name):
        self.u = u  # Node inicial
        self.v = v  # Node final
        self.oneway = oneway == 'True'  # Rua de sentido unico
        self.length = float(length) if length else 0.0  # Comprimento da estrada em metros
        self.custo = float(length) if length else 0.0
        self.geometry = geometry
        self.name = name  # Nome da rua


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, node):
        self.nodes[node.node_id] = node
        if node.node_id not in self.edges:
            self.edges[node.node_id] = []

    def add_edge(self, edge):
        self.edges[edge.u].append(edge)
        reverse_edge = Edge(edge.v, edge.u, edge.oneway,
                            edge.length, edge.geometry, edge.name)
        self.edges[edge.v].append(reverse_edge)
        """if not edge.oneway:
            # Se a rua não é de sentido único, adicionar a areta inversa
            reverse_edge = Edge(edge.v, edge.u, edge.oneway,
                                edge.length, edge.geometry, edge.name)
            self.edges[edge.v].append(reverse_edge)"""

    def clone(self):
        new_graph = Graph()
        new_graph.nodes = self.nodes.copy()
        new_graph.edges = {}
        for node_id, edges in self.edges.items():
            new_graph.edges[node_id] = [Edge(edge.u, edge.v, edge.oneway, edge.length, edge.geometry, edge.name) for edge in edges]
        return new_graph

    def cortar_estrada(self):
        u = input("Insira o ID do nodo inicial da estrada a cortar: ")
        v = input("Insira o ID do nodo final da estrada a cortar: ")

        if u in self.edges and v in self.edges:
            # Remove a aresta u -> v
            self.edges[u] = [edge for edge in self.edges[u] if edge.v != v]
            self.edges[v] = [edge for edge in self.edges[v] if edge.u != u]
            print(f"Estrada entre {u} e {v} cortada.")
        else:
            print("Estrada não encontrada.")

        return self

    def adicionar_transito(self):
        u = input("Insira o ID do nodo inicial da estrada com trânsito: ")
        v = input("Insira o ID do nodo final da estrada com trânsito: ")
        aumento_percentual = float(
            input("Insira a percentagem de aumento no custo da estrada devido ao trânsito (exemplo: 50 para 50%): "))

        if aumento_percentual < 0:
            print("A percentagem de aumento deve ser um valor não negativo.")
            return self
        if u in self.edges:
            estrada_encontrada = False
            for edge in self.edges[u]:
                if edge.v == v:
                    aumento = edge.length * (aumento_percentual / 100.0)
                    edge.custo += aumento
                    estrada_encontrada = True
                    print(
                        f"Trânsito adicionado na estrada de {u} para {v} com um aumento de {aumento_percentual}%. Novo custo: {edge.custo:.2f} metros.")
                    break
            if not estrada_encontrada:
                print("Estrada não encontrada.")
        else:
            print("Estrada não encontrada.")
        return self

    def atualizar_ponto_recolha(self):
        novo_ponto = input("Insira o ID do novo ponto de recolha: ")
        if novo_ponto in self.nodes:

            return novo_ponto
        else:
            print("Ponto de recolha não encontrado no grafo.")
            return None

    # Ver arestas dos grafos (Ruas)
    def ver_arestas(self):
        graph = self
        print("Arestas do Grafo:")
        for u in graph.edges:
            for edge in graph.edges[u]:
                u, v, custo, nome = edge.u, edge.v, edge.length, edge.name
                nome = nome or "Nome não disponível"
                print(f"De {u} para {v}: {custo} metros, Rua: {nome}")

    def heuristic(self, node1_id, node2_id):
        node1 = self.nodes[node1_id]
        node2 = self.nodes[node2_id]
        lat1, lon1 = node1.coordinates
        lat2, lon2 = node2.coordinates

        # Conversão de graus para radianos
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Fórmula de Haversine para cálculo de distância em linha reta
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Raio médio da Terra em quilômetros
        R = 6371.0
        distance = R * c

        return distance

    # Ver arestas de um caminho
    def get_edges_along_path(self, path):
        edges = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            for edge in self.edges[u]:
                if edge.v == v:
                    edges.append(edge)
                    break
        return edges

    def apply_traffic_conditions(self,transport):
        # Aplicar condições de tráfego a todas as arestas

        if transport != 'Bicicleta':
            for node_id in self.edges:
                for edge in self.edges[node_id]:
                    traffic = random.choice(["Normal", "Congestionado", "Leve"])
                    if traffic == "Congestionado":
                        if transport == 'Carro':
                            edge.custo = edge.length * 1.5
                        if transport == 'Moto':
                            edge.custo = edge.length * 1
                    elif traffic == "Leve":
                        if transport == 'Carro':
                            edge.custo = edge.length * 0.8
                        if transport == 'Moto':
                            edge.custo = edge.length * 0.3

    ############################################################################################################################################
    ###########################################         Algoritmos             #################################################################
    ############################################################################################################################################

    def procura_BFS(self, start, end):
        start_time = time.time()
        visited = set()
        fila = Queue()
        fila.put(start)
        visited.add(start)
        parent = {start: None}
        max_space = 1

        while not fila.empty():
            max_space = max(max_space, fila.qsize() + len(visited) + len(parent))

            nodo_atual = fila.get()
            if nodo_atual == end:
                break

            for edge in self.edges.get(nodo_atual, []):
                adjacente = edge.v
                if adjacente not in visited:
                    if adjacente == end:
                        parent[adjacente] = nodo_atual
                        fila = Queue()  # Esvazia a fila para terminar o loop
                        break
                    fila.put(adjacente)
                    parent[adjacente] = nodo_atual
                    visited.add(adjacente)

        path = []
        if end in parent:  # Se um caminho foi encontrado
            while end is not None:
                path.append(end)
                end = parent[end]
            path.reverse()
            custo = sum(edge.custo for edge in self.get_edges_along_path(path))
        else:
            custo = 0
        execution_time = time.time() - start_time
        return path, custo, max_space, execution_time

    def procura_DFS(self, start, end):
        start_time = time.time()
        visited = set()
        stack = [start]
        parent = {start: None}
        max_space = 1

        while stack:
            max_space = max(max_space, len(stack) + len(visited) + len(parent))

            current = stack.pop()
            if current == end:
                parent[end] = parent.get(current)  # Certifica-se de que o end está em parent
                break

            if current not in visited:
                visited.add(current)
                for edge in self.edges.get(current, []):
                    if edge.v not in visited:
                        stack.append(edge.v)
                        parent[edge.v] = current

        path = []
        if end in parent:  # Se um caminho foi encontrado
            while end is not None:
                path.append(end)
                end = parent[end]
            path.reverse()
            custo = sum(edge.custo for edge in self.get_edges_along_path(path))
        else:
            custo = 0
        execution_time = time.time() - start_time
        return path, custo, max_space, execution_time

    def greedy_best_first_search(self, start, end):
        start_time = time.time()
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {node: float('inf') for node in self.nodes}
        g_score[start] = 0
        max_space = 0

        while open_set:
            max_space = max(max_space, len(open_set) + len(came_from) + len(g_score))
            current = heapq.heappop(open_set)[1]

            if current == end:
                path = [end]
                while current != start:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                custo = g_score[end]
                execution_time = time.time() - start_time
                return path, custo, max_space, execution_time

            for edge in self.edges[current]:
                neighbor = edge.v
                tentative_g_score = g_score[current] + edge.custo
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    if not any(neighbor == n[1] for n in open_set):
                        heapq.heappush(open_set, (self.heuristic(neighbor, end), neighbor))
        execution_time = time.time() - start_time
        return [], 0, max_space, execution_time

    def a_star_search(self, start, end):
        start_time = time.time()
        open_set = []
        open_set_hash = set()
        heapq.heappush(open_set, (0, start))
        open_set_hash.add(start)
        came_from = {}
        g_score = {node: float('inf') for node in self.nodes}
        g_score[start] = 0
        f_score = {node: float('inf') for node in self.nodes}
        f_score[start] = self.heuristic(start, end)

        max_space = 0

        while open_set:
            max_space = max(max_space, len(open_set) + len(came_from) + len(g_score) + len(f_score))
            current = heapq.heappop(open_set)[1]
            open_set_hash.remove(current)

            if current == end:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                execution_time = time.time() - start_time
                return path, g_score[end], max_space, execution_time

            for edge in self.edges[current]:
                neighbor = edge.v
                tentative_g_score = g_score[current] + edge.custo
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, end)
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)

        execution_time = time.time() - start_time
        return [], 0, max_space, execution_time

############################################################################################################################################
#######################################         Desenhar Grafo             #################################################################
############################################################################################################################################
    def parse_linestring(linestring):
        coords = re.findall(r"(\-?\d+\.\d+)\s+(\-?\d+\.\d+)", linestring)
        return [(float(x), float(y)) for x, y in coords]

    def midpoint(point1, point2):
        return [(point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2]

    def desenhar_grafo(self, pontoCentral):
        fig = go.Figure()
        arestas_desenhadas = set()

        # Desenhar arestas
        for node_id, edges in self.edges.items():
            for edge in edges:
                if (edge.u, edge.v) in arestas_desenhadas or (edge.v, edge.u) in arestas_desenhadas:
                    continue

                line_coords = Graph.parse_linestring(edge.geometry)
                arestas_desenhadas.add((edge.u, edge.v))  # Marcar a aresta como desenhada

                if line_coords:
                    x_coords, y_coords = zip(*line_coords)
                    mid_pt = Graph.midpoint(line_coords[0], line_coords[-1])

                    fig.add_trace(
                        go.Scatter(x=x_coords, y=y_coords, mode='lines', name=edge.name, line=dict(color='grey')))

                    fig.add_trace(go.Scatter(
                        x=[mid_pt[0]], y=[mid_pt[1]],
                        text=[f'{edge.name} ({edge.custo:.2f} m)'],
                        mode='text', showlegend=False, textposition='bottom center', textfont=dict(size=5)))
                else:
                    start_node = self.nodes[edge.u]
                    end_node = self.nodes[edge.v]
                    mid_pt = Graph.midpoint(start_node.coordinates, end_node.coordinates)

                    fig.add_trace(go.Scatter(
                        x=[start_node.coordinates[0], end_node.coordinates[0]],
                        y=[start_node.coordinates[1], end_node.coordinates[1]],
                        mode='lines', name=edge.name, line=dict(color='grey')))

                    fig.add_trace(go.Scatter(
                        x=[mid_pt[0]], y=[mid_pt[1]],
                        text=[f'{edge.name} ({edge.custo:.2f} m)'],
                        mode='text', showlegend=False, textposition='bottom center', textfont=dict(size=5)))


        for node_id, node in self.nodes.items():
            if node_id == pontoCentral:
                fig.add_trace(
                    go.Scatter(x=[node.coordinates[0]], y=[node.coordinates[1]],
                               text=[f'CENTRAL = {node_id}'], mode='markers+text', textposition='top center',
                               marker=dict(color='red', size=10), textfont=dict(color='green', size=6),
                               showlegend=False))
            else:
                fig.add_trace(
                    go.Scatter(x=[node.coordinates[0]], y=[node.coordinates[1]],
                               text=[node_id], mode='markers+text', textposition='top center',
                               marker=dict(color='blue', size=5), textfont=dict(size=5), name=f'Node {node_id}'))

        # Configurações do layout
        fig.update_layout(title='Grafo', hovermode='closest', showlegend=False,
                          xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        fig.show()