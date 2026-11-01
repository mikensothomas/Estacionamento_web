from pathlib import Path
import os
import re
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from sqlmodel import Session, select

from .database import criar_tabelas, engine
from .models import Usuario
from .security import hash_senha
from .routers import (
    auth, 
    clientes, 
    veiculos, 
    usuarios, 
    vagas, 
    precos,
    movimentacoes
)

app = FastAPI(
    title="Sistema de Estacionamento",
    description="API de estacionamento com CRUD e autenticação JWT.",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")

def criar_usuario_inicial():
    """Verifica se o usuário administrador existe no banco; se não, cria usando o .env."""
    nome = os.getenv("ADMIN_NOME").strip()
    cpf_raw = os.getenv("ADMIN_CPF")
    email = os.getenv("ADMIN_EMAIL").strip().lower()
    senha = os.getenv("ADMIN_SENHA")

    cpf = re.sub(r"\D", "", cpf_raw)

    with Session(engine) as session:
        existente = session.exec(
            select(Usuario).where((Usuario.email == email) | (Usuario.cpf == cpf))
        ).first()

        if existente:
            return

        usuario = Usuario(
            nome_completo=nome,
            cpf=cpf,
            email=email,
            senha_hash=hash_senha(senha),
        )
        session.add(usuario)
        session.commit()

@app.on_event("startup")
def startup():
    criar_tabelas()
    criar_usuario_inicial()

@app.get("/", include_in_schema=False)
def pagina_login():
    return FileResponse(FRONTEND_DIR / "login" / "login.html")

@app.get("/pagina/{nome}", include_in_schema=False)
def pagina_frontend(nome: str):
    permitidas = {"inicial", "clientes", "veiculos", "usuarios", "vagas", "precos", "movimentacoes"}
    if nome not in permitidas:
        raise HTTPException(404, "Página não encontrada.")
    return FileResponse(FRONTEND_DIR / nome / f"{nome}.html")

@app.get("/api/health", tags=["Sistema"])
def health():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(veiculos.router)
app.include_router(usuarios.router)
app.include_router(vagas.router)
app.include_router(precos.router)
app.include_router(movimentacoes.router)