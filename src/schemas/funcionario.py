from pydantic import BaseModel, constr, FutureDate, Field, EmailStr
from pydantic_extra_types.payment import PaymentCardNumber
from typing import Optional

class NovoFuncionario(BaseModel):
    senha: str
    confirmacaoSenha: Optional[str] = None
    email: EmailStr
    nome: str
    idade: int
    funcao: str
    cpf: str = Field(pattern=r"^\d{11}$")

    class Config:
        from_attributes = True

class Funcionario(NovoFuncionario):
    matricula: int # para o bd
    class Config:
        from_attributes = True


class NovoFuncionarioPut(BaseModel):
    senha: Optional[str] = None
    confirmacaoSenha: Optional[str] = None
    email: Optional[EmailStr] = None
    nome: Optional[str] = None
    idade: Optional[int] = None
    funcao: Optional[str] = None
    cpf: str = Field(pattern=r"^\d{11}$", default=None)

    class Config:
        from_attributes = True