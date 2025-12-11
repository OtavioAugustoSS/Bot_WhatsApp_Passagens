import webbrowser
import time
import os
import pyperclip
import pyautogui
import urllib.parse

class WhatsAppSender:
    def __init__(self):
        # Default to 'browser' if not specified
        self.method = os.getenv('NOTIFICATION_METHOD', 'browser').lower()
        self.group_id = os.getenv('WHATSAPP_GROUP_ID', '')

    def send_message(self, message):
        """Envia mensagem usando o método configurado."""
        if self.method == 'log':
            self._send_via_log(message)
        else:
            self._send_via_clipboard(message)

    def _send_via_clipboard(self, message):
        """
        Método Robust (Ctrl+C / Ctrl+V):
        1. Copia msg para o clipboard.
        2. Abre o link do grupo.
        3. Aguarda carregamento.
        4. Cola (Ctrl+V) e Envia (Enter).
        """
        try:
            print(f"--- ENVIANDO VIA CLIPBOARD (Grupo: {self.group_id}) ---")
            
            # 1. Copiar para o Clipboard (Resolve problemas de acentuação/UTF-8)
            pyperclip.copy(message)
            print("Mensagem copiada para a área de transferência.")
            
            # 2. Abrir WhatsApp Web no Grupo Específico
            # Ex: https://web.whatsapp.com/accept?code=XXXXXXX
            whatsapp_url = f"https://web.whatsapp.com/accept?code={self.group_id}"
            webbrowser.open(whatsapp_url)
            
            # 3. Aguardar carregamento (20s é seguro para a maioria das conexões)
            print("Aguardando 20 segundos para carregamento do WhatsApp Web...")
            time.sleep(20)
            
            # 4. Focar e Colar
            # Clicar no centro da tela (opcional, mas ajuda a garantir foco)
            # pyautogui.click(x=...) - Não vamos usar coords fixas por segurança.
            # Apenas Colar
            print("Colando mensagem...")
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2) # Espera breve para a colagem processar
            
            # 5. Enviar
            print("Enviando (Enter)...")
            pyautogui.press('enter')
            
            # 6. Fechar aba (Opcional, Ctrl+W)
            time.sleep(2)
            print("Fechando aba...")
            pyautogui.hotkey('ctrl', 'w')
            
            print("Processo de envio concluído.")
            
        except Exception as e:
            print(f"Erro no envio via Clipboard: {e}")

    def _send_via_log(self, message):
        """Apenas loga no console (modo teste seguro)."""
        print(f"\n[TEST MODE - LOG ONLY] Mensagem que seria enviada:\n{'-'*30}\n{message}\n{'-'*30}\n")
