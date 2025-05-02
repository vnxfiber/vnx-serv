-- Criação da tabela para armazenar a última verificação de cada usuário
CREATE TABLE IF NOT EXISTS user_last_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    last_check_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para melhorar performance
CREATE INDEX IF NOT EXISTS idx_user_last_checks_user_id ON user_last_checks(user_id);

-- Função para atualizar o timestamp de atualização
CREATE OR REPLACE FUNCTION update_user_last_checks_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar o timestamp quando o registro for atualizado
DROP TRIGGER IF EXISTS update_user_last_checks_modtime ON user_last_checks;
CREATE TRIGGER update_user_last_checks_modtime
BEFORE UPDATE ON user_last_checks
FOR EACH ROW
EXECUTE FUNCTION update_user_last_checks_modified_column();

-- Políticas de segurança RLS (Row Level Security)
ALTER TABLE user_last_checks ENABLE ROW LEVEL SECURITY;

-- Política para leitura: usuários só podem ver seus próprios registros
CREATE POLICY user_last_checks_select_policy ON user_last_checks
    FOR SELECT
    USING (auth.uid() = user_id);

-- Política para inserção: usuários só podem criar registros para si mesmos
CREATE POLICY user_last_checks_insert_policy ON user_last_checks
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Política para atualização: usuários só podem atualizar seus próprios registros
CREATE POLICY user_last_checks_update_policy ON user_last_checks
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Política para deleção: usuários só podem deletar seus próprios registros
CREATE POLICY user_last_checks_delete_policy ON user_last_checks
    FOR DELETE
    USING (auth.uid() = user_id); 