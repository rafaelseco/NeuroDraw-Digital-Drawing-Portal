--
-- File generated with SQLiteStudio v3.4.4 on dom jun 23 15:09:07 2024
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Admins
CREATE TABLE Admins (ID INTEGER PRIMARY KEY AUTOINCREMENT, Nome TEXT, Apelido TEXT, NIF TEXT, ID_Atividade INTEGER REFERENCES Atividade (ID));

-- Table: Atividade
CREATE TABLE Atividade (ID INTEGER PRIMARY KEY AUTOINCREMENT, Descricao TEXT);

-- Table: contacto
CREATE TABLE contacto (id INTEGER PRIMARY KEY AUTOINCREMENT, PrimeiroNomeContacto TEXT (20), UltimoNomeContacto TEXT (20), EmailContacto TEXT (30), DescricaoContacto TEXT, estado TEXT, resposta TEXT);

-- Table: Dificuldade
CREATE TABLE Dificuldade (ID INTEGER PRIMARY KEY AUTOINCREMENT, NivelDificuldade TEXT);

-- Table: Especialidade
CREATE TABLE Especialidade (ID INTEGER PRIMARY KEY AUTOINCREMENT, Descricao TEXT);

-- Table: Evento
CREATE TABLE Evento (ID INTEGER PRIMARY KEY AUTOINCREMENT, Descricao TEXT);

-- Table: Exames
CREATE TABLE Exames (ID INTEGER PRIMARY KEY AUTOINCREMENT, ID_Medico INTEGER REFERENCES Medicos (ID), ID_Paciente INTEGER REFERENCES Pacientes (ID), ID_Dificuldade INTEGER REFERENCES Dificuldade (ID), Erro TEXT, PercentagemAcerto TEXT, Tempo TEXT, Data TEXT, ID_Marcacao INTEGER REFERENCES Marcacao (ID), Ficheiro TEXT, Anotacoes TEXT);

-- Table: Funcao
CREATE TABLE Funcao (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Descricao TEXT NOT NULL);

-- Table: login
CREATE TABLE login (login INTEGER PRIMARY KEY NOT NULL UNIQUE, password TEXT, ID INTEGER, latitude NUMERIC, longitude NUMERIC, remember INTEGER);

-- Table: Marcacao
CREATE TABLE Marcacao (ID INTEGER PRIMARY KEY AUTOINCREMENT, ID_Medico TEXT REFERENCES Medicos (ID), ID_Paciente TEXT REFERENCES Pacientes (ID), ID_Evento TEXT REFERENCES Evento (ID), Dte DATETIME, ID_Presenca INTEGER REFERENCES Presenca (ID));

-- Table: Medicos
CREATE TABLE Medicos (ID INTEGER PRIMARY KEY AUTOINCREMENT, Nome TEXT, Apelido TEXT, Idade INTEGER, NrCC INTEGER, NIF_Login TEXT, ID_Especialidade INTEGER REFERENCES Especialidade (ID), Mail TEXT, ID_Sexo INTEGER REFERENCES Sexo (ID), Telemovel TEXT, ID_Atividade INTEGER REFERENCES Atividade (ID), Info INTEGER);

-- Table: Mensagens
CREATE TABLE Mensagens (ID INTEGER PRIMARY KEY AUTOINCREMENT, NIF_Emissor TEXT, NIF_Destinatario TEXT, Data TEXT, Hora TEXT, ConteudoMensagem TEXT, Estado TEXT);

-- Table: Pacientes
CREATE TABLE Pacientes (ID INTEGER PRIMARY KEY AUTOINCREMENT, Nome TEXT, Apelido TEXT, Idade INTEGER, NrCC INTEGER, NIF TEXT, ID_Sexo INTEGER REFERENCES Sexo (ID), Telemovel INTEGER, ID_Medico TEXT REFERENCES Medicos (ID), Email TEXT, ID_Atividade INTEGER REFERENCES Atividade (ID), Info INTEGER);

-- Table: Presenca
CREATE TABLE Presenca (ID INTEGER PRIMARY KEY AUTOINCREMENT, Descricao TEXT);

-- Table: Sexo
CREATE TABLE Sexo (ID INTEGER PRIMARY KEY AUTOINCREMENT, Descricao TEXT);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
