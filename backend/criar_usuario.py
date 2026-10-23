from getpass import getpass
from sqlmodel import Session, select
from app.database import engine, criar_tabelas
from app.models import Usuario
from app.security import hash_senha
import re

def main():
    criar_tabelas()
    nome = input("Nome completo: ").strip()
    cpf = re.sub(r"\D", "", input("CPF (somente números): ").strip())
    email = input("E-mail: ").strip().lower()
    senha = getpass("Senha (mínimo 8 caracteres): ")
    confirmar = getpass("Confirme a senha: ")

    if len(nome) < 2:
        raise SystemExit("Nome inválido.")
    if len(cpf) != 11:
        raise SystemExit("CPF deve conter 11 números.")
    if "@" not in email:
        raise SystemExit("E-mail inválido.")
    if len(senha) < 8:
        raise SystemExit("A senha precisa ter pelo menos 8 caracteres.")
    if senha != confirmar:
        raise SystemExit("As senhas não coincidem.")

    with Session(engine) as session:
        existente = session.exec(
            select(Usuario).where((Usuario.email == email) | (Usuario.cpf == cpf))
        ).first()
        if existente:
            raise SystemExit("Já existe usuário com esse e-mail ou CPF.")
        usuario = Usuario(
            nome_completo=nome,
            cpf=cpf,
            email=email,
            senha_hash=hash_senha(senha),
        )
        session.add(usuario)
        session.commit()
    print("Usuário criado com sucesso. Acesse a tela de login.")

if __name__ == "__main__":
    main()
