from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from ..database import get_session
from ..dependencies import UsuarioAtual
from ..models import Veiculo, VeiculoCriar, VeiculoAtualizar, VeiculoPublico, Cliente

router = APIRouter(prefix="/api/veiculos", tags=["Veículos"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.get("/", response_model=list[VeiculoPublico])
def listar(session: SessionDep, usuario: UsuarioAtual):
    return session.exec(select(Veiculo).order_by(Veiculo.id_veiculo.desc())).all()

@router.get("/{id_veiculo}", response_model=VeiculoPublico)
def obter(id_veiculo: int, session: SessionDep, usuario: UsuarioAtual):
    item = session.get(Veiculo, id_veiculo)
    if not item:
        raise HTTPException(404, "Veículo não encontrado.")
    return item

@router.post("/", response_model=VeiculoPublico, status_code=201)
def criar(dados: VeiculoCriar, session: SessionDep, usuario: UsuarioAtual):
    if not session.get(Cliente, dados.id_cliente):
        raise HTTPException(400, "O cliente informado não existe.")
    item = Veiculo.model_validate(dados)
    session.add(item)
    try:
        session.commit()
        session.refresh(item)
        return item
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "A placa já está cadastrada.")

@router.put("/{id_veiculo}", response_model=VeiculoPublico)
def atualizar(id_veiculo: int, dados: VeiculoAtualizar, session: SessionDep, usuario: UsuarioAtual):
    item = session.get(Veiculo, id_veiculo)
    if not item:
        raise HTTPException(404, "Veículo não encontrado.")
    update = dados.model_dump(exclude_unset=True)
    if update.get("id_cliente") is not None and not session.get(Cliente, update["id_cliente"]):
        raise HTTPException(400, "O cliente informado não existe.")
    item.sqlmodel_update(update)
    session.add(item)
    try:
        session.commit()
        session.refresh(item)
        return item
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "A placa já está cadastrada.")

@router.delete("/{id_veiculo}", status_code=204)
def excluir(id_veiculo: int, session: SessionDep, usuario: UsuarioAtual):
    item = session.get(Veiculo, id_veiculo)
    if not item:
        raise HTTPException(404, "Veículo não encontrado.")
    session.delete(item)
    session.commit()
