import pywhatkit
import time
import os
import requests
import urllib.parse

class WhatsAppSender:
    def __init__(self):
        # Default to 'browser' if not specified, but user can set to 'log' or 'callmebot'
        self.method = os.getenv('NOTIFICATION_METHOD', 'browser').lower()
        self.group_id = os.getenv('WHATSAPP_GROUP_ID', '')
        self.callmebot_phone = os.getenv('CALLMEBOT_PHONE', '')
        self.callmebot_apikey = os.getenv('CALLMEBOT_APIKEY', '')

    def send_message(self, message):
        """Envia mensagem usando o método configurado."""
        if self.method == 'callmebot':
            self._send_via_callmebot(message)
        elif self.method == 'log':
            self._send_via_log(message)
        else:
            # Default: Browser (pywhatkit)
            self._send_via_browser(message)

    def _send_via_browser(self, message):
        """Usa pywhatkit (abre navegador)."""
        try:
            print(f"--- ENVIANDO VIA BROWSER (Grupo: {self.group_id}) ---\n{message}")
            # wait_time=20 para garantir carregamento
            pywhatkit.sendwhatmsg_to_group_instantly(self.group_id, message, wait_time=20, tab_close=True)
            print("Mensagem enviada via Browser.")
        except Exception as e:
            print(f"Erro no envio via Browser: {e}")

    def _send_via_callmebot(self, message):
        """Usa API do CallMeBot (sem navegador)."""
        try:
            print("--- ENVIANDO VIA CALLMEBOT API ---")
            if not self.callmebot_phone or not self.callmebot_apikey:
                print("ERRO: CALLMEBOT_PHONE ou CALLMEBOT_APIKEY não configurados.")
                return

            encoded_msg = urllib.parse.quote(message)
            url = f"https://api.callmebot.com/whatsapp.php?phone={self.callmebot_phone}&text={encoded_msg}&apikey={self.callmebot_apikey}"
            
            response = requests.get(url)
            if response.status_code == 200:
                print("Mensagem enviada via CallMeBot com sucesso!")
            else:
                print(f"Erro CallMeBot: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erro no envio via CallMeBot: {e}")

    def _send_via_log(self, message):
        """Apenas loga no console (modo teste seguro)."""
        print(f"\n[TEST MODE - LOG ONLY] Mensagem que seria enviada:\n{'-'*30}\n{message}\n{'-'*30}\n")
