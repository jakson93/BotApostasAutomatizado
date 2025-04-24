import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Adiciona o diretório raiz ao path para importação dos módulos
sys.path.append('/home/ubuntu/BotApostasAutomatizado')

# Importa os módulos a serem testados
from src.utils.config_manager import ConfigManager
from src.utils.bet_history_manager import BetHistoryManager
from src.telegram.telegram_bot import TelegramBot

class TestBotApostasAutomatizado(unittest.TestCase):
    
    def setUp(self):
        # Configuração inicial para os testes
        self.test_config_path = '/tmp/test_config.json'
        self.test_history_path = '/tmp/test_history.json'
        
        # Limpa arquivos de teste se existirem
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
        if os.path.exists(self.test_history_path):
            os.remove(self.test_history_path)
    
    def tearDown(self):
        # Limpeza após os testes
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
        if os.path.exists(self.test_history_path):
            os.remove(self.test_history_path)
    
    def test_config_manager(self):
        """Testa o gerenciador de configurações"""
        # Cria uma instância do ConfigManager com o arquivo de teste
        config_manager = ConfigManager(self.test_config_path)
        
        # Verifica se as configurações padrão foram carregadas
        telegram_config = config_manager.get_telegram_config()
        self.assertEqual(telegram_config['token'], '6156089370:AAFNQQFaTAMyJdyMa8YU5MTAefAqNbMf9Cw')
        self.assertEqual(telegram_config['chat_id'], '-1001534658039')
        
        # Testa a alteração e salvamento de configurações
        config_manager.set_telegram_config(
            token='test_token',
            chat_id='test_chat_id',
            notification_bet_id='test_bet_id',
            notification_error_id='test_error_id'
        )
        
        config_manager.set_betting_config(
            username='test_user',
            password='test_pass'
        )
        
        # Salva as configurações
        self.assertTrue(config_manager.save_config())
        
        # Cria uma nova instância para verificar se as configurações foram salvas
        new_config_manager = ConfigManager(self.test_config_path)
        new_telegram_config = new_config_manager.get_telegram_config()
        new_betting_config = new_config_manager.get_betting_config()
        
        # Verifica se as configurações foram carregadas corretamente
        self.assertEqual(new_telegram_config['token'], 'test_token')
        self.assertEqual(new_telegram_config['chat_id'], 'test_chat_id')
        self.assertEqual(new_telegram_config['notification_bet_id'], 'test_bet_id')
        self.assertEqual(new_telegram_config['notification_error_id'], 'test_error_id')
        self.assertEqual(new_betting_config['username'], 'test_user')
        self.assertEqual(new_betting_config['password'], 'test_pass')
    
    def test_bet_history_manager(self):
        """Testa o gerenciador de histórico de apostas"""
        # Cria uma instância do BetHistoryManager com o arquivo de teste
        history_manager = BetHistoryManager(self.test_history_path)
        
        # Verifica se o histórico inicial está vazio
        self.assertEqual(len(history_manager.get_history()), 0)
        
        # Adiciona algumas apostas de teste
        bet_data1 = {
            'race_name': 'Chelmsford City',
            'race_number': '4',
            'horse': 'Lovely Lucy',
            'odds': '4.50',
            'bet_type': 'E/W'
        }
        
        bet_data2 = {
            'race_name': 'Ascot',
            'race_number': '2',
            'horse': 'Thunder Strike',
            'odds': '2.75',
            'bet_type': 'Win'
        }
        
        # Adiciona as apostas ao histórico
        self.assertTrue(history_manager.add_bet(bet_data1, 'Sucesso'))
        self.assertTrue(history_manager.add_bet(bet_data2, 'Erro'))
        
        # Verifica se as apostas foram adicionadas
        history = history_manager.get_history()
        self.assertEqual(len(history), 2)
        
        # Verifica os dados das apostas
        self.assertEqual(history[0]['race_name'], 'Chelmsford City')
        self.assertEqual(history[0]['horse'], 'Lovely Lucy')
        self.assertEqual(history[0]['status'], 'Sucesso')
        
        self.assertEqual(history[1]['race_name'], 'Ascot')
        self.assertEqual(history[1]['horse'], 'Thunder Strike')
        self.assertEqual(history[1]['status'], 'Erro')
        
        # Testa os filtros
        filtered_history = history_manager.get_history(filter_race='Chelmsford')
        self.assertEqual(len(filtered_history), 1)
        self.assertEqual(filtered_history[0]['race_name'], 'Chelmsford City')
        
        filtered_history = history_manager.get_history(filter_horse='Thunder')
        self.assertEqual(len(filtered_history), 1)
        self.assertEqual(filtered_history[0]['horse'], 'Thunder Strike')
        
        filtered_history = history_manager.get_history(filter_status='Erro')
        self.assertEqual(len(filtered_history), 1)
        self.assertEqual(filtered_history[0]['status'], 'Erro')
        
        # Testa as estatísticas
        stats = history_manager.get_statistics()
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['success'], 1)
        self.assertEqual(stats['error'], 1)
        self.assertEqual(stats['success_rate'], 50.0)
    
    @patch('telegram.ext.Application')
    def test_telegram_bot_parse_message(self, mock_application):
        """Testa o parsing de mensagens do Telegram"""
        # Cria uma instância do TelegramBot com mocks
        bot = TelegramBot(
            token='test_token',
            chat_id='test_chat_id',
            message_callback=MagicMock(),
            error_callback=MagicMock()
        )
        
        # Testa o parsing de uma mensagem válida
        valid_message = """
        🏇 Nome da Corrida: Chelmsford City  
        📍 Número da Corrida: 4  
        🐎 Cavalo: Lovely Lucy  
        💸 Odds: @ 4.50  
        🎯 Tipo: E/W  
        """
        
        result = bot.parse_bet_message(valid_message)
        
        # Verifica se o parsing foi correto
        self.assertIsNotNone(result)
        self.assertEqual(result['race_name'], 'Chelmsford City')
        self.assertEqual(result['race_number'], '4')
        self.assertEqual(result['horse'], 'Lovely Lucy')
        self.assertEqual(result['odds'], '4.50')
        self.assertEqual(result['bet_type'], 'E/W')
        
        # Testa o parsing de uma mensagem inválida
        invalid_message = "Esta mensagem não contém dados de aposta"
        result = bot.parse_bet_message(invalid_message)
        
        # Verifica se o parsing retornou None para mensagem inválida
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
