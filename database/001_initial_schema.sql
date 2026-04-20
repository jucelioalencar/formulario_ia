-- Migration: 001_initial_schema.sql
-- Create initial tables for formulario_ia application

-- Create usuarios table
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create formularios table
CREATE TABLE IF NOT EXISTS formularios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    link_unico VARCHAR(64) NOT NULL UNIQUE,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create respostas_formulario table
CREATE TABLE IF NOT EXISTS respostas_formulario (
    id SERIAL PRIMARY KEY,
    formulario_id INTEGER NOT NULL REFERENCES formularios(id) ON DELETE CASCADE,
    dados JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_formularios_usuario_id ON formularios(usuario_id);
CREATE INDEX IF NOT EXISTS idx_formularios_link_unico ON formularios(link_unico);
CREATE INDEX IF NOT EXISTS idx_respostas_formulario_id ON respostas_formulario(formulario_id);