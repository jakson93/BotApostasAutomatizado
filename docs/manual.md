# Documentação do Bot de Apostas Automatizado

## Visão Geral

O Bot de Apostas Automatizado é uma aplicação RPA (Robotic Process Automation) desenvolvida para monitorar mensagens do Telegram contendo informações sobre apostas em corridas de cavalos e automatizar o processo de apostas na plataforma Bolsa de Apostas.

A aplicação possui uma interface gráfica moderna e responsiva, desenvolvida com PyQt5, que permite configurar e monitorar todo o processo de automação em tempo real.

## Funcionalidades Principais

- **Monitoramento do Telegram**: Captura automática de mensagens de apostas de um canal específico
- **Interface Gráfica Moderna**: Dashboard completo para visualização e controle
- **Automação RPA**: Preparação para automação de apostas no site da Bolsa de Apostas
- **Sistema de Notificações**: Alertas via notificações do sistema e Telegram
- **Painel Estatístico**: Visualização de estatísticas e gráficos de desempenho
- **Histórico de Apostas**: Registro completo de todas as apostas realizadas
- **Filtros e Buscas**: Capacidade de filtrar apostas por diversos critérios

## Requisitos do Sistema

- Python 3.8 ou superior
- Conexão com a internet
- Conta no Telegram
- Conta na plataforma Bolsa de Apostas
- Bibliotecas Python:
  - PyQt5
  - python-telegram-bot
  - matplotlib
  - numpy

## Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/jakson93/BotApostasAutomatizado.git
cd BotApostasAutomatizado
```

### 2. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as Credenciais

Abra a aplicação e configure:
- Token do Bot do Telegram
- Chat ID do canal a ser monitorado
- Credenciais da Bolsa de Apostas

## Uso da Aplicação

### Iniciar a Aplicação

```bash
python src/main.py
```

### Configuração Inicial

1. Acesse a aba "Configurações"
2. Preencha os campos de configuração do Telegram:
   - Token do Bot: `6156089370:AAFNQQFaTAMyJdyMa8YU5MTAefAqNbMf9Cw` (já preenchido por padrão)
   - Chat ID: `-1001534658039` (já preenchido por padrão)
   - IDs para notificações (opcional)
3. Preencha os campos de configuração da Bolsa de Apostas:
   - Usuário
   - Senha
4. Clique em "Salvar Configurações"
5. Teste as conexões usando os botões "Testar Conexão"

### Iniciar a Automação

1. Na aba "Dashboard", clique no botão "Iniciar Automação"
2. O sistema começará a monitorar as mensagens do Telegram
3. As mensagens recebidas serão exibidas no log
4. As apostas processadas serão exibidas no histórico

### Visualizar Estatísticas

1. Acesse a aba "Estatísticas"
2. Visualize os gráficos de desempenho
3. Use os filtros para analisar dados específicos

### Parar a Automação

1. Clique no botão "Parar Automação" para interromper o monitoramento
2. A aplicação continuará em execução, mas não processará novas mensagens

## Formato das Mensagens do Telegram

O sistema reconhece mensagens no seguinte formato:

```
🏇 Nome da Corrida: Chelmsford City  
📍 Número da Corrida: 4  
🐎 Cavalo: Lovely Lucy  
💸 Odds: @ 4.50  
🎯 Tipo: E/W  
```

## Funcionalidades Avançadas

### Sistema de Notificações

O sistema oferece notificações de duas formas:
- **Notificações do Sistema**: Alertas na área de notificações do sistema operacional
- **Notificações via Telegram**: Mensagens enviadas para IDs configurados

### Minimização para a Bandeja do Sistema

A aplicação pode ser minimizada para a bandeja do sistema, continuando a funcionar em segundo plano. Para acessá-la:
1. Clique duas vezes no ícone na bandeja do sistema para mostrar/ocultar a janela principal
2. Clique com o botão direito no ícone para acessar o menu de contexto

### Filtros e Buscas

Na aba "Estatísticas", você pode filtrar o histórico de apostas por:
- Nome da corrida
- Nome do cavalo
- Status da aposta

## Solução de Problemas

### Problemas de Conexão com o Telegram

1. Verifique se o token do bot está correto
2. Confirme se o bot foi adicionado ao canal especificado
3. Verifique se o chat ID está correto

### Problemas de Automação

1. Verifique se as credenciais da Bolsa de Apostas estão corretas
2. Confirme se o formato das mensagens do Telegram está correto
3. Verifique o log de erros para identificar problemas específicos

## Adicionar Novos Canais ou Contas

### Adicionar Novo Canal do Telegram

1. Crie um novo bot no Telegram usando o BotFather
2. Adicione o bot ao canal desejado
3. Obtenha o chat ID do canal
4. Configure esses dados na aba "Configurações"

### Adicionar Nova Conta da Bolsa de Apostas

1. Acesse a aba "Configurações"
2. Atualize os campos de usuário e senha
3. Salve as configurações
4. Teste a conexão com o botão "Testar Conexão"

## Desenvolvimento Futuro

O sistema foi projetado para permitir futuras expansões, incluindo:

- Suporte multiusuário
- Integração com outras plataformas de apostas
- Estratégias automatizadas de apostas
- Análise preditiva de resultados

## Suporte

Para obter suporte ou relatar problemas, entre em contato através do GitHub:
https://github.com/jakson93/BotApostasAutomatizado
