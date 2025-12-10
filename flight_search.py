import requests
import os
from datetime import datetime

class FlightSearch:
    def __init__(self):
        self.api_key = os.getenv('SERPAPI_KEY', 'YOUR_SERPAPI_KEY')
        self.base_url = "https://serpapi.com/search"

    def search_flights(self, origin, destination, date):
        """
        Busca voos usando SerpApi (Google Flights).
        Retorna uma lista de dicionários com os dados do voo.
        """
        if self.api_key == 'YOUR_SERPAPI_KEY':
            print("AVISO: API Key não configurada. Retornando dados fictícios para teste.")
            return self._get_mock_data(origin, destination, date)

        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": date,
            "currency": "BRL",
            "hl": "pt",
            "api_key": self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            offers = []
            if 'best_flights' in data:
                for flight in data['best_flights']:
                    # Simplificação para extrair dados relevantes
                    # A estrutura real do JSON do SerpApi pode variar, ajuste conforme necessário
                    price = flight.get('price', 0)
                    if isinstance(price, int):
                        pass # já é int
                    else:
                        # Tenta limpar string de preço se necessário
                        pass
                    
                    offer = {
                        'id': f"{origin}-{destination}-{date}-{flight.get('total_duration', '0')}", # ID único improvisado
                        'origin': origin,
                        'destination': destination,
                        'departure_date': date,
                        'price': price,
                        'airline': flight.get('airline_logo', ''), # Apenas URL do logo ou nome se disponível
                        'link': "https://www.google.com/flights" # Link genérico ou extraído se disponível
                    }
                    offers.append(offer)
            return offers

        except Exception as e:
            print(f"Erro na busca de voos: {e}")
            print("⚠️ Falha na API. Usando dados fictícios para demonstração.")
            return self._get_mock_data(origin, destination, date)

    def _get_mock_data(self, origin, destination, date):
        """Retorna dados falsos para teste quando sem API Key."""
        import random
        price = random.randint(200, 1500)
        return [{
            'id': f"MOCK-{origin}-{destination}-{date}-{price}",
            'origin': origin,
            'destination': destination,
            'departure_date': date,
            'price': price,
            'airline': 'Mock Airlines',
            'link': 'http://mock-link.com'
        }]
