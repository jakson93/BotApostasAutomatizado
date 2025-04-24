import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, 
                            QStyle, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

# Importa os módulos do projeto
sys.path.append('/home/ubuntu/BotApostasAutomatizado')
from src.utils.config_manager import ConfigManager

class NotificationSystem:
    """
    Sistema de notificações para o Bot de Apostas Automatizado.
    Implementa notificações via toast (notificações do sistema) e ícone na bandeja do sistema.
    """
    def __init__(self, parent=None):
        self.parent = parent
        self.config_manager = ConfigManager()
        
        # Verifica se o sistema suporta notificações na bandeja
        self.tray_supported = QSystemTrayIcon.isSystemTrayAvailable()
        self.tray_icon = None
        
        if self.tray_supported:
            self.setup_tray_icon()
    
    def setup_tray_icon(self):
        """Configura o ícone na bandeja do sistema."""
        self.tray_icon = QSystemTrayIcon(self.parent)
        
        # Usa um ícone padrão do sistema
        icon = self.parent.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Cria o menu de contexto
        tray_menu = QMenu()
        
        # Ação para mostrar/esconder a janela principal
        show_action = QAction("Mostrar", self.parent)
        show_action.triggered.connect(self.parent.show)
        tray_menu.addAction(show_action)
        
        # Ação para iniciar/parar a automação
        self.start_stop_action = QAction("Iniciar Automação", self.parent)
        self.start_stop_action.triggered.connect(self.toggle_automation)
        tray_menu.addAction(self.start_stop_action)
        
        # Separador
        tray_menu.addSeparator()
        
        # Ação para sair
        quit_action = QAction("Sair", self.parent)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        # Define o menu de contexto
        self.tray_icon.setContextMenu(tray_menu)
        
        # Conecta o sinal de clique no ícone
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Mostra o ícone na bandeja
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """
        Manipula a ativação do ícone na bandeja.
        
        Args:
            reason (QSystemTrayIcon.ActivationReason): Razão da ativação.
        """
        if reason == QSystemTrayIcon.DoubleClick:
            # Mostra ou esconde a janela principal ao clicar duas vezes no ícone
            if self.parent.isVisible():
                self.parent.hide()
            else:
                self.parent.show()
    
    def toggle_automation(self):
        """Alterna entre iniciar e parar a automação."""
        if self.start_stop_action.text() == "Iniciar Automação":
            # Inicia a automação
            self.parent.start_automation()
            self.start_stop_action.setText("Parar Automação")
        else:
            # Para a automação
            self.parent.stop_automation()
            self.start_stop_action.setText("Iniciar Automação")
    
    def update_automation_status(self, running):
        """
        Atualiza o status da automação no menu de contexto.
        
        Args:
            running (bool): Se a automação está em execução.
        """
        if self.tray_supported and self.tray_icon:
            if running:
                self.start_stop_action.setText("Parar Automação")
            else:
                self.start_stop_action.setText("Iniciar Automação")
    
    def show_notification(self, title, message, icon_type=QSystemTrayIcon.Information):
        """
        Mostra uma notificação toast.
        
        Args:
            title (str): Título da notificação.
            message (str): Mensagem da notificação.
            icon_type (QSystemTrayIcon.MessageIcon): Tipo de ícone da notificação.
        """
        if self.tray_supported and self.tray_icon:
            self.tray_icon.showMessage(title, message, icon_type)
    
    def show_bet_notification(self, bet_data, success=True):
        """
        Mostra uma notificação de aposta.
        
        Args:
            bet_data (dict): Dados da aposta.
            success (bool): Se a aposta foi realizada com sucesso.
        """
        title = "Aposta Realizada" if success else "Erro na Aposta"
        message = f"{bet_data['race_name']} - Corrida {bet_data['race_number']} - Cavalo: {bet_data['horse']}"
        icon_type = QSystemTrayIcon.Information if success else QSystemTrayIcon.Warning
        
        self.show_notification(title, message, icon_type)
    
    def minimize_to_tray(self):
        """Minimiza a aplicação para a bandeja do sistema."""
        if self.tray_supported and self.tray_icon:
            self.parent.hide()
            
            # Mostra uma notificação informando que a aplicação continua em execução
            self.show_notification(
                "Bot de Apostas Automatizado",
                "A aplicação continua em execução na bandeja do sistema."
            )
            
            return True
        else:
            return False
