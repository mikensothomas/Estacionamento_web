from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from ..database import get_session
from ..dependencies import UsuarioAtual
from ..models import Cliente, ClienteCriar, ClienteAtualizar, ClientePublico

router = APIRouter(prefix="/api/clientes", tags=["Clientes"], dependencies=[Depends(lambda: None)])
SessionDep = Annotated[Session, Depends(get_session)]

@router.get("/", response_model=list[ClientePublico])
def listar(session: SessionDep, usuario: UsuarioAtual):
    return session.exec(select(Cliente).order_by(Cliente.id_cliente.desc())).all()

@router.get("/{id_cliente}", response_model=ClientePublico)
def obter(id_cliente: int, session: SessionDep, usuario: UsuarioAtual):
    item = session.get(Cliente, id_cliente)
    if not item:
        raise HTTPException(404, "Cliente não encontrado.")
    return item

@router.post("/", response_model=ClientePublico, status_code=201)
def criar(dados: ClienteCriar, session: SessionDep, usuario: UsuarioAtual):
    item = Cliente.model_validate(dados)
    session.add(item)
    try:
        session.commit()
        session.refresh(item)
        return item
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "CPF ou e-mail já cadastrado.")

@router.put("/{id_cliente}", response_model=ClientePublico)
def atualizar(id_cliente: int, dados: ClienteAtualizar, session: SessionDep, usuario: UsuarioAtual):
    item = session.get(Cliente, id_cliente)
    if not item:
        raise HTTPException(404, "Cliente não encontrado.")
    item.sqlmodel_update(dados.model_dump(exclude_unset=True))
    session.add(item)
    try:
        session.commit()
        session.refresh(item)
        return item
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "CPF ou e-mail já cadastrado.")

@router.delete("/{id_cliente}", status_code=204)
def excluir(id_cliente: int, session: SessionDep, usuario: UsuarioAtual):
    item = session.get(Cliente, id_cliente)
    if not item:
        raise HTTPException(404, "Cliente não encontrado.")
    session.delete(item)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Não é possível excluir: o cliente possui veículos vinculados.")
