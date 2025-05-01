// Inicialização do Supabase
const supabase = supabase.createClient(
    'https://cwrxdjfmxntmplwdbnpg.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cnhkamZteG50bXBsd2RibnBnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYwMDI0MzksImV4cCI6MjA2MTU3ODQzOX0.-kFUUiLn2plnEdopteCdxcixyY3pI5O-K-hIk1IL61s'
);

// Função para verificar se o usuário está autenticado
async function checkAuth() {
    const { data: { user }, error } = await supabase.auth.getUser();
    
    if (error || !user) {
        window.location.href = '/login.html';
        return false;
    }
    
    return true;
}

// Função para fazer login
async function login(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password
    });

    if (error) {
        throw error;
    }

    window.location.href = '/adm/dashboard-admin.html';
}

// Função para fazer logout
async function logout() {
    const { error } = await supabase.auth.signOut();
    
    if (error) {
        console.error('Erro ao fazer logout:', error);
        return;
    }
    
    window.location.href = '/login.html';
}

// Exportar funções
window.auth = {
    checkAuth,
    login,
    logout
}; 