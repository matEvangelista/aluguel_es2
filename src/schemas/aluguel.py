import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ValidationError, field_validator, constr, Field, AnyUrl, FutureDate, PastDate

class Aluguel(BaseModel):
    bicicleta: int
    horaInicio: datetime.datetime
    trancaFim: Optional[int] = None
    horaFim: Optional[datetime.datetime] = None
    cobranca: int
    ciclista: int
    trancaInicio: int

    class Config:
        from_attributes = True  # Permite que o Pydantic seja usado com o ORM

class Devolucao(BaseModel):
    bicicleta: int
    horaInicio: datetime.datetime
    horaFim: datetime.datetime
    trancaFim: int
    cobranca: int
    ciclista: int