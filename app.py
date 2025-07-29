import streamlit as st
import sqlite3
import pandas as pd
import os # Para garantir o caminho do DB

# --- Configurações e Constantes ---
DB_NAME = 'uniforms.db'

UNIFORM_TYPES = ["Masculino", "Feminino"]
SIZES = ["PP", "P", "M", "G", "GG", "XG", "XXG", "37","38","39","40","41","42","43","44","45"]
MODELS = ["Polo", "Camiseta básica", "Calçado", "Luva Vaqueta", "Luva"]
COLORS = ["Branca", "Preta", "Azul", "Vermelha", "Amarela", "Cinza", "Verde", "Roxa", "Laranja"]

# --- Funções de Banco de Dados (SQLite) ---

def create_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row # Para acessar colunas por nome
        return conn
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
    return conn

def create_table():
    """Cria a tabela de Items se ela não existir."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uniforms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    type TEXT NOT NULL,
                    size TEXT NOT NULL,
                    model TEXT NOT NULL,
                    color TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    description TEXT
                )
            """)
            conn.commit()
            st.success("Banco de dados e tabela inicializados com sucesso (se necessário)!")
        except sqlite3.Error as e:
            st.error(f"Erro ao criar tabela: {e}")
        finally:
            conn.close()

def insert_uniform(name, uniform_type, size, model, color, quantity, description):
    """Insere um novo Item no banco de dados."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO uniforms (name, type, size, model, color, quantity, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, uniform_type, size, model, color, quantity, description))
            conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Erro ao cadastrar Item: {e}")
            return False
        finally:
            conn.close()

def select_all_uniforms():
    """Retorna todos os Items cadastrados."""
    conn = create_connection()
    uniforms = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM uniforms")
            uniforms = cursor.fetchall()
            uniforms = [tuple(row) for row in uniforms] # Convert Row objects to tuples
        except sqlite3.Error as e:
            st.error(f"Erro ao buscar Items: {e}")
        finally:
            conn.close()
    return uniforms

def select_uniform_by_id(uniform_id):
    """Retorna um Item pelo seu ID."""
    conn = create_connection()
    uniform = None
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM uniforms WHERE id = ?", (uniform_id,))
            uniform = cursor.fetchone()
            if uniform:
                uniform = tuple(uniform) # Convert Row object to tuple
        except sqlite3.Error as e:
            st.error(f"Erro ao buscar Item por ID: {e}")
        finally:
            conn.close()
    return uniform

def update_uniform(uniform_id, name, uniform_type, size, model, color, description):
    """Atualiza os atributos de um Item (exceto a quantidade)."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE uniforms
                SET name = ?, type = ?, size = ?, model = ?, color = ?, description = ?
                WHERE id = ?
            """, (name, uniform_type, size, model, color, description, uniform_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Erro ao atualizar Item: {e}")
            return False
        finally:
            conn.close()

def update_uniform_quantity(uniform_id, new_quantity):
    """Atualiza a quantidade em estoque de um Item."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE uniforms
                SET quantity = ?
                WHERE id = ?
            """, (new_quantity, uniform_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Erro ao atualizar quantidade do Item: {e}")
            return False
        finally:
            conn.close()

def delete_uniform(uniform_id):
    """Exclui um Item do banco de dados."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM uniforms WHERE id = ?", (uniform_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Erro ao excluir Item: {e}")
            return False
        finally:
            conn.close()

# --- Funções de Navegação Streamlit ---

def go_to_page(page_name, uniform_id=None):
    """Altera a página atual no `session_state` e força o re-render."""
    st.session_state.current_page = page_name
    st.session_state.selected_uniform_id = uniform_id # Para passar ID entre páginas
    st.rerun()

# --- Componentes de UI (Páginas) ---

def show_home_page():
    """Exibe a página inicial com as opções de menu."""
    st.image("logoNslog.png", width=200) # <--- AQUI!
    st.title("👕 Controle de Estoque de Items")
    st.write("Selecione uma opção abaixo para gerenciar seu estoque:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Cadastrar Novo Item", use_container_width=True):
            go_to_page("add")
    with col2:
        if st.button("📝 Editar Item", use_container_width=True):
            go_to_page("edit_select") # Vai para a tela de seleção primeiro
    with col3:
        if st.button("📊 Listar Itens", use_container_width=True):
            go_to_page("list")

    col4, col5 = st.columns(2) # Usando 2 colunas para os 2 últimos botões
    with col4:
        if st.button("🗑️ Excluir Item", use_container_width=True):
            go_to_page("delete_select") # Vai para a tela de seleção primeiro
    with col5:
        if st.button("📦 Movimentar Estoque", use_container_width=True):
            go_to_page("move_stock_select") # Vai para a tela de seleção primeiro

def show_add_uniform_page():
    """Página para cadastrar um novo Item."""
    st.title("➕ Cadastrar Novo Item")
    st.write("Preencha os detalhes do novo Item.")

    with st.form("add_uniform_form"):
        uniform_name = st.text_input("Nome do Item (Opcional)", placeholder="Ex: Camiseta Polo Azul MASC P")
        uniform_type = st.selectbox("Tipo", UNIFORM_TYPES, help="Selecione o tipo de Item (Masculino/Feminino)")
        size = st.selectbox("Tamanho", SIZES, help="Selecione o tamanho do Item")
        model = st.selectbox("Modelo", MODELS, help="Selecione o modelo do Item")
        color = st.selectbox("Cor", COLORS, help="Selecione a cor do Item")
        quantity = st.number_input("Quantidade Inicial em Estoque", min_value=0, value=0, step=1, help="Quantidade inicial disponível no estoque")
        description = st.text_area("Descrição (Opcional)", placeholder="Detalhes adicionais sobre o Item", height=100)

        submitted = st.form_submit_button("Cadastrar Item")
        if submitted:
            if quantity < 0:
                st.error("A quantidade inicial em estoque não pode ser negativa.")
            else:
                if insert_uniform(uniform_name, uniform_type, size, model, color, quantity, description):
                    st.success("Item cadastrado com sucesso!")
                    st.balloons()
                    # go_to_page("home") # Redireciona para a página inicial

    if st.button("⬅️ Voltar à Página Inicial"):
        go_to_page("home")

def show_list_uniforms_page():
    """Página para listar todos os Items cadastrados."""
    st.title("📊 Items Cadastrados")

    uniforms = select_all_uniforms()

    if not uniforms:
        st.info("Nenhum Item cadastrado ainda. Utilize a opção 'Cadastrar Novo Item' na tela inicial.")
    else:
        # Criar um DataFrame para exibir de forma organizada
        df = pd.DataFrame(uniforms, columns=["ID", "Nome", "Tipo", "Tamanho", "Modelo", "Cor", "Quantidade", "Descrição"])
        st.dataframe(df.set_index('ID'), use_container_width=True) # Exibe o ID como índice

    st.markdown("---") # Separador visual
    col_list_1, col_list_2, col_list_3, col_list_4 = st.columns(4)
    with col_list_1:
        if st.button("➕ Cadastrar Novo", use_container_width=True):
            go_to_page("add")
    with col_list_2:
        if st.button("📝 Editar Item", use_container_width=True):
            go_to_page("edit_select")
    with col_list_3:
        if st.button("🗑️ Excluir Item", use_container_width=True):
            go_to_page("delete_select")
    with col_list_4:
        if st.button("⬅️ Voltar à Página Inicial", use_container_width=True):
            go_to_page("home")

def show_select_uniform_for_action_page(action_type):
    """
    Página genérica para selecionar um Item antes de Editar, Excluir ou Movimentar Estoque.
    action_type: 'edit', 'delete', 'move_stock'
    """
    if action_type == 'edit':
        st.title("📝 Selecionar Item para Editar")
        button_label = "Editar Item Selecionado"
        next_page = "edit"
    elif action_type == 'delete':
        st.title("🗑️ Selecionar Item para Excluir")
        button_label = "Excluir Item Selecionado"
        next_page = "delete"
    elif action_type == 'move_stock':
        st.title("📦 Selecionar Item para Movimentar Estoque")
        button_label = "Movimentar Estoque do Item Selecionado"
        next_page = "move_stock"
    else:
        st.error("Ação inválida.")
        go_to_page("home")
        return

    uniforms = select_all_uniforms()

    if not uniforms:
        st.warning("Nenhum Item cadastrado para esta ação.")
        if st.button("⬅️ Voltar à Página Inicial"):
            go_to_page("home")
        return

    # Cria uma lista de opções legíveis para o selectbox
    uniform_options = {f"{u[0]} - {u[1]} ({u[2]}, {u[3]}, {u[4]}, {u[5]}) - Qtd: {u[6]}": u[0] for u in uniforms}
    
    selected_option_key = st.selectbox(
        "Selecione um Item:",
        options=list(uniform_options.keys()),
        help="Selecione o Item desejado para prosseguir com a ação."
    )

    if st.button(button_label, type="primary"):
        selected_id = uniform_options[selected_option_key]
        go_to_page(next_page, uniform_id=selected_id)

    if st.button("⬅️ Voltar à Página Inicial"):
        go_to_page("home")

def show_edit_uniform_page(uniform_id):
    """Página para editar os atributos de um Item."""
    uniform = select_uniform_by_id(uniform_id)

    if not uniform:
        st.error("Item não encontrado ou ID inválido.")
        if st.button("⬅️ Voltar"):
            go_to_page("home")
        return

    st.title(f"📝 Editar Item: {uniform[1]} (ID: {uniform[0]})") # uniform[1] é o nome do Item
    st.write("Altere os detalhes do Item abaixo. A quantidade em estoque só pode ser alterada via 'Movimentar Estoque'.")

    # Encontra os índices para preencher os selectbox corretamente
    type_idx = UNIFORM_TYPES.index(uniform[2]) if uniform[2] in UNIFORM_TYPES else 0
    size_idx = SIZES.index(uniform[3]) if uniform[3] in SIZES else 0
    model_idx = MODELS.index(uniform[4]) if uniform[4] in MODELS else 0
    color_idx = COLORS.index(uniform[5]) if uniform[5] in COLORS else 0

    with st.form("edit_uniform_form"):
        uniform_name = st.text_input("Nome do Item (Opcional)", value=uniform[1])
        uniform_type = st.selectbox("Tipo", UNIFORM_TYPES, index=type_idx)
        size = st.selectbox("Tamanho", SIZES, index=size_idx)
        model = st.selectbox("Modelo", MODELS, index=model_idx)
        color = st.selectbox("Cor", COLORS, index=color_idx)
        # Quantidade é exibida, mas desabilitada para edição direta
        st.text_input("Quantidade Atual em Estoque", value=uniform[6], disabled=True, help="Para alterar a quantidade, use a opção 'Movimentar Estoque' na tela inicial.")
        description = st.text_area("Descrição (Opcional)", value=uniform[7], height=100)

        submitted = st.form_submit_button("Salvar Alterações")
        if submitted:
            if update_uniform(uniform_id, uniform_name, uniform_type, size, model, color, description):
                st.success("Item atualizado com sucesso!")
                st.balloons()
                #go_to_page("home")

    if st.button("⬅️ Voltar"):
        go_to_page("home")

def show_delete_uniform_page(uniform_id):
    """Página para confirmar a exclusão de um Item."""
    uniform = select_uniform_by_id(uniform_id)

    if not uniform:
        st.error("Item não encontrado ou ID inválido.")
        if st.button("⬅️ Voltar"):
            go_to_page("home")
        return

    st.title("🗑️ Excluir Item")
    st.warning(f"Você está prestes a excluir o Item: **{uniform[1]}** (ID: {uniform[0]})")
    st.write("Esta ação é irreversível e removerá permanentemente o Item do sistema.")

    if st.button("CONFIRMAR EXCLUSÃO", type="secondary"):
        if delete_uniform(uniform_id):
            st.success("Item excluído com sucesso!")
            #go_to_page("home") # Redireciona para a página inicial

    if st.button("⬅️ Cancelar e Voltar"):
        go_to_page("home")

def show_move_stock_page(uniform_id):
    """Página para movimentar o estoque (entrada/saída)."""
    uniform = select_uniform_by_id(uniform_id)

    if not uniform:
        st.error("Item não encontrado ou ID inválido.")
        if st.button("⬅️ Voltar"):
            go_to_page("home")
        return

    st.title(f"📦 Movimentar Estoque: {uniform[1]} (ID: {uniform[0]})")
    st.markdown(f"Quantidade Atual em Estoque: **<span style='font-size: 24px; color: {'green' if uniform[6] > 0 else 'red'};'>{uniform[6]}</span>**", unsafe_allow_html=True)


    with st.form("move_stock_form"):
        movement_type = st.radio("Tipo de Movimentação", ["Entrada", "Saída"], horizontal=True)
        quantity_change = st.number_input("Quantidade", min_value=1, value=1, step=1, help="Quantidade a ser movimentada")

        submitted = st.form_submit_button("Realizar Movimentação")
        if submitted:
            current_quantity = uniform[6]
            new_quantity = current_quantity

            if movement_type == "Entrada":
                new_quantity = current_quantity + quantity_change
            else: # Saída
                if quantity_change > current_quantity:
                    st.error(f"Não há estoque suficiente para a saída. Quantidade disponível: {current_quantity}")
                    return # Não prossegue com a atualização

                new_quantity = current_quantity - quantity_change

            if update_uniform_quantity(uniform_id, new_quantity):
                st.success("Estoque movimentado com sucesso!")
                st.balloons()
                #go_to_page("home")

    if st.button("⬅️ Voltar"):
        go_to_page("home")

# --- Lógica Principal da Aplicação ---

def main():
    """Função principal que controla o fluxo da aplicação Streamlit."""
    st.set_page_config(page_title="Controle de Estoque de Items", layout="centered", initial_sidebar_state="collapsed")

    # Inicializa o banco de dados e a tabela na primeira execução
    create_table()

    # Inicializa o session_state para controlar a navegação
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    if 'selected_uniform_id' not in st.session_state:
        st.session_state.selected_uniform_id = None

    # Roteamento das páginas
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "add":
        show_add_uniform_page()
    elif st.session_state.current_page == "list":
        show_list_uniforms_page()
    elif st.session_state.current_page == "edit_select":
        show_select_uniform_for_action_page("edit")
    elif st.session_state.current_page == "edit":
        show_edit_uniform_page(st.session_state.selected_uniform_id)
    elif st.session_state.current_page == "delete_select":
        show_select_uniform_for_action_page("delete")
    elif st.session_state.current_page == "delete":
        show_delete_uniform_page(st.session_state.selected_uniform_id)
    elif st.session_state.current_page == "move_stock_select":
        show_select_uniform_for_action_page("move_stock")
    elif st.session_state.current_page == "move_stock":
        show_move_stock_page(st.session_state.selected_uniform_id)

if __name__ == "__main__":
    main()