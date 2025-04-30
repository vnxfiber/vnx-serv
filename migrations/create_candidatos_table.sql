-- Criação da tabela para armazenar candidatos do formulário "Trabalhe Conosco"
CREATE TABLE IF NOT EXISTS candidatos_trabalhe_conosco (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    whatsapp VARCHAR(50) NOT NULL,
    cidadeEstado VARCHAR(255),
    especialidades TEXT[] DEFAULT '{}',
    experiencia TEXT,
    links TEXT,
    status VARCHAR(50) DEFAULT 'pendente',
    atualizado_por UUID REFERENCES auth.users(id),
    data_cadastro TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_atualizacao TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Função para atualizar o timestamp de atualização
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_atualizacao = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar o timestamp quando o registro for atualizado
DROP TRIGGER IF EXISTS update_candidatos_modtime ON candidatos_trabalhe_conosco;
CREATE TRIGGER update_candidatos_modtime
BEFORE UPDATE ON candidatos_trabalhe_conosco
FOR EACH ROW
EXECUTE FUNCTION update_modified_column(); 