# -*- coding: utf-8 -*-
import schedule
import time
import datetime
from flight_search import FlightSearch
from database import init_db, offer_exists, save_offer
from whatsapp_sender import WhatsAppBot 
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração de Rotas
ORIGINS = ['BSB', 'GYN', 'CGB', 'CGR']
DESTINATIONS = ['GRU', 'GIG', 'FOR', 'SSA', 'FLN', 'MIA', 'MCO', 'LIS', 'MAD', 'EZE']

# Limites de Preço (Price Cap)
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
    print(f"\n--- Iniciando Ciclo de Busca Global: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    # Horizontes de Busca (Datas Dinâmicas)
    search_horizons = {
        'Curto Prazo 🏃': 45,
        'Médio Prazo 📅': 90,
        'Longo Prazo ✈️': 150
    }
    
    searcher = FlightSearch()
    sender = WhatsAppBot()
    
    total_offers_sent = 0

    # Lógica: Origem -> Destino -> Horizonte
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
                    
                    # 1. Lógica de Preço Base (Âncora de Comparação)
                    # Tenta usar o insight da API primeiro, senão usa heurística
                    base_price = offer.get('api_high_price')
                    
                    if not base_price:
                        # Markup Heurístico baseado no horizonte
                        markup = 1.10 
                        if days == 90:
                            markup = 1.20 
                        elif days == 150:
                            markup = 1.40 
                        
                        base_price = int(price * markup)
                    
                    # 2. Cálculo de Economia
                    economy = base_price - price
                    percentage = int((economy / base_price) * 100) if base_price > 0 else 0
                    
                    # Regra: Apenas alertar se economia > 10% E preço <= alvo
                    if price <= target_price and price < (base_price * 0.9):
                        if not offer_exists(offer['id']):
                            data_obj = datetime.datetime.strptime(offer['departure_date'], '%Y-%m-%d')
                            formatted_date = data_obj.strftime('%d/%m/%Y')
                            
                            # Template da Mensagem
                            msg = (
                                f"📉 *OPORTUNIDADE ENCONTRADA!*\n"
                                f"✈️ Trecho: {offer['origin_city']} ➡️ {offer['destination_city']}\n"
                                f"⏳ Antecedência: {label} ({days} dias)\n"
                                f"📅 Data: {formatted_date}\n"
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
                            total_offers_sent += 1
                            
                            time.sleep(10)
        
    print(f"\nCiclo finalizado. Total de alertas enviados: {total_offers_sent}")
    
    # Libera recursos
    sender.close()

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
