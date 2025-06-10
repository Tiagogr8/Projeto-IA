import csv
from Node import Node
from Graph import Edge
from Courier import Courier
from Delivery import Delivery
import Graph

def read_nodes(csv_path):
    nodes = {}
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        for row in reader:
            if len(row) == 3:
                try:
                    node_id = row[0]
                    coordinates = (float(row[1]), float(row[2]))
                    nodes[node_id] = Node(node_id, coordinates)
                except ValueError as e:
                    print(f"Erro ao processar a linha: {row}. Erro: {e}")
            else:
                print(f"Linha inválida: {row}")
    return nodes



def read_edges(csv_path, graph):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        for row in reader:
            if len(row) >= 6:  # Ajustado para o número correto de colunas
                try:
                    u, v, oneway, length, geometry, name = row
                    graph.add_edge(Edge(u, v, oneway, length, geometry, name))
                except ValueError as e:
                    print(f"Erro ao processar a linha: {row}. Erro: {e}")
            else:
                print(f"Linha inválida: {row}")

def load_couriers_from_csv(filepath, lista_estafetas, graph, central_collection_point):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pula o cabeçalho se houver
        for row in reader:
            courier_id, transport_type, base_speed, max_weight = row
            courier = Courier(courier_id, transport_type, float(base_speed), float(max_weight), graph, central_collection_point)
            lista_estafetas.append(courier)
        return lista_estafetas

def load_deliveries_from_csv(filepath, lista_encomendas, central_collection_point):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pula o cabeçalho se houver
        for row in reader:
            delivery_id, destination_node, deadline, weight, volume = row
            delivery = Delivery(delivery_id, central_collection_point, destination_node, float(deadline), float(weight), float(volume))
            lista_encomendas.append(delivery)
        return lista_encomendas