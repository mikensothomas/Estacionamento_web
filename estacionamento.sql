CREATE DATABASE IF NOT EXISTS estacionamento
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE estacionamento;


-- =========================================
-- 2. TABELA CLIENTES
-- =========================================

CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    nome_completo VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    tipo_cliente ENUM('Mensalista', 'Horista')
        NOT NULL DEFAULT 'Horista'
);


-- =========================================
-- 3. TABELA VEICULOS
-- =========================================

CREATE TABLE veiculos (
    id_veiculo INT AUTO_INCREMENT PRIMARY KEY,
    modelo VARCHAR(100) NOT NULL,
    placa VARCHAR(7) NOT NULL UNIQUE,
    cor ENUM('verde', 'vermelho', 'amarelo', 'branco', 'azul') NOT NULL,
    marca VARCHAR(100) NOT NULL,
    id_cliente INT NOT NULL,

    CONSTRAINT fk_veiculos_clientes
        FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


-- =========================================
-- 4. TABELA USUARIOS
-- =========================================

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(150) NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);


-- =========================================
-- 5. TABELA VAGAS
-- =========================================

CREATE TABLE vaga (
    id_vaga INT AUTO_INCREMENT PRIMARY KEY,
    numero_vaga INT NOT NULL UNIQUE,
    disponibilidade ENUM('Disponível', 'Ocupada')
        NOT NULL DEFAULT 'Disponível'
);


-- =========================================
-- 6. TABELA PRECOS
-- =========================================

CREATE TABLE precos (
    id_preco INT AUTO_INCREMENT PRIMARY KEY,
    valor_hora DECIMAL(10,2) NOT NULL,
    valor_mensal DECIMAL(10,2) NOT NULL
);
