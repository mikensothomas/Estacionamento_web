from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator, model_validator
import re
from sqlalchemy import Column, Enum as SAEnum

class TipoCliente(str, Enum):
    mensalista = "Mensalista"
    horista = "Horista"

class TipoPessoa(str, Enum):
    FISICA = "Fisica"
    JURIDICA = "Juridica"


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

def validar_cpf_valido(cpf: str) -> str:
    cpf = re.sub(r"\D", "", cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValueError("CPF inválido.")

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito1 = 0 if resto == 10 else resto

    if digito1 != int(cpf[9]):
        raise ValueError("CPF inválido.")

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito2 = 0 if resto == 10 else resto

    if digito2 != int(cpf[10]):
        raise ValueError("CPF inválido.")

    return cpf


def validar_cnpj_valido(cnpj: str) -> str:
    cnpj = re.sub(r"\D", "", cnpj)

    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        raise ValueError("CNPJ inválido.")

    def calcular_digito(base: str, pesos: list[int]) -> int:
        soma = sum(int(numero) * peso for numero, peso in zip(base, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    primeiro = calcular_digito(
        cnpj[:12],
        [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
    )

    segundo = calcular_digito(
        cnpj[:12] + str(primeiro),
        [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
    )

    if cnpj[-2:] != f"{primeiro}{segundo}":
        raise ValueError("CNPJ inválido.")

    return cnpj


def validar_documento(tipo_pessoa: TipoPessoa, documento: str) -> str:
    if tipo_pessoa == TipoPessoa.FISICA:
        return validar_cpf_valido(documento)

    if tipo_pessoa == TipoPessoa.JURIDICA:
        return validar_cnpj_valido(documento)

    raise ValueError("Tipo de pessoa inválido.")


class ClienteBase(SQLModel):
    tipo_pessoa: TipoPessoa
    documento: str = Field(min_length=11, max_length=14, index=True, unique=True)

    nome_completo: str = Field(min_length=2, max_length=150)
    email: EmailStr = Field(max_length=150, unique=True)
    telefone: str = Field(min_length=8, max_length=20)
    tipo_cliente: TipoCliente = TipoCliente.horista

    cep: str = Field(min_length=8, max_length=9)
    rua: str = Field(min_length=2, max_length=150)
    bairro: str = Field(min_length=2, max_length=100)
    estado: str = Field(min_length=2, max_length=2)
    numero_casa: str = Field(min_length=1, max_length=20)
    numero_apartamento: Optional[str] = Field(default=None, max_length=20)
    complemento: Optional[str] = Field(default=None, max_length=100)

    @field_validator("documento")
    @classmethod
    def limpar_documento(cls, value: str) -> str:
        return re.sub(r"\D", "", value)

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)

        if len(digits) != 8:
            raise ValueError("O CEP deve conter 8 números.")

        return digits

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: str) -> str:
        return value.strip().upper()

    @model_validator(mode="after")
    def validar_tipo_documento(self):
        validar_documento(
            self.tipo_pessoa,
            self.documento
        )
        return self


class Cliente(ClienteBase, table=True):
    __tablename__ = "clientes"

    tipo_pessoa: TipoPessoa = Field(
        sa_column=Column(
            SAEnum(
                TipoPessoa,
                values_callable=lambda enum_cls: [
                    item.value for item in enum_cls
                ],
            ),
            nullable=False,
        )
    )

    tipo_cliente: TipoCliente = Field(
        default=TipoCliente.horista,
        sa_column=Column(
            SAEnum(
                TipoCliente,
                values_callable=lambda enum_cls: [
                    item.value for item in enum_cls
                ],
            ),
            nullable=False,
        ),
    )

    id_cliente: Optional[int] = Field(default=None, primary_key=True)


class ClienteCriar(ClienteBase):
    pass


class ClienteAtualizar(SQLModel):
    tipo_pessoa: Optional[TipoPessoa] = None
    documento: Optional[str] = Field(default=None, min_length=11, max_length=14)

    nome_completo: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(default=None, min_length=8, max_length=20)
    tipo_cliente: Optional[TipoCliente] = None

    cep: Optional[str] = Field(default=None, min_length=8, max_length=9)
    rua: Optional[str] = Field(default=None, min_length=2, max_length=150)
    bairro: Optional[str] = Field(default=None, min_length=2, max_length=100)
    estado: Optional[str] = Field(default=None, min_length=2, max_length=2)
    numero_casa: Optional[str] = Field(default=None, min_length=1, max_length=20)
    numero_apartamento: Optional[str] = Field(default=None, max_length=20)
    complemento: Optional[str] = Field(default=None, max_length=100)

    @field_validator("documento")
    @classmethod
    def limpar_documento(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return re.sub(r"\D", "", value)

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        digits = re.sub(r"\D", "", value)

        if len(digits) != 8:
            raise ValueError("O CEP deve conter 8 números.")

        return digits

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.strip().upper()


class ClientePublico(SQLModel):
    id_cliente: int
    tipo_pessoa: TipoPessoa
    documento: str
    nome_completo: str
    email: EmailStr
    telefone: str
    tipo_cliente: TipoCliente

    # Sem restrições de tamanho para permitir a leitura
    # de registros antigos ainda sem endereço.
    cep: str = ""
    rua: str = ""
    bairro: str = ""
    estado: str = ""
    numero_casa: str = ""
    numero_apartamento: Optional[str] = None
    complemento: Optional[str] = None


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

    disponibilidade: DisponibilidadeVaga = Field(
        default=DisponibilidadeVaga.disponivel,
        sa_column=Column(
            SAEnum(
                DisponibilidadeVaga,
                values_callable=lambda enum_cls: [
                    item.value for item in enum_cls
                ],
            ),
            nullable=False,
        ),
    )

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


class StatusMovimentacao(str, Enum):
    em_andamento = "Em andamento"
    finalizada = "Finalizada"


class MovimentacaoBase(SQLModel):
    id_veiculo: int
    id_vaga: int


class Movimentacao(MovimentacaoBase, table=True):
    __tablename__ = "movimentacoes"

    id_movimentacao: Optional[int] = Field(
        default=None,
        primary_key=True,
    )

    data_hora_entrada: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    data_hora_saida: Optional[datetime] = Field(
        default=None,
        nullable=True,
    )

    valor_total: Optional[Decimal] = Field(
        default=None,
        max_digits=10,
        decimal_places=2,
        nullable=True,
    )

    status: StatusMovimentacao = Field(
        default=StatusMovimentacao.em_andamento,
        sa_column=Column(
            SAEnum(
                StatusMovimentacao,
                values_callable=lambda enum_cls: [
                    item.value for item in enum_cls
                ],
            ),
            nullable=False,
            default=StatusMovimentacao.em_andamento,
        ),
    )


class MovimentacaoEntrada(SQLModel):
    id_veiculo: int = Field(gt=0)
    id_vaga: int = Field(gt=0)


class MovimentacaoPublica(SQLModel):
    id_movimentacao: int
    id_veiculo: int
    id_vaga: int
    data_hora_entrada: datetime
    data_hora_saida: Optional[datetime] = None
    valor_total: Optional[Decimal] = None
    status: StatusMovimentacao