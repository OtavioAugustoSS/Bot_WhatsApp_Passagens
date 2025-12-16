# ✈️ Bot de Passagens Aéreas no WhatsApp

Um bot Python sofisticado que monitora o Google Flights via SerpApi para encontrar as melhores ofertas de passagens e envia alertas automatizados para um grupo de WhatsApp usando Selenium.

![Python](https://img.shields.io/badge/Python-3.13-blue) ![Selenium](https://img.shields.io/badge/Selenium-4.0-green) ![SerpApi](https://img.shields.io/badge/API-SerpApi-orange)

## 🚀 Funcionalidades

- **Monitoramento Multi-Rotas**: Busca voos de múltiplas origens (BSB, GYN, CGB, CGR) para grandes destinos nacionais e internacionais (MIA, LIS, MAD, MCO, EZE, GRU, GIG, etc.).
- **Filtro Inteligente**: 
  - Busca dinâmica de datas (Curto, Médio e Longo prazo).
  - Filtro de preço alvo por destino.
  - Detecção de "Oferta Real": Só alerta se o preço for significativamente menor que a média histórica (Insights da API ou algoritmo heurístico).
- **Alertas Automatizados no WhatsApp**: 
  - Usa sessão persistente do Selenium (Perfil de Usuário Chrome) para enviar mensagens sem precisar escanear QR Code repetidamente.
  - Envio robusto usando simulação de área de transferência (Ctrl+V) para suportar emojis e formatação perfeitamente.
- **Deep Linking**: Gera links diretos do Google Flights para reserva imediata.
- **Rastreamento via Banco de Dados**: Evita duplicidade de alertas para a mesma oferta usando um banco de dados SQLite local.

## 🛠️ Pré-requisitos

- **Python 3.10+**
- **Google Chrome** instalado.
- **Chave SerpApi**: Você precisa de uma conta na [SerpApi](https://serpapi.com/) para consultar o Google Flights.

## 📦 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/flight-bot.git
   cd flight-bot
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Crie um arquivo `.env` na raiz do projeto:
   ```env
   SERPAPI_KEY=sua_chave_serpapi_aqui
   WHATSAPP_GROUP_NAME="Nome Exato do Seu Grupo de WhatsApp"
   ```

## 🤖 Como Usar

1. Execute o bot:
   ```bash
   python main.py
   ```

2. **Configuração Inicial**: 
   - Uma janela do Chrome irá abrir.
   - **Escaneie o QR Code do WhatsApp Web** com seu celular.
   - O bot salvará sua sessão na pasta `chrome_profile` localmente. Nas próximas vezes, o login será automático.

3. O bot começará a buscar voos e enviar alertas para o grupo configurado a cada 30 minutos.

## ⚙️ Configuração

Você pode personalizar os parâmetros de busca no arquivo `main.py`:
- `ORIGINS`: Lista de códigos de aeroportos de origem.
- `DESTINATIONS`: Lista de códigos de aeroportos de destino.
- `PRICE_TARGETS`: Limite máximo de preço para cada destino.

## 📝 Licença

Este projeto está licenciado sob a Licença MIT.
