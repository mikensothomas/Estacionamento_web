from datetime import datetime, timezone
from decimal import Decimal
from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import UsuarioAtual
from ..models import (
    Cliente,
    DisponibilidadeVaga,
    Movimentacao,
    MovimentacaoEntrada,
    MovimentacaoPublica,
    Preco,
    StatusMovimentacao,
    TipoCliente,
    Vaga,
    Veiculo
)

router = APIRouter(
    prefix="/api/movimentacoes",
    tags=["Movimentações"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post(
    "/entrada",
    response_model=MovimentacaoPublica,
    status_code=201,
)
def registrar_entrada(
    dados: MovimentacaoEntrada,
    session: SessionDep,
    usuario: UsuarioAtual,
):
    try:
        veiculo = session.exec(
            select(Veiculo)
            .where(Veiculo.id_veiculo == dados.id_veiculo)
            .with_for_update()
        ).first()

        if not veiculo:
            raise HTTPException(
                status_code=404,
                detail="Veículo não encontrado.",
            )

        movimentacao_aberta = session.exec(
            select(Movimentacao).where(
                Movimentacao.id_veiculo == dados.id_veiculo,
                Movimentacao.status == StatusMovimentacao.em_andamento,
            )
        ).first()

        if movimentacao_aberta:
            raise HTTPException(
                status_code=409,
                detail="Este veículo já possui uma entrada em aberto.",
            )

        vaga = session.exec(
            select(Vaga)
            .where(Vaga.id_vaga == dados.id_vaga)
            .with_for_update()
        ).first()

        if not vaga:
            raise HTTPException(
                status_code=404,
                detail="Vaga não encontrada.",
            )

        if vaga.disponibilidade != DisponibilidadeVaga.disponivel:
            raise HTTPException(
                status_code=409,
                detail="A vaga selecionada não está disponível.",
            )

        movimentacao = Movimentacao(
            id_veiculo=dados.id_veiculo,
            id_vaga=dados.id_vaga,
            data_hora_entrada=datetime.now(timezone.utc)
        )

        vaga.disponibilidade = DisponibilidadeVaga.ocupada

        session.add(movimentacao)
        session.add(vaga)
        session.commit()
        session.refresh(movimentacao)

        return movimentacao

    except HTTPException:
        session.rollback()
        raise

    except Exception:
        session.rollback()
        raise


@router.post(
    "/saida/{id_movimentacao}",
    response_model=MovimentacaoPublica,
)
def registrar_saida(
    id_movimentacao: int,
    session: SessionDep,
    usuario: UsuarioAtual,
):
    try:
        movimentacao = session.exec(
            select(Movimentacao)
            .where(
                Movimentacao.id_movimentacao == id_movimentacao
            )
            .with_for_update()
        ).first()

        if not movimentacao:
            raise HTTPException(
                status_code=404,
                detail="Movimentação não encontrada.",
            )

        if movimentacao.status != StatusMovimentacao.em_andamento:
            raise HTTPException(
                status_code=409,
                detail="Esta movimentação já foi finalizada.",
            )

        veiculo = session.get(
            Veiculo,
            movimentacao.id_veiculo,
        )

        if not veiculo:
            raise HTTPException(
                status_code=404,
                detail="Veículo não encontrado.",
            )

        cliente = session.get(
            Cliente,
            veiculo.id_cliente,
        )

        if not cliente:
            raise HTTPException(
                status_code=404,
                detail="Cliente associado ao veículo não encontrado.",
            )

        vaga = session.exec(
            select(Vaga)
            .where(Vaga.id_vaga == movimentacao.id_vaga)
            .with_for_update()
        ).first()

        if not vaga:
            raise HTTPException(
                status_code=404,
                detail="Vaga associada à movimentação não encontrada.",
            )

        agora = datetime.now(timezone.utc)

        tempo_permanencia = agora - movimentacao.data_hora_entrada

        if tempo_permanencia.total_seconds() < 0:
            raise HTTPException(
                status_code=400,
                detail="O horário de saída não pode ser anterior ao horário de entrada."
            )

        if cliente.tipo_cliente == TipoCliente.mensalista:
            valor_total = Decimal("0.00")

        else:
            preco = session.exec(
                select(Preco)
                .order_by(Preco.id_preco.desc())
            ).first()

            if not preco:
                raise HTTPException(
                    status_code=409,
                    detail="Cadastre os preços antes de registrar a saída.",
                )

            permanencia_segundos = (
                agora - movimentacao.data_hora_entrada
            ).total_seconds()

            horas_cobradas = max(
                1,
                ceil(permanencia_segundos / 3600),
            )

            valor_total = (
                preco.valor_hora * horas_cobradas
            ).quantize(Decimal("0.01"))

        movimentacao.data_hora_saida = agora
        movimentacao.valor_total = valor_total
        movimentacao.status = StatusMovimentacao.finalizada

        vaga.disponibilidade = DisponibilidadeVaga.disponivel

        session.add(movimentacao)
        session.add(vaga)
        session.commit()
        session.refresh(movimentacao)

        return movimentacao

    except HTTPException:
        session.rollback()
        raise

    except Exception:
        session.rollback()
        raise


@router.get(
    "/abertas",
    response_model=list[MovimentacaoPublica],
)
def listar_abertas(
    session: SessionDep,
    usuario: UsuarioAtual,
):
    return session.exec(
        select(Movimentacao)
        .where(
            Movimentacao.status == StatusMovimentacao.em_andamento
        )
        .order_by(Movimentacao.data_hora_entrada.desc())
    ).all()


@router.get(
    "/historico",
    response_model=list[MovimentacaoPublica],
)
def listar_historico(
    session: SessionDep,
    usuario: UsuarioAtual,
):
    return session.exec(
        select(Movimentacao)
        .where(
            Movimentacao.status == StatusMovimentacao.finalizada
        )
        .order_by(Movimentacao.data_hora_saida.desc())
    ).all()