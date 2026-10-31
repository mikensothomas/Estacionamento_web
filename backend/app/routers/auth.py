from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from ..database import get_session
from ..models import LoginEntrada, TokenResposta, Usuario, UsuarioPublico
from ..security import verificar_senha, criar_token
from ..dependencies import UsuarioAtual

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/login", response_model=TokenResposta)
def login(dados: LoginEntrada, session: SessionDep):
    usuario = session.exec(select(Usuario).where(Usuario.email == dados.email)).first()
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, segundos = criar_token(usuario.email)
    return TokenResposta(access_token=token, expires_in=segundos)

@router.get("/me", response_model=UsuarioPublico)
def meu_usuario(usuario: UsuarioAtual):
    return usuario

@router.post("/logout")
def logout(usuario: UsuarioAtual):
    return {"mensagem": "Logout solicitado. Remova o token armazenado no navegador."}
