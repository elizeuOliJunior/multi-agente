#!/bin/bash

# Script de setup para Sistema Multi-Agente CLI - Economia Brasileira
# Execute: chmod +x setup_cli.sh && ./setup_cli.sh

echo "🤖 Sistema Multi-Agente CLI - Economia Brasileira"
echo "================================================="

# Verificar Python
echo "📋 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.9+ e tente novamente."
    exit 1
fi
echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual
echo "🏗️  Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "ℹ️  Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements_cli.txt

# Verificar instalação
echo "🔍 Verificando instalação..."
python3 -c "
try:
    import langchain_openai, langgraph, dotenv
    print('✅ Dependências principais instaladas')
except ImportError as e:
    print(f'❌ Erro: {e}')
    exit(1)
"

# Configurar variáveis de ambiente
echo "⚙️  Configurando ambiente..."
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || echo "
# Configurações do Sistema Multi-Agente CLI
GITHUB_TOKEN=seu_token_github_aqui
OPENAI_API_KEY=

MODEL_NAME=gpt-4o-mini
MODEL_ENDPOINT=https://models.github.ai/inference
MODEL_TEMPERATURE=0.3

DEBUG_MODE=false
LOG_LEVEL=INFO
" > .env
    echo "📝 Arquivo .env criado. Configure suas credenciais!"
    echo ""
    echo "IMPORTANTE:"
    echo "1. Edite o arquivo .env com suas credenciais"
    echo "2. Configure GITHUB_TOKEN ou OPENAI_API_KEY"
    echo ""
else
    echo "ℹ️  Arquivo .env já existe"
fi

echo ""
echo "🎉 Setup CLI concluído!"
echo ""
echo "Para executar o sistema:"
echo "1. source venv/bin/activate"
echo "2. python main_cli.py"
echo ""
echo "Ou use o script run_cli.sh"
