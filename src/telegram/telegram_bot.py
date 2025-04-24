import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

class TelegramBot:
    def __init__(self, token, chat_id, message_callback=None, error_callback=None):
        """
        Inicializa o bot do Telegram.
        
        Args:
            token (str): Token do bot do Telegram
            chat_id (str): ID do chat a ser monitorado
            message_callback (callable): Função de callback para mensagens recebidas
            error_callback (callable): Função de callback para erros
        """
        self.token = token
        self.chat_id = chat_id
        self.message_callback = message_callback
        self.error_callback = error_callback
        self.application = None
        self.running = False
        
        # Configuração de logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
    
    async def start_command(self, update: Update, context: CallbackContext) -> None:
        """Envia mensagem quando o comando /start é emitido."""
        await update.message.reply_text('Bot de Apostas Automatizado iniciado!')
    
    async def help_command(self, update: Update, context: CallbackContext) -> None:
        """Envia mensagem quando o comando /help é emitido."""
        await update.message.reply_text('Envie mensagens no formato de apostas para processamento automático.')
    
    async def handle_message(self, update: Update, context: CallbackContext) -> None:
        """Processa mensagens recebidas."""
        # Verifica se a mensagem veio do chat monitorado
        if str(update.effective_chat.id) != self.chat_id:
            return
        
        message_text = update.message.text
        
        # Verifica se a mensagem tem o formato esperado de aposta
        if "Nome da Corrida:" in message_text and "Cavalo:" in message_text:
            bet_data = self.parse_bet_message(message_text)
            
            if bet_data and self.message_callback:
                self.message_callback(bet_data)
                
            await update.message.reply_text('Aposta recebida e processada!')
    
    def parse_bet_message(self, message_text):
        """
        Analisa a mensagem de aposta e extrai os dados relevantes.
        
        Args:
            message_text (str): Texto da mensagem
            
        Returns:
            dict: Dicionário com os dados da aposta ou None se o formato for inválido
        """
        try:
            # Inicializa o dicionário de dados da aposta
            bet_data = {}
            
            # Extrai o nome da corrida
            if "Nome da Corrida:" in message_text:
                race_name_line = message_text.split("Nome da Corrida:")[1].split("\n")[0].strip()
                bet_data["race_name"] = race_name_line
            
            # Extrai o número da corrida
            if "Número da Corrida:" in message_text:
                race_number_line = message_text.split("Número da Corrida:")[1].split("\n")[0].strip()
                bet_data["race_number"] = race_number_line
            
            # Extrai o nome do cavalo
            if "Cavalo:" in message_text:
                horse_line = message_text.split("Cavalo:")[1].split("\n")[0].strip()
                bet_data["horse"] = horse_line
            
            # Extrai as odds
            if "Odds:" in message_text:
                odds_line = message_text.split("Odds:")[1].split("\n")[0].strip()
                # Remove o @ se existir
                odds_value = odds_line.replace("@", "").strip()
                bet_data["odds"] = odds_value
            
            # Extrai o tipo de aposta
            if "Tipo:" in message_text:
                bet_type_line = message_text.split("Tipo:")[1].split("\n")[0].strip()
                bet_data["bet_type"] = bet_type_line
            
            # Verifica se todos os campos necessários foram extraídos
            required_fields = ["race_name", "race_number", "horse", "odds", "bet_type"]
            if all(field in bet_data for field in required_fields):
                return bet_data
            else:
                return None
        
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Erro ao analisar mensagem: {str(e)}")
            return None
    
    async def send_notification(self, message):
        """
        Envia uma notificação para o chat monitorado.
        
        Args:
            message (str): Mensagem a ser enviada
        """
        if self.application:
            try:
                await self.application.bot.send_message(chat_id=self.chat_id, text=message)
                return True
            except Exception as e:
                if self.error_callback:
                    self.error_callback(f"Erro ao enviar notificação: {str(e)}")
                return False
        return False
    
    async def error_handler(self, update: Update, context: CallbackContext) -> None:
        """Lida com erros do Telegram."""
        error_message = f"Erro: {context.error}"
        self.logger.error(error_message)
        
        if self.error_callback:
            self.error_callback(error_message)
    
    async def start(self):
        """Inicia o bot do Telegram."""
        if self.running:
            return False
        
        try:
            # Cria a aplicação
            self.application = Application.builder().token(self.token).build()
            
            # Adiciona handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Adiciona handler de erro
            self.application.add_error_handler(self.error_handler)
            
            # Inicia o polling
            self.running = True
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            return True
        
        except Exception as e:
            error_message = f"Erro ao iniciar o bot: {str(e)}"
            self.logger.error(error_message)
            
            if self.error_callback:
                self.error_callback(error_message)
            
            self.running = False
            return False
    
    async def stop(self):
        """Para o bot do Telegram."""
        if not self.running or not self.application:
            return True
        
        try:
            # Para o polling e a aplicação
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            
            self.running = False
            return True
        
        except Exception as e:
            error_message = f"Erro ao parar o bot: {str(e)}"
            self.logger.error(error_message)
            
            if self.error_callback:
                self.error_callback(error_message)
            
            return False
    
    def is_running(self):
        """Retorna se o bot está em execução."""
        return self.running
