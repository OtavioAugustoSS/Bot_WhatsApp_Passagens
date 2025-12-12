# -*- coding: utf-8 -*-
import schedule
import time
import datetime
from flight_search import FlightSearch
from database import init_db, offer_exists, save_offer
from whatsapp_sender import WhatsAppSender
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração de Rotas
# Configuração de Rotas
# Configuração de Rotas
ORIGINS = ['BSB', 'GYN', 'CGB', 'CGR']
DESTINATIONS = ['GRU', 'GIG', 'FOR', 'SSA', 'FLN', 'MIA', 'MCO', 'LIS', 'MAD', 'EZE']


# Tabela de Preços-Alvo (Price Cap)
# Se o preço encontrado for maior que isso, não enviamos.
PRICE_TARGETS = {
    'MIA': 2800, 
    'MCO': 3000, 
    'LIS': 3500, 
    'MAD': 3500, 
    'EZE': 1500,
    'GRU': 400,
    'GIG': 400,
    'SAO': 400,
    'RIO': 400,
    'FOR': 900,
    'SSA': 700,
    'FLN': 500
}

def job():
    print(f"\n--- Iniciando ciclo de busca GLOBAL (Smart Filter): {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    # 1. Datas Dinâmicas com Categorias (Horizontes)
    search_horizons = {
        'Curto Prazo 🏃': 45,
        'Médio Prazo 📅': 90,
        'Longo Prazo ✈️': 150
    }
    
    searcher = FlightSearch()
    sender = WhatsAppSender()
    
    total_ofertas_enviadas = 0

    # 3. Lógica de Loop: Origem -> Destino -> Horizonte (Data)
    for origin in ORIGINS:
        for destination in DESTINATIONS:
            if origin == destination:
                continue

            target_price = PRICE_TARGETS.get(destination, 99999)

            for label, days in search_horizons.items():
                date = (datetime.date.today() + datetime.timedelta(days=days)).strftime('%Y-%m-%d')
                
                print(f">>> Buscando: {origin} -> {destination} [{label}] Data: {date}")
                
                time.sleep(1) 
                
                offers = searcher.search_flights(origin, destination, date)
                
                if not offers:
                    continue

                for offer in offers:
                    price = offer['price']
                    
                    # 1. Lógica de Preço Base (Comparação)
                    # Tenta usar o insight da API primeiro
                    base_price = offer.get('api_high_price')
                    
                    # Se não tiver insight, usa heurística baseada no horizonte
                    if not base_price:
                        markup = 1.10 # Padrão (Curto Prazo)
                        if days == 90:
                            markup = 1.20 # Médio Prazo (+20%)
                        elif days == 150:
                            markup = 1.40 # Longo Prazo (+40%)
                        
                        base_price = int(price * markup)
                    
                    # 2. Cálculo de Economia
                    economy = base_price - price
                    # Evita divisão por zero
                    percentage = int((economy / base_price) * 100) if base_price > 0 else 0
                    
                    # Regra: Só mostrar se economia for relevante (> 10%)
                    # E se estiver dentro do target (mantendo regra anterior de qualidade)
                    if price <= target_price and price < (base_price * 0.9):
                        if not offer_exists(offer['id']):
                            data_obj = datetime.datetime.strptime(offer['departure_date'], '%Y-%m-%d')
                            data_formatada = data_obj.strftime('%d/%m/%Y')
                            
                            # 3. Nova Mensagem com Comparação
                            msg = (
                                f"📉 *OPORTUNIDADE ENCONTRADA!*\n"
                                f"✈️ Trecho: {offer['origin_city']} ➡️ {offer['destination_city']}\n"
                                f"⏳ Antecedência: {label} ({days} dias)\n"
                                f"📅 Data: {data_formatada}\n"
                                f"🏨 Cia: {offer.get('airline', 'N/A')}\n\n"
                                f"❌ Média p/ essa data: ~R$ {base_price}~\n"
                                f"✅ *PREÇO ATUAL: R$ {price}*\n"
                                f"🔥 Economia: R$ {economy} ({percentage}%)\n\n"
                                f"👇 GARANTA AGORA:\n"
                                f"{offer['link']}"
                            )
                            
                            print(f"!!! MATCH !!! {origin}->{destination} | R$ {price} (Econ: {percentage}%)")
                            sender.send_message(msg)
                            save_offer(offer)
                            total_ofertas_enviadas += 1
                            
                            time.sleep(10)
        
    print(f"\nCiclo concluído. Total de {total_ofertas_enviadas} ofertas enviadas.")

def main():
    print("🤖 Bot Iniciado! (Pressione Ctrl+C para parar)")
    init_db()
    
    # Primeira execução
    job()
    
    # Agendamento
    schedule.every(30).minutes.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
