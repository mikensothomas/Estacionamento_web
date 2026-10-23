# Sistema de Estacionamento

Sistema full-stack para cadastro e gerenciamento de clientes, veículos, usuários, vagas e preços.

- Backend: Python, FastAPI, SQLModel, SQLAlchemy e MySQL.
- Autenticação: JWT Bearer Token com expiração de 60 minutos.
- Frontend: HTML, CSS e JavaScript puro.
- CRUD: clientes, veículos, usuários, vagas e preços.
- As rotas `/api/*`, exceto login, exigem token válido.
- O frontend é servido pelo próprio FastAPI; abra `http://127.0.0.1:8000/`.

## 1. Requisitos

- Python 3.11 ou superior recomendado.
- MySQL Server 8.0 ou compatível.
- Um navegador moderno.

## 2. Criar banco e usuário no MySQL

Entre no MySQL Workbench e execute (ajuste a senha se desejar):

```sql
CREATE DATABASE IF NOT EXISTS estacionamento
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'estacionamento_user'@'localhost'
  IDENTIFIED BY 'TroqueEstaSenha123!';
GRANT ALL PRIVILEGES ON estacionamento.* TO 'estacionamento_user'@'localhost';
FLUSH PRIVILEGES;
```

Você também pode usar um usuário MySQL existente. Configure a conexão no arquivo `backend/.env`.

## 3. Instalar dependências

Abra um terminal na pasta `sistema_estacionamento`:

### Windows (CMD)

```bat
py -m venv .venv
.venv\Scripts\activate
cd backend
copy .env.example .env
```

Edite `backend/.env` e informe host, porta, banco, usuário e senha do seu MySQL. Depois:

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
Copy-Item .env.example .env
```

Edite `.env`, então execute `pip install -r requirements.txt`.

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
cd backend
cp .env.example .env
```

Edite `.env` e execute `pip install -r requirements.txt`.

## 4. Criar o primeiro usuário administrador

Com o terminal em `sistema_estacionamento/backend` e o ambiente virtual ativo:

```bash
python criar_usuario.py
```

O script pede nome, CPF, e-mail e senha e grava a senha como hash Argon2. Use esse usuário na tela de login. Não existe senha padrão embutida.

## 5. Iniciar o sistema

Ainda dentro da pasta `backend`:

```bash
uvicorn app.main:app --reload
```

Acesse:
- Aplicação: http://127.0.0.1:8000/
- Documentação interativa: http://127.0.0.1:8000/docs
- Verificação de saúde: http://127.0.0.1:8000/api/health

Na primeira inicialização, o SQLModel cria as tabelas ausentes. Para ambientes reais, use migrações (por exemplo, Alembic) em vez de depender de `create_all`.

## 6. Dependências

Todas estão em `backend/requirements.txt`:
- `fastapi`
- `uvicorn[standard]`
- `sqlmodel`
- `pymysql`
- `python-dotenv`
- `PyJWT`
- `pwdlib[argon2]`
- `email-validator`
- `python-multipart`

## 7. Estrutura

```text
sistema_estacionamento/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── static.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── security.py
│   │   ├── models.py
│   │   └── main.py
│   ├── .env.example
│   ├── criar_usuario.py
│   └── requirements.txt
└── frontend/
    ├── login/
    ├── inicial/
    ├── clientes/
    ├── veiculos/
    ├── usuarios/
    ├── vagas/
    └── precos/
```

## 8. Segurança e observações

- Configure `SECRET_KEY` com uma chave aleatória longa e privada antes de usar.
- Tokens expiram em 60 minutos; o frontend retorna à tela de login quando recebe `401`.
- Senhas são armazenadas como hash Argon2, nunca em texto puro.
- Rotas privadas exigem `Authorization: Bearer <token>`.
- O frontend esconde as páginas privadas sem sessão, mas a proteção real é feita no backend.
- O campo `disponibilidade` da vaga é atualizado no CRUD; vincular automaticamente ocupação a entradas/saídas de veículos exigiria uma tabela de movimentações, que não faz parte do modelo solicitado.
- O projeto não implementa recuperação de senha, confirmação de e-mail, níveis de permissão nem histórico de estacionamento.
