from database import get_connection
import mysql.connector

def clear_history():
    print("Conectando ao banco de dados...")
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            print("Apagando histórico de ofertas enviadas...")
            # Usa TRUNCATE para limpar a tabela e resetar o ID autoincrement
            cursor.execute("TRUNCATE TABLE ofertas_enviadas")
            conn.commit()
            print("✅ Sucesso! O histórico foi limpo. O bot agora vai reenviar todas as ofertas.")
        except mysql.connector.Error as e:
            print(f"Erro ao limpar banco: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        print("Erro: Não foi possível conectar ao banco.")

if __name__ == "__main__":
    clear_history()
