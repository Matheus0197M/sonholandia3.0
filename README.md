# Sonholândia 3.0

Aplicação web para compartilhamento de sonhos com sistema completo de autenticação.

## 🚀 Funcionalidades

- ✅ Login com email/usuário e senha
- ✅ Login automático (modo teste)
- ✅ Login com Google OAuth
- ✅ Login com Facebook OAuth
- ✅ Cadastro de novos usuários
- ✅ Recuperação de senha
- ✅ Feed de sonhos
- ✅ Sistema de sessão seguro

## 📁 Estrutura do Projeto

```
sonholandia3.0/
├── app.py                 # Aplicação principal
├── config/                # Configurações
│   └── __init__.py       # Classe Config
├── models/                # Modelos de banco de dados
│   └── __init__.py       # Funções de banco de dados
├── routes/                # Rotas da aplicação
│   ├── __init__.py       # Blueprints
│   ├── auth.py           # Rotas de autenticação
│   ├── main.py           # Rotas principais
│   └── oauth.py          # Rotas OAuth
├── utils/                 # Utilitários
│   └── __init__.py       # Funções auxiliares
├── templates/             # Templates HTML
│   ├── index.html        # Página de login
│   ├── signup.html       # Página de cadastro
│   ├── forgot_password.html  # Recuperação de senha
│   ├── reset_password.html   # Redefinir senha
│   └── feed.html         # Feed de sonhos
├── static/                # Arquivos estáticos
│   ├── css/              # Estilos
│   ├── js/               # JavaScript
│   └── assets/           # Imagens
├── requirements.txt      # Dependências
└── users.db              # Banco de dados SQLite (gerado automaticamente)
```

## 🛠️ Instalação

1. **Clone o repositório** (ou navegue até a pasta do projeto)

2. **Crie um ambiente virtual** (recomendado):
```bash
python -m venv venv
```

3. **Ative o ambiente virtual**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

5. **Configure as variáveis de ambiente**:
   - Crie um arquivo `.env` na raiz do projeto
   - Copie o exemplo abaixo e preencha com suas credenciais:

```env
# Chave secreta do Flask
SECRET_KEY=sua_chave_secreta_aqui

# Banco de dados
DATABASE=users.db

# OAuth Google (opcional)
GOOGLE_CLIENT_ID=seu_google_client_id
GOOGLE_CLIENT_SECRET=seu_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google

# OAuth Facebook (opcional)
FACEBOOK_CLIENT_ID=seu_facebook_client_id
FACEBOOK_CLIENT_SECRET=seu_facebook_client_secret
FACEBOOK_REDIRECT_URI=http://localhost:5000/auth/facebook

# Email para recuperação de senha (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_de_app

# SSL/TLS
SSL_VERIFY=True
```

## 🔑 Como obter credenciais OAuth

### Google OAuth:
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Vá em "APIs & Services" > "Credentials"
4. Clique em "Create Credentials" > "OAuth client ID"
5. Configure o tipo de aplicação (Web application)
6. Adicione URI de redirecionamento: `http://localhost:5000/auth/google`
7. Copie o Client ID e Client Secret para o `.env`

### Facebook OAuth:
1. Acesse [Facebook Developers](https://developers.facebook.com/)
2. Crie um novo app
3. Adicione o produto "Facebook Login"
4. Configure as URLs de redirecionamento: `http://localhost:5000/auth/facebook`
5. Copie o App ID e App Secret para o `.env`

## 🚀 Executando a aplicação

```bash
python app.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 📝 Rotas Disponíveis

- `/` - Página de login
- `/loginNormal` - Login com email/senha (POST)
- `/loginAutomatico` - Login automático (teste)
- `/loginWithGoogle` - Iniciar login com Google
- `/loginWithFacebook` - Iniciar login com Facebook
- `/signUp` - Cadastro de usuário
- `/forgotPassword` - Solicitar recuperação de senha
- `/resetPassword/<token>` - Redefinir senha com token
- `/feed` - Feed de sonhos (requer autenticação)
- `/logout` - Sair da conta

## 🔒 Segurança

- Senhas são armazenadas com hash usando Werkzeug
- Tokens de reset de senha expiram em 1 hora
- Sessões protegidas
- Validação de dados de entrada
- Proteção contra SQL injection (usando prepared statements)

## 📦 Dependências Principais

- Flask - Framework web
- Authlib - OAuth integration
- Werkzeug - Segurança e utilitários
- python-dotenv - Gerenciamento de variáveis de ambiente
- certifi - Certificados SSL

## 🐛 Troubleshooting

### Erro de SSL ao usar OAuth:
- Verifique se as credenciais estão corretas no `.env`
- Em desenvolvimento, você pode definir `SSL_VERIFY=False` (não recomendado para produção)

### Banco de dados não encontrado:
- O banco de dados é criado automaticamente na primeira execução
- Certifique-se de ter permissões de escrita na pasta do projeto

## 📄 Licença

Ver arquivo LICENSE

## 👥 Contribuidores

Golden Boy | Copyright © Sonholândia | 2025
