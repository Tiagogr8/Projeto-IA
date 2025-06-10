class Courier:
    def __init__(self, courier_id, transport_type, base_speed, max_weight, graph, current_node, score=5):
        self.courier_id = courier_id
        self.transport_type = transport_type
        self.base_speed = base_speed
        self.speed = base_speed
        self.max_weight = max_weight
        self.current_load = 0
        self.graph = graph
        self.current_node = current_node
        self.score = score
        self.is_available = True
        self.deliveries = []

    def can_accept_delivery(self, delivery):
        return self.current_load + delivery.weight <= self.max_weight and self.is_available

    def assign_delivery(self, delivery):
        if self.can_accept_delivery(delivery):
            self.current_load += delivery.weight
            self.deliveries.append(delivery)
            delivery.assigned_to = self.courier_id
            self.update_speed()  # Atualiza a velocidade após adicionar o peso da entrega
            return True
        return False

    def update_speed(self):
        if self.transport_type == 'Bicicleta':
            self.speed = self.base_speed - 0.6 * self.current_load
        elif self.transport_type == 'Moto':
            self.speed = self.base_speed - 0.5 * self.current_load
        elif self.transport_type == 'Carro':
            self.speed = self.base_speed - 0.1 * self.current_load

    def update_score(self):
        total_rating = sum(delivery.customer_rating for delivery in self.deliveries if delivery.customer_rating is not None)
        num_ratings = sum(1 for delivery in self.deliveries if delivery.customer_rating is not None)
        if num_ratings > 0:
            self.score = total_rating / num_ratings
        else:
            self.score = 0

    def calculate_delivery_time_and_ecological_impact(self, new_delivery):
        total_distance = 0
        current_node = self.current_node
        total_load = self.current_load + new_delivery.weight

        # Calcula a distância total percorrida para as entregas já atribuídas
        for delivery in self.deliveries:
            total_distance += self.graph.heuristic(current_node, delivery.destination_node)
            current_node = delivery.destination_node

        # Inclui a distância para a nova entrega
        total_distance += self.graph.heuristic(current_node, new_delivery.destination_node)

        # Calcula o tempo total de entrega
        effective_speed = self.calculate_effective_speed(total_load)
        total_delivery_time = total_distance / effective_speed

        # Cálculo do impacto ecológico
        ecological_impact = 0
        if self.transport_type == 'Moto':
            emissions_per_km = 0.08
            ecological_impact = emissions_per_km * total_distance
        elif self.transport_type == 'Carro':
            emissions_per_km = 0.12
            weight_factor = 1 + new_delivery.weight / 100
            ecological_impact = emissions_per_km * total_distance * weight_factor

        return total_delivery_time, ecological_impact

    def calculate_effective_speed(self, total_load):
        # Calcula a velocidade com base no peso total (carga atual mais a nova entrega)
        if self.transport_type == 'Bicicleta':
            return max(self.base_speed - 0.6 * total_load, 1)  # Evita velocidade negativa ou zero
        elif self.transport_type == 'Moto':
            return max(self.base_speed - 0.5 * total_load, 1)
        elif self.transport_type == 'Carro':
            return max(self.base_speed - 0.1 * total_load, 1)
        return self.base_speed