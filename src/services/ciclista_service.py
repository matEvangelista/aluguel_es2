import datetime
from fastapi import HTTPException
from typing import List
from fastapi.openapi.utils import status_code_ranges
from sqlalchemy.orm import Session, joinedload
from ..models import Ciclista, CartaoCreditoDB, Passaporte, FuncionarioDB, AluguelDB
from ..schemas import NovoCiclista, NovoCartaoDeCredito, NovoFuncionario, Funcionario, Aluguel, Devolucao, Bicicleta
from ..controllers import AluguelController
import requests


class CiclistaService:
    def __init__(self, db: Session, url_externo:str = None, url_equipamento: str = None):
        self.db = db
        self.url_externo = url_externo
        self.url_equipamento = url_equipamento

    def enviar_email(self, assunto, mensagem, endereco_email):
        url = self.url_externo + "/enviarEmail"
        # Dados do corpo da requisição
        corpo = {
            "email": endereco_email,
            "assunto": assunto,
            "mensagem": mensagem
        }
        headers = {
            "Content-Type": "application/json"  # Certifique-se de enviar como JSON
        }
        response = requests.post(url, json=corpo, headers=headers)
        # verificando a resposta
        return response.status_code == 200

    def validar_cartao(self, cartao:NovoCartaoDeCredito):
        url = self.url_externo + "/validaCartaoDeCredito"
        corpo = {
            "numero": cartao.numero,
            "validade": cartao.validade.isoformat(),
            "cvv": cartao.cvv,
            "nomeTitular": cartao.nomeTitular
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=corpo, headers=headers)
        return response.status_code == 200

    def busca_tranca(self, id_tranca: int):
        url = self.url_equipamento + f"/tranca/{id_tranca}"
        headers = {'accept': 'application/json'}
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return None
        return resp.json()

    def busca_bicicleta(self, id_tranca: int):
        url = self.url_equipamento + f"/tranca/{id_tranca}/bicicleta"
        headers = {'accept': 'application/json'}
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return None
        return resp.json()

    def busca_bicicleta_por_id(self, id_bicicleta):
        url = self.url_equipamento + f"/bicicleta/{id_bicicleta}"
        headers = {'accept': 'application/json'}
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return None
        return resp.json()

    def bicicleta_em_uso(self, id_bicleta: int):
        url = self.url_equipamento + f"/bicicleta/{id_bicleta}"
        headers = {'accept': 'application/json'}
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return False
        return resp.json()['status']=='EM_USO'

    def destranca(self, id_tranca, id_bicicleta):
        url = self.url_equipamento + f"/tranca/{id_tranca}/destrancar"
        corpo = {
            "bicicleta": id_bicicleta,
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=corpo, headers=headers)
        if response.status_code != 200:
            return None
        return response.json()

    def tranca(self, id_tranca, id_bicicleta):
        url = self.url_equipamento + f"/tranca/{id_tranca}/trancar"
        corpo = {
            "bicicleta": id_bicicleta,
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=corpo, headers=headers)
        if response.status_code != 200:
            return None
        return response.json()

    def fazer_cobranca(self, id_ciclista, valor):
        url = self.url_externo + "/cobranca"
        corpo = {
            "ciclista": id_ciclista,
            "valor": valor
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=corpo, headers=headers)
        if response.status_code != 200:
            return None
        return response.json()

    def fazer_cobranca_pendente(self, id_ciclista, valor):
        url = self.url_externo + "/filaCobranca"
        corpo = {
            "ciclista": id_ciclista,
            "valor": valor
        }
        headers = {
            "Content-Type": "application/json"  # Certifique-se de enviar como JSON
        }
        response = requests.post(url, json=corpo, headers=headers)
        if response.status_code != 200:
            return None
        return response.json()


    def cadastrar_ciclista(self, ciclista: NovoCiclista, meio_de_pagamento: NovoCartaoDeCredito):

        if not ciclista.nacionalidade == 'BRASILEIRO' and ciclista.passaporte is None:
            raise Exception("Estrangeiro sem passaporte.")
        if ciclista.nacionalidade.lower() == 'ESTRANGEIRO' and ciclista.cpf is None:
            raise Exception("Brasileiro sem cpf.")

        if self.conferir_email_ja_foi_utilizado(ciclista.email):
            raise Exception("Outro ciclista possui este email.")

        # criar o objeto Ciclista sem o relacionamento aninhado
        ciclista_data = ciclista.model_dump(exclude={"passaporte"})
        ciclista_data["urlFotoDocumento"] = str(ciclista_data["urlFotoDocumento"])
        novo_ciclista = Ciclista(**ciclista_data)


        # Se houver dados do passaporte, cria a instância do modelo Passaporte
        if ciclista.passaporte:
            passaporte_data = ciclista.passaporte.model_dump()
            novo_ciclista.passaporte = Passaporte(**passaporte_data)

        cartao_valido = self.validar_cartao(meio_de_pagamento)

        if not cartao_valido:
            raise HTTPException(status_code=422, detail="Cartão de crédito inválido.")

        # Adicionar o Ciclista ao banco de dados
        self.db.add(novo_ciclista)
        self.db.commit()
        self.db.refresh(novo_ciclista)

        # Criar o objeto de meio de pagamento associado ao ciclista
        meio_de_pagamento_data = meio_de_pagamento.model_dump()
        novo_meio_de_pagamento = CartaoCreditoDB(**meio_de_pagamento_data, ciclista_id=novo_ciclista.id)
        self.db.add(novo_meio_de_pagamento)
        self.db.commit()

        mensagem = (
            f"Caro {ciclista.nome},<br><br> Sua inscrição no sistema de bicletas do grupo A precisa ser validada agora"
            f"<br><br>Cordialmente, <br>Grupo A")

        # enviar email para novo ciclista
        enviou_email = self.enviar_email(assunto="Cadastro de ciclista -- Grupo A",
                                         mensagem=mensagem,
                                         endereco_email=ciclista.email)

        if not enviou_email:
            raise HTTPException(422, "Não foi possível enviar o email")

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
        ciclista = self.recupera_ciclista_por_id(id_ciclista)

        if not ciclista:
            raise HTTPException(404, "Ciclista não encontrado")

        if ciclista.status == 'AGUARDANDO_CONFIRMACAO':
            raise HTTPException(422, "Ciclista não ativou email")

        # atualiza os campos do ciclista
        for key, value in dados_ciclista.items():
            if key != "passaporte" and hasattr(ciclista, key):
                setattr(ciclista, key, value if key != "urlFotoDocumento" else str(value))

        if ciclista.nacionalidade == 'BRASILEIRO' and ciclista.cpf is None:
            raise HTTPException(422, "Brasileiro sem CPF")
        if ciclista.nacionalidade == 'ESTRANGEIRO' and ciclista.passaporte is None:
            raise HTTPException(422, "Estrangeiro sem Passaporte")

        if "passaporte" in dados_ciclista.keys():
            if dados_ciclista['passaporte'] is not None:
                passaporte_dados = dados_ciclista["passaporte"]
                if ciclista.passaporte:
                    for key, value in passaporte_dados.items():
                        if hasattr(ciclista.passaporte, key):
                            setattr(ciclista.passaporte, key, value)
                else:
                    passaporte = Passaporte(**passaporte_dados, ciclista_id=ciclista.id)
                    self.db.add(passaporte)
                    ciclista.passaporte = passaporte
            else:
                passaporte = ciclista.passaporte
                self.db.delete(passaporte)
                self.db.commit()
                ciclista.passaporte = None

        self.db.commit()
        self.db.refresh(ciclista)

        assunto = "Atualização de dados"
        mensagem = (f"Prezado {ciclista.nome},<br><br> Informamos que seus dados foram atualizados com sucesso"
                    f"<br><br>Cordialmente, <br>Grupo A")

        enviou_email = self.enviar_email(assunto=assunto, mensagem=mensagem, endereco_email=ciclista.email)
        if not enviou_email:
            raise HTTPException(422, "Email não pode ser enviado.")

        return ciclista

    def ativar_ciclista(self, id_ciclista: int):

        ciclista = self.recupera_ciclista_por_id(id_ciclista)

        if not ciclista:
            raise HTTPException(status_code=404, detail="Cicilista não encontrado.")

        if ciclista.status == 'CONFIRMADO':
            raise HTTPException(status_code=422, detail="Ciclista já confirmado.")

        ciclista.status = 'CONFIRMADO'

        try:
            self.db.commit()
            self.db.refresh(ciclista)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Erro ao ativar o ciclista.") from e

        return ciclista

    def busca_cartao(self, id_ciclista: int):
        ciclista = self.recupera_ciclista_por_id(id_ciclista)

        if not ciclista:
            raise HTTPException(404, "Ciclista não encontrado")

        cartao = (
            self.db.query(CartaoCreditoDB)
            .filter(CartaoCreditoDB.ciclista_id == ciclista.id)
            .first()
        )

        if not cartao:
            raise HTTPException(status_code=404, detail="Ciclista não tem cartão")

        return cartao

    def edita_cartao(self, id_ciclista: int, novo_cartao: NovoCartaoDeCredito):
        ciclista = self.recupera_ciclista_por_id(id_ciclista)
        if not ciclista:
            raise HTTPException(404, "Ciclista não encontrado")

        if ciclista.status == 'AGUARDANDO_CONFIRMACAO':
            raise HTTPException(422, "Ciclista não foi ativado.")

        cartao_valido = self.validar_cartao(cartao=novo_cartao)

        if not cartao_valido:
            raise HTTPException(422, "Cartão de crédito inválido.")

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

        enviou_email = self.enviar_email(assunto="Edição de Cartão -- Grupo A",
                                         mensagem=f"Prezado {ciclista.nome},<br><br>"
                                                  f"O cartão de crédito foi editado com sucesso.<br><br>"
                                                  f"Cordialmente,<br>Grupo A",
                                         endereco_email=ciclista.email)
        if not enviou_email:
            raise HTTPException(422, "Email não enviado.")

    def conferir_email_ja_foi_utilizado(self, email):
        return self.db.query(Ciclista).filter(Ciclista.email == email).first() is not None

    def ciclista_pode_alugar(self, id_ciclista):
        ciclista = self.recupera_ciclista_por_id(id_ciclista)
        if ciclista is None:
            raise HTTPException(404, "Ciclista não encontrado")

        aluguel = self.db.query(AluguelDB).filter(AluguelDB.ciclista_id == id_ciclista, AluguelDB.horaFim.is_(None)).first()

        if not aluguel and ciclista.status == 'CONFIRMADO':
            return True
        return False

    def busca_bicicleta_alugada(self, id_ciclista):
        ciclista = self.recupera_ciclista_por_id(id_ciclista)
        if not ciclista:
            raise Exception("Ciclista não encontrado.")

        aluguel = (
            self.db.query(AluguelDB)
            .filter(AluguelDB.ciclista_id == id_ciclista, AluguelDB.horaFim.is_(None))
            .first()
        )
        if aluguel is None:
            return None
        bicicleta_id = aluguel.bicicleta

        bicicleta = self.busca_bicicleta_por_id(id_bicicleta=bicicleta_id)
        if not bicicleta:
            raise HTTPException(404, "Bicicleta não encontrada.")
        bicicleta = Bicicleta(id=bicicleta['id'],
                              marca=bicicleta['marca'],
                              modelo=bicicleta['modelo'],
                              ano=bicicleta['ano'],
                              numero=bicicleta['numero'],
                              status=bicicleta['status'])
        return bicicleta


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
        funcionario = self.db.query(FuncionarioDB).filter(FuncionarioDB.matricula == id_funcionario).first()
        return funcionario

    def editar_funcionario(self, id_funcionario, dados_funcionario):
        funcionario = self.recupera_funcionario(id_funcionario)
        if not funcionario:
            return None
        # altera eventuais os campos do funcionário
        for key, value in dados_funcionario.items():
            if hasattr(funcionario, key):
                setattr(funcionario, key, value)

        self.db.commit()
        self.db.refresh(funcionario)
        return self.db.query(FuncionarioDB).filter(FuncionarioDB.matricula == id_funcionario).first()

    def delete_funcionario(self, id_funcionario: int):
        # Recupera o funcionário pelo ID
        funcionario = self.db.query(FuncionarioDB).filter(FuncionarioDB.matricula == id_funcionario).first()

        if not funcionario:
            return None

        # Deleta o funcionário
        self.db.delete(funcionario)
        self.db.commit()

        return True

    def realizar_aluguel(self, id_ciclista, id_tranca_inicio):
        ciclista = self.recupera_ciclista_por_id(id_ciclista)
        if not ciclista:
            raise HTTPException(status_code=404, detail="Ciclista não encontrado.")

        aluguel = self.db.query(AluguelDB).filter(AluguelDB.ciclista_id == id_ciclista,
                                                  AluguelDB.trancaFim.is_(None)).first()

        if aluguel:
            self.enviar_email(assunto="Aviso: você ainda possui uma aluguel ativo",
                              mensagem=f"Prezado {ciclista.nome},<br><br>Notamos que você tentou fazer um novo aluguel, "
                                       f"mas ainda existe outro em seu nome. Para realizar um novo aluguel, encerre seu aluguel atual.<br><br>"
                                       f"Cordialmente,<br>Grupo A",
                              endereco_email=ciclista.email)
            raise HTTPException(status_code=422, detail="Ciclista já possui aluguel")

        if ciclista.status == 'AGUARDANDO_CONFIRMACAO':
            raise HTTPException(status_code=422, detail="Ciclista precisa ser ativado.")

        bicicleta = self.busca_bicicleta(id_tranca=id_tranca_inicio)
        if not bicicleta:
            raise HTTPException(422, "Bicicleta não encontrada.")

        tranca = self.busca_tranca(id_tranca_inicio)
        if not tranca or tranca['status'] != 'OCUPADA':
            raise HTTPException(422, "Tranca não encontrada ou com defeito.")

        cobranca = self.fazer_cobranca(id_ciclista=id_ciclista, valor=10)
        string_cobranca = "Houve cobrança de <b>R$10,00<b/>"
        if not cobranca:
            string_cobranca = "Há uma cobrança pendente de <b>R$10,00<b/>"
            cobranca = self.fazer_cobranca_pendente(id_ciclista, 10)
            if not cobranca:
                raise HTTPException(422, 'Não foi possível fazer a cobrança.')

        tranca = self.destranca(id_tranca=id_tranca_inicio, id_bicicleta=bicicleta['numero'])
        if not tranca:
            raise HTTPException(422, "Tranca não pode ser liberada.")

        hora_inicio = datetime.datetime.now()

        aluguel = Aluguel(
            bicicleta=bicicleta['numero'],
            trancaInicio=id_tranca_inicio,
            cobranca=cobranca['id'],
            ciclista=id_ciclista,
            horaInicio=hora_inicio  # Definindo a hora de início corretamente
        )

        # Criando o objeto de banco de dados AluguelDB e inserindo no banco
        aluguel_banco = AluguelDB(
            ciclista_id = id_ciclista,
            trancaInicio = id_tranca_inicio,
            cobranca=cobranca['id'],
            horaInicio=hora_inicio,
            bicicleta=bicicleta['numero']
        )

        self.db.add(aluguel_banco)
        self.db.commit()
        self.db.refresh(aluguel_banco)

        self.enviar_email("Aluguel de Bicicleta -- Grupo A",
                          mensagem=f"Prezado {ciclista.nome},<br>"
                                   f"O aluguel da bicicleta {bicicleta['numero']} foi feito com sucesso às {hora_inicio}<br>"
                                   f"{string_cobranca}<br><br>Cordialmente,<br>Grupo A.",
                          endereco_email=ciclista.email)

        return aluguel

    def realizar_devolucao(self, id_bicicleta, id_tranca_fim):
        aluguel = self.db.query(AluguelDB).filter(AluguelDB.bicicleta == id_bicicleta,
                                                  AluguelDB.trancaFim.is_(None),
                                                  AluguelDB.horaFim.is_(None)).first()
        if not aluguel:
            raise HTTPException(status_code=404, detail="Tranca ou bicicleta não existem")

        tranca = self.busca_tranca(id_tranca_fim)
        if tranca is None or tranca['status'] != 'DISPONIVEL':
            raise HTTPException(status_code=422, detail="Tranca não está disponível")

        if not self.bicicleta_em_uso(id_bicicleta):
            raise HTTPException(status_code=422, detail="Tranca não está disponível")

        hora_inicial = aluguel.horaInicio
        hora_final = datetime.datetime.now()

        aluguel.horaFim = hora_final
        aluguel.trancaFim = id_tranca_fim

        valor_a_cobrar = AluguelController.calcula_valor_extra(hora_inicial, hora_final)
        string_cobranca = ""
        if valor_a_cobrar > 0:
            string_cobranca = f"Houve uma cobranca adicional de R${valor_a_cobrar}."
            nova_cobranca = self.fazer_cobranca(id_ciclista=aluguel.ciclista_id, valor=valor_a_cobrar)
            if nova_cobranca is None:
                cobranca_pendente = self.fazer_cobranca_pendente(aluguel.ciclista_id, valor=valor_a_cobrar)
                if not cobranca_pendente:
                    raise HTTPException(422, "Erro ao fazer cobranca.")
                aluguel.cobranca_adicional = cobranca_pendente['id']
                string_cobranca =f"Há uma cobranca pendente de R${valor_a_cobrar}."
            aluguel.cobranca_adicional = nova_cobranca['id']

        ciclista = self.recupera_ciclista_por_id(aluguel.ciclista_id)

        self.enviar_email(mensagem=f"Prezado {ciclista.nome},<br><br> Registramos sua devolução às {aluguel.horaFim}.<br>"
                          f"{string_cobranca}<br><br>Cordialmente,<br>Grupo A.", assunto="Devolução -- Grupo A",
                          endereco_email=ciclista.email)

        self.db.commit()
        self.db.refresh(aluguel)

        self.tranca(id_tranca_fim, id_bicicleta)

        devolucao = Devolucao(
            bicicleta=id_bicicleta,
            horaInicio=hora_inicial,
            horaFim=hora_final,
            trancaFim=id_tranca_fim,
            cobranca=aluguel.cobranca_adicional,
            ciclista=aluguel.ciclista_id
        )

        return devolucao