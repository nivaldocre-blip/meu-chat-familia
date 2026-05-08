import flet as ft
import os # ESSA LINHA É NOVA

def main(page: ft.Page):
    page.title = "Chat Família"
    page.theme_mode = "light"
    page.padding = 0
    
    usuario_atual = ""
    chat = ft.Column(expand=True, scroll="always", spacing=10)

    def criar_balao(texto, autor):
        sou_eu = (autor == usuario_atual)
        alinhamento = "end" if sou_eu else "start"
        cor_balao = "#005c4b" if sou_eu else "#333333" 
        
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text(autor, size=10, color="white", weight="bold"),
                        ft.Text(texto, color="white", size=16),
                    ], spacing=2, tight=True),
                    padding=12,
                    bgcolor=cor_balao,
                    border_radius=ft.BorderRadius(15, 15, 15 if sou_eu else 0, 0 if sou_eu else 15),
                    shadow=ft.BoxShadow(blur_radius=5, color="black26"),
                )
            ],
            alignment=alinhamento
        )

    def on_message(msg_data):
        if isinstance(msg_data, dict):
            chat.controls.append(criar_balao(msg_data["texto"], msg_data["autor"]))
            page.update()

    page.pubsub.subscribe(on_message)

    txt_msg = ft.TextField(
        hint_text="Digite aqui...",
        expand=True,
        border_radius=20,
        on_submit=lambda _: enviar_click(None)
    )

    def enviar_click(e):
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
                    content=ft.Text(f"Chat: {usuario_atual}", color="white", weight="bold"),
                    bgcolor="#008069", padding=15
                ),
                ft.Container(content=chat, expand=True, padding=10),
                ft.Container(
                    content=ft.Row([txt_msg, ft.IconButton(icon="send", on_click=enviar_click)]),
                    padding=10
                )
            )
            page.update()

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("Chat Família", size=30, weight="bold"),
                nome_input,
                ft.ElevatedButton("Entrar", on_click=entrar)
            ], horizontal_alignment="center"),
            padding=50, alignment="center"
        )
    )

if __name__ == "__main__":
    # ESSA LINHA ABAIXO É O QUE FAZ FUNCIONAR NO RENDER:
    ft.app(target=main, view=None, port=int(os.getenv("PORT", 8080)), host="0.0.0.0")
