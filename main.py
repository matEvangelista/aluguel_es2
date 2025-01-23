import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.openapi.utils import status_code_ranges
from pydantic import ValidationError, EmailStr
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from typing import List
from sqlalchemy import text
from database import SessionLocal
from src.schemas import (NovoCiclista, Ciclista, NovoCartaoDeCredito, CartaoCredito, Funcionario,
                         NovoFuncionario, NovoCiclistaPut, NovoFuncionarioPut, Bicicleta, Aluguel, Devolucao)
from src.services import CiclistaService
load_dotenv()
URL_EXTERNO=os.getenv('URL_EXTERNO')
URL_EQUIPAMENTO=os.getenv("URL_EQUIPAMENTO")

app = FastAPI()

# Dependency para injetar o banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/restaurarBanco", status_code=200, tags=["Aluguel"], description="Banco restaurado.")
def restaurar_banco(db: Session = Depends(get_db)):
    tabelas = ['ciclista', 'cartao_credito', 'funcionario', 'passaporte', 'aluguel']
    for tabela in tabelas:
        string = f'DELETE from {tabela}'
        db.execute(text(string))
    db.commit()

@app.post("/ciclista", response_model=Ciclista, status_code=201, tags=["Aluguel"])
def cadastrar_ciclista(
    ciclista: NovoCiclista = Body(...),
    meioDePagamento: NovoCartaoDeCredito = Body(...),
    db: Session = Depends(get_db),
):
    ciclista_service = CiclistaService(db, url_externo=URL_EXTERNO)
    try:
        novo_ciclista = ciclista_service.cadastrar_ciclista(ciclista, meioDePagamento)
        return novo_ciclista
    except ValidationError:
        raise HTTPException(status_code=422, detail="Parâmetros incorretos.")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.get("/ciclista/{idCiclista}", status_code=200, response_model=Ciclista, tags=["Aluguel"])
def recupera_ciclista(
        idCiclista: int,
        db: Session = Depends(get_db)
):
    ciclista_service = CiclistaService(db)
    ciclista = ciclista_service.recupera_ciclista_por_id(idCiclista)
    if not ciclista:
        raise HTTPException(status_code=404, detail="Ciclista não encontrado.")
    return ciclista

@app.put("/ciclista/{idCiclista}", response_model=Ciclista, status_code=200, tags=["Aluguel"])
def atualizar_ciclista(idCiclista: int, ciclista: NovoCiclistaPut = Body(...), db: Session = Depends(get_db)):
    service = CiclistaService(db, url_externo=URL_EXTERNO)
    dados_atualizados = ciclista.model_dump(exclude_unset=True)  # Só inclui os campos que foram enviados
    ciclista_atualizado = service.atualizar_ciclista(idCiclista, dados_atualizados)
    return ciclista_atualizado

@app.post("/ciclista/{idCiclista}/ativar", status_code=200, response_model=Ciclista, tags=["Aluguel"])
def ativar_ciclista(idCiclista: int, db: Session = Depends(get_db)):
    service = CiclistaService(db)
    ciclista = service.ativar_ciclista(idCiclista)
    return ciclista

@app.post("/ciclista/existeEmail/{email}", status_code=200, response_model=bool, tags=['Aluguel'])
def conferir_email_ja_foi_utilizado(email: EmailStr, db: Session = Depends(get_db)):
    service = CiclistaService(db)
    return service.conferir_email_ja_foi_utilizado(email)

@app.get("/ciclista/{idCiclista}/permiteAluguel", status_code=200, tags=['Aluguel'], response_model=bool)
def ciclista_pode_alugar(idCiclista: int, db: Session = Depends(get_db)):
    ciclista_service = CiclistaService(db, url_externo=URL_EXTERNO, url_equipamento=URL_EQUIPAMENTO)
    resp = ciclista_service.ciclista_pode_alugar(idCiclista)
    return resp

@app.get("/ciclista/{idCiclista}/bicicletaAlugada", status_code=200, tags=['Aluguel'], response_model=Bicicleta|None)
def buscar_bicicleta_alugada_atualmente(idCiclista: int, db: Session = Depends(get_db)):
    ciclista_service = CiclistaService(db)
    resp = ciclista_service.busca_bicicleta_alugada(idCiclista)
    return resp

@app.get("/cartaoDeCredito/{idCiclista}", status_code=200, response_model=CartaoCredito, tags=['Aluguel'])
def busca_cartao(idCiclista:int, db: Session = Depends(get_db)):
    service = CiclistaService(db)
    cartao = service.busca_cartao(idCiclista)
    if not cartao:
        raise HTTPException(status_code=404, detail="Ciclista não encontrado.")
    return cartao

@app.put("/cartaoDeCredito/{idCiclista}", status_code=200, tags=['Aluguel'])
def editar_cartao(idCiclista:int, cartao: NovoCartaoDeCredito = Body(...), db: Session = Depends(get_db)):
    ciclista_service = CiclistaService(db, url_externo=URL_EXTERNO)
    ciclista_service.edita_cartao(idCiclista, cartao)

@app.get("/funcionario", status_code=200, tags=['Aluguel'], response_model=List[Funcionario])
def recupera_funcionarios(db: Session = Depends(get_db)):
    ciclista_service = CiclistaService(db)
    return ciclista_service.recupera_funcionarios()

@app.post("/funcionario", response_model=Funcionario, status_code=200, tags=["Aluguel"])
def cadastrar_funcionario(
    funcionario: NovoFuncionario = Body(...),
    db: Session = Depends(get_db),
):
    ciclista_service = CiclistaService(db)
    try:
        novo_funcionario = ciclista_service.cadastrar_funcionario(funcionario)
        return novo_funcionario
    except ValidationError:
        raise HTTPException(status_code=422, detail="Parâmetros incorretos.")

@app.get("/funcionario/{idFuncionario}", response_model=Funcionario, status_code=200, tags=['Aluguel'])
def recuperar_funcionario(idFuncionario: int, db: Session = Depends(get_db)):
    ciclista_service = CiclistaService(db)
    funcionario = ciclista_service.recupera_funcionario(idFuncionario)
    if not funcionario:
        raise HTTPException(status_code=404, detail='Funcionário não existe.')
    return funcionario

@app.put("/funcionario/{idFuncionario}", response_model=Funcionario, status_code=200, tags=["Aluguel"])
def editar_funcionario(idFuncionario, novo_funcionario: NovoFuncionarioPut = Body(...), db: Session = Depends(get_db)):
    ciclista_service = CiclistaService(db)
    dados_atualizados = novo_funcionario.model_dump(exclude_unset=True)  # Só inclui os campos que foram enviados
    funcionaro_atualizado = ciclista_service.editar_funcionario(idFuncionario, dados_atualizados)
    if not funcionaro_atualizado:
        raise HTTPException(status_code=404, detail='Funcionário não existe.')
    return funcionaro_atualizado

@app.delete("/funcionario/{idFuncionario}", status_code=200, tags=["Aluguel"], response_model=None,
            response_description="Dados removidos.")
def delete_funcionario(idFuncionario: int, db: Session = Depends(get_db)):
    ciclista_service = CiclistaService(db)
    resultado = ciclista_service.delete_funcionario(idFuncionario)
    if not resultado:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

@app.post("/aluguel", status_code=200, response_model=Aluguel, tags=["Aluguel"])
def realizar_aluguel(ciclista: int = Body(...), trancaInicio: int = Body(...), db: Session = Depends(get_db)):
    ciclista_service = CiclistaService(db, url_equipamento=URL_EQUIPAMENTO, url_externo=URL_EXTERNO)
    resultado = ciclista_service.realizar_aluguel(ciclista, trancaInicio)
    return resultado

@app.post("/devolucao", status_code=200, response_model=Devolucao, tags=["Aluguel"])
def realizar_devolucao(idTranca: int = Body(...), idBicicleta: int = Body(...), db: Session = Depends(get_db)):
    ciclista_service = CiclistaService(db, url_externo=URL_EXTERNO, url_equipamento=URL_EQUIPAMENTO)
    resp = ciclista_service.realizar_devolucao(idBicicleta, idTranca)
    return resp