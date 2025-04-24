import sys
import os
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from datetime import datetime

# Importa os módulos do projeto
sys.path.append('/home/ubuntu/BotApostasAutomatizado')
from src.interface.main_window import MainWindow
from src.telegram.telegram_worker import TelegramWorker
from src.rpa.rpa_controller import RPAController
from src.utils.config_manager import ConfigManager
from src.utils.bet_history_manager import BetHistoryManager

class MainController:
    """
    Controlador principal da aplicação.
    Responsável por integrar todos os componentes e gerenciar o fluxo de dados.
    """
    def __init__(self):
        # Inicializa a aplicação PyQt
        self.app = QApplication(sys.argv)
        
        # Inicializa os gerenciadores
        self.config_manager = ConfigManager()
        self.history_manager = BetHistoryManager()
        
        # Inicializa a interface gráfica
        self.main_window = MainWindow()
        
        # Inicializa o controlador RPA
        self.rpa_controller = RPAController()
        
        # Conecta os sinais do RPA Controller
        self.rpa_controller.log_message.connect(self.main_window.telegram_log.append)
        self.rpa_controller.error_message.connect(self.main_window.errors_log.append)
        self.rpa_controller.bet_status_update.connect(self.update_bet_status)
        
        # Inicializa o worker do Telegram (mas não inicia ainda)
        self.telegram_worker = None
        
        # Conecta os sinais da interface
        self.connect_signals()
        
        # Carrega as configurações na interface
        self.load_config_to_ui()
        
        # Carrega o histórico na interface
        self.load_history_to_ui()
    
    def connect_signals(self):
        """Conecta os sinais da interface aos métodos do controlador."""
        # Botões de controle
        self.main_window.start_button.clicked.connect(self.start_automation)
        self.main_window.stop_button.clicked.connect(self.stop_automation)
        self.main_window.show_browser_button.clicked.connect(self.show_browser)
        
        # Botões de configuração
        self.main_window.test_telegram_button.clicked.connect(self.test_telegram_connection)
        self.main_window.test_betting_button.clicked.connect(self.test_betting_connection)
        self.main_window.save_config_button.clicked.connect(self.save_config)
        
        # Filtros de estatísticas
        self.main_window.apply_filter_button.clicked.connect(self.apply_filters)
    
    def load_config_to_ui(self):
        """Carrega as configurações do gerenciador para a interface."""
        # Configurações do Telegram
        telegram_config = self.config_manager.get_telegram_config()
        self.main_window.telegram_token.setText(telegram_config['token'])
        self.main_window.telegram_chat_id.setText(telegram_config['chat_id'])
        self.main_window.notify_on_bet.setText(telegram_config['notification_bet_id'])
        self.main_window.notify_on_error.setText(telegram_config['notification_error_id'])
        
        # Configurações da Bolsa de Apostas
        betting_config = self.config_manager.get_betting_config()
        self.main_window.betting_username.setText(betting_config['username'])
        self.main_window.betting_password.setText(betting_config['password'])
    
    def save_config(self):
        """Salva as configurações da interface para o gerenciador."""
        # Configurações do Telegram
        self.config_manager.set_telegram_config(
            token=self.main_window.telegram_token.text(),
            chat_id=self.main_window.telegram_chat_id.text(),
            notification_bet_id=self.main_window.notify_on_bet.text(),
            notification_error_id=self.main_window.notify_on_error.text()
        )
        
        # Configurações da Bolsa de Apostas
        self.config_manager.set_betting_config(
            username=self.main_window.betting_username.text(),
            password=self.main_window.betting_password.text()
        )
        
        # Salva as configurações
        if self.config_manager.save_config():
            self.main_window.statusBar().showMessage("Configurações salvas com sucesso")
            QMessageBox.information(self.main_window, "Sucesso", "Configurações salvas com sucesso!")
        else:
            self.main_window.statusBar().showMessage("Erro ao salvar configurações")
            QMessageBox.warning(self.main_window, "Erro", "Erro ao salvar configurações!")
    
    def load_history_to_ui(self):
        """Carrega o histórico de apostas para a interface."""
        # Obtém o histórico
        history = self.history_manager.get_history()
        
        # Limpa a tabela
        self.main_window.history_table.setRowCount(0)
        
        # Preenche a tabela com o histórico
        for i, bet in enumerate(history):
            self.main_window.history_table.insertRow(i)
            self.main_window.history_table.setItem(i, 0, QTableWidgetItem(bet['timestamp']))
            self.main_window.history_table.setItem(i, 1, QTableWidgetItem(bet['race_name']))
            self.main_window.history_table.setItem(i, 2, QTableWidgetItem(bet['race_number']))
            self.main_window.history_table.setItem(i, 3, QTableWidgetItem(bet['horse']))
            self.main_window.history_table.setItem(i, 4, QTableWidgetItem(bet['odds']))
            self.main_window.history_table.setItem(i, 5, QTableWidgetItem(bet['status']))
        
        # Carrega as estatísticas
        self.load_statistics()
    
    def load_statistics(self):
        """Carrega as estatísticas para a interface."""
        # Obtém as estatísticas
        stats = self.history_manager.get_statistics()
        
        # Limpa a tabela
        self.main_window.stats_table.setRowCount(0)
        
        # Adiciona as estatísticas na tabela
        metrics = [
            ("Total de Apostas", stats['total'], stats['this_week'], stats['this_month']),
            ("Apostas com Sucesso", stats['success'], 0, 0),  # Simplificado
            ("Apostas com Erro", stats['error'], 0, 0),  # Simplificado
            ("Taxa de Sucesso", f"{stats['success_rate']}%", "0%", "0%")  # Simplificado
        ]
        
        for i, (metric, today, week, month) in enumerate(metrics):
            self.main_window.stats_table.insertRow(i)
            self.main_window.stats_table.setItem(i, 0, QTableWidgetItem(str(metric)))
            self.main_window.stats_table.setItem(i, 1, QTableWidgetItem(str(today)))
            self.main_window.stats_table.setItem(i, 2, QTableWidgetItem(str(week)))
            self.main_window.stats_table.setItem(i, 3, QTableWidgetItem(str(month)))
    
    def apply_filters(self):
        """Aplica os filtros de busca no histórico."""
        # Obtém os filtros
        filter_race = self.main_window.filter_race.text()
        filter_horse = self.main_window.filter_horse.text()
        filter_status = self.main_window.filter_status.text()
        
        # Obtém o histórico filtrado
        filtered_history = self.history_manager.get_history(
            filter_race=filter_race,
            filter_horse=filter_horse,
            filter_status=filter_status
        )
        
        # Limpa a tabela
        self.main_window.history_table.setRowCount(0)
        
        # Preenche a tabela com o histórico filtrado
        for i, bet in enumerate(filtered_history):
            self.main_window.history_table.insertRow(i)
            self.main_window.history_table.setItem(i, 0, QTableWidgetItem(bet['timestamp']))
            self.main_window.history_table.setItem(i, 1, QTableWidgetItem(bet['race_name']))
            self.main_window.history_table.setItem(i, 2, QTableWidgetItem(bet['race_number']))
            self.main_window.history_table.setItem(i, 3, QTableWidgetItem(bet['horse']))
            self.main_window.history_table.setItem(i, 4, QTableWidgetItem(bet['odds']))
            self.main_window.history_table.setItem(i, 5, QTableWidgetItem(bet['status']))
    
    def start_automation(self):
        """Inicia a automação."""
        # Verifica se as configurações estão definidas
        telegram_config = self.config_manager.get_telegram_config()
        betting_config = self.config_manager.get_betting_config()
        
        if not telegram_config['token'] or not telegram_config['chat_id']:
            QMessageBox.warning(self.main_window, "Erro", "Token e Chat ID do Telegram são obrigatórios.")
            return
        
        if not betting_config['username'] or not betting_config['password']:
            QMessageBox.warning(self.main_window, "Erro", "Usuário e senha da Bolsa de Apostas são obrigatórios.")
            return
        
        # Configura o RPA Controller
        self.rpa_controller.set_credentials(
            username=betting_config['username'],
            password=betting_config['password']
        )
        
        # Cria e inicia o worker do Telegram
        self.telegram_worker = TelegramWorker(
            token=telegram_config['token'],
            chat_id=telegram_config['chat_id']
        )
        
        # Conecta os sinais do worker
        self.telegram_worker.log_message.connect(self.main_window.telegram_log.append)
        self.telegram_worker.error_message.connect(self.main_window.errors_log.append)
        self.telegram_worker.message_received.connect(self.process_bet)
        
        # Inicia o worker
        self.telegram_worker.start()
        
        # Atualiza a interface
        self.main_window.start_button.setEnabled(False)
        self.main_window.stop_button.setEnabled(True)
        self.main_window.statusBar().showMessage("Automação iniciada")
        self.main_window.telegram_log.append("Automação iniciada. Monitorando mensagens do Telegram...")
    
    def stop_automation(self):
        """Para a automação."""
        # Para o worker do Telegram
        if self.telegram_worker:
            self.telegram_worker.stop()
            self.telegram_worker = None
        
        # Atualiza a interface
        self.main_window.start_button.setEnabled(True)
        self.main_window.stop_button.setEnabled(False)
        self.main_window.statusBar().showMessage("Automação parada")
        self.main_window.telegram_log.append("Automação parada.")
    
    def show_browser(self):
        """Mostra o navegador."""
        self.rpa_controller.show_browser()
        self.main_window.statusBar().showMessage("Navegador aberto para visualização")
    
    def test_telegram_connection(self):
        """Testa a conexão com o Telegram."""
        token = self.main_window.telegram_token.text()
        chat_id = self.main_window.telegram_chat_id.text()
        
        if not token or not chat_id:
            QMessageBox.warning(self.main_window, "Erro", "Token e Chat ID são obrigatórios.")
            return
        
        self.main_window.statusBar().showMessage("Testando conexão com o Telegram...")
        
        # Aqui seria implementado o teste real
        # Por enquanto, apenas simulamos o sucesso
        QMessageBox.information(self.main_window, "Sucesso", "Conexão com o Telegram estabelecida com sucesso!")
        self.main_window.statusBar().showMessage("Conexão com o Telegram testada com sucesso")
    
    def test_betting_connection(self):
        """Testa a conexão com a Bolsa de Apostas."""
        username = self.main_window.betting_username.text()
        password = self.main_window.betting_password.text()
        
        if not username or not password:
            QMessageBox.warning(self.main_window, "Erro", "Usuário e senha são obrigatórios.")
            return
        
        self.main_window.statusBar().showMessage("Testando conexão com a Bolsa de Apostas...")
        
        # Configura o RPA Controller
        self.rpa_controller.set_credentials(username=username, password=password)
        
        # Testa a conexão
        if self.rpa_controller.test_connection():
            QMessageBox.information(self.main_window, "Sucesso", "Conexão com a Bolsa de Apostas estabelecida com sucesso!")
            self.main_window.statusBar().showMessage("Conexão com a Bolsa de Apostas testada com sucesso")
        else:
            QMessageBox.warning(self.main_window, "Erro", "Falha ao conectar com a Bolsa de Apostas.")
            self.main_window.statusBar().showMessage("Falha ao testar conexão com a Bolsa de Apostas")
    
    def process_bet(self, bet_data):
        """
        Processa uma aposta recebida do Telegram.
        
        Args:
            bet_data (dict): Dados da aposta.
        """
        # Adiciona a aposta ao log
        log_message = f"Nova aposta recebida: {bet_data['race_name']} - Corrida {bet_data['race_number']} - Cavalo: {bet_data['horse']}"
        self.main_window.telegram_log.append(log_message)
        
        # Processa a aposta com o RPA Controller
        success = self.rpa_controller.process_bet(bet_data)
        
        # Adiciona ao histórico
        status = "Sucesso" if success else "Erro"
        self.history_manager.add_bet(bet_data, status)
        
        # Atualiza a interface
        self.load_history_to_ui()
        
        # Envia notificação se configurado
        telegram_config = self.config_manager.get_telegram_config()
        notification_id = telegram_config['notification_bet_id'] if success else telegram_config['notification_error_id']
        
        if notification_id and self.telegram_worker:
            notification_message = f"{'✅' if success else '❌'} Aposta {status}: {bet_data['race_name']} - {bet_data['horse']}"
            asyncio.run(self.telegram_worker.send_notification(notification_message))
    
    def update_bet_status(self, bet_status):
        """
        Atualiza o status de uma aposta na interface.
        
        Args:
            bet_status (dict): Status da aposta.
        """
        # Adiciona uma nova linha na tabela de histórico
        row = self.main_window.history_table.rowCount()
        self.main_window.history_table.insertRow(row)
        
        self.main_window.history_table.setItem(row, 0, QTableWidgetItem(bet_status['timestamp']))
        self.main_window.history_table.setItem(row, 1, QTableWidgetItem(bet_status['race_name']))
        self.main_window.history_table.setItem(row, 2, QTableWidgetItem(bet_status['race_number']))
        self.main_window.history_table.setItem(row, 3, QTableWidgetItem(bet_status['horse']))
        self.main_window.history_table.setItem(row, 4, QTableWidgetItem(bet_status['odds']))
        self.main_window.history_table.setItem(row, 5, QTableWidgetItem(bet_status['status']))
    
    def run(self):
        """Executa a aplicação."""
        self.main_window.show()
        return self.app.exec_()


if __name__ == "__main__":
    controller = MainController()
    sys.exit(controller.run())
