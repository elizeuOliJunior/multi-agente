#!/bin/bash

# Script para executar o Sistema Multi-Agente CLI
# Execute: chmod +x run_cli.sh && ./run_cli.sh

echo "🚀 Iniciando Sistema Multi-Agente CLI..."

# Verificar se ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado. Execute ./setup_cli.sh primeiro."
    exit 1
fi

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando exemplo..."
    echo "
# Configurações do Sistema Multi-Agente CLI
GITHUB_TOKEN=seu_token_github_aqui
OPENAI_API_KEY=

MODEL_NAME=gpt-4o-mini
MODEL_ENDPOINT=https://models.github.ai/inference
MODEL_TEMPERATURE=0.3

DEBUG_MODE=false
LOG_LEVEL=INFO
" > .env
    echo "📝 Configure suas credenciais no arquivo .env e execute novamente."
    exit 1
fi

# Carregar variáveis de ambiente
set -a
source .env
set +a

# Verificar se token está configurado
if [ -z "$GITHUB_TOKEN" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Nenhum token de API configurado."
    echo "Configure GITHUB_TOKEN ou OPENAI_API_KEY no arquivo .env"
    exit 1
fi

# Executar testes básicos (opcional)
if [ "$1" = "--test" ]; then
    echo "🧪 Executando testes..."
    python -m pytest test_system.py -v
    if [ $? -ne 0 ]; then
        echo "❌ Testes falharam. Verifique a configuração."
        exit 1
    fi
    echo "✅ Testes passaram!"
fi

echo "🤖 Iniciando interface CLI..."
echo "📍 Para sair, digite 'quit' ou pressione Ctrl+C"
echo ""

# Iniciar aplicação CLI
python main_cli.py
