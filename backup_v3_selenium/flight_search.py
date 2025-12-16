import requests
import os
import urllib.parse
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class FlightSearch:
    def __init__(self):
        self.api_key = os.getenv('SERPAPI_KEY')
        self.base_url = "https://serpapi.com/search"

    def search_flights(self, origin, destination, date):
        """
        Busca preços de voos usando a Google Flights API da SerpApi.
        Retorna uma lista de dicionários com as melhores ofertas.
        """
        if not self.api_key:
            print("ERRO: SERPAPI_KEY não configurada no .env")
            return []

        # Parâmetros para engine Google Flights (SerpApi)
        # Type 2 = One Way (Só ida)
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": date,
            "currency": "BRL",
            "hl": "pt",
            "gl": "br", 
            "type": "2",
            "api_key": self.api_key
        }

        print(f"Buscando voos de {origin} para {destination} em {date}...")

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                print(f"Erro da API: {data['error']}")
                return []

            # Dicionário de Cidades (Mapeamento IATA)
            IATA_CITIES = {
                'GRU': 'São Paulo',
                'CGH': 'São Paulo',
                'VCP': 'Campinas',
                'SAO': 'São Paulo',
                'MIA': 'Miami',
                'BSB': 'Brasília',
                'GIG': 'Rio de Janeiro',
                'SDU': 'Rio de Janeiro',
                'RIO': 'Rio de Janeiro',
                'CNF': 'Belo Horizonte',
                'JFK': 'Nova York',
                'LIS': 'Lisboa',
                'MAD': 'Madrid',
                'PAR': 'Paris',
                'CDG': 'Paris',
                'DXB': 'Dubai',
                'GYN': 'Goiânia',
                'CGB': 'Cuiabá',
                'CGR': 'Campo Grande',
                'FOR': 'Fortaleza',
                'SSA': 'Salvador',
                'FLN': 'Florianópolis',
                'MCO': 'Orlando',
                'EZE': 'Buenos Aires'
            }
            
            origin_city = IATA_CITIES.get(origin, origin)
            destination_city = IATA_CITIES.get(destination, destination)

            ofertas = []
            
            # Combina resultados de melhores voos e outros voos
            flights_found = data.get('best_flights', []) + data.get('other_flights', [])
            
            # Calcular preço âncora (Média dos preços encontrados)
            all_prices = [f.get('price') for f in flights_found if f.get('price')]
            avg_price = int(sum(all_prices) / len(all_prices)) if all_prices else 0
            
            # Insights de Preço da API
            api_high_price = None
            if 'price_insights' in data and 'typical_price_range' in data['price_insights']:
                range_vals = data['price_insights']['typical_price_range']
                if isinstance(range_vals, list) and len(range_vals) > 1:
                     api_high_price = range_vals[1]

            # Preço máximo de referência
            max_price = avg_price

            for flight in flights_found:
                try:
                    price = flight.get('price')
                    if price is None:
                        continue
                    
                    airline = "Companhia Desconhecida"
                    if 'flights' in flight and len(flight['flights']) > 0:
                        airline = flight['flights'][0].get('airline', airline)
                    
                    # Gerar Deep Link do Google Flights
                    query_string = f"Flights from {origin} to {destination} on {date} oneway"
                    encoded_query = urllib.parse.quote(query_string)
                    link_seguro = f"https://www.google.com/travel/flights?q={encoded_query}&curr=BRL"
                    
                    print(f"DEBUG - Link: {link_seguro}")
                    
                    voo_id = f"{origin}-{destination}-{date}-{airline}-{price}"

                    oferta = {
                        'id': voo_id,
                        'origin': origin,
                        'destination': destination,
                        'origin_city': origin_city,
                        'destination_city': destination_city,
                        'departure_date': date,
                        'price': price,
                        'original_price': max_price,
                        'api_high_price': api_high_price,
                        'airline': airline,
                        'link': link_seguro
                    }
                    ofertas.append(oferta)
                    
                except Exception as e:
                    print(f"Erro ao processar item: {e}")
                    continue

            # Ordenação por Preço
            ofertas.sort(key=lambda x: x['price'])
            
            # Filtro: Manter apenas ofertas abaixo do preço médio/âncora
            ofertas_filtradas = [o for o in ofertas if o['price'] < max_price]
            
            # Retorna apenas as Top 3 ofertas
            return ofertas_filtradas[:3]

        except Exception as e:
            print(f"Erro na requisição: {e}")
            return []
