import flet as ft
import os
import sqlite3

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect("chat.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS mensagens 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, autor TEXT, texto TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

def main(page: ft.Page):
    page.title = "Chat Família"
    page.theme_mode = "light"
    
    # Tenta ler o nome salvo no navegador do celular
    usuario_salvo = page.client_storage.get("user_name")
    
    chat = ft.Column(expand=True, scroll="always", spacing=10)

    def criar_balao(texto, autor):
        # Pega o nome de quem está logado agora
        nome_atual = page.client_storage.get("user_name")
        sou_eu = (autor == nome_atual)
        
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text(autor, size=10, color="white", weight="bold"),
                        ft.Text(texto, color="white", size=16),
                    ], spacing=2, tight=True),
                    padding=12,
                    bgcolor="#005c4b" if sou_eu else "#333333",
                    border_radius=ft.border_radius.only(
                        top_left=15, top_right=15, 
                        bottom_left=0 if not sou_eu else 15, 
                        bottom_right=0 if sou_eu else 15
                    ),
                )
            ],
            alignment=ft.MainAxisAlignment.END if sou_eu else ft.MainAxisAlignment.START
        )

    def on_message(msg):
        chat.controls.append(criar_balao(msg['texto'], msg['autor']))
        page.update()

    page.pubsub.subscribe(on_message)

    txt_msg = ft.TextField(hint_text="Mensagem...", expand=True, border_radius=20)

    def enviar(e):
        user = page.client_storage.get("user_name")
        if txt_msg.value and user:
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO mensagens (autor, texto) VALUES (?, ?)", (user, txt_msg.value))
            db_conn.commit()
            page.pubsub.send_all({"autor": user, "texto": txt_msg.value})
            txt_msg.value = ""
            page.update()

    def entrar(e):
        if nome_input.value:
            # SALVA O NOME NO CELULAR AQUI
            page.client_storage.set("user_name", nome_input.value)
            montar_chat()

    def montar_chat():
        page.clean()
        # Carrega o que já foi falado
        cursor = db_conn.cursor()
        cursor.execute("SELECT autor, texto FROM mensagens ORDER BY id ASC")
        for row in cursor.fetchall():
            chat.controls.append(criar_balao(row[1], row[0]))
            
        page.add(
            ft.Container(content=ft.Text(f"Logado como: {page.client_storage.get('user_name')}", color="white"), bgcolor="#008069", padding=10),
            chat,
            ft.Container(content=ft.Row([txt_msg, ft.ElevatedButton("Enviar", on_click=enviar)]), padding=10)
        )
        page.update()

    # SE JÁ TEM NOME SALVO, ENTRA DIRETO
    if usuario_salvo:
        montar_chat()
    else:
        nome_input = ft.TextField(label="Seu Nome")
        page.add(
            ft.Text("Chat Família", size=25),
            nome_input,
            ft.ElevatedButton("Entrar", on_click=entrar)
        )

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
