import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

# Adiciona o diretório raiz ao path para importação dos módulos
sys.path.append('/home/ubuntu/BotApostasAutomatizado')

# Importa os módulos do projeto
from src.interface.main_window import MainWindow
from src.telegram.telegram_worker import TelegramWorker
from src.rpa.rpa_controller import RPAController
from src.utils.config_manager import ConfigManager
from src.utils.bet_history_manager import BetHistoryManager
from src.utils.notification_system import NotificationSystem
from src.interface.statistics_widget import StatisticsWidget

class DemoApp:
    """
    Aplicação de demonstração para o Bot de Apostas Automatizado.
    Simula o recebimento de mensagens do Telegram e o processamento de apostas.
    """
    def __init__(self):
        # Inicializa a aplicação PyQt
        self.app = QApplication(sys.argv)
        
        # Inicializa a interface gráfica
        self.main_window = MainWindow()
        
        # Adiciona o widget de estatísticas à aba de estatísticas
        self.stats_widget = StatisticsWidget()
        self.main_window.stats_tab.layout().addWidget(self.stats_widget)
        
        # Inicializa o sistema de notificações
        self.notification_system = NotificationSystem(self.main_window)
        
        # Inicializa os gerenciadores
        self.config_manager = ConfigManager()
        self.history_manager = BetHistoryManager()
        
        # Inicializa o controlador RPA
        self.rpa_controller = RPAController()
        
        # Conecta os sinais
        self.connect_signals()
        
        # Carrega as configurações e histórico
        self.load_config_to_ui()
        self.load_history_to_ui()
        
        # Configura o timer para simulação de mensagens
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.simulate_telegram_message)
        
        # Conecta os botões da interface
        self.main_window.start_button.clicked.connect(self.start_demo)
        self.main_window.stop_button.clicked.connect(self.stop_demo)
        self.main_window.show_browser_button.clicked.connect(self.show_browser)
        
        # Mensagem de boas-vindas
        self.main_window.telegram_log.append("Bem-vindo ao Bot de Apostas Automatizado!")
        self.main_window.telegram_log.append("Clique em 'Iniciar Automação' para começar a demonstração.")
        self.main_window.telegram_log.append("Esta versão de demonstração simula o recebimento de mensagens do Telegram.")
    
    def connect_signals(self):
        """Conecta os sinais da interface aos métodos do controlador."""
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
    
    def start_demo(self):
        """Inicia a demonstração."""
        # Atualiza a interface
        self.main_window.start_button.setEnabled(False)
        self.main_window.stop_button.setEnabled(True)
        self.main_window.statusBar().showMessage("Demonstração iniciada")
        self.main_window.telegram_log.append("Demonstração iniciada. Simulando recebimento de mensagens do Telegram...")
        
        # Inicia o timer para simulação de mensagens
        self.demo_timer.start(10000)  # Simula uma mensagem a cada 10 segundos
        
        # Mostra notificação
        self.notification_system.show_notification(
            "Bot de Apostas Automatizado",
            "Demonstração iniciada. Aguarde o recebimento de mensagens simuladas."
        )
    
    def stop_demo(self):
        """Para a demonstração."""
        # Para o timer
        self.demo_timer.stop()
        
        # Atualiza a interface
        self.main_window.start_button.setEnabled(True)
        self.main_window.stop_button.setEnabled(False)
        self.main_window.statusBar().showMessage("Demonstração parada")
        self.main_window.telegram_log.append("Demonstração parada.")
        
        # Mostra notificação
        self.notification_system.show_notification(
            "Bot de Apostas Automatizado",
            "Demonstração parada."
        )
    
    def show_browser(self):
        """Simula a abertura do navegador."""
        self.main_window.statusBar().showMessage("Abrindo navegador...")
        self.main_window.telegram_log.append("Navegador aberto para visualização.")
        
        # Simula a abertura do navegador
        QMessageBox.information(
            self.main_window,
            "Navegador",
            "Em uma implementação completa, esta ação abriria o navegador automatizado para visualização."
        )
    
    def test_telegram_connection(self):
        """Testa a conexão com o Telegram."""
        token = self.main_window.telegram_token.text()
        chat_id = self.main_window.telegram_chat_id.text()
        
        if not token or not chat_id:
            QMessageBox.warning(self.main_window, "Erro", "Token e Chat ID são obrigatórios.")
            return
        
        self.main_window.statusBar().showMessage("Testando conexão com o Telegram...")
        
        # Simula o teste de conexão
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
        
        # Simula o teste de conexão
        QMessageBox.information(self.main_window, "Sucesso", "Conexão com a Bolsa de Apostas estabelecida com sucesso!")
        self.main_window.statusBar().showMessage("Conexão com a Bolsa de Apostas testada com sucesso")
    
    def simulate_telegram_message(self):
        """Simula o recebimento de uma mensagem do Telegram."""
        # Lista de apostas simuladas
        sample_bets = [
            {
                'race_name': 'Chelmsford City',
                'race_number': '4',
                'horse': 'Lovely Lucy',
                'odds': '4.50',
                'bet_type': 'E/W'
            },
            {
                'race_name': 'Ascot',
                'race_number': '2',
                'horse': 'Thunder Strike',
                'odds': '2.75',
                'bet_type': 'Win'
            },
            {
                'race_name': 'Newmarket',
                'race_number': '5',
                'horse': 'Golden Arrow',
                'odds': '3.20',
                'bet_type': 'Place'
            },
            {
                'race_name': 'Doncaster',
                'race_number': '1',
                'horse': 'Silver Bullet',
                'odds': '6.00',
                'bet_type': 'E/W'
            }
        ]
        
        # Escolhe uma aposta aleatória
        import random
        bet_data = random.choice(sample_bets)
        
        # Formata a mensagem
        message = f"""
        🏇 Nome da Corrida: {bet_data['race_name']}  
        📍 Número da Corrida: {bet_data['race_number']}  
        🐎 Cavalo: {bet_data['horse']}  
        💸 Odds: @ {bet_data['odds']}  
        🎯 Tipo: {bet_data['bet_type']}  
        """
        
        # Adiciona a mensagem ao log
        self.main_window.telegram_log.append(f"Nova mensagem recebida do Telegram:")
        self.main_window.telegram_log.append(message)
        
        # Processa a aposta
        self.process_bet(bet_data)
        
        # Mostra notificação
        self.notification_system.show_bet_notification(bet_data, success=True)
    
    def process_bet(self, bet_data):
        """
        Processa uma aposta simulada.
        
        Args:
            bet_data (dict): Dados da aposta.
        """
        # Adiciona a aposta ao log
        log_message = f"Processando aposta: {bet_data['race_name']} - Corrida {bet_data['race_number']} - Cavalo: {bet_data['horse']}"
        self.main_window.telegram_log.append(log_message)
        
        # Simula o processamento da aposta
        self.main_window.telegram_log.append(f"Buscando corrida: {bet_data['race_name']} - Número {bet_data['race_number']}...")
        time.sleep(0.5)
        
        self.main_window.telegram_log.append(f"Buscando cavalo: {bet_data['horse']}...")
        time.sleep(0.5)
        
        self.main_window.telegram_log.append(f"Realizando aposta {bet_data['bet_type']} com odds {bet_data['odds']}...")
        time.sleep(0.5)
        
        # Simula sucesso ou erro aleatoriamente
        import random
        success = random.random() > 0.2  # 80% de chance de sucesso
        
        if success:
            status = "Sucesso"
            self.main_window.telegram_log.append("Aposta realizada com sucesso!")
        else:
            status = "Erro - Odds alteradas"
            self.main_window.telegram_log.append("Erro ao realizar aposta: Odds foram alteradas.")
            self.main_window.errors_log.append(f"Erro na aposta {bet_data['race_name']} - {bet_data['horse']}: Odds foram alteradas.")
        
        # Adiciona ao histórico
        self.history_manager.add_bet(bet_data, status)
        
        # Atualiza a interface
        self.load_history_to_ui()
        
        # Atualiza as estatísticas
        self.stats_widget.update_statistics()
    
    def run(self):
        """Executa a aplicação."""
        self.main_window.show()
        return self.app.exec_()


if __name__ == "__main__":
    demo = DemoApp()
    sys.exit(demo.run())
