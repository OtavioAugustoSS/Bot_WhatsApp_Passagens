import requests
import os
import urllib.parse
from dotenv import load_dotenv

# Carrega variáveis de ambiente imediatamente
load_dotenv()

class FlightSearch:
    def __init__(self):
        self.api_key = os.getenv('SERPAPI_KEY')
        self.base_url = "https://serpapi.com/search"

    def buscar_voo(self, origem, destino, data_ida):
        """
        Busca preços de voos usando a Google Flights API da SerpApi.
        Retorna uma lista de dicionários com as melhores ofertas.
        """
        if not self.api_key:
            raise Exception("ERRO CRÍTICO: SERPAPI_KEY não encontrada no arquivo .env.")

        params = {
            "engine": "google_flights",
            "departure_id": origem,
            "arrival_id": destino,
            "outbound_date": data_ida,
            "currency": "BRL",
            "hl": "pt",
            "gl": "br",     # Garante localização Brasil
            "type": "2",    # 1=Round Trip, 2=One Way
            "api_key": self.api_key
        }

        print(f"Buscando voos de {origem} para {destino} em {data_ida}...")

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status() # Levanta exceção para erros 4xx/5xx
            data = response.json()
            
            # Verifica erro lógico da API
            if "error" in data:
                raise Exception(f"Erro retornado pela SerpApi: {data['error']}")

            ofertas = []
            
            # Combina melhores voos e outros voos
            all_flights = data.get('best_flights', []) + data.get('other_flights', [])

            for flight in all_flights:
                try:
                    price = flight.get('price')
                    if price is None:
                        continue

                    # Extração da Companhia Aérea
                    airline_name = "Companhia Desconhecida"
                    if 'flights' in flight and len(flight['flights']) > 0:
                        first_leg = flight['flights'][0]
                        airline_name = first_leg.get('airline', 'N/A')
                        
                        # Tenta identificar se é operado por outra
                        operating = first_leg.get('operating_airline')
                        if operating and operating != airline_name:
                            airline_name = f"{airline_name} (Op. por {operating})"

                    # Construção do Link Dinâmico (Deep Link)
                    # Formato: Flights to DESTINATION from ORIGIN on DATE oneway
                    query_text = f"Flights to {destino} from {origem} on {data_ida} oneway"
                    encoded_query = urllib.parse.quote(query_text)
                    link_final = f"https://www.google.com/travel/flights?q={encoded_query}&curr=BRL"
                    
                    # ID único atualizado
                    voo_id = f"{origem}-{destino}-{data_ida}-{airline_name}-{price}"

                    oferta = {
                        'id': voo_id,
                        'origin': origem,
                        'destination': destino,
                        'departure_date': data_ida,
                        'price': price,
                        'airline': airline_name,
                        'link': link_final
                    }
                    ofertas.append(oferta)

                except Exception as item_error:
                    print(f"Erro ao processar um dos voos: {item_error}")
                    continue

            return ofertas

        except requests.exceptions.RequestException as e:
            print(f"ERRO DE CONEXÃO/API: {e}")
            if e.response is not None:
                print(f"Detalhes do erro: {e.response.text}")
            # Retorna lista vazia mas NÃO usa mock
            return []
        except Exception as e:
            print(f"ERRO INESPERADO: {e}")
            raise e # Levanta o erro conforme solicitado se for algo crítico de lógica

if __name__ == "__main__":
    searcher = FlightSearch()
    
    # Data dinâmica para garantir teste válido
    from datetime import datetime, timedelta
    next_month = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"--- TESTE UNITÁRIO: Buscando para {next_month} ---")
    
    try:
        resultados = searcher.buscar_voo("GRU", "MIA", next_month)
        if resultados:
            print(f"\nSucesso! {len(resultados)} voos encontrados.")
            melhor = min(resultados, key=lambda x: x['price'] if isinstance(x['price'], int) else 999999)
            print(f"Melhor Opção: {melhor['airline']}")
            print(f"Preço: R$ {melhor['price']}")
            print(f"Link: {melhor['link']}")
        else:
            print("Nenhum resultado retornado (verifique logs de erro acima).")
    except Exception as e:
        print(f"Teste falhou com exceção: {e}")
