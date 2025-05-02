-- Criação da tabela para armazenar notificações
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- Função para atualizar o timestamp de atualização
CREATE OR REPLACE FUNCTION update_notification_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar o timestamp quando o registro for atualizado
DROP TRIGGER IF EXISTS update_notifications_modtime ON notifications;
CREATE TRIGGER update_notifications_modtime
BEFORE UPDATE ON notifications
FOR EACH ROW
EXECUTE FUNCTION update_notification_modified_column();

-- Políticas de segurança RLS (Row Level Security)
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Política para leitura: usuários só podem ver suas próprias notificações
CREATE POLICY notifications_select_policy ON notifications
    FOR SELECT
    USING (auth.uid() = user_id);

-- Política para inserção: usuários só podem criar notificações para si mesmos
CREATE POLICY notifications_insert_policy ON notifications
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Política para atualização: usuários só podem atualizar suas próprias notificações
CREATE POLICY notifications_update_policy ON notifications
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Política para deleção: usuários só podem deletar suas próprias notificações
CREATE POLICY notifications_delete_policy ON notifications
    FOR DELETE
    USING (auth.uid() = user_id); 