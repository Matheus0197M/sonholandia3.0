"""Integração OAuth Google usando Flet"""
import flet as ft
from flet.auth.providers.google_oauth_provider import GoogleOAuthProvider
import threading
import webbrowser
import time

# Variável global para armazenar os dados do usuário após login
oauth_user_data = None
oauth_error = None
oauth_complete = False

# Credenciais do Google OAuth
client_id = '1044696575740-1v767ju0o31hm1dfads0cqfpgbp3n3f6.apps.googleusercontent.com'
id_secreto = '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'

def get_oauth_user_data():
    """Retorna os dados do usuário após login OAuth"""
    global oauth_user_data, oauth_error, oauth_complete
    return oauth_user_data, oauth_error, oauth_complete

def reset_oauth_state():
    """Reseta o estado do OAuth para uma nova tentativa"""
    global oauth_user_data, oauth_error, oauth_complete
    oauth_user_data = None
    oauth_error = None
    oauth_complete = False

def main(page: ft.Page):
    """Função principal do Flet para OAuth Google"""
    global oauth_user_data, oauth_error, oauth_complete
    
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.title = "Login com Google - Sonholândia"

    # URL de callback do Flet OAuth
    redirect_url = 'http://localhost:8550/oauth_callback'
    
    provider = GoogleOAuthProvider(
        client_id=client_id,
        client_secret=id_secreto, 
        redirect_url=redirect_url
    )

    # Inicializa textResult antes de usar
    textResult = ft.Column()

    def loginGoogle(e):
        """Inicia o fluxo OAuth"""
        global oauth_error, oauth_complete
        try:
            page.login(provider)
        except Exception as ex:
            print(f'Erro ao iniciar login: {ex}')
            oauth_error = 'Login não disponível,ou, Erro ao tentar logar'
            oauth_complete = True
            textResult.controls.clear()
            textResult.controls.append(
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        alignment='center',
                        horizontal_alignment='center',
                        spacing=10,
                        controls=[
                            ft.Text(
                                "Erro ao iniciar login!",
                                size=20,
                                weight='bold',
                                color=ft.colors.RED
                            ),
                            ft.Text(
                                "Fechando esta janela...",
                                size=12,
                                color=ft.colors.GREY
                            )
                        ]
                    )
                )
            )
            page.update()
            
            # Fecha a janela após 1 segundo
            def close_window_error():
                time.sleep(1)
                try:
                    page.window_close()
                except:
                    pass
            
            threading.Thread(target=close_window_error, daemon=True).start()

    def on_login(e):
        """Callback quando o login é concluído"""
        global oauth_user_data, oauth_error, oauth_complete
        
        if e.error:
            oauth_error = 'Login não disponível,ou, Erro ao tentar logar'
            oauth_complete = True
            print(f'Erro no login: {e.error}')
            textResult.controls.clear()
            textResult.controls.append(
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        alignment='center',
                        horizontal_alignment='center',
                        spacing=10,
                        controls=[
                            ft.Text(
                                "Erro ao fazer login!",
                                size=20,
                                weight='bold',
                                color=ft.colors.RED
                            ),
                            ft.Text(
                                "Fechando esta janela...",
                                size=12,
                                color=ft.colors.GREY
                            )
                        ]
                    )
                )
            )
            
            # Fecha a janela após 1 segundo em caso de erro
            def close_window_error():
                time.sleep(1)
                try:
                    page.window_close()
                except:
                    pass
            
            threading.Thread(target=close_window_error, daemon=True).start()
        else:
            # Login bem-sucedido - armazena os dados
            user = page.auth.user
            oauth_user_data = {
                'name': user.name,
                'email': user.email,
                'picture': getattr(user, 'picture', None),
                'id': getattr(user, 'id', None)
            }
            oauth_complete = True
            print('Logado com sucesso via Flet')
            print(f'Dados do usuário: {oauth_user_data}')

            textResult.controls.clear()
            textResult.controls.append(
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        alignment='center',
                        horizontal_alignment='center',
                        spacing=10,
                        controls=[
                            ft.Text(
                                "Login realizado com sucesso!",
                                size=20,
                                weight='bold',
                                color=ft.colors.GREEN
                            ),
                            ft.Text(f"Bem-vindo, {user.name}"),
                            ft.Text(f"Email: {user.email}"),
                            ft.Text(
                                "Redirecionando para o site...",
                                size=12,
                                color=ft.colors.GREY
                            )
                        ]
                    )
                )
            )
            
            # Fecha a janela após 2 segundos em caso de sucesso
            def close_window():
                time.sleep(2)
                try:
                    page.window_close()
                except:
                    pass

            threading.Thread(target=close_window, daemon=True).start()

        page.update()

    page.on_login = on_login

    login_button = ft.Container(
        alignment=ft.alignment.center,
        content=ft.ElevatedButton(
            'Fazer Login com o Google',
            icon="login",
            on_click=loginGoogle,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE_700,
                color=ft.colors.WHITE
            )
        )
    )

    page.add(
        ft.Container(
            alignment=ft.alignment.center,
            content=ft.Text(
                'Fazer Login com o Google',
                size=32,
                weight='900'
            )
        ),
        ft.Container(
            alignment=ft.alignment.center,
            content=ft.Image(
                src='https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/google.png',
                width=50,
                height=50
            )
        ),
        login_button,
        ft.Divider(),
        textResult
    )

def start_flet_oauth():
    """Inicia o servidor Flet OAuth em uma thread separada"""
    def run_flet():
        ft.app(
            target=main,
            port=8550,
            view=ft.AppView.FLET_APP_WEB,
            web_renderer=ft.WebRenderer.HTML
        )
    
    thread = threading.Thread(target=run_flet, daemon=True)
    thread.start()
    
    # Aguarda um pouco para o servidor iniciar
    time.sleep(1)
    
    # Abre o navegador
    webbrowser.open('http://localhost:8550')
    
    return thread