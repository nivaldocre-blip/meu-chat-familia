import flet as ft
import os

def main(page: ft.Page):
    page.title = "Chat Família"
    
    usuario_atual = ""
    chat = ft.Column(expand=True, scroll="always")

    def on_message(msg):
        chat.controls.append(ft.Text(f"{msg['autor']}: {msg['texto']}"))
        page.update()

    page.pubsub.subscribe(on_message)

    txt_msg = ft.TextField(hint_text="Mensagem...", expand=True)

    def enviar(e):
        if txt_msg.value:
            page.pubsub.send_all({"autor": usuario_atual, "texto": txt_msg.value})
            txt_msg.value = ""
            page.update()

    nome_input = ft.TextField(label="Seu Nome")

    def entrar(e):
        nonlocal usuario_atual
        if nome_input.value:
            usuario_atual = nome_input.value
            page.clean()
            page.add(
                ft.Text(f"Logado como: {usuario_atual}", weight="bold"),
                chat,
                ft.Row([txt_msg, ft.IconButton(icon="send", on_click=enviar)])
            )
            page.update()

    page.add(ft.Text("Chat Família"), nome_input, ft.ElevatedButton("Entrar", on_click=entrar))

if __name__ == "__main__":
    # O SEGREDO: Pegar a porta que o Render exigir ou usar 8080 por padrão
    porta = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
