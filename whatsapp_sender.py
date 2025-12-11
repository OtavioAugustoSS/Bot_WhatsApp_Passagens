import pywhatkit
import time
import os

class WhatsAppSender:
    def __init__(self):
        # Default to 'browser' if not specified, but user can set to 'log'
        self.method = os.getenv('NOTIFICATION_METHOD', 'browser').lower()
        self.group_id = os.getenv('WHATSAPP_GROUP_ID', '')

    def send_message(self, message):
        """Envia mensagem usando o método configurado."""
        if self.method == 'log':
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

    def _send_via_log(self, message):
        """Apenas loga no console (modo teste seguro)."""
        print(f"\n[TEST MODE - LOG ONLY] Mensagem que seria enviada:\n{'-'*30}\n{message}\n{'-'*30}\n")
