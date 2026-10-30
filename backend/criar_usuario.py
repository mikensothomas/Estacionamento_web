import re
from sqlmodel import Session, select
from app.database import engine, criar_tabelas
from app.models import Usuario
from app.security import hash_senha
from decouple import config
from dotenv import load_dotenv
import os
load_dotenv()

def main():
    criar_tabelas()

    nome = config("ADMIN_NOME", default="").strip()
    cpf_raw = config("ADMIN_CPF", default="")
    email = config("ADMIN_EMAIL", default="").strip().lower()
    senha = config("ADMIN_SENHA", default="")

    cpf = re.sub(r"\D", "", cpf_raw)

    if len(nome) < 2:
        raise SystemExit("Erro: Nome inválido no arquivo .env")
    if len(cpf) != 11:
        raise SystemExit("Erro: CPF deve conter 11 números no arquivo .env")
    if "@" not in email:
        raise SystemExit("Erro: E-mail inválido no arquivo .env")
    if len(senha) < 8:
        raise SystemExit("Erro: A senha precisa ter pelo menos 8 caracteres no arquivo .env")

    with Session(engine) as session:
        existente = session.exec(
            select(Usuario).where((Usuario.email == email) | (Usuario.cpf == cpf))
        ).first()
        
        if existente:
            print("Aviso: O usuário com este e-mail ou CPF já está cadastrado no banco.")
            return

        usuario = Usuario(
            nome_completo=nome,
            cpf=cpf,
            email=email,
            senha_hash=hash_senha(senha),
        )
        session.add(usuario)
        session.commit()
        
if __name__ == "__main__":
    main()