from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from ..database import get_session
from ..dependencies import UsuarioAtual
from ..models import Vaga, VagaCriar, VagaAtualizar, VagaPublico

router = APIRouter(prefix="/api/vagas", tags=["Vagas"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.get("/", response_model=list[VagaPublico])
def listar(session: SessionDep, usuario: UsuarioAtual): # type: ignore
    return session.exec(select(Vaga).order_by(Vaga.numero_vaga)).all()

@router.get("/{id_vaga}", response_model=VagaPublico)
def obter(id_vaga: int, session: SessionDep, usuario: UsuarioAtual): # type: ignore
    item = session.get(Vaga, id_vaga)
    if not item:
        raise HTTPException(404, "Vaga não encontrada.")
    return item

@router.post("/", response_model=VagaPublico, status_code=201)
def criar(dados: VagaCriar, session: SessionDep, usuario: UsuarioAtual): # type: ignore
    item = Vaga.model_validate(dados)
    session.add(item)
    try:
        session.commit()
        session.refresh(item)
        return item
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Esse número de vaga já está cadastrado.")

@router.put("/{id_vaga}", response_model=VagaPublico)
def atualizar(id_vaga: int, dados: VagaAtualizar, session: SessionDep, usuario: UsuarioAtual): # type: ignore
    item = session.get(Vaga, id_vaga)
    if not item:
        raise HTTPException(404, "Vaga não encontrada.")
    item.sqlmodel_update(dados.model_dump(exclude_unset=True))
    session.add(item)
    try:
        session.commit()
        session.refresh(item)
        return item
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Esse número de vaga já está cadastrado.")

@router.delete("/{id_vaga}", status_code=204)
def excluir(id_vaga: int, session: SessionDep, usuario: UsuarioAtual): # type: ignore
    item = session.get(Vaga, id_vaga)
    if not item:
        raise HTTPException(404, "Vaga não encontrada.")
    session.delete(item)
    session.commit()
