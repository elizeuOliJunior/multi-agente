# CHANGELOG - Sistema Multi-Agente CLI

## [2.0.0] - 2025-11-03

### 🚀 Nova Versão CLI
- **Interface CLI completa** substituindo Streamlit
- **Interação via terminal** com comandos intuitivos
- **Sistema multi-agente mantido** (funcionalidade 100% preservada)
- **Performance otimizada** sem overhead do frontend web

### ✨ Funcionalidades Adicionadas
- Interface de linha de comando interativa
- Comandos especiais (help, status, cache, quit)
- Suporte a cores e formatação no terminal
- Sistema de ajuda integrado
- Cache com informações detalhadas
- Logs melhorados para debugging

### 🔧 Melhorias Técnicas
- Removida dependência do Streamlit
- Requirements otimizado para CLI
- Scripts de setup e execução automática
- Tratamento melhorado de erros
- Documentação específica para CLI

### 📦 Arquivos da Versão CLI
- `main_cli.py` - Interface principal CLI
- `requirements_cli.txt` - Dependências otimizadas
- `setup_cli.sh` - Script de instalação automática
- `run_cli.sh` - Script de execução
- `README_CLI.md` - Documentação completa

### 🎯 Compatibilidade
- ✅ Mantém todos os agentes (Research, Chart, Weather)
- ✅ Mantém sistema de cache e logs
- ✅ Mantém configurações do .env
- ✅ Mantém ferramentas (IBGE, BCB, Web Search)
- ✅ Mantém prompts especializados

### 🚀 Como Migrar
1. Use `main_cli.py` em vez de `main.py`
2. Use `requirements_cli.txt` em vez de `requirements.txt`
3. Execute `./setup_cli.sh` para configurar
4. Execute `./run_cli.sh` para usar
