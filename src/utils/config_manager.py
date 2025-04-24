import os
import json
from datetime import datetime

class ConfigManager:
    """
    Gerenciador de configurações para o Bot de Apostas Automatizado.
    Responsável por salvar e carregar configurações do sistema.
    """
    def __init__(self, config_file_path=None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_file_path (str, optional): Caminho para o arquivo de configurações.
                Se não for fornecido, será usado o caminho padrão.
        """
        if config_file_path is None:
            # Define o caminho padrão para o arquivo de configurações
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.config_file_path = os.path.join(base_dir, 'config.json')
        else:
            self.config_file_path = config_file_path
        
        # Configurações padrão
        self.default_config = {
            'telegram': {
                'token': '6156089370:AAFNQQFaTAMyJdyMa8YU5MTAefAqNbMf9Cw',
                'chat_id': '-1001534658039',
                'notification_bet_id': '',
                'notification_error_id': ''
            },
            'betting': {
                'username': '',
                'password': ''
            },
            'app': {
                'auto_start': False,
                'show_browser': False,
                'first_run': True
            }
        }
        
        # Carrega as configurações
        self.config = self.load_config()
    
    def load_config(self):
        """
        Carrega as configurações do arquivo.
        
        Returns:
            dict: Configurações carregadas ou configurações padrão se o arquivo não existir.
        """
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as f:
                    return json.load(f)
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"Erro ao carregar configurações: {str(e)}")
            return self.default_config.copy()
    
    def save_config(self):
        """
        Salva as configurações no arquivo.
        
        Returns:
            bool: True se as configurações foram salvas com sucesso, False caso contrário.
        """
        try:
            with open(self.config_file_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {str(e)}")
            return False
    
    def get_telegram_config(self):
        """
        Obtém as configurações do Telegram.
        
        Returns:
            dict: Configurações do Telegram.
        """
        return self.config['telegram']
    
    def set_telegram_config(self, token, chat_id, notification_bet_id='', notification_error_id=''):
        """
        Define as configurações do Telegram.
        
        Args:
            token (str): Token do bot do Telegram.
            chat_id (str): ID do chat a ser monitorado.
            notification_bet_id (str, optional): ID para notificações de apostas.
            notification_error_id (str, optional): ID para notificações de erros.
        """
        self.config['telegram']['token'] = token
        self.config['telegram']['chat_id'] = chat_id
        self.config['telegram']['notification_bet_id'] = notification_bet_id
        self.config['telegram']['notification_error_id'] = notification_error_id
    
    def get_betting_config(self):
        """
        Obtém as configurações da Bolsa de Apostas.
        
        Returns:
            dict: Configurações da Bolsa de Apostas.
        """
        return self.config['betting']
    
    def set_betting_config(self, username, password):
        """
        Define as configurações da Bolsa de Apostas.
        
        Args:
            username (str): Nome de usuário para login.
            password (str): Senha para login.
        """
        self.config['betting']['username'] = username
        self.config['betting']['password'] = password
    
    def get_app_config(self):
        """
        Obtém as configurações da aplicação.
        
        Returns:
            dict: Configurações da aplicação.
        """
        return self.config['app']
    
    def set_app_config(self, auto_start=None, show_browser=None, first_run=None):
        """
        Define as configurações da aplicação.
        
        Args:
            auto_start (bool, optional): Se a automação deve iniciar automaticamente.
            show_browser (bool, optional): Se o navegador deve ser mostrado.
            first_run (bool, optional): Se é a primeira execução da aplicação.
        """
        if auto_start is not None:
            self.config['app']['auto_start'] = auto_start
        
        if show_browser is not None:
            self.config['app']['show_browser'] = show_browser
        
        if first_run is not None:
            self.config['app']['first_run'] = first_run
    
    def reset_to_default(self):
        """
        Redefine as configurações para os valores padrão.
        
        Returns:
            bool: True se as configurações foram redefinidas com sucesso, False caso contrário.
        """
        try:
            self.config = self.default_config.copy()
            return self.save_config()
        except Exception as e:
            print(f"Erro ao redefinir configurações: {str(e)}")
            return False
