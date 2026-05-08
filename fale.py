import flet as ft
import os
import sqlite3

# --- BANCO DE DADOS (Para as mensagens não sumirem) ---
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
    
    # Criamos uma variável simples para o nome
    page.session.set("user", "")
    
    chat = ft.Column(expand=True, scroll="always", spacing=10)

    def criar_balao(texto, autor):
        sou_eu = (autor == page.session.get("user"))
        alinhamento = ft.MainAxisAlignment.END if sou_eu else ft.MainAxisAlignment.START
        cor_fundo = "#005c4b" if sou_eu else "#333333"
        
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text(autor, size=10, color="white", weight="bold"),
                        ft.Text(texto, color="white", size=16),
                    ], spacing=2, tight=True),
                    padding=12,
                    bgcolor=cor_fundo,
                    border_radius=ft.border_radius.only(
                        top_left=15, top_right=15, 
                        bottom_left=0 if not sou_eu else 15, 
                        bottom_right=0 if sou_eu else 15
                    ),
                )
            ],
            alignment=alinhamento
        )

    def carregar_historico():
        cursor = db_conn.cursor()
        cursor.execute("SELECT autor, texto FROM mensagens ORDER BY id ASC")
        for row in cursor.fetchall():
            chat.controls.append(criar_balao(row[1], row[0]))
        page.update()

    def on_message(msg):
        chat.controls.append(criar_balao(msg['texto'], msg['autor']))
        page.update()

    page.pubsub.subscribe(on_message)

    txt_msg = ft.TextField(
        hint_text="Mensagem...", 
        expand=True, 
        border_radius=20, 
        on_submit=lambda _: enviar(None)
    )

    def enviar(e):
        user = page.session.get("user")
        if txt_msg.value and user:
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO mensagens (autor, texto) VALUES (?, ?)", (user, txt_msg.value))
            db_conn.commit()
            page.pubsub.send_all({"autor": user, "texto": txt_msg.value})
            txt_msg.value = ""
            page.update()

    def entrar_clique(e):
        if nome_input.value:
            page.session.set("user", nome_input.value)
            page.clean()
            page.add(
                ft.Container(
                    content=ft.Text(f"Logado como: {nome_input.value}", color="white", weight="bold"),
                    bgcolor="#008069", padding=15
                ),
                ft.Container(content=chat, expand=True, padding=10),
                ft.Container(
                    content=ft.Row([
                        txt_msg, 
                        # Corrigido: usando ElevatedButton para evitar erro de ícone
                        ft.ElevatedButton("Enviar", on_click=enviar) 
                    ]),
                    padding=10
                )
            )
            carregar_historico()
            page.update()

    nome_input = ft.TextField(label="Seu Nome", width=300)
    
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("Chat Família", size=30, weight="bold"),
                nome_input,
                ft.ElevatedButton("Entrar", on_click=entrar_clique)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=50, alignment=ft.alignment.center
        )
    )

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    # Adicionamos o assets_dir para evitar erros de armazenamento
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
