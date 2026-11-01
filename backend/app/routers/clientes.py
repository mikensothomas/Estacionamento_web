from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import usuario_atual
from ..models import validar_documento
from ..models import (
    Cliente,
    ClienteCriar,
    ClienteAtualizar,
    ClientePublico,
    Usuario,
)

router = APIRouter(
    prefix="/api/clientes",
    tags=["Clientes"],
)


@router.get("/", response_model=list[ClientePublico])
def listar(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(usuario_atual),
):
    return session.exec(
        select(Cliente).order_by(Cliente.id_cliente.desc())
    ).all()


@router.get("/{id_cliente}", response_model=ClientePublico)
def obter(
    id_cliente: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(usuario_atual),
):
    item = session.get(Cliente, id_cliente)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado.",
        )

    return item


@router.post("/", response_model=ClientePublico, status_code=201)
def criar(
    dados: ClienteCriar,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(usuario_atual),
):
    item = Cliente.model_validate(dados)

    session.add(item)

    try:
        session.commit()
        session.refresh(item)
        return item

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=409,
            detail="CPF ou e-mail já cadastrado.",
        )


@router.put("/{id_cliente}", response_model=ClientePublico)
def atualizar(
    id_cliente: int,
    dados: ClienteAtualizar,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(usuario_atual),
):
    item = session.get(Cliente, id_cliente)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado.",
        )

    dados_atualizados = dados.model_dump(exclude_unset=True)

    tipo_pessoa = dados_atualizados.get("tipo_pessoa", item.tipo_pessoa)
    documento = dados_atualizados.get("documento", item.documento)

    try:
        validar_documento(tipo_pessoa, documento)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro))

    item.sqlmodel_update(dados_atualizados)

    item.sqlmodel_update(
        dados.model_dump(exclude_unset=True)
    )

    session.add(item)

    try:
        session.commit()
        session.refresh(item)
        return item

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=409,
            detail="CPF ou e-mail já cadastrado.",
        )


@router.delete("/{id_cliente}", status_code=204)
def excluir(
    id_cliente: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(usuario_atual),
):
    item = session.get(Cliente, id_cliente)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado.",
        )

    session.delete(item)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=409,
            detail="Não é possível excluir: o cliente possui veículos vinculados.",
        )