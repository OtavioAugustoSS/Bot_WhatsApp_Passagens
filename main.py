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

def job():
    print(f"\n--- Iniciando ciclo de busca: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    origin = "GRU"
    destination = "MIA"
    
    # Busca para amanhã (data dinâmica)
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    date = tomorrow
    
    searcher = FlightSearch()
    sender = WhatsAppSender()
    
    offers = searcher.search_flights(origin, destination, date)
    
    if not offers:
        print("Nenhuma oferta encontrada.")
        return

    enviados_count = 0
    for offer in offers:
        if not offer_exists(offer['id']):
            # 2. Copywriting e Correção de Acentuação
            # Formatando a data de YYYY-MM-DD para DD/MM/YYYY
            data_obj = datetime.datetime.strptime(offer['departure_date'], '%Y-%m-%d')
            data_formatada = data_obj.strftime('%d/%m/%Y')
            
            # Construção da mensagem com Emojis e Quebras de linha
            # Usando f-string normal, Python 3 trata utf-8 nativamente
            # Construção da mensagem com Unicode Escapes e Layout Novo
            # Construção da mensagem com Unicode Escapes e Layout Novo
            msg = (
                f"🚨 *ALERTA DE PRE\u00C7O BAIXO!* 🚨\n\n"
                f"✈️ *De:* {offer['origin']} - {offer['origin_city']} \n"
                f"🛬 *Para:* {offer['destination']} - {offer['destination_city']}\n"
                f"📅 *Data:* {offer['departure_date']}\n"
                f"🏨 *Cia:* {offer.get('airline', 'N/A')}\n\n"
                f"❌ ~De: R$ {offer['original_price']}~\n"
                f"✅ *Por: R$ {offer['price']}*\n\n"
                f"👇 *GARANTA AGORA:*\n"
                f"{offer['link']}"
            )
            
            print(f"Enviando a oferta: R$ {offer['price']} ({offer['airline']})")
            sender.send_message(msg)
            save_offer(offer)
            enviados_count += 1
            
            # Pausa para não atropelar o navegador
            time.sleep(8)
        
    if enviados_count > 0:
        print(f"Ciclo concluído. {enviados_count} ofertas enviadas.")

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
