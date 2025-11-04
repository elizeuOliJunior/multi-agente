# 🤖 Sistema Multi-Agente - Economia Brasileira (CLI)

Sistema inteligente baseado em **LangGraph** e **GPT-4o-mini** para análise econômica brasileira, com interface de linha de comando (CLI).

## 🎯 Funcionalidades

### **🔍 Agente de Pesquisa Econômica**
- Consulta dados oficiais do IBGE e Banco Central
- Informações sobre PIB, indicadores econômicos
- Análise de dados municipais e estaduais
- Séries históricas econômicas

### **📊 Agente de Visualização**
- Geração de gráficos históricos
- Análises comparativas entre regiões
- Visualizações de séries temporais
- Criação automática de charts

### **🌤️ Agente Climático**
- Informações meteorológicas atuais
- Previsões do tempo por cidade
- Dados climáticos brasileiros
- Consultas regionais

## 🚀 Instalação e Configuração

### **Pré-requisitos**
- Python 3.9+
- Git (opcional)
- Token do GitHub Models ou OpenAI API

### **1. Setup Automático**
```bash
# Dar permissão e executar setup
chmod +x setup_cli.sh
./setup_cli.sh
```

### **2. Configurar Credenciais**
Edite o arquivo `.env`:
```env
# Token do GitHub Models (recomendado)
GITHUB_TOKEN=ghp_seu_token_aqui

# OU Token da OpenAI
OPENAI_API_KEY=sk-sua_chave_aqui

# Configurações do modelo
MODEL_NAME=gpt-4o-mini
MODEL_ENDPOINT=https://models.github.ai/inference
MODEL_TEMPERATURE=0.3
```

### **3. Executar o Sistema**
```bash
# Opção A: Script automático
chmod +x run_cli.sh
./run_cli.sh

# Opção B: Manual
source venv/bin/activate
python main_cli.py
```

## 💬 Como Usar

### **Interface de Linha de Comando**
```
🤖 SISTEMA MULTI-AGENTE - ECONOMIA BRASILEIRA
========================================
Sistema inteligente com agentes especializados:
🔍 Pesquisa Econômica | 📊 Gráficos | 🌤️ Clima
========================================

💬 Digite suas perguntas (ou 'help' para ajuda, 'quit' para sair)
------------------------------------------------------------

🔮 Você: Qual o PIB do Brasil em 2023?
```

### **Exemplos de Consultas**

#### **📊 Consultas Econômicas:**
```
🔮 Você: Qual o PIB do Brasil em 2023?
🔮 Você: PIB per capita de São Paulo
🔮 Você: Economia de Minas Gerais nos últimos 5 anos
🔮 Você: Compare PIB de Rio de Janeiro e São Paulo
```

#### **📈 Gráficos e Visualizações:**
```
🔮 Você: Crie um gráfico do PIB brasileiro dos últimos 5 anos
🔮 Você: Visualizar economia de Brasília
🔮 Você: Gráfico comparativo de estados do Sudeste
```

#### **🌤️ Consultas Climáticas:**
```
🔮 Você: Como está o clima em São Paulo hoje?
🔮 Você: Temperatura em Brasília agora
🔮 Você: Previsão do tempo para o Rio de Janeiro
```

#### **🔄 Consultas Combinadas:**
```
🔮 Você: PIB de Salvador e clima atual da cidade
🔮 Você: Economia de Curitiba, fazer gráfico e informar clima
```

### **⚙️ Comandos Especiais**
```
help/ajuda     - Mostra ajuda do sistema
status/info    - Status e informações do sistema
clear/limpar   - Limpa a tela
cache clear    - Limpa cache do sistema
cache info     - Informações do cache
quit/exit/sair - Sair do sistema
```

## 🏗️ Arquitetura do Sistema

### **Componentes Principais**
```
main_cli.py          # Interface CLI principal
tools.py             # Ferramentas dos agentes
prompts.py           # Prompts especializados
utils.py             # Utilitários e cache
requirements_cli.txt # Dependências (sem Streamlit)
.env                 # Configurações
```

### **Fluxo Multi-Agente**
```
Consulta → Análise → Roteamento → Agente(s) → Processamento → Resposta
    ↓         ↓          ↓            ↓           ↓             ↓
  NLP     Intenção   Palavras    Research/    Ferramentas   Resultado
         Confiança   -chave      Chart/       APIs/Tools    Formatado
         Entidades              Weather      Python/Web
```

## 🛠️ Desenvolvimento

### **Estrutura de Agentes**
- **Research Agent**: Busca web + APIs oficiais (IBGE, BCB)
- **Chart Agent**: Execução Python + Matplotlib/Seaborn  
- **Weather Agent**: Dados meteorológicos + Previsões
- **Router**: Análise de intenção e roteamento inteligente

### **Executar Testes**
```bash
# Testes básicos
python -m pytest test_system.py -v

# Com coverage
pip install pytest-cov
python -m pytest test_system.py --cov=.
```

### **Debug e Logs**
```bash
# Modo debug
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG
python main_cli.py
```

## 📊 Performance

### **Métricas Típicas**
- **Tempo de resposta**: 2-8 segundos
- **Taxa de sucesso**: 95%+
- **Modelos suportados**: GPT-4o-mini, GPT-4o
- **Cache TTL**: 30 minutos
- **Concorrência**: Single-threaded

## 🔧 Solução de Problemas

### **Erros Comuns**

#### **Token não configurado**
```bash
❌ Token de API não configurado!
# Solução: Configure GITHUB_TOKEN no .env
```

#### **Modelo indisponível**
```bash
❌ Error code: 400 - unavailable model
# Solução: Use gpt-4o-mini ou configure OpenAI API
```

#### **Dependências faltando**
```bash
❌ ImportError: No module named 'langchain'
# Solução: Execute ./setup_cli.sh novamente
```

### **Verificações de Diagnóstico**
```bash
# Testar configuração
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Token OK' if os.getenv('GITHUB_TOKEN') else 'Token faltando')"

# Testar imports
python -c "import langchain_openai, langgraph; print('✅ Imports OK')"

# Testar modelo
python test_model_access.py
```

## 📚 Recursos Adicionais

### **Documentação Técnica**
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [GitHub Models](https://github.com/marketplace/models)
- [OpenAI API](https://platform.openai.com/docs)

### **APIs Utilizadas**
- **IBGE**: Dados municipais e regionais
- **Banco Central**: Séries temporais econômicas
- **DuckDuckGo**: Busca web geral
- **GitHub Models**: Acesso ao GPT-4o-mini

## 🤝 Contribuição

### **Como Contribuir**
1. Fork do repositório
2. Crie branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit das mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

### **Desenvolvimento Local**
```bash
# Clone e setup
git clone <repo>
cd sistema-multi-agente-cli
./setup_cli.sh

# Executar em modo desenvolvimento
export DEBUG_MODE=true
python main_cli.py
```

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🙋 Suporte

Para dúvidas e problemas:
1. Consulte este README
2. Execute `python main_cli.py` e digite `help`
3. Verifique os logs de erro
4. Abra uma issue no repositório

---

**Desenvolvido com ❤️ usando LangGraph, GPT-4o-mini e Python**
