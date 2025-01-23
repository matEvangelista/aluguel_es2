from pydantic import BaseModel, EmailStr, ValidationError, field_validator, constr, Field, AnyUrl, FutureDate, PastDate
from pydantic_extra_types.country import CountryAlpha2
from typing import Optional, Annotated
from ..models import Passaporte as PassaporteDB
from enum import Enum

class Nacionalidade(str, Enum):
    BRASILEIRO = 'BRASILEIRO'
    ESTRANGEIRO = 'ESTRANGEIRO'

class Passaporte(BaseModel):
    numero: str
    validade: FutureDate
    pais: CountryAlpha2
    class Meta:
        from_attributes = PassaporteDB

class NovoCiclista(BaseModel):
    nome: str
    email: EmailStr
    nacionalidade: Nacionalidade
    nascimento: PastDate
    senha: str
    cpf: Optional[str] = Field(pattern=r"^\d{11}$", default=None)
    passaporte: Optional[Passaporte] = None
    urlFotoDocumento: Optional[AnyUrl] = None


    class Config:
        from_attributes = True  # Permite que o Pydantic converta objetos ORM para schemas

class Ciclista(NovoCiclista):
    id: int
    status: str
    class Config:
        from_attributes = True


class NovoCiclistaPut(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    nacionalidade: Optional[Nacionalidade] = None
    nascimento: Optional[PastDate] = None
    senha: Optional[str] = None
    cpf: Optional[str] = Field(pattern=r"^\d{11}$", default=None)
    passaporte: Optional[Passaporte] = None
    urlFotoDocumento: Optional[AnyUrl] = None

    class Config:
        from_attributes = True

