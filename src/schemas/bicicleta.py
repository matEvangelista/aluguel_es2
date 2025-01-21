from pydantic import BaseModel, Field

class Bicicleta(BaseModel):
    id: int
    marca: str
    modelo: str
    ano: str = Field(pattern=r"^\d{4}$")
    numero: int
    status: str
