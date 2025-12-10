import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Estabelece conexão com o banco de dados MySQL."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'passagens_db'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def init_db():
    """Inicializa o banco de dados criando a tabela se não existir."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            with open('schema.sql', 'r') as f:
                schema = f.read()
            # Executa comandos SQL do arquivo (pode conter múltiplos comandos)
            statements = schema.split(';')
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
            conn.commit()
            print("Banco de dados inicializado com sucesso.")
        except Error as e:
            print(f"Erro ao inicializar banco de dados: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

def offer_exists(voo_id):
    """Verifica se uma oferta já foi enviada."""
    conn = get_connection()
    exists = False
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT id FROM ofertas_enviadas WHERE voo_id = %s"
            cursor.execute(query, (voo_id,))
            result = cursor.fetchone()
            if result:
                exists = True
        except Error as e:
            print(f"Erro ao verificar oferta: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return exists

def save_offer(offer_data):
    """Salva uma oferta enviada no banco de dados."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO ofertas_enviadas (voo_id, origem, destino, data_ida, preco)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                offer_data['id'],
                offer_data['origin'],
                offer_data['destination'],
                offer_data['departure_date'],
                offer_data['price']
            ))
            conn.commit()
            print(f"Oferta {offer_data['id']} salva no banco.")
        except Error as e:
            print(f"Erro ao salvar oferta: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
