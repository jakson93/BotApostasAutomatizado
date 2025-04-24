import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QComboBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

# Importa os módulos do projeto
sys.path.append('/home/ubuntu/BotApostasAutomatizado')
from src.utils.bet_history_manager import BetHistoryManager

class StatisticsWidget(QWidget):
    """
    Widget avançado para exibição de estatísticas e gráficos.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_manager = BetHistoryManager()
        self.setup_ui()
        
        # Timer para atualização automática
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_statistics)
        self.update_timer.start(30000)  # Atualiza a cada 30 segundos
    
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Painel Estatístico Avançado")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Controles de período
        period_layout = QHBoxLayout()
        period_label = QLabel("Período:")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Todos"])
        self.period_combo.setCurrentIndex(3)  # "Todos" por padrão
        self.period_combo.currentIndexChanged.connect(self.update_statistics)
        
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_combo)
        period_layout.addStretch()
        
        refresh_button = QPushButton("Atualizar")
        refresh_button.clicked.connect(self.update_statistics)
        period_layout.addWidget(refresh_button)
        
        main_layout.addLayout(period_layout)
        
        # Layout para gráficos
        charts_layout = QHBoxLayout()
        
        # Gráfico de pizza para status das apostas
        self.pie_figure = plt.figure(figsize=(5, 4))
        self.pie_canvas = FigureCanvas(self.pie_figure)
        
        # Gráfico de barras para apostas por dia
        self.bar_figure = plt.figure(figsize=(5, 4))
        self.bar_canvas = FigureCanvas(self.bar_figure)
        
        charts_layout.addWidget(self.pie_canvas)
        charts_layout.addWidget(self.bar_canvas)
        
        main_layout.addLayout(charts_layout)
        
        # Resumo de estatísticas
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        main_layout.addWidget(self.stats_text)
        
        # Inicializa os gráficos
        self.update_statistics()
    
    def update_statistics(self):
        """Atualiza as estatísticas e gráficos."""
        # Obtém o período selecionado
        period_index = self.period_combo.currentIndex()
        days_filter = None
        
        if period_index == 0:  # Hoje
            days_filter = 1
        elif period_index == 1:  # Últimos 7 dias
            days_filter = 7
        elif period_index == 2:  # Últimos 30 dias
            days_filter = 30
        
        # Obtém as estatísticas
        stats = self.calculate_statistics(days_filter)
        
        # Atualiza o texto de estatísticas
        self.update_stats_text(stats)
        
        # Atualiza os gráficos
        self.update_pie_chart(stats)
        self.update_bar_chart(stats)
    
    def calculate_statistics(self, days_filter=None):
        """
        Calcula estatísticas avançadas com base no histórico de apostas.
        
        Args:
            days_filter (int, optional): Filtro de dias para as estatísticas.
            
        Returns:
            dict: Estatísticas calculadas.
        """
        # Obtém o histórico completo
        history = self.history_manager.get_history()
        
        # Inicializa as estatísticas
        stats = {
            'total': 0,
            'success': 0,
            'error': 0,
            'success_rate': 0,
            'daily_bets': {},
            'avg_odds': 0,
            'total_odds': 0,
            'races': set(),
            'horses': set()
        }
        
        # Filtra por período se necessário
        if days_filter:
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days_filter)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            history = [bet for bet in history if bet['timestamp'].split(' ')[0] >= cutoff_str]
        
        # Calcula as estatísticas
        for bet in history:
            stats['total'] += 1
            
            # Contagem por status
            if 'Sucesso' in bet['status']:
                stats['success'] += 1
            elif 'Erro' in bet['status']:
                stats['error'] += 1
            
            # Odds
            try:
                odds = float(bet['odds'].replace(',', '.'))
                stats['total_odds'] += odds
            except:
                pass
            
            # Contagem por dia
            day = bet['timestamp'].split(' ')[0]
            if day in stats['daily_bets']:
                stats['daily_bets'][day] += 1
            else:
                stats['daily_bets'][day] = 1
            
            # Corridas e cavalos únicos
            stats['races'].add(bet['race_name'])
            stats['horses'].add(bet['horse'])
        
        # Calcula médias e taxas
        if stats['total'] > 0:
            stats['success_rate'] = round((stats['success'] / stats['total']) * 100, 2)
            stats['avg_odds'] = round(stats['total_odds'] / stats['total'], 2)
        
        # Ordena os dias para o gráfico de barras
        stats['sorted_days'] = sorted(stats['daily_bets'].keys())
        stats['daily_counts'] = [stats['daily_bets'][day] for day in stats['sorted_days']]
        
        # Limita a 7 dias para o gráfico de barras
        if len(stats['sorted_days']) > 7:
            stats['sorted_days'] = stats['sorted_days'][-7:]
            stats['daily_counts'] = stats['daily_counts'][-7:]
        
        return stats
    
    def update_stats_text(self, stats):
        """Atualiza o texto de estatísticas."""
        text = f"""
        <h3>Resumo Estatístico</h3>
        <p><b>Total de Apostas:</b> {stats['total']}</p>
        <p><b>Apostas com Sucesso:</b> {stats['success']} ({stats['success_rate']}%)</p>
        <p><b>Apostas com Erro:</b> {stats['error']}</p>
        <p><b>Odds Média:</b> {stats['avg_odds']}</p>
        <p><b>Corridas Únicas:</b> {len(stats['races'])}</p>
        <p><b>Cavalos Únicos:</b> {len(stats['horses'])}</p>
        """
        
        self.stats_text.setHtml(text)
    
    def update_pie_chart(self, stats):
        """Atualiza o gráfico de pizza."""
        self.pie_figure.clear()
        
        # Verifica se há dados
        if stats['total'] == 0:
            ax = self.pie_figure.add_subplot(111)
            ax.text(0.5, 0.5, "Sem dados disponíveis", 
                    horizontalalignment='center', verticalalignment='center')
            ax.axis('off')
            self.pie_canvas.draw()
            return
        
        # Dados para o gráfico
        labels = ['Sucesso', 'Erro']
        sizes = [stats['success'], stats['error']]
        colors = ['#4CAF50', '#F44336']
        
        # Cria o gráfico
        ax = self.pie_figure.add_subplot(111)
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title('Status das Apostas')
        
        self.pie_canvas.draw()
    
    def update_bar_chart(self, stats):
        """Atualiza o gráfico de barras."""
        self.bar_figure.clear()
        
        # Verifica se há dados
        if not stats['sorted_days']:
            ax = self.bar_figure.add_subplot(111)
            ax.text(0.5, 0.5, "Sem dados disponíveis", 
                    horizontalalignment='center', verticalalignment='center')
            ax.axis('off')
            self.bar_canvas.draw()
            return
        
        # Formata as datas para exibição
        display_days = [day.split('-')[2] + '/' + day.split('-')[1] for day in stats['sorted_days']]
        
        # Cria o gráfico
        ax = self.bar_figure.add_subplot(111)
        bars = ax.bar(display_days, stats['daily_counts'], color='#2196F3')
        
        # Adiciona os valores acima das barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.0f}', ha='center', va='bottom')
        
        ax.set_title('Apostas por Dia')
        ax.set_xlabel('Data')
        ax.set_ylabel('Número de Apostas')
        
        self.bar_figure.tight_layout()
        self.bar_canvas.draw()
