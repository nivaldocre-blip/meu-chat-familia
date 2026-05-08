import flet as ft
import os

def main(page: ft.Page):
    page.title = "Chat Família"
    page.theme_mode = "light"
    
    usuario_atual = ""
    chat = ft.Column(expand=True, scroll="always", spacing=10)

    def criar_balao(texto, autor):
        sou_eu = (autor == usuario_atual)
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
        if txt_msg.value:
            page.pubsub.send_all({"autor": usuario_atual, "texto": txt_msg.value})
            txt_msg.value = ""
            page.update()

    nome_input = ft.TextField(label="Seu Nome", width=300)

    def entrar(e):
        nonlocal usuario_atual
        if nome_input.value:
            usuario_atual = nome_input.value
            page.clean()
            page.add(
                ft.Container(
                    content=ft.Text(f"Logado como: {usuario_atual}", color="white", weight="bold"),
                    bgcolor="#008069", padding=15
                ),
                chat,
                ft.Container(
                    content=ft.Row([txt_msg, ft.ElevatedButton("Enviar", on_click=enviar)]),
                    padding=10
                )
            )
            page.update()

    page.add(
        ft.Column([
            ft.Text("Chat Família", size=30, weight="bold"),
            nome_input,
            ft.ElevatedButton("Entrar", on_click=entrar)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
