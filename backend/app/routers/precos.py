from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..dependencies import UsuarioAtual
from ..models import Preco, PrecoCriar, PrecoAtualizar, PrecoPublico

router = APIRouter(prefix="/api/precos", tags=["Preços"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.get("/", response_model=list[PrecoPublico])
def listar(session: SessionDep, usuario: UsuarioAtual):
    return session.exec(select(Preco).order_by(Preco.id_preco.desc())).all()

@router.get("/{id_preco}", response_model=PrecoPublico)
def obter(id_preco: int, session: SessionDep, usuario: UsuarioAtual):
    item = session.get(Preco, id_preco)
    if not item:
        raise HTTPException(404, "Preço não encontrado.")
    return item

@router.post("/", response_model=PrecoPublico, status_code=201)
def criar(dados: PrecoCriar, session: SessionDep, usuario: UsuarioAtual):
    item = Preco.model_validate(dados)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.put("/{id_preco}", response_model=PrecoPublico)
def atualizar(id_preco: int, dados: PrecoAtualizar, session: SessionDep, usuario: UsuarioAtual):
    item = session.get(Preco, id_preco)
    if not item:
        raise HTTPException(404, "Preço não encontrado.")
    item.sqlmodel_update(dados.model_dump(exclude_unset=True))
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.delete("/{id_preco}", status_code=204)
def excluir(id_preco: int, session: SessionDep, usuario: UsuarioAtual):
    item = session.get(Preco, id_preco)
    if not item:
        raise HTTPException(404, "Preço não encontrado.")
    session.delete(item)
    session.commit()
