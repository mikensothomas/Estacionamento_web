from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from ..database import get_session
from ..dependencies import UsuarioAtual
from ..models import Usuario, UsuarioCriar, UsuarioAtualizar, UsuarioPublico
from ..security import hash_senha

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.get("/", response_model=list[UsuarioPublico])
def listar(session: SessionDep, usuario: UsuarioAtual): # type: ignore
    return session.exec(select(Usuario).order_by(Usuario.id_usuario.desc())).all()

@router.get("/{id_usuario}", response_model=UsuarioPublico)
def obter(id_usuario: int, session: SessionDep, usuario: UsuarioAtual): # type: ignore
    item = session.get(Usuario, id_usuario)
    if not item:
        raise HTTPException(404, "Usuário não encontrado.")
    return item

@router.post("/", response_model=UsuarioPublico, status_code=201)
def criar(dados: UsuarioCriar, session: SessionDep, usuario: UsuarioAtual): # type: ignore
    item = Usuario(
        nome_completo=dados.nome_completo,
        cpf=dados.cpf,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
    )
    session.add(item)
    try:
        session.commit()
        session.refresh(item)
        return item
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "CPF ou e-mail já cadastrado.")

@router.put("/{id_usuario}", response_model=UsuarioPublico)
def atualizar(id_usuario: int, dados: UsuarioAtualizar, session: SessionDep, usuario: UsuarioAtual): # type: ignore
    item = session.get(Usuario, id_usuario)
    if not item:
        raise HTTPException(404, "Usuário não encontrado.")
    alteracoes = dados.model_dump(exclude_unset=True, exclude={"senha"})
    for campo, valor in alteracoes.items():
        setattr(item, campo, valor)
    if dados.senha:
        item.senha_hash = hash_senha(dados.senha)
    session.add(item)
    try:
        session.commit()
        session.refresh(item)
        return item
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "CPF ou e-mail já cadastrado.")

@router.delete("/{id_usuario}", status_code=204)
def excluir(id_usuario: int, session: SessionDep, usuario: UsuarioAtual): # type: ignore
    if usuario.id_usuario == id_usuario:
        raise HTTPException(400, "Você não pode excluir o usuário conectado.")
    item = session.get(Usuario, id_usuario)
    if not item:
        raise HTTPException(404, "Usuário não encontrado.")
    session.delete(item)
    session.commit()
