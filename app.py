from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from manipulador_tickets import ManipuladorTickets

app = Flask(__name__)

CHAVE_API = "CHAVE DA API"


# Função para conectar ao banco de dados MySQL
def conectar_banco():
    return mysql.connector.connect(
        host="localhost",
        user="thales",
        password="141452",
        database="AUTOMACAO"
    )


# Função para salvar o diário no banco de dados
def salvar_no_banco(ticket_id, blip, cliente, criticidade, descricao, user_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    sql = """
    INSERT INTO diarios (ticket_id, blip, cliente, criticidade, descricao, user_id)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (ticket_id, blip, cliente, criticidade, descricao, user_id))
    conn.commit()
    cursor.close()
    conn.close()


@app.route('/')
def index():
    username = request.args.get('user_id')  # O nome do usuário será passado pela URL
    conn = conectar_banco()
    cursor = conn.cursor()

    # Buscar o user_id baseado no username
    cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        return render_template('index.html', erro="Usuário não encontrado.")

    user_id = user[0]  # ID do usuário encontrado

    # Busca somente os tickets daquele usuário para o dia atual
    cursor.execute("SELECT ticket_id, blip, cliente, criticidade, descricao FROM diarios WHERE user_id = %s AND data = CURDATE()", (user_id,))
    tickets_salvos = cursor.fetchall()

    tickets_formatados = []
    for ticket in tickets_salvos:
        ticket_id = f"<strong>{ticket[0]}/{ticket[1]} {ticket[2]}</strong>"
        criticidade_str = f"<span class='critical'>(C)</span>" if ticket[3] == 'C' else f"<span class='return'>(R)</span>" if ticket[3] == 'R' else ''
        descricao = ticket[4]
        ticket_formatado = f"{ticket_id} {criticidade_str}<br> {descricao}"
        tickets_formatados.append(ticket_formatado)

    cursor.close()
    conn.close()
    return render_template('index.html', tickets=tickets_formatados)

@app.route('/buscar_tickets', methods=['POST'])
def buscar_tickets():
    ids_tickets = request.form.get('ids_tickets')
    blips = request.form.get('blip')
    criticidade = request.form.get('criticidade')
    username = request.form.get('user_id').strip()  # O campo user_id captura o nome do usuário

    # Verifica se os IDs e BLIPs foram preenchidos corretamente
    ids_tickets_list = [id.strip() for id in ids_tickets.split(',')]
    blips_list = [blip.strip() for blip in blips.split(',')]

    if len(ids_tickets_list) != len(blips_list):
        return redirect(url_for('index', erro="A quantidade de IDs de tickets não corresponde à quantidade de BLIPs."))

    # Buscar o user_id com base no nome do usuário
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user is None:
        return redirect(url_for('index', erro="Usuário não encontrado."))

    user_id = user['id']  # Agora temos o user_id correto

    # Instancia o manipulador de tickets
    manipulador_tickets = ManipuladorTickets(chave_api=CHAVE_API)

    try:
        # Associa cada ID de ticket com seu BLIP correspondente e realiza a busca
        for ticket_id, blip in zip(ids_tickets_list, blips_list):
            tickets = manipulador_tickets.obter_tickets_por_ids(ticket_id, criticidade)
            if not tickets:
                continue  # Se nenhum ticket for encontrado para o ID atual, passa para o próximo

            # Salvar os tickets no banco de dados para o usuário logado
            for ticket in tickets:
                cliente = manipulador_tickets.obter_nome_cliente(ticket)
                descricao = ticket.get('actions', [{}])[-1].get('description', 'Sem descrição')
                salvar_no_banco(ticket_id, blip, cliente, criticidade, descricao, user_id)

        return redirect(url_for('index', user_id=username))  # Passa o username pela URL para filtrar depois
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return redirect(url_for('index', erro="Ocorreu um erro durante a busca dos tickets."))

@app.route('/limpar_diario', methods=['POST'])
def limpar_diario():
    username = request.form.get('user_id').strip()

    if not username:
        return redirect(url_for('index', erro="Usuário não especificado."))

    # Buscar o user_id com base no nome do usuário
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        return redirect(url_for('index', erro="Usuário não encontrado."))

    user_id = user['id']

    # Excluir todos os tickets do dia atual para o usuário
    try:
        cursor.execute("DELETE FROM diarios WHERE user_id = %s AND data = CURDATE()", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index', user_id=username, msg="Diário limpo com sucesso."))
    except Exception as e:
        print(f"Ocorreu um erro ao limpar o diário: {e}")
        return redirect(url_for('index', erro="Ocorreu um erro ao limpar o diário."))

if __name__ == "__main__":
    app.run()
