import streamlit as st
import hashlib

st.set_page_config(layout="wide")

# CSS personalizado para a página de login
st.markdown("""
<style>
    .login-container {
        max-width: 500px;
        margin: 100px auto;
        padding: 30px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        text-align: center;
    }
    .login-header {
        font-size: 2.2rem;
        color: #1a5276;
        margin-bottom: 1.5rem;
        font-weight: 700;
    }
    .login-subtitle {
        color: #7f8c8d;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    .login-input {
        margin: 20px 0;
    }
    .login-button {
        background: linear-gradient(135deg, #1a5276 0%, #2874a6 100%);
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 10px;
    }
    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    .login-logo {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        color: #1a5276;
    }
    .login-error {
        background: #f8d7da;
        color: #721c24;
        padding: 12px;
        border-radius: 8px;
        margin: 15px 0;
        border-left: 4px solid #e74c3c;
    }
    .login-info {
        background: #d1ecf1;
        color: #0c5460;
        padding: 12px;
        border-radius: 8px;
        margin: 15px 0;
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE AUTENTICAÇÃO ESTILIZADA ---
def check_password():
    """Retorna `True` se o usuário forneceu a senha correta."""
    
    def password_entered():
        """Verifica se a senha digitada está correta."""
        if st.session_state["password"] == st.secrets["authentication"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Não armazena a senha
        else:
            st.session_state["password_correct"] = False

    # Container principal de login
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Logo e título
        st.markdown('<div class="login-logo">🏥</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="login-header">UNIDAS MEDICAL</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Dashboard de Performance e Análise</p>', unsafe_allow_html=True)
        
        if "password_correct" not in st.session_state:
            # Mostra o input para senha.
            st.text_input(
                "🔒 Senha de Acesso", 
                type="password", 
                on_change=password_entered, 
                key="password",
                help="Digite a senha fornecida para acessar o dashboard",
                label_visibility="collapsed",
                placeholder="Digite sua senha de acesso..."
            )
            
            # Botão de entrar
            if st.button("🚀 Acessar Dashboard", type="primary", use_container_width=True):
                password_entered()
                st.rerun()
            
            # Informações
            st.markdown("""
            <div class="login-info">
                💡 Acesso restrito à equipe Unidas Medical. 
                Entre em contato com o administrador se precisar de acesso.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            return False
        
        elif not st.session_state["password_correct"]:
            # Senha incorreta
            st.text_input(
                "🔒 Senha de Acesso", 
                type="password", 
                on_change=password_entered, 
                key="password",
                help="Senha incorreta. Tente novamente.",
                label_visibility="collapsed",
                placeholder="Digite sua senha de acesso..."
            )
            
            # Botão de entrar
            if st.button("🚀 Tentar Novamente", type="primary", use_container_width=True):
                password_entered()
                st.rerun()
            
            # Mensagem de erro
            st.markdown("""
            <div class="login-error">
                ❌ Senha incorreta. Por favor, verifique e tente novamente.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            return False
        
        else:
            # Senha correta.
            st.markdown('</div>', unsafe_allow_html=True)
            return True

# --- VERIFICAÇÃO DE SENHA ---
if not check_password():
    # Adiciona um footer na página de login
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Unidas Medical © 2025 - Todos os direitos reservados</p>", unsafe_allow_html=True)
    st.stop()  # Para a execução se a senha não for fornecida corretamente

# --- PAGE SETUP (SÓ EXECUTA SE A SENHA ESTIVER CORRETA) ---
dash_page = st.Page(
    "Modules/Unidas_dashboard_month.py",
    title="Mês Atual",
    icon="📊"
)

dash_YTD_page = st.Page(
    "Modules/Unidas_dashboard_YTD.py",
    title="YTD",
    icon="📈"
)

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Dashboard Unidas": [dash_page, dash_YTD_page],
    }
)

# --- RUN NAVIGATION ---
pg.run()