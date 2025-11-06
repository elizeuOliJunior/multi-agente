#!/usr/bin/env python3
"""
Sistema Multi-Agente para Economia Brasileira - Versão CLI OTIMIZADA
Versão com timeouts aprimorados e performance melhorada
"""

import os
import json
import sys
import time
from typing import Dict, Any, List
from datetime import datetime
import signal

# ✅ Carregar variáveis do .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv não instalado. Execute: pip install python-dotenv")
    print("Tentando continuar sem carregar .env...")

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain import hub

# ✅ CORREÇÃO: Usar AgentExecutor com timeouts
from langchain.agents import create_react_agent, AgentExecutor

# Importar ferramentas e prompts locais
try:
    from tools import web_search_tool, python_repl_tool, print_pretty, AGENT_TOOLS
    from prompts import (
        RESEARCH_AGENT_PROMPT, 
        CHART_AGENT_PROMPT, 
        WEATHER_AGENT_PROMPT,
        ROUTER_AGENT_PROMPT
    )
    from utils import QueryAnalyzer, cache_manager, generate_cache_key, log_agent_activity
except ImportError as e:
    print(f"❌ Erro na importação: {e}")
    print("Certifique-se de que todos os arquivos estão no mesmo diretório")
    sys.exit(1)

# Configuração do modelo
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("OPENAI_API_KEY")
ENDPOINT = "https://models.github.ai/inference"
MODEL = "gpt-4o-mini"

# ✅ CONFIGURAÇÕES DE TIMEOUT
AGENT_TIMEOUT = 30  # 30 segundos max por agente
MAX_ITERATIONS = 20  # Mais iterações permitidas
REQUEST_TIMEOUT = 10  # Timeout para requests HTTP

class TimeoutException(Exception):
    """Exceção para timeout de agente"""
    pass

def timeout_handler(signum, frame):
    """Handler para timeout"""
    raise TimeoutException("Agent execution timed out")

class BrazilianEconomyAgentSystem:
    """Sistema Multi-Agente para Economia Brasileira - Versão CLI Otimizada"""

    def __init__(self):
        """Inicializa o sistema multi-agente"""
        if not TOKEN:
            print("❌ Token de API não configurado!")
            print("Configure GITHUB_TOKEN ou OPENAI_API_KEY nas variáveis de ambiente.")
            print("Exemplo: export GITHUB_TOKEN=seu_token")
            sys.exit(1)

        print("🚀 Inicializando sistema multi-agente...")

        # Configurar o LLM com timeout
        self.llm = ChatOpenAI(
            model=MODEL,
            base_url=ENDPOINT,
            api_key=TOKEN,
            temperature=0.3,
            request_timeout=REQUEST_TIMEOUT
        )

        # Analisador de consultas
        self.query_analyzer = QueryAnalyzer()

        # ✅ CORREÇÃO: Configurar prompts e agentes otimizados
        print("   🔧 Configurando prompts...")
        self._setup_prompts()

        print("   🔍 Criando agentes otimizados...")
        self._setup_agents()

        print("✅ Sistema inicializado com sucesso!")
        print(f"🤖 Modelo: {MODEL}")
        print(f"⏱️  Timeout por agente: {AGENT_TIMEOUT}s")
        print(f"🔄 Max iterações: {MAX_ITERATIONS}")
        print("-" * 60)

    def _setup_prompts(self):
        """Configura os prompts otimizados para cada agente"""
        # ✅ PROMPT OTIMIZADO: Mais direto e eficiente
        optimized_template = """You are a helpful assistant specialized in Brazilian economic data.

Answer the following questions as best you can. You have access to the following tools:

{tools}

IMPORTANT INSTRUCTIONS:
- Be direct and concise in your answers
- If you can't find specific data, provide the best available information
- Always cite your sources
- If a search fails, try a simpler search term
- Provide a final answer even if the data is not perfect

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

        self.base_prompt = PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
            template=optimized_template
        )

    def _setup_agents(self):
        """Configura os agentes otimizados"""

        # ✅ Agente de Pesquisa OTIMIZADO
        research_prompt = self._create_specialized_prompt(
            self.base_prompt, 
            "You specialize in Brazilian economic data, GDP, and statistical information from IBGE and government sources.",
            "pesquisa econômica brasileira"
        )
        research_agent = create_react_agent(self.llm, AGENT_TOOLS["research"], research_prompt)
        self.research_executor = AgentExecutor(
            agent=research_agent,
            tools=AGENT_TOOLS["research"],
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=MAX_ITERATIONS,
            max_execution_time=AGENT_TIMEOUT,
            early_stopping_method="generate"
        )

        # ✅ Agente de Gráficos OTIMIZADO
        chart_prompt = self._create_specialized_prompt(
            self.base_prompt,
            "You specialize in creating charts and data visualizations using Python and matplotlib.",
            "criação de gráficos e visualizações"
        )
        chart_agent = create_react_agent(self.llm, AGENT_TOOLS["chart"], chart_prompt)
        self.chart_executor = AgentExecutor(
            agent=chart_agent,
            tools=AGENT_TOOLS["chart"],
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=MAX_ITERATIONS,
            max_execution_time=AGENT_TIMEOUT,
            early_stopping_method="generate"
        )

        # ✅ Agente Climático OTIMIZADO
        weather_prompt = self._create_specialized_prompt(
            self.base_prompt,
            "You specialize in weather and climate information for Brazilian cities.",
            "consultas climáticas e meteorológicas"
        )
        weather_agent = create_react_agent(self.llm, AGENT_TOOLS["weather"], weather_prompt)
        self.weather_executor = AgentExecutor(
            agent=weather_agent,
            tools=AGENT_TOOLS["weather"],
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=MAX_ITERATIONS,
            max_execution_time=AGENT_TIMEOUT,
            early_stopping_method="generate"
        )

    def _create_specialized_prompt(self, base_prompt, specialization, description):
        """Cria um prompt especializado mais eficiente"""
        specialized_template = f"""{specialization}

{base_prompt.template}"""

        return PromptTemplate(
            input_variables=base_prompt.input_variables,
            template=specialized_template
        )

    def _route_query(self, query: str) -> str:
        """Determina qual agente deve processar a consulta"""
        query_lower = query.lower()

        # Lógica de roteamento baseada em palavras-chave
        if any(word in query_lower for word in ["clima", "tempo", "temperatura", "chuva", "meteorológico"]):
            return "weather"
        elif any(word in query_lower for word in ["gráfico", "chart", "plotar", "visualizar", "plot", "graph"]):
            return "chart"
        elif any(word in query_lower for word in ["pesquisa", "economia", "pib", "dados", "ibge", "estatística"]):
            return "research"
        else:
            return "research"  # Default para pesquisa

    def process_query(self, query: str) -> Dict[str, Any]:
        """Processa uma consulta através do sistema multi-agente com timeout"""
        print(f"🔍 Processando: {query}")
        print("-" * 60)

        start_time = time.time()

        try:
            # Verificar cache primeiro
            cache_key = generate_cache_key("system", query)
            cached_result = cache_manager.get(cache_key)

            if cached_result:
                print("⚡ Resultado encontrado no cache!")
                log_agent_activity("system", "cache_hit", {"query": query})
                return cached_result

            # Analisar consulta
            analysis = self.query_analyzer.analyze_query(query)
            print(f"🧠 Análise: Intenção={analysis.intent} | Confiança={analysis.confidence:.2f}")

            if analysis.entities:
                print(f"🏷️  Entidades: {', '.join(analysis.entities)}")

            log_agent_activity("system", "query_analyzed", {
                "intent": analysis.intent,
                "confidence": analysis.confidence,
                "entities": analysis.entities
            })

            # Roteamento e execução com timeout
            route = self._route_query(query)
            print(f"🎯 Rota selecionada: {route}")

            print(f"\n🤖 Executando agente (timeout: {AGENT_TIMEOUT}s)...")

            # ✅ EXECUÇÃO COM TIMEOUT E TRATAMENTO DE ERRO
            result = None
            try:
                # Configurar timeout usando signal (Unix/Linux) ou threading (Windows)
                if hasattr(signal, 'SIGALRM'):
                    # Unix/Linux
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(AGENT_TIMEOUT + 5)  # 5s extra de margem

                # Executar agente apropriado
                if route == "research":
                    log_agent_activity("research_agent", "processing_query")
                    result = self.research_executor.invoke({"input": query})
                elif route == "chart":
                    log_agent_activity("chart_agent", "generating_visualization")
                    result = self.chart_executor.invoke({"input": query})
                elif route == "weather":
                    log_agent_activity("weather_agent", "fetching_climate_data")
                    result = self.weather_executor.invoke({"input": query})
                else:
                    # Fallback para pesquisa
                    log_agent_activity("research_agent", "processing_query")
                    result = self.research_executor.invoke({"input": query})

                # Desativar timeout
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)

                print(f"   ✓ Agente {route} executado com sucesso")

            except TimeoutException:
                print(f"   ⏱️  Timeout atingido ({AGENT_TIMEOUT}s)")
                result = {"output": f"Consulta sobre '{query}' teve timeout. Tente uma pergunta mais específica ou simples."}

            except Exception as e:
                print(f"   ❌ Erro durante execução: {str(e)[:100]}...")
                # Fallback com resposta básica
                result = {"output": f"Não foi possível processar completamente a consulta '{query}'. Erro: {str(e)[:100]}..."}

            end_time = time.time()
            processing_time = end_time - start_time

            # Formatar resultado
            final_result = {
                "success": True,
                "content": result.get("output", "Resposta não disponível"),
                "agent_used": route,
                "query": query,
                "analysis": {
                    "intent": analysis.intent,
                    "confidence": analysis.confidence,
                    "entities": analysis.entities,
                    "keywords": analysis.keywords
                },
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }

            # Salvar no cache apenas se sucesso
            if processing_time < AGENT_TIMEOUT:
                cache_manager.set(cache_key, final_result)

            return final_result

        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time

            print(f"❌ Erro no processamento: {e}")
            log_agent_activity("system", "error", {"error": str(e), "query": query})

            return {
                "success": False,
                "error": str(e),
                "query": query,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }

class CLIInterface:
    """Interface de linha de comando otimizada"""

    def __init__(self):
        """Inicializa a interface CLI"""
        self.system = None
        self.running = True

    def start(self):
        """Inicia a interface CLI"""
        self.print_banner()

        # Inicializar sistema
        try:
            self.system = BrazilianEconomyAgentSystem()
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            print("\n🔧 Possíveis soluções:")
            print("1. Verifique se o .env está configurado corretamente")
            print("2. Execute: pip install langchain langchain-community langchainhub")
            print("3. Instale dependências: pip install -r requirements_cli.txt")
            print("4. Verifique conexão com internet")
            return

        # Loop principal
        self.main_loop()

    def print_banner(self):
        """Imprime banner de boas-vindas"""
        print("\n" + "="*80)
        print("🤖 SISTEMA MULTI-AGENTE - ECONOMIA BRASILEIRA (OTIMIZADO)")
        print("="*80)
        print("Sistema inteligente com agentes especializados:")
        print("🔍 Pesquisa Econômica | 📊 Gráficos | 🌤️ Clima")
        print(f"⚡ Performance: {MAX_ITERATIONS} iterações max, {AGENT_TIMEOUT}s timeout")
        print("="*80)

    def main_loop(self):
        """Loop principal da interface"""
        print("\n💬 Digite suas perguntas (ou 'help' para ajuda, 'quit' para sair)")
        print("💡 Para melhor performance, faça perguntas específicas e diretas")
        print("-" * 60)

        while self.running:
            try:
                # Input do usuário
                query = input("\n🔮 Você: ").strip()

                if not query:
                    continue

                # Comandos especiais
                if query.lower() in ['quit', 'exit', 'sair']:
                    self.handle_quit()
                    break
                elif query.lower() in ['help', 'ajuda']:
                    self.show_help()
                    continue
                elif query.lower() in ['clear', 'limpar']:
                    self.clear_screen()
                    continue
                elif query.lower().startswith('cache'):
                    self.handle_cache_commands(query)
                    continue
                elif query.lower() in ['status', 'info']:
                    self.show_status()
                    continue

                # Processar consulta
                self.process_and_display_query(query)

            except KeyboardInterrupt:
                print("\n\n👋 Sistema interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
                continue

    def process_and_display_query(self, query: str):
        """Processa e exibe resultado de uma consulta"""
        result = self.system.process_query(query)

        print("\n" + "="*60)
        print("📊 RESULTADOS")
        print("="*60)

        if result["success"]:
            # Mostrar conteúdo da resposta
            print(f"\n🤖 {result['agent_used'].upper()}:")
            print("-" * 40)
            print(result["content"])

            # Mostrar estatísticas
            print("\n" + "="*60)
            print("📈 ESTATÍSTICAS")
            print("="*60)
            print(f"⏱️  Tempo de processamento: {result['processing_time']:.2f}s")
            print(f"🎯 Agente usado: {result['agent_used']}")
            print(f"🧠 Intenção detectada: {result['analysis']['intent']}")
            print(f"🎭 Confiança: {result['analysis']['confidence']:.2f}")

            if result['analysis']['entities']:
                print(f"🏷️  Entidades: {', '.join(result['analysis']['entities'])}")

            # Feedback de performance
            if result['processing_time'] > 20:
                print("\n💡 Dica: Para respostas mais rápidas, faça perguntas mais específicas")

        else:
            print(f"❌ Erro: {result['error']}")
            print("\n💡 Dicas:")
            print("• Verifique sua conexão com a internet")
            print("• Tente uma pergunta mais simples e específica")
            print("• Use termos como 'PIB Brasil 2023', 'economia São Paulo'")

    def show_help(self):
        """Mostra ajuda do sistema otimizada"""
        print("\n" + "="*60)
        print("📖 AJUDA - SISTEMA MULTI-AGENTE OTIMIZADO")
        print("="*60)

        print("\n🔍 TIPOS DE CONSULTA (EXEMPLOS OTIMIZADOS):")
        print("• Simples: 'PIB Brasil 2023', 'População São Paulo'")
        print("• Específicas: 'PIB per capita Rio Janeiro', 'Economia Minas Gerais'")
        print("• Gráficos: 'Gráfico PIB últimos 5 anos'")  
        print("• Clima: 'Temperatura São Paulo hoje'")

        print("\n⚡ DICAS DE PERFORMANCE:")
        print("• Seja específico: 'PIB SP 2023' ao invés de 'economia paulista'")
        print("• Evite perguntas muito abertas ou complexas")
        print("• Mencione anos específicos quando relevante")
        print(f"• Timeout automático: {AGENT_TIMEOUT}s por consulta")

        print("\n⚙️  COMANDOS ESPECIAIS:")
        print("• help/ajuda - Mostra esta ajuda")
        print("• status/info - Status do sistema")
        print("• clear/limpar - Limpa a tela")
        print("• cache clear - Limpa cache do sistema")
        print("• cache info - Informações do cache")
        print("• quit/exit/sair - Sair do sistema")

        print("\n💡 EXEMPLOS RÁPIDOS:")
        print("🔮 Você: PIB Brasil 2023")
        print("🔮 Você: População Rio de Janeiro")
        print("🔮 Você: Temperatura Brasília")

        print("\n" + "="*60)

    def show_status(self):
        """Mostra status do sistema otimizado"""
        print("\n" + "="*60)
        print("📊 STATUS DO SISTEMA OTIMIZADO")
        print("="*60)
        print(f"🤖 Modelo: {MODEL}")
        print(f"🔗 Endpoint: {ENDPOINT}")
        print(f"✅ Status: Operacional")
        print(f"🗄️  Cache: Ativo")
        print(f"⚡ Agentes: 3 especializados (AgentExecutor)")
        print(f"⏱️  Timeout: {AGENT_TIMEOUT}s por agente")
        print(f"🔄 Max iterações: {MAX_ITERATIONS}")
        print(f"📡 Request timeout: {REQUEST_TIMEOUT}s")
        print("="*60)

    def handle_cache_commands(self, query: str):
        """Trata comandos relacionados ao cache"""
        if 'clear' in query.lower():
            cache_manager.clear()
            print("✅ Cache limpo com sucesso!")
        elif 'info' in query.lower():
            print("🗄️  Informações do cache:")
            print(f"   • Items em cache: {len(cache_manager.cache)}")
            print("   • TTL: 30 minutos")

    def clear_screen(self):
        """Limpa a tela"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()

    def handle_quit(self):
        """Trata saída do sistema"""
        print("\n👋 Obrigado por usar o Sistema Multi-Agente Otimizado!")
        print("🎯 Estatísticas da sessão salvas em logs")
        print("Até a próxima! 🚀")
        self.running = False

def main():
    """Função principal"""
    try:
        cli = CLIInterface()
        cli.start()
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
