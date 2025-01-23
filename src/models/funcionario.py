from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class FuncionarioDB(Base):
    __tablename__ = "funcionario"

    matricula = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    confirmacaoSenha = Column(String, nullable=True)
    cpf = Column(String, nullable=False)
    funcao = Column(String, nullable=False)
    idade = Column(Integer, nullable=False)
