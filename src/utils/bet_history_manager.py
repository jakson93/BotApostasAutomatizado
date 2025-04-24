import os
import json
from datetime import datetime

class BetHistoryManager:
    """
    Gerenciador de histórico de apostas para o Bot de Apostas Automatizado.
    Responsável por salvar e carregar o histórico de apostas realizadas.
    """
    def __init__(self, history_file_path=None):
        """
        Inicializa o gerenciador de histórico.
        
        Args:
            history_file_path (str, optional): Caminho para o arquivo de histórico.
                Se não for fornecido, será usado o caminho padrão.
        """
        if history_file_path is None:
            # Define o caminho padrão para o arquivo de histórico
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.history_file_path = os.path.join(base_dir, 'bet_history.json')
        else:
            self.history_file_path = history_file_path
        
        # Carrega o histórico
        self.history = self.load_history()
    
    def load_history(self):
        """
        Carrega o histórico do arquivo.
        
        Returns:
            list: Histórico carregado ou lista vazia se o arquivo não existir.
        """
        try:
            if os.path.exists(self.history_file_path):
                with open(self.history_file_path, 'r') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"Erro ao carregar histórico: {str(e)}")
            return []
    
    def save_history(self):
        """
        Salva o histórico no arquivo.
        
        Returns:
            bool: True se o histórico foi salvo com sucesso, False caso contrário.
        """
        try:
            with open(self.history_file_path, 'w') as f:
                json.dump(self.history, f, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar histórico: {str(e)}")
            return False
    
    def add_bet(self, bet_data, status):
        """
        Adiciona uma aposta ao histórico.
        
        Args:
            bet_data (dict): Dados da aposta.
            status (str): Status da aposta (Sucesso, Erro, etc.).
            
        Returns:
            bool: True se a aposta foi adicionada com sucesso, False caso contrário.
        """
        try:
            # Cria o registro da aposta
            bet_record = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'race_name': bet_data.get('race_name', ''),
                'race_number': bet_data.get('race_number', ''),
                'horse': bet_data.get('horse', ''),
                'odds': bet_data.get('odds', ''),
                'bet_type': bet_data.get('bet_type', ''),
                'status': status
            }
            
            # Adiciona ao histórico
            self.history.append(bet_record)
            
            # Salva o histórico
            return self.save_history()
        except Exception as e:
            print(f"Erro ao adicionar aposta ao histórico: {str(e)}")
            return False
    
    def get_history(self, limit=None, filter_race=None, filter_horse=None, filter_status=None):
        """
        Obtém o histórico de apostas com opções de filtragem.
        
        Args:
            limit (int, optional): Limite de registros a serem retornados.
            filter_race (str, optional): Filtro por nome da corrida.
            filter_horse (str, optional): Filtro por nome do cavalo.
            filter_status (str, optional): Filtro por status da aposta.
            
        Returns:
            list: Histórico filtrado.
        """
        # Aplica os filtros
        filtered_history = self.history
        
        if filter_race:
            filtered_history = [bet for bet in filtered_history if filter_race.lower() in bet['race_name'].lower()]
        
        if filter_horse:
            filtered_history = [bet for bet in filtered_history if filter_horse.lower() in bet['horse'].lower()]
        
        if filter_status:
            filtered_history = [bet for bet in filtered_history if filter_status.lower() in bet['status'].lower()]
        
        # Ordena por timestamp (mais recente primeiro)
        filtered_history = sorted(filtered_history, key=lambda x: x['timestamp'], reverse=True)
        
        # Aplica o limite
        if limit and isinstance(limit, int) and limit > 0:
            filtered_history = filtered_history[:limit]
        
        return filtered_history
    
    def get_statistics(self):
        """
        Calcula estatísticas sobre as apostas realizadas.
        
        Returns:
            dict: Estatísticas das apostas.
        """
        try:
            # Inicializa as estatísticas
            stats = {
                'total': len(self.history),
                'success': 0,
                'error': 0,
                'today': 0,
                'this_week': 0,
                'this_month': 0
            }
            
            # Data atual
            now = datetime.now()
            today = now.strftime('%Y-%m-%d')
            
            # Calcula as estatísticas
            for bet in self.history:
                # Contagem por status
                if 'Sucesso' in bet['status']:
                    stats['success'] += 1
                elif 'Erro' in bet['status']:
                    stats['error'] += 1
                
                # Contagem por período
                bet_date = bet['timestamp'].split(' ')[0]  # Extrai apenas a data
                if bet_date == today:
                    stats['today'] += 1
                
                # Verifica se está na semana atual (simplificado)
                bet_datetime = datetime.strptime(bet['timestamp'], '%Y-%m-%d %H:%M:%S')
                days_diff = (now - bet_datetime).days
                
                if days_diff < 7:
                    stats['this_week'] += 1
                
                if days_diff < 30:
                    stats['this_month'] += 1
            
            # Calcula a taxa de sucesso
            if stats['total'] > 0:
                stats['success_rate'] = round((stats['success'] / stats['total']) * 100, 2)
            else:
                stats['success_rate'] = 0
            
            return stats
        except Exception as e:
            print(f"Erro ao calcular estatísticas: {str(e)}")
            return {
                'total': 0,
                'success': 0,
                'error': 0,
                'today': 0,
                'this_week': 0,
                'this_month': 0,
                'success_rate': 0
            }
    
    def clear_history(self):
        """
        Limpa todo o histórico de apostas.
        
        Returns:
            bool: True se o histórico foi limpo com sucesso, False caso contrário.
        """
        try:
            self.history = []
            return self.save_history()
        except Exception as e:
            print(f"Erro ao limpar histórico: {str(e)}")
            return False
