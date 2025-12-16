from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import pyperclip
import webbrowser

class WhatsAppBot:
    def __init__(self):
        self.group_name = os.getenv('WHATSAPP_GROUP_NAME')
        self.driver = None
        if not self.group_name:
            print("ERRO: WHATSAPP_GROUP_NAME não configurado no .env")
            return

        options = webdriver.ChromeOptions()
        profile_path = os.path.join(os.getcwd(), 'chrome_profile')
        options.add_argument(f"user-data-dir={profile_path}")
        
        # Stability Flags
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")

        print("Iniciando WebDriver...")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 60)
        
        # Open WhatsApp once at startup
        self._ensure_whatsapp_open()

    def _ensure_whatsapp_open(self):
        """Garante que o WhatsApp Web esteja carregado e pronto."""
        if "web.whatsapp.com" not in self.driver.current_url:
            print("Abrindo WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
        print("Aguardando carregamento da página (ou scan do QR Code)...")
        # pane-side é o container da lista de chats
        self.wait.until(EC.presence_of_element_located((By.ID, "pane-side")))
        print("WhatsApp Web carregado!")

    def _open_group_chat(self):
        """Busca e abre o chat do grupo alvo."""
        try:
            print(f"Buscando pelo grupo: {self.group_name}")
            
            # Encontrar caixa de busca
            search_box_xpath = '//div[@contenteditable="true"][@data-tab="3"]'
            search_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, search_box_xpath)))
            
            # Limpar e Buscar
            search_box.clear()
            search_box.send_keys(self.group_name)
            time.sleep(1.5) 
            
            # Clicar no Chat
            chat_xpath = f'//span[@title="{self.group_name}"]'
            chat_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, chat_xpath)))
            chat_element.click()
            print("Chat aberto.")
            time.sleep(1) 
            return True
            
        except Exception as e:
            print(f"Erro ao abrir chat: {e}")
            return False

    def send_message(self, message):
        if not self.driver:
            return

        try:
            self._ensure_whatsapp_open()
            
            if not self._open_group_chat():
                print("Não foi possível abrir o chat do grupo.")
                return

            print("Enviando mensagem...")
            
            # Localizar caixa de mensagem
            message_box_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
            message_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, message_box_xpath)))
            
            # 1. Copiar mensagem para área de transferência (Suporte a Emojis)
            pyperclip.copy(message)
            
            # 2. Colar (Ctrl + V)
            message_box.send_keys(Keys.CONTROL + 'v')
            time.sleep(1) 
            
            # 3. Enviar (Enter)
            message_box.send_keys(Keys.ENTER)
            print("Mensagem enviada!")
            
            # Delay de segurança
            time.sleep(2)

        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def close(self):
        if self.driver:
            print("Encerrando WebDriver...")
            self.driver.quit()
