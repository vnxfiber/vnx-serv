from supabase import create_client
import os

class SupabaseClient:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.client = None
        
        if self.supabase_url and self.supabase_key:
            self.client = create_client(self.supabase_url, self.supabase_key)
    
    def get_client(self):
        if not self.client:
            raise Exception("Cliente Supabase não inicializado. Verifique as variáveis de ambiente SUPABASE_URL e SUPABASE_KEY")
        return self.client 