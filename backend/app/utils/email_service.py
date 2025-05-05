import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Importar o logger
from .logger import logger

class EmailService:
    def __init__(self, smtp_server='smtp.gmail.com', smtp_port=587, sender_email=None, sender_password=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        
    def enviar_email(self, destinatario, assunto, conteudo_html, conteudo_texto=None):
        """
        Envia um e-mail para o destinatário especificado.
        
        Args:
            destinatario (str): E-mail do destinatário
            assunto (str): Assunto do e-mail
            conteudo_html (str): Conteúdo HTML do e-mail
            conteudo_texto (str, opcional): Conteúdo em texto plano para clientes que não suportam HTML
            
        Returns:
            bool: True se o e-mail foi enviado com sucesso, False caso contrário
        """
        try:
            # Se as credenciais não foram fornecidas, apenas registrar o e-mail e retornar
            if not self.sender_email or not self.sender_password:
                logger.info(f"Simulando envio de e-mail para {destinatario}")
                logger.info(f"Assunto: {assunto}")
                logger.info(f"Conteúdo: {conteudo_texto or conteudo_html}")
                return True
                
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = self.sender_email
            msg['To'] = destinatario
            
            # Anexar versão em texto plano, se fornecida
            if conteudo_texto:
                msg.attach(MIMEText(conteudo_texto, 'plain'))
                
            # Anexar versão HTML
            msg.attach(MIMEText(conteudo_html, 'html'))
            
            # Criar contexto SSL
            context = ssl.create_default_context()
            
            # Enviar e-mail
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, destinatario, msg.as_string())
                
            logger.info(f"E-mail enviado com sucesso para {destinatario}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {destinatario}: {str(e)}", exc_info=True)
            return False
            
    def enviar_notificacao_parceiro(self, parceiro, status_aprovacao):
        """
        Envia notificação por e-mail para um parceiro técnico.
        
        Args:
            parceiro (dict): Dados do parceiro
            status_aprovacao (str): Status de aprovação (Aprovado, Rejeitado, Pendente)
            
        Returns:
            bool: True se o e-mail foi enviado com sucesso, False caso contrário
        """
        try:
            destinatario = parceiro.get('email')
            nome = parceiro.get('nome_completo', 'Parceiro')
            
            if status_aprovacao == 'Aprovado':
                assunto = "Parabéns! Sua inscrição como parceiro técnico foi aprovada"
                conteudo_html = f"""
                <html>
                <body>
                    <h2>Bem-vindo à nossa rede de parceiros técnicos!</h2>
                    <p>Olá {nome},</p>
                    <p>Temos o prazer de informar que sua inscrição como parceiro técnico foi <strong>aprovada</strong>!</p>
                    <p>Agora você faz parte oficialmente da nossa rede de parceiros técnicos.</p>
                    <p>Em breve entraremos em contato com mais informações.</p>
                    <p>Atenciosamente,<br>Equipe de Parceiros</p>
                </body>
                </html>
                """
            elif status_aprovacao == 'Rejeitado':
                assunto = "Informação sobre sua inscrição como parceiro técnico"
                conteudo_html = f"""
                <html>
                <body>
                    <h2>Resultado da sua inscrição</h2>
                    <p>Olá {nome},</p>
                    <p>Informamos que sua inscrição como parceiro técnico foi <strong>rejeitada</strong> neste momento.</p>
                    <p>Isso não impede que você faça uma nova inscrição futuramente com informações atualizadas.</p>
                    <p>Se tiver dúvidas, por favor entre em contato conosco.</p>
                    <p>Atenciosamente,<br>Equipe de Parceiros</p>
                </body>
                </html>
                """
            else:
                assunto = "Recebemos sua inscrição como parceiro técnico"
                conteudo_html = f"""
                <html>
                <body>
                    <h2>Inscrição recebida com sucesso!</h2>
                    <p>Olá {nome},</p>
                    <p>Recebemos sua inscrição como parceiro técnico e ela está em análise pela nossa equipe.</p>
                    <p>Em breve você receberá uma resposta sobre o status da sua inscrição.</p>
                    <p>Atenciosamente,<br>Equipe de Parceiros</p>
                </body>
                </html>
                """
                
            return self.enviar_email(destinatario, assunto, conteudo_html)
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação para parceiro: {str(e)}", exc_info=True)
            return False

# Instância global para uso em toda a aplicação
email_service = EmailService() 