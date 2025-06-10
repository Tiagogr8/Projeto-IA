class Delivery:
    def __init__(self, delivery_id,collection_point, destination_node, deadline, weight, volume):
        self.delivery_id = delivery_id
        self.destination_node = destination_node
        self.deadline = deadline  # Prazo em horas
        self.weight = weight
        self.volume = volume
        self.collection_point = collection_point
        self.customer_rating = None
        self.assigned_to = None
        self.status = 'Pendente'  # Inicialmente, todas as entregas estão pendentes
        self.tempo_entrega = None
        self.preco = None

    def assign_to_courier(self, courier_id):
        self.assigned_to = courier_id
        self.status = 'Atribuída'

    # Avaliar a entrega
    def set_customer_rating(self, rating):
        if 0 <= rating <= 5:
            self.customer_rating = rating
        else:
            raise ValueError("Customer rating must be between 0 and 5.")

    # Atualizar o status da encomenda
    def update_status(self, new_status):
        self.status = new_status
        print(f"Status da entrega {self.delivery_id} atualizado para {new_status}.")

    def calcular_preco(self, tipo_veiculo):
        # Definir coeficientes baseados no tipo de veículo
        coeficientes_veiculo = {
            'Bicicleta': 0.8,  # Mais ecológico, menor custo
            'Moto': 1.0,
            'Carro': 1.2  # Menos ecológico, maior custo
        }
        coeficiente = coeficientes_veiculo.get(tipo_veiculo, 1)

        # Calcular o preço baseado no tempo, peso e coeficiente ecológico
        taxa_base = 2.0  # Taxa base por entrega
        taxa_por_kg = 0.5  # Taxa adicional por kg
        taxa_por_hora = 1.0  # Taxa adicional por hora de entrega

        self.preco = round(taxa_base + (taxa_por_kg * self.weight) + (taxa_por_hora * self.tempo_entrega) * coeficiente, 2)