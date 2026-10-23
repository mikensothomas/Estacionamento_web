from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError
from .database import criar_tabelas
from .routers import auth, clientes, veiculos, usuarios, vagas, precos

app = FastAPI(
    title="Sistema de Estacionamento",
    description="API de estacionamento com CRUD e autenticação JWT.",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")

@app.on_event("startup")
def startup():
    # Cria tabelas ausentes; não altera tabelas existentes.
    criar_tabelas()

@app.get("/", include_in_schema=False)
def pagina_login():
    return FileResponse(FRONTEND_DIR / "login" / "login.html")

@app.get("/pagina/{nome}", include_in_schema=False)
def pagina_frontend(nome: str):
    permitidas = {"inicial", "clientes", "veiculos", "usuarios", "vagas", "precos"}
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
