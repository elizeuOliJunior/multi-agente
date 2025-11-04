"""
Ferramentas otimizadas para o sistema multi-agente.
Inclui ferramentas para busca web, execução de código Python e utilitários.
"""

import json
import requests
from typing import Annotated, Dict, Any, List
from datetime import datetime

from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_community.tools import DuckDuckGoSearchRun

# Configurar ferramentas de busca
duckduckgo_search = DuckDuckGoSearchRun(max_results=5)

# REPL Python para execução de código
repl = PythonREPL()

@tool
def web_search_tool(
    query: Annotated[str, "Consulta de busca na web para encontrar informações atualizadas"]
) -> str:
    """
    Ferramenta de busca na web otimizada para encontrar informações econômicas e climáticas.

    Args:
        query: String de busca otimizada

    Returns:
        Resultados da busca formatados
    """
    try:
        # Melhorar a query para obter resultados mais precisos
        enhanced_query = _enhance_search_query(query)

        # Realizar busca
        results = duckduckgo_search.run(enhanced_query)

        # Processar e formatar resultados
        formatted_results = _format_search_results(results, query)

        return formatted_results

    except Exception as e:
        return f"Erro na busca web: {str(e)}. Tente reformular a consulta."

@tool  
def python_repl_tool(
    code: Annotated[str, "Código Python para execução - ideal para análises e gráficos"]
) -> str:
    """
    Executa código Python com foco em análises de dados e criação de gráficos.

    Args:
        code: Código Python válido para execução

    Returns:
        Resultado da execução ou mensagem de erro
    """
    try:
        # Adicionar imports comuns se não estiverem presentes
        enhanced_code = _enhance_python_code(code)

        # Executar código
        result = repl.run(enhanced_code)

        # Processar resultado
        result_str = f"Código executado com sucesso:\n```python\n{enhanced_code}\n```\n\nSaída: {result}"

        # Verificar se é uma tarefa completa
        if any(keyword in code.lower() for keyword in ['plt.show()', 'plt.savefig', 'finalizado', 'completo']):
            result_str += "\n\n✅ Tarefa concluída. Responda com FINAL ANSWER se apropriado."

        return result_str

    except Exception as e:
        return f"Erro na execução: {repr(e)}\n\nVerifique a sintaxe e tente novamente."

@tool
def ibge_data_tool(
    endpoint: Annotated[str, "Endpoint da API do IBGE (ex: '/v1/localidades/municipios')"],
    params: Annotated[Dict[str, Any], "Parâmetros da consulta"] = {}
) -> str:
    """
    Acessa dados oficiais do IBGE através de suas APIs.

    Args:
        endpoint: Caminho da API do IBGE
        params: Parâmetros adicionais para a consulta

    Returns:
        Dados formatados do IBGE ou mensagem de erro
    """
    try:
        base_url = "https://servicodados.ibge.gov.br/api"
        url = f"{base_url}{endpoint}"

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Formatar dados para apresentação
        if isinstance(data, list) and len(data) > 0:
            formatted_data = _format_ibge_data(data)
            return f"Dados do IBGE obtidos com sucesso:\n{formatted_data}"
        else:
            return f"Dados obtidos: {json.dumps(data, ensure_ascii=False, indent=2)}"

    except requests.exceptions.RequestException as e:
        return f"Erro ao acessar API do IBGE: {e}"
    except Exception as e:
        return f"Erro no processamento dos dados: {e}"

@tool
def bcb_data_tool(
    series_code: Annotated[str, "Código da série do Banco Central (ex: '4'  para PIB)"],
    start_date: Annotated[str, "Data inicial no formato dd/mm/yyyy"] = "",
    end_date: Annotated[str, "Data final no formato dd/mm/yyyy"] = ""
) -> str:
    """
    Acessa dados econômicos do Sistema de Séries Temporais do Banco Central.

    Args:
        series_code: Código da série temporal
        start_date: Data de início da consulta
        end_date: Data final da consulta

    Returns:
        Dados econômicos formatados
    """
    try:
        base_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
        url = f"{base_url}.{series_code}/dados"

        params = {"formato": "json"}
        if start_date:
            params["dataInicial"] = start_date
        if end_date:
            params["dataFinal"] = end_date

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data:
            formatted_data = _format_bcb_data(data, series_code)
            return f"Dados do Banco Central obtidos:\n{formatted_data}"
        else:
            return "Nenhum dado encontrado para os parâmetros especificados."

    except requests.exceptions.RequestException as e:
        return f"Erro ao acessar API do Banco Central: {e}"
    except Exception as e:
        return f"Erro no processamento: {e}"

def _enhance_search_query(query: str) -> str:
    """Melhora queries de busca para obter resultados mais precisos"""

    # Mapear termos em português para queries mais efetivas
    enhancements = {
        'pib': 'PIB Brasil dados oficiais IBGE',
        'economia': 'economia brasileira dados oficiais',
        'municipio': 'município Brasil dados IBGE',
        'cidade': 'cidade Brasil economia PIB',
        'clima': 'clima tempo Brasil INMET',
        'temperatura': 'temperatura clima Brasil'
    }

    query_lower = query.lower()
    for term, enhancement in enhancements.items():
        if term in query_lower:
            query = f"{query} {enhancement}"
            break

    # Adicionar filtros para fontes confiáveis
    reliable_sources = "site:ibge.gov.br OR site:bcb.gov.br OR site:gov.br"

    return f"{query} {reliable_sources}"

def _format_search_results(results: str, original_query: str) -> str:
    """Formata resultados de busca de forma estruturada"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    formatted = f"""
🔍 RESULTADOS DA BUSCA - {timestamp}
Query: {original_query}

{results}

💡 DICA: Verifique sempre a data e fonte das informações encontradas.
"""

    return formatted

def _enhance_python_code(code: str) -> str:
    """Adiciona imports comuns se necessário"""

    imports_needed = []

    # Verificar se precisa de imports específicos
    if any(lib in code for lib in ['plt.', 'pyplot']):
        imports_needed.append('import matplotlib.pyplot as plt')

    if 'sns.' in code or 'seaborn' in code:
        imports_needed.append('import seaborn as sns')

    if 'pd.' in code or 'DataFrame' in code:
        imports_needed.append('import pandas as pd')

    if 'np.' in code or 'numpy' in code:
        imports_needed.append('import numpy as np')

    # Adicionar imports se necessário
    if imports_needed:
        imports_block = '\n'.join(imports_needed) + '\n\n'
        # Só adicionar se não estão já presentes
        existing_imports = [imp for imp in imports_needed if imp in code]
        new_imports = [imp for imp in imports_needed if imp not in existing_imports]

        if new_imports:
            imports_block = '\n'.join(new_imports) + '\n\n'
            code = imports_block + code

    return code

def _format_ibge_data(data: List[Dict]) -> str:
    """Formata dados do IBGE para apresentação"""

    if not data:
        return "Nenhum dado disponível"

    # Limitar número de resultados para não sobrecarregar
    display_data = data[:10] if len(data) > 10 else data

    formatted_lines = []
    for item in display_data:
        if isinstance(item, dict):
            # Extrair informações principais
            nome = item.get('nome', 'N/A')
            if 'microrregiao' in item:
                micro = item['microrregiao'].get('nome', 'N/A')
                formatted_lines.append(f"• {nome} (Microrregião: {micro})")
            else:
                formatted_lines.append(f"• {nome}")
        else:
            formatted_lines.append(f"• {item}")

    result = '\n'.join(formatted_lines)

    if len(data) > 10:
        result += f"\n\n... e mais {len(data) - 10} resultados"

    return result

def _format_bcb_data(data: List[Dict], series_code: str) -> str:
    """Formata dados do Banco Central para apresentação"""

    if not data:
        return "Nenhum dado disponível"

    # Mapear códigos de série para nomes amigáveis
    series_names = {
        '4': 'PIB - Produto Interno Bruto',
        '433': 'IPCA - Índice de Preços ao Consumidor Amplo',
        '1178': 'Taxa Selic',
        '12': 'Taxa de Câmbio'
    }

    series_name = series_names.get(series_code, f'Série {series_code}')

    # Mostrar últimos valores
    display_data = data[-10:] if len(data) > 10 else data

    formatted_lines = [f"📊 {series_name}\n"]

    for item in display_data:
        data_point = item.get('data', 'N/A')
        valor = item.get('valor', 'N/A')
        formatted_lines.append(f"{data_point}: {valor}")

    if len(data) > 10:
        formatted_lines.append(f"\n(Mostrando últimos 10 de {len(data)} registros)")

    return '\n'.join(formatted_lines)

def print_pretty(event: Dict[str, Any]) -> None:
    """
    Função de debug para visualizar eventos do sistema multi-agente.

    Args:
        event: Evento do sistema para logging
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*60}")
    print(f"🤖 EVENTO DO SISTEMA - {timestamp}")
    print(f"{'='*60}")

    for node_key, node_data in event.items():
        print(f"\n📍 NÓ: {node_key.upper()}")
        print("-" * 40)

        if isinstance(node_data, dict) and "messages" in node_data:
            messages = node_data["messages"]
            for i, message in enumerate(messages[-3:]):  # Mostrar últimas 3 mensagens
                message_type = message.__class__.__name__
                content = message.content[:200] + "..." if len(message.content) > 200 else message.content

                print(f"  Mensagem {i+1} ({message_type}):")
                print(f"    {content}")
        else:
            print(f"  Dados: {str(node_data)[:200]}")

    print(f"\n{'='*60}\n")

# Lista de todas as ferramentas disponíveis
AVAILABLE_TOOLS = [
    web_search_tool,
    python_repl_tool, 
    ibge_data_tool,
    bcb_data_tool
]

# Configurações das ferramentas por agente
AGENT_TOOLS = {
    "research": [web_search_tool, ibge_data_tool, bcb_data_tool],
    "chart": [python_repl_tool],
    "weather": [web_search_tool],
    "router": []  # Router não precisa de ferramentas específicas
}
