import schedule
import time
from flight_search import FlightSearch
from database import init_db, offer_exists, save_offer
from whatsapp_sender import WhatsAppSender
import os

def job():
    print(f"Iniciando busca de passagens: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configurações de busca (podem vir de config ou DB)
    origin = "GRU"
    destination = "MIA"
    import datetime
    # Define data para amanhã (ou outra data futura desejada)
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    date = tomorrow
    
    searcher = FlightSearch()
    sender = WhatsAppSender()
    
    offers = searcher.buscar_voo(origin, destination, date)
    
    if not offers:
        print("Nenhuma oferta encontrada.")
        return

    for offer in offers:
        # Verifica se já enviou esta oferta específica
        if not offer_exists(offer['id']):
            # Monta mensagem
            msg = (
                f"✈️ PROMOÇÃO ENCONTRADA! ✈️\n"
                f"De: {offer['origin']} Para: {offer['destination']}\n"
                f"Data: {offer['departure_date']}\n"
                f"Preço: R$ {offer['price']}\n"
                f"Link: {offer['link']}"
            )
            
            # Envia notificação
            sender.send_message(msg)
            
            # Salva no banco para não enviar novamente
            save_offer(offer)
        else:
            print(f"Oferta {offer['id']} já enviada anteriormente.")

def main():
    print("Inicializando Bot de Passagens...")
    init_db()
    
    # Executa uma vez imediatamente ao iniciar
    job()
    
    # Agenda para rodar a cada 30 minutos
    schedule.every(30).minutes.do(job)
    
    print("Agendamento configurado. Aguardando execuções...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
