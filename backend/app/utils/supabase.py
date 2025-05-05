from supabase import create_client, Client
import logging

# Importar o logger
from .logger import logger

class SupabaseClient:
    _instance = None
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                logger.debug("Inicializando cliente Supabase...")
                cls._client = create_client(
                    'https://cwrxdjfmxntmplwdbnpg.supabase.co',
                    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cnhkamZteG50bXBsd2RibnBnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjAwMjQzOSwiZXhwIjoyMDYxNTc4NDM5fQ.wUCecHTnyEwSVoH_-ruIV4fIGibr0vNkGZPbTVBM8uY'
                )
                # Teste de conexão
                test = cls._client.table('admin_users').select("*").limit(1).execute()
                logger.debug(f"Teste de conexão Supabase bem-sucedido: {test}")
            except Exception as e:
                logger.error(f"Erro ao inicializar Supabase: {str(e)}", exc_info=True)
                cls._client = None
        return cls._client 