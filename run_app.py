# run_app.py
import os
import sys
import time
import subprocess

print("DEBUG (run_app.py): Script iniciado.")
print(f"DEBUG (run_app.py): sys.executable (executável do PyInstaller): {sys.executable}")
print(f"DEBUG (run_app.py): sys.version: {sys.version}")
print(f"DEBUG (run_app.py): os.getcwd(): {os.getcwd()}")

# Determinar o caminho para o ambiente de execução do PyInstaller
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
    print(f"DEBUG (run_app.py): sys._MEIPASS (diretório de extração): {base_path}")
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    print(f"DEBUG (run_app.py): Rodando em modo de desenvolvimento. Base path: {base_path}")

try:
    os.chdir(base_path)
    print(f"DEBUG (run_app.py): Diretório de trabalho alterado para: {os.getcwd()}")
except Exception as e:
    print(f"ERRO CRÍTICO (run_app.py): Falha ao mudar o diretório de trabalho para {base_path}: {e}")
    print("Verifique permissões ou integridade do pacote PyInstaller.")
    time.sleep(10)
    sys.exit(1)

# --- INÍCIO DA MUDANÇA NO run_app.py ---
# Vamos tentar encontrar o python.exe de forma mais robusta.
python_executable = None

# 1. Tentar o local mais comum: base_path
candidate_path = os.path.join(base_path, "python.exe")
if os.path.exists(candidate_path):
    python_executable = candidate_path

# 2. Tentar na pasta Lib\site-packages\ (onde o PyInstaller pode colocar o runtime)
if not python_executable:
    candidate_path = os.path.join(base_path, "Lib", "site-packages", "python.exe")
    if os.path.exists(candidate_path):
        python_executable = candidate_path

# 3. Tentar no _internal (onde o bootloader do PyInstaller pode residir)
if not python_executable:
    # Em --onedir, sys.executable (o NSLOG_App_Executavel.exe) está na pasta pai do _internal
    # Então, python.exe pode estar em _internal/
    candidate_path = os.path.join(os.path.dirname(sys.executable), "_internal", "python.exe")
    if os.path.exists(candidate_path):
        python_executable = candidate_path

# 4. Fallback: procurar no mesmo diretório do executável principal
if not python_executable:
    candidate_path = os.path.join(os.path.dirname(sys.executable), "python.exe")
    if os.path.exists(candidate_path):
        python_executable = candidate_path

if not python_executable:
    print(f"ERRO CRÍTICO (run_app.py): Não foi possível encontrar o python.exe empacotado após múltiplas tentativas.")
    print(f"Tentados caminhos relativos a '{base_path}' e '{os.path.dirname(sys.executable)}'.")
    time.sleep(10)
    sys.exit(1)

print(f"DEBUG (run_app.py): Interpretador Python empacotado encontrado em: {python_executable}")
# --- FIM DA MUDANÇA NO run_app.py ---

streamlit_app_path = "app.py"
print(f"DEBUG (run_app.py): Caminho do aplicativo Streamlit a ser executado: {streamlit_app_path}")
print(f"DEBUG (run_app.py): app.py existe no diretório atual? {os.path.exists(streamlit_app_path)}")

command = [
    python_executable,
    "-m", "streamlit", "run", streamlit_app_path,
    "--server.port", "8501",
    "--browser.gatherUsageStats", "false",
    "--server.enableXsrfProtection", "false",
    "--server.enableCORS", "false",
    "--server.baseUrlPath", "/",
]

print(f"DEBUG (run_app.py): Comando a ser executado: {' '.join(command)}")

try:
    print("DEBUG (run_app.py): Iniciando o Streamlit via subprocess...")
    process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr, text=True)
    print("DEBUG (run_app.py): Streamlit subprocess iniciado.")
    process.wait() 
    print("DEBUG (run_app.py): Processo Streamlit finalizado.")

except Exception as e:
    print(f"\n--- ERRO CRÍTICO (run_app.py): Falha ao iniciar ou executar Streamlit via subprocess ---")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensagem: {e}")
    import traceback
    traceback.print_exc()
    time.sleep(5) # Pausa extra em caso de erro

print("DEBUG (run_app.py): Fim do script. Pressione Enter para fechar o console.")
input("")