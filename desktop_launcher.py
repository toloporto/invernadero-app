"""
Lanzador de escritorio para Invernadero Galego.
Inicia el servidor uvicorn y abre la aplicación en modo ventana nativa independiente (Desktop App).
"""
import sys
import time
import subprocess
import webbrowser
import os
import shutil

SERVER_URL = "http://127.0.0.1:8000"

def buscar_navegador_para_modo_app():
    """Busca navegadores compatibles con el modo ventana independiente (--app)."""
    rutas_candidatas = [
        # Microsoft Edge (Windows estándar)
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        # Google Chrome
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        # Brave Browser
        os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    for ruta in rutas_candidatas:
        if os.path.exists(ruta):
            return ruta

    # En Linux o macOS
    for bin_name in ["google-chrome", "chromium", "microsoft-edge"]:
        path = shutil.which(bin_name)
        if path:
            return path
    return None

def abrir_ventana_app():
    """Abre la URL en modo ventana nativa de escritorio."""
    time.sleep(1.2)
    navegador = buscar_navegador_para_modo_app()
    if navegador:
        try:
            print(f"[Desktop App] Iniciando ventana nativa con: {navegador}")
            subprocess.Popen([navegador, f"--app={SERVER_URL}"])
            return
        except Exception as e:
            print(f"[Aviso] No se pudo iniciar en modo app ({e}), abriendo en navegador por defecto.")
    webbrowser.open(SERVER_URL)

if __name__ == "__main__":
    import threading
    import uvicorn

    print("=" * 65)
    print("🌱 INICIANDO INVERNADERO GALEGO • MODO APLICACIÓN DE ESCRITORIO")
    print("=" * 65)

    # Abrir ventana en segundo plano una vez inicie el servidor
    hilo_ventana = threading.Thread(target=abrir_ventana_app, daemon=True)
    hilo_ventana.start()

    # Arrancar servidor ASGI
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, log_level="warning")
