import mysql.connector
from mysql.connector import errorcode

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'user': 'thales',          # Substitua pelo seu usuário do MySQL
    'password': '141452', # Substitua pela sua senha do MySQL
}

DB_NAME = 'automacao'

# Função para criar o banco de dados
def criar_banco(conexao, cursor):
    try:
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Banco de dados '{DB_NAME}' criado com sucesso!")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            print(f"Banco de dados '{DB_NAME}' já existe.")
        else:
            print(f"Erro ao criar banco de dados: {err}")

# Função para criar tabelas
def criar_tabelas(conexao, cursor):
    cursor.execute(f"USE {DB_NAME}")

    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            senha_hash VARCHAR(255) NOT NULL,
            is_master BOOLEAN DEFAULT 0
        );
    """)

    # Tabela de Diários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticket_id VARCHAR(100) NOT NULL,
            blip VARCHAR(100),
            cliente VARCHAR(255),
            criticidade VARCHAR(1),
            descricao TEXT,
            data DATE DEFAULT (CURRENT_DATE),
            user_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
    """)

    print("Tabelas criadas com sucesso!")

# Função para inserir usuários iniciais
def inserir_usuarios(cursor):
    usuarios_iniciais = [
        ('rafael', '$2b$12$e.hjZGAOQ3ypDxD8MwKh4ezyRbZgzQ2.pNNGp3ZzZ6GiFoyc.ZCQe', 0),
        ('thales', '$2b$12$s4tm1f9v8ZTqz.wKlLsy9eM8R8g2GRzOx1ZbG3OoTlzBGU3SMN2Ei', 0),
        ('leonardo', '$2b$12$4NjHbjpk1x8Y3vEQKN3uTOEnxYPfgtRbAaRXwnL7EKwFczPS0Z6fq', 0),
        ('henrique', '$2b$12$bbCEmnGfA1.joGNdqKDL4OhGVhoqGRgoKLMyYIuRcf7AwDDOUhfnC', 0)
    ]
    for usuario in usuarios_iniciais:
        try:
            cursor.execute("""
                INSERT INTO usuarios (username, senha_hash, is_master)
                VALUES (%s, %s, %s)
            """, usuario)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                print(f"Usuário '{usuario[0]}' já existe.")
            else:
                print(f"Erro ao inserir usuário: {err}")

# Função principal
def main():
    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        cursor = conexao.cursor()

        criar_banco(conexao, cursor)
        criar_tabelas(conexao, cursor)
        inserir_usuarios(cursor)

        conexao.commit()
        cursor.close()
        conexao.close()

        print("Configuração concluída com sucesso!")

    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")

if __name__ == "__main__":
    main()
