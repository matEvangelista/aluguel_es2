from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Double
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Ciclista(Base):
    __tablename__ = "ciclista"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    nacionalidade = Column(String, nullable=False)
    nascimento = Column(Date, nullable=False)
    senha = Column(String, nullable=False)
    status = Column(String, default="INATIVO", nullable=False)
    cpf = Column(String, nullable=True)
    urlFotoDocumento = Column(String, nullable=True)

    # relacionamento com Passaporte
    passaporte = relationship("Passaporte", back_populates="ciclista", uselist=False)

    # relacionamento com Passaporte
    meio_de_pagamento = relationship("CartaoCreditoDB", back_populates="ciclista", uselist=False)

    # relacionamento com Passaporte
    aluguel = relationship("AluguelDB", back_populates="ciclista", uselist=False)


class Passaporte(Base):
    __tablename__ = "passaporte"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String, nullable=False)
    validade = Column(Date, nullable=False)
    pais = Column(String, nullable=False)
    ciclista_id = Column(Integer, ForeignKey("ciclista.id"), nullable=False)

    #relacionamento com ciclista
    ciclista = relationship("Ciclista", back_populates="passaporte")

class CartaoCreditoDB(Base):
    __tablename__ = "cartao_credito"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nomeTitular = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    validade = Column(Date, nullable=False)
    cvv = Column(String, nullable=False)
    ciclista_id = Column(Integer, ForeignKey("ciclista.id"), nullable=False)

    # relacionamento com ciclista
    ciclista = relationship("Ciclista", back_populates="meio_de_pagamento")


class AluguelDB(Base):
    __tablename__ = "aluguel"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ciclista_id = Column(Integer, ForeignKey("ciclista.id"), nullable=False)
    horaInicio = Column(DateTime, nullable=False)
    horaFim = Column(DateTime, nullable=True)
    trancaInicio = Column(DateTime, nullable=False)
    trancaFim = Column(DateTime, nullable=True)
    cobranca = Column(Double, nullable=False)
    bicicleta = Column(Integer, nullable=False)

    # Relacionamento com Ciclista
    ciclista = relationship("Ciclista", back_populates="aluguel")
