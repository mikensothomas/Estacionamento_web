from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator
import re


class TipoCliente(str, Enum):
    mensalista = "Mensalista"
    horista = "Horista"


class DisponibilidadeVaga(str, Enum):
    disponivel = "Disponível"
    ocupada = "Ocupada"


class UsuarioBase(SQLModel):
    nome_completo: str = Field(min_length=2, max_length=150)
    cpf: str = Field(min_length=11, max_length=11, index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True, max_length=150)

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if len(digits) != 11:
            raise ValueError("O CPF deve conter 11 números.")
        return digits


class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuarios"
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    senha_hash: str = Field(max_length=255)


class UsuarioCriar(UsuarioBase):
    senha: str = Field(min_length=8, max_length=128)


class UsuarioAtualizar(SQLModel):
    nome_completo: Optional[str] = Field(default=None, min_length=2, max_length=150)
    cpf: Optional[str] = Field(default=None, min_length=11, max_length=11)
    email: Optional[EmailStr] = None
    senha: Optional[str] = Field(default=None, min_length=8, max_length=128)

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        digits = re.sub(r"\D", "", value)
        if len(digits) != 11:
            raise ValueError("O CPF deve conter 11 números.")
        return digits


class UsuarioPublico(UsuarioBase):
    id_usuario: int


class LoginEntrada(SQLModel):
    email: EmailStr
    senha: str


class TokenResposta(SQLModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ClienteBase(SQLModel):
    cpf: str = Field(min_length=11, max_length=11, index=True, unique=True)
    nome_completo: str = Field(min_length=2, max_length=150)
    email: EmailStr = Field(max_length=150, unique=True)
    telefone: str = Field(min_length=8, max_length=20)
    tipo_cliente: TipoCliente = TipoCliente.horista

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if len(digits) != 11:
            raise ValueError("O CPF deve conter 11 números.")
        return digits


class Cliente(ClienteBase, table=True):
    __tablename__ = "clientes"
    id_cliente: Optional[int] = Field(default=None, primary_key=True)


class ClienteCriar(ClienteBase):
    pass


class ClienteAtualizar(SQLModel):
    cpf: Optional[str] = Field(default=None, min_length=11, max_length=11)
    nome_completo: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(default=None, min_length=8, max_length=20)
    tipo_cliente: Optional[TipoCliente] = None

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        digits = re.sub(r"\D", "", value)
        if len(digits) != 11:
            raise ValueError("O CPF deve conter 11 números.")
        return digits


class ClientePublico(ClienteBase):
    id_cliente: int


class VeiculoBase(SQLModel):
    modelo: str = Field(min_length=1, max_length=100)
    placa: str = Field(min_length=7, max_length=7, index=True)
    cor: str = Field(min_length=1, max_length=50)
    marca: str = Field(min_length=1, max_length=100)
    id_cliente: int

    @field_validator("placa")
    @classmethod
    def validar_placa(cls, value: str) -> str:
        placa = re.sub(r"[^A-Za-z0-9]", "", value).upper()
        if len(placa) != 7:
            raise ValueError("A placa deve conter 7 caracteres alfanuméricos.")
        return placa


class Veiculo(VeiculoBase, table=True):
    __tablename__ = "veiculos"
    id_veiculo: Optional[int] = Field(default=None, primary_key=True)


class VeiculoCriar(VeiculoBase):
    pass


class VeiculoAtualizar(SQLModel):
    modelo: Optional[str] = Field(default=None, min_length=1, max_length=100)
    placa: Optional[str] = Field(default=None, min_length=7, max_length=7)
    cor: Optional[str] = Field(default=None, min_length=1, max_length=50)
    marca: Optional[str] = Field(default=None, min_length=1, max_length=100)
    id_cliente: Optional[int] = None

    @field_validator("placa")
    @classmethod
    def validar_placa(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        placa = re.sub(r"[^A-Za-z0-9]", "", value).upper()
        if len(placa) != 7:
            raise ValueError("A placa deve conter 7 caracteres alfanuméricos.")
        return placa


class VeiculoPublico(VeiculoBase):
    id_veiculo: int


class VagaBase(SQLModel):
    numero_vaga: int = Field(gt=0, unique=True, index=True)
    disponibilidade: DisponibilidadeVaga = DisponibilidadeVaga.disponivel


class Vaga(VagaBase, table=True):
    __tablename__ = "vaga"
    id_vaga: Optional[int] = Field(default=None, primary_key=True)


class VagaCriar(VagaBase):
    pass


class VagaAtualizar(SQLModel):
    numero_vaga: Optional[int] = Field(default=None, gt=0)
    disponibilidade: Optional[DisponibilidadeVaga] = None


class VagaPublico(VagaBase):
    id_vaga: int


class PrecoBase(SQLModel):
    valor_hora: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    valor_mensal: Decimal = Field(ge=0, max_digits=10, decimal_places=2)


class Preco(PrecoBase, table=True):
    __tablename__ = "precos"
    id_preco: Optional[int] = Field(default=None, primary_key=True)


class PrecoCriar(PrecoBase):
    pass


class PrecoAtualizar(SQLModel):
    valor_hora: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    valor_mensal: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)


class PrecoPublico(PrecoBase):
    id_preco: int
