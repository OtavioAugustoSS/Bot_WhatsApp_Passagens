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
ORIGINS = ['BSB']
DESTINATIONS = ['SCL', 'FLN', 'NVT']

# Limites de Preço (Price Cap Absurdamente Agressivos)
PRICE_TARGETS = {
    'SCL': 900, 
    'FLN': 400,
    'NVT': 400
}

def job(sender):
    print(f"\n--- Iniciando Ciclo de Busca (Feriadões): {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    # Janela de Datas Estrita e Finais de semana prolongados (Sab-Ter)
    start_window = datetime.date(2026, 6, 20)
    end_window = datetime.date(2026, 7, 30)
    
    date_pairs = []
    curr_date = start_window
    while curr_date <= end_window:
        if curr_date.weekday() == 5: # Sábado
            return_date = curr_date + datetime.timedelta(days=3) # Terça da semana seguinte
            if return_date <= end_window:
                date_pairs.append((curr_date, return_date))
        curr_date += datetime.timedelta(days=1)
    
    searcher = FlightSearch()
    
    total_offers_sent = 0

    # Lógica: Origem -> Destino -> Datas (Sab -> Ter)
    for origin in ORIGINS:
        for destination in DESTINATIONS:
            if origin == destination:
                continue

            target_price = PRICE_TARGETS.get(destination, 99999)

            for outbound_date, return_date in date_pairs:
                outbound_str = outbound_date.strftime('%Y-%m-%d')
                return_str = return_date.strftime('%Y-%m-%d')
                
                print(f">>> Buscando: {origin} -> {destination} | Ida: {outbound_str} | Volta: {return_str}")
                
                time.sleep(1) 
                
                offers = searcher.search_flights(origin, destination, outbound_str, return_str)
                
                if not offers:
                    continue

                # Processar APENAS a oferta mais barata (como a lista já vem ordenada, é a primeira)
                best_offer = offers[0]
                price = best_offer['price']
                
                # 1. Lógica de Preço Base (Âncora de Comparação)
                base_price = best_offer.get('api_high_price')
                
                if not base_price:
                    # Se a API não der insight pra ida e volta, assumimos um markup padrão para estimativa de "preço normal"
                    base_price = int(price * 1.50)
                
                # 2. Cálculo de Economia
                economy = base_price - price
                percentage = int((economy / base_price) * 100) if base_price > 0 else 0
                
                # 3. Filtro de "Promoção Incrível" (>= 35% de desconto OU abaixo da agressiva margem alvo)
                is_incredible_promo = (percentage >= 35) or (price <= target_price)
                
                if is_incredible_promo:
                    if not offer_exists(best_offer['id']):
                        data_ida_obj = datetime.datetime.strptime(best_offer['departure_date'], '%Y-%m-%d')
                        data_ida_fmt = data_ida_obj.strftime('%d/%m/%Y')
                        
                        data_volta_obj = datetime.datetime.strptime(best_offer['return_date'], '%Y-%m-%d')
                        data_volta_fmt = data_volta_obj.strftime('%d/%m/%Y')
                        
                        # Template da Mensagem
                        msg = (
                            f"🚨 *PROMOÇÃO ABSURDA ENCONTRADA!* 🚨\n"
                            f"✈️ Trecho: {best_offer['origin_city']} ➡️ {best_offer['destination_city']} (Ida e Volta)\n"
                            f"📅 Ida: {data_ida_fmt} (Sábado)\n"
                            f"📅 Volta: {data_volta_fmt} (Terça)\n"
                            f"🏨 Cia: {best_offer.get('airline', 'N/A')}\n\n"
                            f"❌ Preço Normal: ~R$ {base_price}~\n"
                            f"✅ *PREÇO ATUAL: R$ {price}*\n"
                            f"🔥 Economia: R$ {economy} (-{percentage}%)\n\n"
                            f"👇 GARANTA AGORA (Google Flights):\n"
                            f"{best_offer['link']}"
                        )
                        
                        print(f"!!! MATCH !!! {origin}->{destination} | R$ {price} (Econ: {percentage}%)")
                        sender.send_message(msg)
                        save_offer(best_offer)
                        total_offers_sent += 1
                        
                        time.sleep(10)
        
    print(f"\nCiclo finalizado. Total de alertas enviados: {total_offers_sent}")
    print("Aguardando próximo ciclo. (WhatsApp mantido aberto)")

def main():
    print("🤖 Bot Iniciado! (Pressione Ctrl+C para parar e fechar tudo)")
    init_db()
    
    # Criamos a instância de envio (Navegador) apeas UMA vez na inicialização
    sender = WhatsAppBot()
    
    # Primeira execução
    job(sender)
    
    # Agendamento - executará a mesma função enviando o sender
    schedule.every(30).minutes.do(job, sender)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário. Fechando WhatsApp...")
        sender.close()

if __name__ == "__main__":
    main()
