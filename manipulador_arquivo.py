import requests
import json

class ManipuladorTickets:
    def __init__(self, chave_api):
        self.chave_api = chave_api

    def obter_tickets_por_ids(self, ids_tickets, criticidade):
        """Busca tickets pela API do Movidesk, com base nos IDs fornecidos."""
        ids_lista = [ticket_id.strip() for ticket_id in ids_tickets.split(',')]
        filtro = ' or '.join([f"id eq {ticket_id}" for ticket_id in ids_lista])

        params = {
            'token': self.chave_api,
            '$select': 'id,subject,status,createdDate,actions',
            '$expand': 'actions($select=id,type,description,createdDate),clients($expand=organization($select=businessName))',
            '$filter': filtro
        }

        try:
            response = requests.get('https://api.movidesk.com/public/v1/tickets', params=params)
            if response.status_code == 200:
                tickets = response.json()
                print(f"{len(tickets)} tickets encontrados.")

                # Salva os dados brutos em um arquivo JSON
                self.salvar_tickets_brutos(tickets)

                return tickets
            else:
                print(f"Erro: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Erro na conexão: {e}")
            return []

    def salvar_tickets_brutos(self, tickets):
        """Salva os dados brutos dos tickets em um arquivo JSON."""
        try:
            with open("tickets_brutos.json", "w", encoding='utf-8') as arquivo_json:
                json.dump(tickets, arquivo_json, ensure_ascii=False, indent=4)
            print("Dados brutos dos tickets salvos com sucesso em 'tickets_brutos.json'.")
        except Exception as e:
            print(f"Erro ao salvar os dados brutos: {e}")

    def obter_nome_cliente(self, ticket):
        """Prioriza o nome da organização quando disponível, caso contrário, usa outro campo."""
        try:
            client = ticket.get('clients', [{}])[0]  # Pega o primeiro cliente
            organization = client.get('organization', {}).get('businessName')
            if organization:
                return organization
            else:
                return client.get('businessName', 'Nome Não Encontrado')  # Usa outro campo como fallback
        except Exception as e:
            print(f"Erro ao obter nome do cliente: {e}")
            return 'Nome Não Encontrado'
