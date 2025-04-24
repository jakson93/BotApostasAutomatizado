import asyncio
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from datetime import datetime

# Importa os módulos do projeto
sys.path.append('/home/ubuntu/BotApostasAutomatizado')
from src.telegram.telegram_bot import TelegramBot

class TelegramWorker(QThread):
    """
    Worker thread para executar o bot do Telegram em segundo plano.
    """
    message_received = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    error_message = pyqtSignal(str)
    
    def __init__(self, token, chat_id):
        super().__init__()
        self.token = token
        self.chat_id = chat_id
        self.running = False
        self.bot = None
        
    def message_callback(self, bet_data):
        """Callback para mensagens recebidas do Telegram."""
        self.message_received.emit(bet_data)
        self.log_message.emit(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Nova aposta recebida: {bet_data['race_name']} - {bet_data['horse']}")
    
    def error_callback(self, error_message):
        """Callback para erros do Telegram."""
        self.error_message.emit(error_message)
    
    async def run_bot(self):
        """Executa o bot do Telegram."""
        self.bot = TelegramBot(
            token=self.token,
            chat_id=self.chat_id,
            message_callback=self.message_callback,
            error_callback=self.error_callback
        )
        
        self.log_message.emit("Iniciando bot do Telegram...")
        success = await self.bot.start()
        
        if success:
            self.log_message.emit("Bot do Telegram iniciado com sucesso!")
            
            # Mantém o bot em execução até que a flag running seja False
            while self.running:
                await asyncio.sleep(1)
            
            # Para o bot quando a flag running for False
            await self.bot.stop()
            self.log_message.emit("Bot do Telegram parado.")
        else:
            self.error_message.emit("Falha ao iniciar o bot do Telegram.")
    
    def run(self):
        """Método executado quando o thread é iniciado."""
        self.running = True
        asyncio.run(self.run_bot())
    
    def stop(self):
        """Para o bot do Telegram."""
        self.running = False
        
    async def send_notification(self, message):
        """Envia uma notificação pelo Telegram."""
        if self.bot and self.bot.is_running():
            success = await self.bot.send_notification(message)
            if success:
                self.log_message.emit(f"Notificação enviada: {message}")
            else:
                self.error_message.emit(f"Falha ao enviar notificação: {message}")
            return success
        else:
            self.error_message.emit("Bot não está em execução. Não foi possível enviar notificação.")
            return False
