CREATE DATABASE IF NOT EXISTS mikensonthomas_estacionamento
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mikensonthomas_estacionamento;

-- =========================================
-- TABELA: usuarios
-- =========================================
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(150) NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,

    INDEX idx_usuarios_cpf (cpf),
    INDEX idx_usuarios_email (email)
) ENGINE=InnoDB;


-- =========================================
-- TABELA: clientes
-- =========================================
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    nome_completo VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,

    tipo_cliente ENUM('Mensalista', 'Horista')
        NOT NULL DEFAULT 'Horista',

    INDEX idx_clientes_cpf (cpf)
) ENGINE=InnoDB;


-- =========================================
-- TABELA: veiculos
-- =========================================
CREATE TABLE IF NOT EXISTS veiculos (
    id_veiculo INT AUTO_INCREMENT PRIMARY KEY,
    modelo VARCHAR(100) NOT NULL,
    placa VARCHAR(7) NOT NULL,
    cor VARCHAR(50) NOT NULL,
    marca VARCHAR(100) NOT NULL,
    id_cliente INT NOT NULL,

    CONSTRAINT fk_veiculos_clientes
        FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    INDEX idx_veiculos_placa (placa)
) ENGINE=InnoDB;


-- =========================================
-- TABELA: vaga
-- =========================================
CREATE TABLE IF NOT EXISTS vaga (
    id_vaga INT AUTO_INCREMENT PRIMARY KEY,
    numero_vaga INT NOT NULL UNIQUE,

    disponibilidade ENUM('Disponível', 'Ocupada')
        NOT NULL DEFAULT 'Disponível',

    INDEX idx_vaga_numero (numero_vaga)
) ENGINE=InnoDB;


-- =========================================
-- TABELA: precos
-- =========================================
CREATE TABLE IF NOT EXISTS precos (
    id_preco INT AUTO_INCREMENT PRIMARY KEY,
    valor_hora DECIMAL(10,2) NOT NULL,
    valor_mensal DECIMAL(10,2) NOT NULL,

    CONSTRAINT chk_precos_valor_hora
        CHECK (valor_hora >= 0),

    CONSTRAINT chk_precos_valor_mensal
        CHECK (valor_mensal >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS movimentacoes (
    id_movimentacao INT AUTO_INCREMENT PRIMARY KEY,
    id_veiculo INT NOT NULL,
    id_vaga INT NOT NULL,

    data_hora_entrada DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_hora_saida DATETIME NULL,

    valor_total DECIMAL(10,2) NULL,

    status ENUM('Em andamento', 'Finalizada')
        NOT NULL DEFAULT 'Em andamento',

    CONSTRAINT fk_movimentacoes_veiculo
        FOREIGN KEY (id_veiculo)
        REFERENCES veiculos(id_veiculo)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_movimentacoes_vaga
        FOREIGN KEY (id_vaga)
        REFERENCES vaga(id_vaga)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    INDEX idx_movimentacoes_veiculo (id_veiculo),
    INDEX idx_movimentacoes_vaga_status (id_vaga, status),
    INDEX idx_movimentacoes_status (status),
    INDEX idx_movimentacoes_entrada (data_hora_entrada)
) ENGINE=InnoDB;

ALTER TABLE clientes
ADD COLUMN cep VARCHAR(9) NOT NULL DEFAULT '',
ADD COLUMN rua VARCHAR(150) NOT NULL DEFAULT '',
ADD COLUMN bairro VARCHAR(100) NOT NULL DEFAULT '',
ADD COLUMN estado VARCHAR(2) NOT NULL DEFAULT '',
ADD COLUMN numero_casa VARCHAR(20) NOT NULL DEFAULT '',
ADD COLUMN numero_apartamento VARCHAR(20) NULL,
ADD COLUMN complemento VARCHAR(100) NULL;

ALTER TABLE clientes
ADD COLUMN tipo_pessoa ENUM('Fisica', 'Juridica') NOT NULL DEFAULT 'Fisica',
ADD COLUMN documento VARCHAR(14) NULL;