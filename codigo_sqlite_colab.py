# Sistema de Gestão de Eventos Culturais - SQLite
# Para usar no Google Colab

import sqlite3
from datetime import datetime, timedelta
import hashlib
import random
import string

# ========== CONFIGURAÇÃO DO BANCO DE DADOS ==========

def criar_conexao():
    """Cria conexão com o banco de dados SQLite"""
    conn = sqlite3.connect('eventos_culturais.db')
    return conn

def criar_tabelas():
    """Cria todas as tabelas do sistema"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        telefone TEXT,
        cpf_cnpj TEXT UNIQUE,
        tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('participante', 'organizador', 'patrocinador')),
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabela de Eventos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organizador_id INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        descricao TEXT,
        data_inicio TIMESTAMP NOT NULL,
        data_fim TIMESTAMP,
        local TEXT NOT NULL,
        categoria TEXT NOT NULL,
        capacidade_maxima INTEGER NOT NULL,
        vagas_disponiveis INTEGER NOT NULL,
        valor_ingresso REAL DEFAULT 0,
        gratuito BOOLEAN DEFAULT 1,
        status TEXT DEFAULT 'ativo' CHECK(status IN ('ativo', 'cancelado', 'finalizado')),
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organizador_id) REFERENCES usuarios(id)
    )
    ''')
    
    # Tabela de Inscrições
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inscricoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participante_id INTEGER NOT NULL,
        evento_id INTEGER NOT NULL,
        data_inscricao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'confirmada' CHECK(status IN ('confirmada', 'cancelada', 'presente')),
        codigo_confirmacao TEXT UNIQUE NOT NULL,
        presente BOOLEAN DEFAULT 0,
        data_checkin TIMESTAMP,
        FOREIGN KEY (participante_id) REFERENCES usuarios(id),
        FOREIGN KEY (evento_id) REFERENCES eventos(id),
        UNIQUE(participante_id, evento_id)
    )
    ''')
    
    # Tabela de Avaliações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS avaliacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participante_id INTEGER NOT NULL,
        evento_id INTEGER NOT NULL,
        nota INTEGER NOT NULL CHECK(nota >= 1 AND nota <= 5),
        comentario TEXT,
        data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (participante_id) REFERENCES usuarios(id),
        FOREIGN KEY (evento_id) REFERENCES eventos(id),
        UNIQUE(participante_id, evento_id)
    )
    ''')
    
    # Tabela de Lista de Espera
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lista_espera (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participante_id INTEGER NOT NULL,
        evento_id INTEGER NOT NULL,
        posicao INTEGER NOT NULL,
        data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notificado BOOLEAN DEFAULT 0,
        FOREIGN KEY (participante_id) REFERENCES usuarios(id),
        FOREIGN KEY (evento_id) REFERENCES eventos(id),
        UNIQUE(participante_id, evento_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Tabelas criadas com sucesso!")

# ========== FUNÇÕES DE USUÁRIOS ==========

def cadastrar_usuario(nome, email, senha, telefone, cpf_cnpj, tipo_usuario):
    """Cadastra um novo usuário no sistema"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    # Hash da senha (segurança básica)
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    try:
        cursor.execute('''
        INSERT INTO usuarios (nome, email, senha, telefone, cpf_cnpj, tipo_usuario)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, email, senha_hash, telefone, cpf_cnpj, tipo_usuario))
        
        conn.commit()
        usuario_id = cursor.lastrowid
        print(f"✅ Usuário cadastrado com sucesso! ID: {usuario_id}")
        return usuario_id
    except sqlite3.IntegrityError as e:
        print(f"❌ Erro: {e}")
        return None
    finally:
        conn.close()

def listar_usuarios(tipo=None):
    """Lista todos os usuários ou por tipo"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    if tipo:
        cursor.execute('SELECT * FROM usuarios WHERE tipo_usuario = ?', (tipo,))
    else:
        cursor.execute('SELECT * FROM usuarios')
    
    usuarios = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*80}")
    print(f"{'ID':<5} {'Nome':<25} {'Email':<30} {'Tipo':<15}")
    print(f"{'='*80}")
    
    for user in usuarios:
        print(f"{user[0]:<5} {user[1]:<25} {user[2]:<30} {user[6]:<15}")
    
    print(f"{'='*80}\n")
    return usuarios

# ========== FUNÇÕES DE EVENTOS ==========

def criar_evento(organizador_id, titulo, descricao, data_inicio, local, categoria, 
                 capacidade_maxima, valor_ingresso=0, gratuito=True):
    """Cria um novo evento cultural"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO eventos (organizador_id, titulo, descricao, data_inicio, local, 
                           categoria, capacidade_maxima, vagas_disponiveis, 
                           valor_ingresso, gratuito)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (organizador_id, titulo, descricao, data_inicio, local, categoria,
              capacidade_maxima, capacidade_maxima, valor_ingresso, gratuito))
        
        conn.commit()
        evento_id = cursor.lastrowid
        print(f"✅ Evento criado com sucesso! ID: {evento_id}")
        return evento_id
    except Exception as e:
        print(f"❌ Erro ao criar evento: {e}")
        return None
    finally:
        conn.close()

def listar_eventos(status='ativo'):
    """Lista eventos por status"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT e.id, e.titulo, e.data_inicio, e.local, e.categoria, 
           e.vagas_disponiveis, e.capacidade_maxima, u.nome as organizador
    FROM eventos e
    JOIN usuarios u ON e.organizador_id = u.id
    WHERE e.status = ?
    ORDER BY e.data_inicio
    ''', (status,))
    
    eventos = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*100}")
    print(f"{'ID':<5} {'Título':<30} {'Data':<20} {'Local':<20} {'Vagas':<10}")
    print(f"{'='*100}")
    
    for evento in eventos:
        vagas_info = f"{evento[5]}/{evento[6]}"
        print(f"{evento[0]:<5} {evento[1]:<30} {evento[2]:<20} {evento[3]:<20} {vagas_info:<10}")
    
    print(f"{'='*100}\n")
    return eventos

def buscar_eventos(categoria=None, data_min=None):
    """Busca eventos por filtros"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    query = '''
    SELECT e.*, u.nome as organizador
    FROM eventos e
    JOIN usuarios u ON e.organizador_id = u.id
    WHERE e.status = 'ativo'
    '''
    params = []
    
    if categoria:
        query += ' AND e.categoria = ?'
        params.append(categoria)
    
    if data_min:
        query += ' AND e.data_inicio >= ?'
        params.append(data_min)
    
    query += ' ORDER BY e.data_inicio'
    
    cursor.execute(query, params)
    eventos = cursor.fetchall()
    conn.close()
    
    return eventos

# ========== FUNÇÕES DE INSCRIÇÕES ==========

def gerar_codigo_confirmacao():
    """Gera código único de confirmação"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def inscrever_participante(participante_id, evento_id):
    """Inscreve um participante em um evento"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    # Verificar vagas disponíveis
    cursor.execute('SELECT vagas_disponiveis FROM eventos WHERE id = ?', (evento_id,))
    resultado = cursor.fetchone()
    
    if not resultado:
        print("❌ Evento não encontrado!")
        conn.close()
        return None
    
    vagas_disponiveis = resultado[0]
    
    if vagas_disponiveis <= 0:
        print("❌ Não há vagas disponíveis! Deseja entrar na lista de espera?")
        conn.close()
        return 'lista_espera'
    
    codigo = gerar_codigo_confirmacao()
    
    try:
        cursor.execute('''
        INSERT INTO inscricoes (participante_id, evento_id, codigo_confirmacao)
        VALUES (?, ?, ?)
        ''', (participante_id, evento_id, codigo))
        
        # Atualizar vagas disponíveis
        cursor.execute('''
        UPDATE eventos 
        SET vagas_disponiveis = vagas_disponiveis - 1
        WHERE id = ?
        ''', (evento_id,))
        
        conn.commit()
        inscricao_id = cursor.lastrowid
        print(f"✅ Inscrição realizada com sucesso!")
        print(f"📋 Código de confirmação: {codigo}")
        return inscricao_id
    except sqlite3.IntegrityError:
        print("❌ Você já está inscrito neste evento!")
        return None
    finally:
        conn.close()

def adicionar_lista_espera(participante_id, evento_id):
    """Adiciona participante à lista de espera"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    # Obter próxima posição
    cursor.execute('''
    SELECT COALESCE(MAX(posicao), 0) + 1 
    FROM lista_espera 
    WHERE evento_id = ?
    ''', (evento_id,))
    
    posicao = cursor.fetchone()[0]
    
    try:
        cursor.execute('''
        INSERT INTO lista_espera (participante_id, evento_id, posicao)
        VALUES (?, ?, ?)
        ''', (participante_id, evento_id, posicao))
        
        conn.commit()
        print(f"✅ Adicionado à lista de espera na posição {posicao}")
        return True
    except sqlite3.IntegrityError:
        print("❌ Você já está na lista de espera deste evento!")
        return False
    finally:
        conn.close()

def cancelar_inscricao(participante_id, evento_id):
    """Cancela uma inscrição e libera vaga"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        UPDATE inscricoes 
        SET status = 'cancelada'
        WHERE participante_id = ? AND evento_id = ? AND status = 'confirmada'
        ''', (participante_id, evento_id))
        
        if cursor.rowcount > 0:
            # Liberar vaga
            cursor.execute('''
            UPDATE eventos 
            SET vagas_disponiveis = vagas_disponiveis + 1
            WHERE id = ?
            ''', (evento_id,))
            
            conn.commit()
            print("✅ Inscrição cancelada com sucesso!")
            return True
        else:
            print("❌ Inscrição não encontrada ou já cancelada!")
            return False
    finally:
        conn.close()

def realizar_checkin(codigo_confirmacao):
    """Realiza check-in no evento usando código"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        UPDATE inscricoes 
        SET presente = 1, status = 'presente', data_checkin = CURRENT_TIMESTAMP
        WHERE codigo_confirmacao = ? AND status = 'confirmada'
        ''', (codigo_confirmacao,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ Check-in realizado com sucesso!")
            return True
        else:
            print("❌ Código inválido ou check-in já realizado!")
            return False
    finally:
        conn.close()

def listar_minhas_inscricoes(participante_id):
    """Lista todas as inscrições de um participante"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT e.titulo, e.data_inicio, e.local, i.status, i.codigo_confirmacao, i.presente
    FROM inscricoes i
    JOIN eventos e ON i.evento_id = e.id
    WHERE i.participante_id = ?
    ORDER BY e.data_inicio DESC
    ''', (participante_id,))
    
    inscricoes = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*100}")
    print(f"{'Evento':<30} {'Data':<20} {'Local':<20} {'Status':<15} {'Presente'}")
    print(f"{'='*100}")
    
    for insc in inscricoes:
        presente = '✓' if insc[5] else '✗'
        print(f"{insc[0]:<30} {insc[1]:<20} {insc[2]:<20} {insc[3]:<15} {presente}")
    
    print(f"{'='*100}\n")
    return inscricoes

# ========== FUNÇÕES DE AVALIAÇÕES ==========

def avaliar_evento(participante_id, evento_id, nota, comentario=""):
    """Permite participante avaliar evento após participação"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    # Verificar se participou
    cursor.execute('''
    SELECT presente FROM inscricoes 
    WHERE participante_id = ? AND evento_id = ?
    ''', (participante_id, evento_id))
    
    resultado = cursor.fetchone()
    
    if not resultado or not resultado[0]:
        print("❌ Você precisa ter participado do evento para avaliá-lo!")
        conn.close()
        return False
    
    try:
        cursor.execute('''
        INSERT INTO avaliacoes (participante_id, evento_id, nota, comentario)
        VALUES (?, ?, ?, ?)
        ''', (participante_id, evento_id, nota, comentario))
        
        conn.commit()
        print("✅ Avaliação registrada com sucesso!")
        return True
    except sqlite3.IntegrityError:
        print("❌ Você já avaliou este evento!")
        return False
    finally:
        conn.close()

def visualizar_avaliacoes(evento_id):
    """Visualiza todas as avaliações de um evento"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT u.nome, a.nota, a.comentario, a.data_avaliacao
    FROM avaliacoes a
    JOIN usuarios u ON a.participante_id = u.id
    WHERE a.evento_id = ?
    ORDER BY a.data_avaliacao DESC
    ''', (evento_id,))
    
    avaliacoes = cursor.fetchall()
    
    if avaliacoes:
        # Calcular média
        cursor.execute('''
        SELECT AVG(nota) as media, COUNT(*) as total
        FROM avaliacoes
        WHERE evento_id = ?
        ''', (evento_id,))
        
        stats = cursor.fetchone()
        
        print(f"\n{'='*80}")
        print(f"📊 Média de Avaliações: {stats[0]:.1f}/5.0 ({stats[1]} avaliações)")
        print(f"{'='*80}")
        print(f"{'Participante':<25} {'Nota':<10} {'Comentário'}")
        print(f"{'='*80}")
        
        for av in avaliacoes:
            estrelas = '⭐' * av[1]
            print(f"{av[0]:<25} {estrelas:<10} {av[2] if av[2] else ''}")
        
        print(f"{'='*80}\n")
    else:
        print("ℹ️  Nenhuma avaliação disponível para este evento.")
    
    conn.close()
    return avaliacoes

# ========== RELATÓRIOS E CONSULTAS ==========

def relatorio_evento(evento_id):
    """Gera relatório completo de um evento"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    # Dados do evento
    cursor.execute('''
    SELECT e.*, u.nome as organizador
    FROM eventos e
    JOIN usuarios u ON e.organizador_id = u.id
    WHERE e.id = ?
    ''', (evento_id,))
    
    evento = cursor.fetchone()
    
    if not evento:
        print("❌ Evento não encontrado!")
        conn.close()
        return
    
    # Estatísticas de inscrições
    cursor.execute('''
    SELECT 
        COUNT(*) as total_inscricoes,
        SUM(CASE WHEN status = 'confirmada' THEN 1 ELSE 0 END) as confirmadas,
        SUM(CASE WHEN status = 'cancelada' THEN 1 ELSE 0 END) as canceladas,
        SUM(CASE WHEN presente = 1 THEN 1 ELSE 0 END) as presentes
    FROM inscricoes
    WHERE evento_id = ?
    ''', (evento_id,))
    
    stats = cursor.fetchone()
    
    # Avaliações
    cursor.execute('''
    SELECT AVG(nota) as media, COUNT(*) as total_avaliacoes
    FROM avaliacoes
    WHERE evento_id = ?
    ''', (evento_id,))
    
    aval_stats = cursor.fetchone()
    
    conn.close()
    
    # Exibir relatório
    print(f"\n{'='*80}")
    print(f"📊 RELATÓRIO DO EVENTO")
    print(f"{'='*80}")
    print(f"Título: {evento[2]}")
    print(f"Organizador: {evento[13]}")
    print(f"Data: {evento[4]}")
    print(f"Local: {evento[6]}")
    print(f"Categoria: {evento[7]}")
    print(f"Capacidade: {evento[8]} pessoas")
    print(f"\n{'='*80}")
    print(f"📈 ESTATÍSTICAS DE INSCRIÇÕES")
    print(f"{'='*80}")
    print(f"Total de Inscrições: {stats[0]}")
    print(f"Confirmadas: {stats[1]}")
    print(f"Canceladas: {stats[2]}")
    print(f"Presentes: {stats[3]}")
    
    if stats[1] > 0:
        taxa_comparecimento = (stats[3] / stats[1]) * 100
        print(f"Taxa de Comparecimento: {taxa_comparecimento:.1f}%")
    
    print(f"\n{'='*80}")
    print(f"⭐ AVALIAÇÕES")
    print(f"{'='*80}")
    
    if aval_stats[1] > 0:
        print(f"Média de Avaliação: {aval_stats[0]:.1f}/5.0")
        print(f"Total de Avaliações: {aval_stats[1]}")
    else:
        print("Nenhuma avaliação disponível")
    
    print(f"{'='*80}\n")

def eventos_por_categoria():
    """Exibe estatísticas de eventos por categoria"""
    conn = criar_conexao()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT categoria, COUNT(*) as total, 
           SUM(capacidade_maxima - vagas_disponiveis) as inscritos
    FROM eventos
    WHERE status = 'ativo'
    GROUP BY categoria
    ORDER BY total DESC
    ''')
    
    categorias = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"📊 EVENTOS POR CATEGORIA")
    print(f"{'='*60}")
    print(f"{'Categoria':<30} {'Eventos':<15} {'Inscritos'}")
    print(f"{'='*60}")
    
    for cat in categorias:
        print(f"{cat[0]:<30} {cat[1]:<15} {cat[2]}")
    
    print(f"{'='*60}\n")

# ========== DADOS DE EXEMPLO ==========

def popular_dados_exemplo():
    """Popula o banco com dados de exemplo para demonstração"""
    print("📝 Populando banco de dados com dados de exemplo...\n")
    
    # Cadastrar usuários
    print("👥 Cadastrando usuários...")
    org1 = cadastrar_usuario("Maria Silva", "maria@cultura.com", "senha123", 
                             "21999991111", "12345678901", "organizador")
    org2 = cadastrar_usuario("João Santos", "joao@eventos.com", "senha456",
                             "21999992222", "98765432100", "organizador")
    
    part1 = cadastrar_usuario("Ana Costa", "ana@email.com", "senha789",
                              "21999993333", "11122233344", "participante")
    part2 = cadastrar_usuario("Pedro Oliveira", "pedro@email.com", "senha321",
                              "21999994444", "55566677788", "participante")
    part3 = cadastrar_usuario("Julia Mendes", "julia@email.com", "senha654",
                              "21999995555", "99988877766", "participante")
    
    patrocinador = cadastrar_usuario("Empresa Cultural LTDA", "contato@empresa.com", 
                                     "senha987", "21999996666", "12345678000199", "patrocinador")
    
    # Criar eventos
    print("\n🎭 Criando eventos...")
    data_evento1 = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    data_evento2 = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
    data_evento3 = (datetime.now() + timedelta(days=21)).strftime('%Y-%m-%d %H:%M:%S')
    
    ev1 = criar_evento(org1, "Festival de Música Popular", 
                      "Grande festival com artistas locais", data_evento1,
                      "Praça Central", "Música", 100, 0, True)
    
    ev2 = criar_evento(org1, "Oficina de Teatro Comunitário",
                      "Aprenda técnicas básicas de teatro", data_evento2,
                      "Centro Cultural", "Teatro", 30, 0, True)
    
    ev3 = criar_evento(org2, "Exposição de Arte Contemporânea",
                      "Obras de artistas locais emergentes", data_evento3,
                      "Galeria Municipal", "Artes Visuais", 50, 0, True)
    
    # Realizar inscrições
    print("\n📝 Realizando inscrições...")
    inscrever_participante(part1, ev1)
    inscrever_participante(part2, ev1)
    inscrever_participante(part3, ev1)
    inscrever_participante(part1, ev2)
    inscrever_participante(part2, ev3)
    
    print("\n✅ Banco de dados populado com sucesso!")
    print("\nℹ️  Use as funções abaixo para interagir com o sistema:")
    print("   - listar_usuarios()")
    print("   - listar_eventos()")
    print("   - relatorio_evento(evento_id)")
    print("   - eventos_por_categoria()")

# ========== EXECUÇÃO PRINCIPAL ==========

if __name__ == "__main__":
    print("🎭 SISTEMA DE GESTÃO DE EVENTOS CULTURAIS")
    print("="*80)
    print("\n Criando estrutura do banco de dados...\n")
    
    criar_tabelas()
    
    print("\n🔄 Deseja popular com dados de exemplo? (s/n)")
    print("   (No Colab, execute: popular_dados_exemplo())")
    
    # Exemplo de uso
    print("\n📚 EXEMPLOS DE USO:")
    print("-"*80)
    print("# Popular com dados de exemplo:")
    print("popular_dados_exemplo()")
    print("\n# Listar todos os eventos:")
    print("listar_eventos()")
    print("\n# Ver relatório de um evento:")
    print("relatorio_evento(1)")
    print("\n# Listar minhas inscrições:")
    print("listar_minhas_inscricoes(3)")
    print("\n# Realizar check-in:")
    print("realizar_checkin('ABC123XYZ')")
    print("\n# Avaliar evento:")
    print("avaliar_evento(3, 1, 5, 'Evento maravilhoso!')")
    print("-"*80)