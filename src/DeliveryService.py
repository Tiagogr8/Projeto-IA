import plotly.graph_objects as go
from Graph import Graph

class DeliveryService:

    def __init__(self, graph):
        self.couriers = []
        self.deliveries = []
        self.graph = graph

    def add_courier(self, courier):
        # Verifica se o estafeta já existe na lista
        for i, existing_courier in enumerate(self.couriers):
            if existing_courier.courier_id == courier.courier_id:
                # Remove o estafeta existente
                self.couriers.pop(i)
                break
        # Adiciona o novo estafeta
        self.couriers.append(courier)

    def add_delivery(self, delivery):
        # Verifica se a encomenda já existe na lista
        for i, existing_delivery in enumerate(self.deliveries):
            if existing_delivery.delivery_id == delivery.delivery_id:
                # Remove a encomenda existente
                self.deliveries.pop(i)
                break
        # Adiciona a nova encomenda
        self.deliveries.append(delivery)

    def allocate_deliveries_to_couriers(self):
        self.deliveries.sort(key=lambda d: d.deadline)  # Ordenar entregas por prazo

        for delivery in self.deliveries:
            if delivery.status != 'Pendente':
                continue  # Ignorar entregas que já foram atribuídas ou concluídas

            best_courier = None
            best_score = float('inf')
            best_courier_score = -1

            for courier in self.couriers:
                if courier.can_accept_delivery(delivery):
                    score = self.calculate_compatibility_score(courier, delivery)
                    if score < best_score or (score == best_score and courier.score > best_courier_score):
                        best_score = score
                        best_courier_score = courier.score
                        best_courier = courier

            if best_courier:
                success = best_courier.assign_delivery(delivery)
                if success:
                    delivery.assign_to_courier(best_courier.courier_id)
                    delivery.update_status('Atribuída')
                    estimated_time, ecological_impact = best_courier.calculate_delivery_time_and_ecological_impact(delivery)
                    print(f"Encomenda {delivery.delivery_id} atribuída a estafeta {best_courier.courier_id}. "
                          f"Tempo estimado de entrega: {estimated_time:.2f}h.")

    def calculate_compatibility_score(self, courier, delivery):
        estimated_time, ecological_impact = courier.calculate_delivery_time_and_ecological_impact(delivery)
        deadline = float(delivery.deadline) if isinstance(delivery.deadline, str) else delivery.deadline
        deadline_factor = max(1, (deadline - estimated_time) / deadline)
        return ecological_impact * 0.5 + deadline_factor * 0.5



    # Calcular os caminhos para cada estafeta para todos os algoritmos e ver qual é o melhor
    def calculate_route_for_courier(self, courier):
        print(f"\n{'=' * 200}")
        print(f"Calculando rotas para o estafeta {courier.courier_id} no ponto central de coleta")
        print(f"{'=' * 200}")

        best_algorithm = None
        best_cost = float('inf')
        best_total_path = None
        paths = {}
        delivery_time_algorithm = {}
        resultados = {
            "BFS": {"custo": 0, "tempo": 0, "espaco": 0},
            "DFS": {"custo": 0, "tempo": 0, "espaco": 0},
            "Greedy": {"custo": 0, "tempo": 0, "espaco": 0},
            "A*": {"custo": 0, "tempo": 0, "espaco": 0}
        }

        for delivery in courier.deliveries:
            delivery_time_algorithm[delivery.delivery_id] = {alg: float('inf') for alg in resultados}

        for nome_algoritmo, funcao_procura in [("BFS", courier.graph.procura_BFS),
                                               ("DFS", courier.graph.procura_DFS),
                                               ("Greedy", courier.graph.greedy_best_first_search),
                                               ("A*", courier.graph.a_star_search)]:
            print(f"\n{'-' * 20} Utilizando {nome_algoritmo} {'-' * 20}")
            current_node = courier.current_node
            custo_total = 0
            total_delivery_time = 0
            espaco_total = 0
            tempo_total_execucao = 0
            current_load = sum(delivery.weight for delivery in courier.deliveries)
            path_for_algorithm = [current_node]

            for delivery in courier.deliveries:
                current_speed = courier.calculate_effective_speed(current_load)
                path, custo, espaco, tempo_execucao = funcao_procura(current_node, delivery.destination_node)

                if path:
                    custo_km = custo / 1000.0
                    tempo_entrega = custo_km / current_speed
                    delivery_time_algorithm[delivery.delivery_id][nome_algoritmo] = tempo_entrega
                    total_delivery_time += tempo_entrega
                    print(f"\nEntrega {delivery.delivery_id}:")
                    print(f"De {current_node} para {delivery.destination_node}")
                    print(f"Peso Atual: {current_load} kg, Velocidade: {current_speed:.2f} km/h")
                    print(f"  Caminho ({nome_algoritmo}): {' -> '.join(path)}")
                    print(f"  Custo: {custo:.2f}")
                    print(f"  Distância: {custo_km:.2f} km")
                    print(f"  Tempo : {tempo_entrega:.2f}h")
                    custo_total += custo
                    espaco_total += espaco
                    tempo_total_execucao += tempo_execucao
                    current_node = delivery.destination_node
                    path_for_algorithm.extend(path[1:])  # Não duplicar o nó inicial

                current_load -= delivery.weight

            paths[nome_algoritmo] = {'caminho': path_for_algorithm, 'custo': custo_total, 'tempo': total_delivery_time}
            resultados[nome_algoritmo]['custo'] += custo_total
            resultados[nome_algoritmo]['tempo'] += tempo_total_execucao
            resultados[nome_algoritmo]['espaco'] += espaco_total

            if custo_total < best_cost:
                best_cost = custo_total
                best_algorithm = nome_algoritmo
                best_total_path = path_for_algorithm

        for delivery in courier.deliveries:
            delivery.tempo_entrega = delivery_time_algorithm[delivery.delivery_id][best_algorithm]

        print(f"\n{'-' * 50}")
        print(f"Melhor caminho encontrado: {best_algorithm}")
        print(f"Caminho: {' -> '.join([str(node) for node in best_total_path])}")
        print(f"Custo total: {best_cost}")
        print(f"{'-' * 50}")

        self.draw_paths_on_graph(courier.graph, courier, paths, best_algorithm, best_total_path)
        return best_algorithm, best_total_path, resultados

    # Funcao para avaliar as entregas
    def evaluate_deliveries(self):
        for delivery in self.deliveries:
            if delivery.status == 'Concluída':
                vehicle_type = 'Desconhecido'
                id_courier = 'Desconhecido'

                if delivery.assigned_to:
                    courier = next((c for c in self.couriers if c.courier_id == delivery.assigned_to), None)
                    if courier:
                        vehicle_type = courier.transport_type
                        id_courier = courier.courier_id
                central_collection_point = 'Ponto Central'  # Substitua pelo nome real ou ID do ponto central

                tempo_entrega_str = f"{delivery.tempo_entrega:.2f}h" if delivery.tempo_entrega is not None else "Não disponível"

                print(
                    f"\nAvalie a entrega {delivery.delivery_id} do {central_collection_point} para {delivery.destination_node}.")
                print(
                    f"Prazo: {delivery.deadline}h, Tempo de Entrega: {tempo_entrega_str}, Estafeta: {id_courier}, Veículo: {vehicle_type}, Preço: {delivery.preco}")

                try:
                    rating = int(input("Digite sua avaliação (0-5): "))
                    delivery.set_customer_rating(rating)
                    print(f"Avaliação recebida: {rating} estrelas.")
                except ValueError:
                    print("Entrada inválida. Avaliação não foi registrada.")

##########################################################################################################################################################
########################################## Desenhar os caminhos dos algoritmos num grafo #################################################################
##########################################################################################################################################################

    def draw_paths_on_graph(self, graph, courier, paths, best_algorithm, best_path):
        fig = go.Figure()

        # Adicionando arestas do grafo
        for node_id, edges in graph.edges.items():
            for edge in edges:
                line_coords = Graph.parse_linestring(edge.geometry)
                if line_coords:
                    x_coords, y_coords = zip(*line_coords)
                else:
                    start_node = graph.nodes[edge.u]
                    end_node = graph.nodes[edge.v]
                    x_coords = [start_node.coordinates[0], end_node.coordinates[0]]
                    y_coords = [start_node.coordinates[1], end_node.coordinates[1]]

                mid_pt = Graph.midpoint((x_coords[0], y_coords[0]), (x_coords[-1], y_coords[-1]))
                fig.add_trace(
                    go.Scatter(x=x_coords, y=y_coords, mode='lines', line=dict(color='grey'), showlegend=False))
                fig.add_trace(
                    go.Scatter(x=[mid_pt[0]], y=[mid_pt[1]], text=[f'{edge.name} ({edge.custo:.2f} m)'], mode='text',
                               showlegend=False, textposition='bottom center', textfont=dict(size=8)))

        for node_id, node in graph.nodes.items():
            fig.add_trace(go.Scatter(
                x=[node.coordinates[0]], y=[node.coordinates[1]],
                mode='markers', marker=dict(color='blue', size=5),
                name=f'{node_id}',
                showlegend=False
            ))

        pickup_node_coords = graph.nodes[courier.current_node].coordinates
        fig.add_trace(go.Scatter(x=[pickup_node_coords[0]], y=[pickup_node_coords[1]], mode='markers+text',
                                 marker=dict(color='orange', size=20), text=['Ponto de Recolha'],
                                 textposition='top center', textfont=dict(color='orange', size=15,family='Arial, bold'),name='Ponto de Recolha'))

        # Cores para os caminhos dos algoritmos
        path_colors = {"BFS": "green", "DFS": "red", "Greedy": "purple", "A*": "blue", "Melhor Caminho": "yellow"}
        line_width = 3

        # Adicionando caminhos dos algoritmos
        def draw_paths(path, color, algorithm, custo, legendgroup):
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                for edge in graph.edges[u]:
                    if edge.v == v:
                        if edge.geometry:
                            line_coords = Graph.parse_linestring(edge.geometry)
                            x_coords, y_coords = zip(*line_coords)
                        else:
                            x_coords = [graph.nodes[u].coordinates[0], graph.nodes[v].coordinates[0]]
                            y_coords = [graph.nodes[u].coordinates[1], graph.nodes[v].coordinates[1]]
                        fig.add_trace(
                            go.Scatter(x=x_coords, y=y_coords, mode='lines', line=dict(color=color, width=line_width),
                                       legendgroup=legendgroup, showlegend=False))

            # Adiciona uma legenda no final do caminho
            last_node_coords = graph.nodes[path[-1]].coordinates
            fig.add_trace(go.Scatter(x=[last_node_coords[0]], y=[last_node_coords[1]], mode='markers',
                                     marker=dict(color=color, size=10), name=f'{algorithm} (Custo: {custo:.2f})',
                                     legendgroup=legendgroup))

        # Desenha os caminhos dos algoritmos
        for algorithm, path_info in paths.items():
                path = path_info.get('caminho')
                custo = path_info.get('custo', 0)
                if path:
                    draw_paths(path, path_colors[algorithm], algorithm, custo, algorithm)

            # Desenha o melhor caminho
        if best_path:
            best_cost = paths[best_algorithm]['custo']
            draw_paths(best_path, "yellow", f"Melhor Caminho {best_algorithm}", best_cost, "Melhor Caminho")

        # Pontos de destino das entrefas
        for i, delivery in enumerate(courier.deliveries):
            end_node_coords = graph.nodes[delivery.destination_node].coordinates

            # Ponto de início da entrega atual
            if i == 0:
                start_node_coords = pickup_node_coords
                start_label = f'Início {delivery.delivery_id}'
            else:
                previous_delivery = courier.deliveries[i - 1]
                start_node_coords = graph.nodes[previous_delivery.destination_node].coordinates
                start_label = f'Início {delivery.delivery_id}'

            # Ponto de destino da entrega atual
            end_label = f'Destino {delivery.delivery_id}'

            # Adicionar rótulos para ponto de início
            fig.add_trace(go.Scatter(x=[start_node_coords[0]], y=[start_node_coords[1]], mode='markers+text',
                                     marker=dict(color='lightblue', size=20), text=[start_label],
                                     textposition='bottom center',textfont=dict(color='lightblue', size=12,family='Arial, bold'), name=start_label))

            # Adicionar rótulos para ponto de destino
            fig.add_trace(go.Scatter(x=[end_node_coords[0]], y=[end_node_coords[1]], mode='markers+text',
                                     marker=dict(color='blue', size=20), text=[end_label],
                                     textposition='bottom center',textfont=dict(color='blue', size=12,family='Arial, bold'), name=end_label))

        # Configurações do layout
        fig.update_layout(title=f"Caminhos do Estafeta {courier.courier_id}", hovermode='closest', showlegend=True,
                          margin=dict(l=20, r=20, t=40, b=20))
        fig.show()
