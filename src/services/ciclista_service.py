from http.client import HTTPException
from typing import List
from fastapi.openapi.utils import status_code_ranges
from sqlalchemy.orm import Session, joinedload
from ..models import Ciclista, CartaoCreditoDB, Passaporte, FuncionarioDB, AluguelDB
from ..schemas import NovoCiclista, NovoCartaoDeCredito, NovoFuncionario, Funcionario

class CiclistaService:
    def __init__(self, db: Session):
        self.db = db

    def cadastrar_ciclista(self, ciclista: NovoCiclista, meio_de_pagamento: NovoCartaoDeCredito):
        # Criar o objeto Ciclista sem o relacionamento aninhado
        ciclista_data = ciclista.model_dump(exclude={"passaporte"})
        ciclista_data["urlFotoDocumento"] = str(ciclista_data["urlFotoDocumento"])
        novo_ciclista = Ciclista(**ciclista_data)

        # Se houver dados do passaporte, cria a instância do modelo Passaporte
        if ciclista.passaporte:
            passaporte_data = ciclista.passaporte.model_dump()
            novo_ciclista.passaporte = Passaporte(**passaporte_data)

        # Adicionar o Ciclista ao banco de dados
        self.db.add(novo_ciclista)
        self.db.commit()
        self.db.refresh(novo_ciclista)

        # Criar o objeto de meio de pagamento associado ao ciclista
        meio_de_pagamento_data = meio_de_pagamento.model_dump()
        novo_meio_de_pagamento = CartaoCreditoDB(**meio_de_pagamento_data, ciclista_id=novo_ciclista.id)
        self.db.add(novo_meio_de_pagamento)
        self.db.commit()

        return novo_ciclista

    def recupera_ciclista_por_id(self, id_ciclista:int):
        ciclista = (
            self.db.query(Ciclista)
            .options(joinedload(Ciclista.passaporte))
            .filter(Ciclista.id == id_ciclista)
            .first()
        )
        return ciclista

    def atualizar_ciclista(self, id_ciclista: int, dados_ciclista: dict):
        # Recupera o ciclista pelo ID
        ciclista = self.recupera_ciclista_por_id(id_ciclista)

        if not ciclista:
            return None

        # Atualiza os campos do ciclista
        for key, value in dados_ciclista.items():
            if key != "passaporte" and hasattr(ciclista, key):
                setattr(ciclista, key, value if key != "urlFotoDocumento" else str(value))

        # Atualiza ou cria o passaporte, se enviado
        if "passaporte" in dados_ciclista:
            passaporte_dados = dados_ciclista["passaporte"]
            if ciclista.passaporte:
                # Atualiza o passaporte existente
                for key, value in passaporte_dados.items():
                    if hasattr(ciclista.passaporte, key):
                        setattr(ciclista.passaporte, key, value)
            else:
                # Cria um novo passaporte
                passaporte = Passaporte(**passaporte_dados, ciclista_id=ciclista.id)
                self.db.add(passaporte)
                ciclista.passaporte = passaporte

        # Commit na atualização
        self.db.commit()
        self.db.refresh(ciclista)
        return ciclista

    def ativar_ciclista(self, id_ciclista: int):

        ciclista = self.recupera_ciclista_por_id(id_ciclista)

        if not ciclista:
            return None

        ciclista.status = 'ATIVO'

        self.db.commit()
        self.db.refresh(ciclista)

        return ciclista

    def busca_cartao(self, id_ciclista: int):
        ciclista = self.recupera_ciclista_por_id(id_ciclista)

        if not ciclista:
            return None

        cartao = (
            self.db.query(CartaoCreditoDB)
            .filter(CartaoCreditoDB.ciclista_id == ciclista.id)
            .first()
        )

        return cartao

    def edita_cartao(self, id_ciclista: int, novo_cartao = NovoCartaoDeCredito):
        ciclista = self.recupera_ciclista_por_id(id_ciclista)
        if not ciclista:
            return None

        cartao = (
            self.db.query(CartaoCreditoDB)
            .filter(CartaoCreditoDB.ciclista_id == ciclista.id)
            .first()
        )

        dados_cartao = novo_cartao.model_dump(exclude_unset=True)
        for key, value in dados_cartao.items():
            setattr(cartao, key, value)

        self.db.commit()
        self.db.refresh(cartao)
        return True

    def conferir_email_ja_foi_utilizado(self, email):
        return self.db.query(Ciclista).filter(Ciclista.email == email).first() is not None

    def ciclista_pode_alugar(self, id_ciclista):
        ciclista = self.recupera_ciclista_por_id(id_ciclista)
        if ciclista is None:
            return None
        aluguel = self.db.query(AluguelDB).filter(AluguelDB.ciclista_id == id_ciclista, AluguelDB.horaFim.is_(None)).first()
        if not aluguel:
            return True
        return False

    def busca_bicicleta_alugada(self, id_ciclista):
        ciclista = self.recupera_ciclista_por_id(id_ciclista)
        print(ciclista)
        if not ciclista:
            raise Exception("Ciclista não encontrado.")

        bicicleta = (
            self.db.query(AluguelDB)
            .filter(AluguelDB.ciclista_id == id_ciclista, AluguelDB.horaFim.is_(None))
            .first()
        )
        bicicleta_id = None
        if bicicleta:
            bicicleta_id = bicicleta.bicicleta

        #todo : chamar api do Leo pra puxar a bicicleta
        if not bicicleta:
            return None


    def recupera_funcionarios(self) -> List[Funcionario]:
        funcionarios = self.db.query(FuncionarioDB).all()
        return [Funcionario.model_validate(func) for func in funcionarios]

    def cadastrar_funcionario(self, funcionario: NovoFuncionario) -> Funcionario:
        # Cria o objeto Ciclista
        novo_funcionario = FuncionarioDB(**funcionario.model_dump())
        self.db.add(novo_funcionario)
        self.db.commit()
        self.db.refresh(novo_funcionario)

        return novo_funcionario

    def recupera_funcionario(self, id_funcionario):
        funcionario = self.db.query(FuncionarioDB).filter(FuncionarioDB.id == id_funcionario).first()
        return funcionario

    def editar_funcionario(self, id_funcionario, dados_funcionario):
        funcionario = self.recupera_funcionario(id_funcionario)
        if not funcionario:
            return None
        # Atualiza os campos do funcionário (se houver)
        for key, value in dados_funcionario.items():
            if hasattr(funcionario, key):
                setattr(funcionario, key, value)

        self.db.commit()
        self.db.refresh(funcionario)
        return self.db.query(FuncionarioDB).filter(FuncionarioDB.id == id_funcionario).first()

    def delete_funcionario(self, id_funcionario: int):
        # Recupera o funcionário pelo ID
        funcionario = self.db.query(FuncionarioDB).filter(FuncionarioDB.id == id_funcionario).first()

        # Se o funcionário não for encontrado, retorna None
        if not funcionario:
            return None

        # Deleta o funcionário
        self.db.delete(funcionario)
        self.db.commit()

        return True
