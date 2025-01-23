-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2025-01-21 14:49:57.664


DROP TABLE IF EXISTS ciclista;
DROP TABLE IF EXISTS aluguel;
DROP TABLE IF EXISTS cartao_credito;
DROP TABLE IF EXISTS passaporte;
DROP TABLE IF EXISTS funcionario;


-- Table: ciclista
CREATE TABLE if not exists ciclista (
    id integer NOT NULL CONSTRAINT ciclista_pk PRIMARY KEY AUTOINCREMENT,
    nome varchar(250) NOT NULL,
    email varchar(250) NOT NULL,
    nacionalidade varchar(250) NOT NULL,
    nascimento date NOT NULL,
    senha varchar(250) NOT NULL,
    urlFotoDocumento varchar(250),
    cpf varchar(11),
    status varchar(250) NOT NULL
);
-- Inserindo os dados na tabela ciclista
INSERT INTO ciclista (id, nome, email, nacionalidade, nascimento, senha, cpf, status)
VALUES 
(1, 'Fulano Beltrano', 'user@example.com', 'BRASILEIRO', '2021-05-02', 'ABC123', '78804034009', 'CONFIRMADO'),
(2, 'Fulano Beltrano', 'user2@example.com', 'BRASILEIRO', '2021-05-02', 'ABC123', '43943488039', 'AGUARDANDO_CONFIRMACAO'),
(3, 'Fulano Beltrano', 'user3@example.com', 'BRASILEIRO', '2021-05-02', 'ABC123', '10243164084', 'CONFIRMADO'),
(4, 'Fulano Beltrano', 'user4@example.com', 'BRASILEIRO', '2021-05-02', 'ABC123', '30880150017', 'CONFIRMADO');


-- Table: aluguel
CREATE TABLE if not exists aluguel (
    id integer NOT NULL CONSTRAINT aluguel_pk PRIMARY KEY AUTOINCREMENT,
    ciclista_id integer NOT NULL,
    horaInicio datetime NOT NULL,
    horaFim datetime,
    trancaInicio integer NOT NULL,
    trancaFim integer,
    cobranca integer NOT NULL,
    bicicleta integer NOT NULL,
    cobranca_adicional integer,
    CONSTRAINT aluguel_ciclista FOREIGN KEY (ciclista_id)
    REFERENCES ciclista (id)
);

INSERT into aluguel (ciclista_id, horaInicio, trancaInicio, cobranca, bicicleta) 
values(3, datetime('now'), 2, 1, 3); 

-- Aluguel 2: Ciclista 4, Bicicleta 5
INSERT INTO aluguel (ciclista_id, horaInicio, trancaInicio, cobranca, bicicleta)
VALUES (4, datetime('now', '-2 hours'), 4, 2, 5);

-- Aluguel 3: Ciclista 3, Bicicleta 1 (Finalizado com cobrança extra pendente)
INSERT INTO aluguel (ciclista_id, horaInicio, horaFim, trancaInicio, trancaFim, cobranca, bicicleta)
VALUES (3, datetime('now', '-2 hours'), datetime('now'), 1, 2, 3, 1);


-- Table: cartao_credito
CREATE TABLE IF NOT EXISTS cartao_credito (
    id integer NOT NULL CONSTRAINT cartao_credito_pk PRIMARY KEY AUTOINCREMENT,
    ciclista_id integer NOT NULL,
    numero varchar(12) NOT NULL,
    validade date NOT NULL,
    cvv varchar(3) NOT NULL,
    nomeTitular varchar(250) NOT NULL,
    CONSTRAINT Table_2_Cicilista FOREIGN KEY (ciclista_id)
    REFERENCES ciclista (id)
);


-- Table: funcionario
CREATE TABLE IF NOT EXISTS funcionario (
    matricula integer NOT NULL CONSTRAINT funcionario_pk PRIMARY KEY AUTOINCREMENT,
    nome varchar(250) NOT NULL,
    email varchar(250) NOT NULL,
    senha varchar(250) NOT NULL,
    confirmacaoSenha varchar(250),
    cpf varchar(11) NOT NULL,
    funcao varchar(250) NOT NULL,
    idade integer NOT NULL
);
INSERT INTO funcionario (matricula, nome, email, senha, cpf, funcao, idade)
VALUES 
(12345, 'Beltrano', 'employee@example.com', '123', '99999999999', 'Reparador', 25);



-- Table: passaporte
CREATE TABLE passaporte (
    id integer NOT NULL CONSTRAINT id PRIMARY KEY AUTOINCREMENT,
    numero varchar(250) NOT NULL,
    validade varchar(10) NOT NULL,
    pais varchar(2) NOT NULL,
    ciclista_id date NOT NULL,
    CONSTRAINT passaporte_cicilista FOREIGN KEY (ciclista_id)
    REFERENCES ciclista (id)
);

-- End of file.

