from Delivery import Delivery
from Courier import Courier
from Graph import Graph
from DeliveryService import DeliveryService
from parser import load_couriers_from_csv, load_deliveries_from_csv, read_edges, read_nodes
import tkinter as tk
import matplotlib.pyplot as plt

root = tk.Tk()
root.title("Encomenda")
root.withdraw()

# Grafo para indicarmos no mapa o ponto de entrega das encomendas
class GraphApp:
    def __init__(self, master, graph):
        self.master = master
        self.graph = graph
        self.setup_ui(master)
    def setup_ui(self, master):
        master.title("Seleção de Localização de Encomendas no Grafo")
        self.canvas = tk.Canvas(master, width=800, height=600)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.confirm_button = tk.Button(master, text="Confirmar Seleção", command=self.confirm_selection)
        self.confirm_button.pack()
        self.instruction_label = tk.Label(master, text="Clique no mapa para selecionar o nó de partida")
        self.instruction_label.pack()
        self.draw_graph()

    def normalize_coordinates(self, x, y):
        norm_x = (x - self.min_x) / (self.max_x - self.min_x) * 800
        norm_y = (y - self.min_y) / (self.max_y - self.min_y) * 600
        return norm_x, norm_y

    def draw_graph(self):
        self.calculate_boundaries()
        for node_id, node in self.graph.nodes.items():
            x, y = self.normalize_coordinates(*node.coordinates)
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="blue")

        for node_id, edges in self.graph.edges.items():
            for edge in edges:
                self.draw_edge(edge)

    def calculate_boundaries(self):
        x_coords, y_coords = zip(*[node.coordinates for node in self.graph.nodes.values()])
        self.min_x, self.max_x = min(x_coords), max(x_coords)
        self.min_y, self.max_y = min(y_coords), max(y_coords)

    def draw_edge(self, edge):
        if edge.geometry:
            points = Graph.parse_linestring(edge.geometry)
            norm_points = [self.normalize_coordinates(x, y) for x, y in points]
            flat_points = [val for pair in norm_points for val in pair]

            if len(flat_points) >= 4:
                self.canvas.create_line(*flat_points, fill="black")
                mid_index = len(norm_points) // 2
                midpoint_x, midpoint_y = norm_points[mid_index]
                self.canvas.create_text(midpoint_x, midpoint_y, text=edge.name, fill="black", font=("Arial", 5))
        else:
            start_x, start_y = self.normalize_coordinates(*self.graph.nodes[edge.u].coordinates)
            end_x, end_y = self.normalize_coordinates(*self.graph.nodes[edge.v].coordinates)
            self.canvas.create_line(start_x, start_y, end_x, end_y, fill="black")
            midpoint_x, midpoint_y = (start_x + end_x) / 2, (start_y + end_y) / 2
            self.canvas.create_text(midpoint_x, midpoint_y, text=edge.name, fill="black", font=("Arial", 5))

    def on_canvas_click(self, event):
        if self.selected_destination_node is not None:
            return

        x, y = event.x, event.y
        clicked_node = self.find_closest_node(x, y)

        self.selected_destination_node = clicked_node
        print(f"Nó de destino selecionado: {self.selected_destination_node}")
        self.confirm_selection()

    def get_selected_nodes(self):
        return self.selected_destination_node

    def find_closest_node(self, x, y):
        closest_node = None
        min_dist = float('inf')
        for node_id, node in self.graph.nodes.items():
            norm_x, norm_y = self.normalize_coordinates(node.coordinates[0], node.coordinates[1])
            dist = ((x - norm_x) ** 2 + (y - norm_y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_node = node_id
        return closest_node

    def confirm_selection(self):
        self.selection_confirmed = True
        self.master.quit()

    def open_window(self):
        self.selected_destination_node = None
        self.selection_confirmed = False
        self.master.mainloop()
        if not self.selection_confirmed:
            return None
        return self.selected_destination_node

    def close_window(self):
        if self.master.winfo_exists():
            self.master.destroy()

################################################################################################################################################################################################
################################################################################################################################################################################################

def view_deliveries(deliveries):
    if not deliveries:
        print("Não há encomendas para exibir.")
        return

    print("\nLista de Encomendas:")
    for delivery in deliveries:
        print(f"ID: {delivery.delivery_id}, Início: {delivery.collection_point}, Destino: {delivery.destination_node}, "
              f"Prazo: {delivery.deadline}h, Peso: {delivery.weight}kg, Volume: {delivery.volume}, "
              f"Status: {delivery.status}, Avaliação: {delivery.customer_rating or 'Não avaliada'}")

def view_couriers(couriers):
    if not couriers:
        print("Não há estafetas para exibir.")
        return

    print("\nLista de Estafetas:")
    for courier in couriers:
        print(
            f"ID: {courier.courier_id}, Tipo de Transporte: {courier.transport_type}, Velocidade Base: {courier.base_speed}km/h, Velocidade Atual: {courier.speed}km/h, "
            f"Carga Máxima: {courier.max_weight}kg,  Carga Atual: {courier.current_load}kg,Ponto Atual: {courier.current_node}, Score: {courier.score:.2f}")



# Funcao para adicionar uma encomenda à lista de encomendas
def add_delivery(graph, central_collection_point):
    escolha_no = input("Deseja digitar o nó de destino (1) ou selecionar no mapa (2)? ")
    destination_node = None

    if escolha_no == '1':
        destination_node = input("Digite o nó de destino: ")
    elif escolha_no == '2':
        toplevel = tk.Toplevel(root)
        graph_app = GraphApp(toplevel, graph)
        print("Clique no mapa para selecionar o nó de destino.")
        destination_node = graph_app.open_window()  # Ignora o nó de partida
        graph_app.close_window()
        if destination_node is None:
            print("Seleção cancelada.")
            return

    if destination_node:
        print("Adicionando nova encomenda.")
        delivery_id = input("Digite o ID da encomenda: ")
        try:
            deadline = float(input("Digite o prazo (em horas): "))
            weight = float(input("Digite o peso da encomenda: "))
            volume = float(input("Digite o volume da encomenda: "))
            nova_encomenda = Delivery(delivery_id, central_collection_point, destination_node, deadline, weight, volume)
            return nova_encomenda
        except ValueError:
            print("Erro: Entrada inválida. A encomenda não foi adicionada.")
    else:
        print("Seleção de nó de destino inválida. A encomenda não foi adicionada.")


# Funcao para adiconar um estafeta à lista de estafetas
def add_courier(graph, central_collection_point):
    print("\nAdicionar Estafeta:")
    courier_id = input("ID do Estafeta: ")
    transport_type = input("Tipo de Transporte (Bicicleta/Moto/Carro): ")
    try:
        base_speed = float(input("Velocidade Base (km/h): "))
        max_weight = float(input("Peso Máximo de Carga (kg): "))
        courier = Courier(courier_id, transport_type, base_speed, max_weight, graph, central_collection_point)
        print(f"Estafeta {courier_id} adicionado com sucesso.")
        return courier
    except ValueError:
        print("Erro: Entrada inválida. O estafeta não foi adicionado.")


def menu_grafo(graph, central):
    while True:
        print("\nMenu do Grafo:")
        print("1. Desenhar Grafo")
        print("2. Ver Nodes")
        print("3. Ver Arestas")
        print("4. Carregar Grafo de CSV")
        print("5. Cortar Estrada")
        print("6. Adicionar Transito")
        print("7. Atualizar ponto de recolha")
        print("0. Voltar ao Menu Principal")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            graph.desenhar_grafo(central)
        elif escolha == '2':
            print(graph.nodes)
        elif escolha == '3':
            graph.ver_arestas()
        elif escolha == '4':
            nodes_filepath = input("Insira o path dos nodes: ")
            edges_filepath = input("Insira o path das edges: ")
            graph = Graph()
            nodes = read_nodes(nodes_filepath)
            for node in nodes.values():
                graph.add_node(node)
            read_edges(edges_filepath, graph)
            print("Grafo carregado com sucesso!")
        elif escolha == '5':
            graph.cortar_estrada()
        elif escolha == '6':
            graph.adicionar_transito()
        elif escolha == '7':
            novo_ponto = input("Insira o ID do novo ponto de recolha: ")
            if novo_ponto in graph.nodes:
                central = novo_ponto
            else:
                print("Ponto de recolha não encontrado no grafo.")
        elif escolha == '0':
            break
    return graph,central


def simulate(delivery_service):
    custos_totais = {alg: 0 for alg in ["BFS", "DFS", "Greedy", "A*"]}
    tempos_totais = {alg: 0 for alg in ["BFS", "DFS", "Greedy", "A*"]}
    espacos_totais = {alg: 0 for alg in ["BFS", "DFS", "Greedy", "A*"]}
    numero_entregas = 0

    for courier in delivery_service.couriers:
        courier.graph = delivery_service.graph.clone()
        courier.graph.apply_traffic_conditions(courier.transport_type)

    for courier in delivery_service.couriers:
        _, _, resultados = delivery_service.calculate_route_for_courier(courier)
        numero_entregas += len(courier.deliveries)
        for alg, resultado in resultados.items():
            custos_totais[alg] += resultado['custo']
            tempos_totais[alg] += resultado['tempo']
            espacos_totais[alg] += resultado['espaco']

    custos_medios = {alg: custo / numero_entregas for alg, custo in custos_totais.items()}
    tempos_medios = {alg: tempo / numero_entregas for alg, tempo in tempos_totais.items()}
    espacos_medios = {alg: espaco / numero_entregas for alg, espaco in espacos_totais.items()}

    criar_grafico_comparativo(custos_medios, tempos_medios, espacos_medios)

    for delivery in delivery_service.deliveries:
        if delivery.status == 'Atribuída':
            courier = next((c for c in delivery_service.couriers if c.courier_id == delivery.assigned_to), None)
            delivery.update_status('Concluída')
            delivery.calcular_preco(courier.transport_type)
    # Avaliação das Entregas
    delivery_service.evaluate_deliveries()
    # Atualização do Score dos Estafetas
    for courier in delivery_service.couriers:
        courier.update_score()
        print(f"Score atualizado do estafeta {courier.courier_id}: {courier.score:.2f}")


def criar_grafico_comparativo(custos_medios, tempos_medios, espacos_medios):
    algoritmos = list(custos_medios.keys())
    custos = list(custos_medios.values())
    tempos = list(tempos_medios.values())
    espacos = list(espacos_medios.values())

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))

    # Gráfico de Custo Médio
    axes[0].bar(algoritmos, custos, color=['blue', 'green', 'purple', 'red'])
    axes[0].set_title('Custo')
    axes[0].set_xlabel('Algoritmos')
    axes[0].set_ylabel('Custo')

    # Gráfico de Tempo Médio
    axes[1].bar(algoritmos, tempos, color=['blue', 'green', 'purple', 'red'])
    axes[1].set_title('Tempo')
    axes[1].set_xlabel('Algoritmos')
    axes[1].set_ylabel('Tempo')

    # Gráfico de Espaço Médio
    axes[2].bar(algoritmos, espacos, color=['blue', 'green', 'purple', 'red'])
    axes[2].set_title('Espaço')
    axes[2].set_xlabel('Algoritmos')
    axes[2].set_ylabel('Espaço')

    plt.tight_layout()
    plt.show()



def menu(graph):
    lista_encomendas = []
    lista_estafetas = []
    delivery_service = DeliveryService(graph)
    ponto_recolha = '245058608'

    while True:
        print("\nMenu Principal:")
        print("1. Menu do Grafo")
        print("2. Adicionar Encomenda")
        print("3. Adicionar Estafeta")
        print("4. Carregar Encomendas de CSV")
        print("5. Carregar Estafetas de CSV")
        print("6. Atribuir Entregas")
        print("7. Iniciar Simulação")
        print("8. Ver Encomendas")
        print("9. Ver Estafetas")
        print("0. Sair")
        escolha = input("Escolha uma opção: ")

        if  escolha == '1':
            graph, novo_ponto = menu_grafo(graph, ponto_recolha)
            if novo_ponto and novo_ponto != ponto_recolha:
                ponto_recolha = novo_ponto
            delivery_service = DeliveryService(graph)
        elif escolha == '2':
            encomenda = add_delivery(graph,ponto_recolha)
            delivery_service.add_delivery(encomenda)
        elif escolha == '3':
            estafeta = add_courier(graph, ponto_recolha)
            delivery_service.add_courier(estafeta)
        elif escolha == '4':
            filepath = input("Insira o caminho do arquivo CSV para encomendas: ")
            try:
                lista_encomendas = load_deliveries_from_csv(filepath, lista_encomendas, ponto_recolha)
                if lista_encomendas:
                    for encomenda in lista_encomendas:
                        delivery_service.add_delivery(encomenda)
                    print("Encomendas carregadas com sucesso.")
                else:
                    print("Nenhuma encomenda foi carregada. Verifique se o arquivo CSV está correto.")
            except Exception as e:
                print(f"Erro ao carregar encomendas: {e}")

        elif escolha == '5':
            filepath = input("Insira o caminho do arquivo CSV para estafetas: ")
            try:
                lista_estafetas = load_couriers_from_csv(filepath, lista_estafetas, graph, ponto_recolha)
                if lista_estafetas:
                    for estafeta in lista_estafetas:
                        delivery_service.add_courier(estafeta)
                    print("Estafetas carregados com sucesso.")
                else:
                    print("Nenhum estafeta foi carregado. Verifique se o arquivo CSV está correto.")
            except Exception as e:
                print(f"Erro ao carregar estafetas: {e}")
        elif escolha == '6':
            if not lista_estafetas:
                print("Nenhum estafeta disponivel. Por favor, adicione ou carregue estafetas primeiro.")
            elif not lista_encomendas:
                print("Nenhuma encomenda disponivel. Por favor, adicione ou carregue encomendas primeiro.")
            else:
                for encomenda in lista_encomendas:
                    delivery_service.add_delivery(encomenda)
                for estafeta in lista_estafetas:
                    delivery_service.add_courier(estafeta)
                delivery_service.allocate_deliveries_to_couriers()
            print("Entregas atribuídas aos estafetas.")
        elif escolha == '7':
            try:
                simulate(delivery_service)
            except Exception as e:
                print(f"Erro: {e}")
        elif escolha == '8':
            view_deliveries(delivery_service.deliveries)
        elif escolha == '9':
            view_couriers(delivery_service.couriers)
        elif escolha == '0':
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")


def run(csv_nodes_path, csv_connections_path):

    # Construir grafo com base nos csv
    graph = Graph()
    nodes = read_nodes(csv_nodes_path)
    for node in nodes.values():
        graph.add_node(node)
    read_edges(csv_connections_path, graph)

    menu(graph)

    return 0

if __name__ == "__main__":
    csv_nodes_path = 'csv/nodes.csv'
    csv_connections_path = 'csv/edges.csv'

    run(csv_nodes_path, csv_connections_path)
