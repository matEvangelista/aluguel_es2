from pydantic import BaseModel, constr, FutureDate, Field
from pydantic_extra_types.payment import PaymentCardNumber
from typing import Optional

class NovoCartaoDeCredito(BaseModel):
    numero: PaymentCardNumber
    validade: FutureDate
    cvv: str = Field(pattern=r"^\d{3}$")
    nomeTitular: str

    class Config:
        from_attributes = True

class CartaoCredito(NovoCartaoDeCredito):
    id: int
    ciclista_id: int  # Relacionado ao ciclista no banco de dados

    class Config:
        from_attributes = True
