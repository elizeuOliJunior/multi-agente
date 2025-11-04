"""
Testes para o sistema multi-agente de economia brasileira.
"""

import pytest
import os
from unittest.mock import Mock, patch
from main import BrazilianEconomyAgentSystem
from tools import web_search_tool, python_repl_tool, ibge_data_tool

class TestBrazilianEconomyAgentSystem:
    """Testes para o sistema principal"""

    @pytest.fixture
    def agent_system(self):
        """Fixture para criar instância do sistema"""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            return BrazilianEconomyAgentSystem()

    def test_system_initialization(self, agent_system):
        """Testa se o sistema inicializa corretamente"""
        assert agent_system is not None
        assert agent_system.research_agent is not None
        assert agent_system.chart_agent is not None
        assert agent_system.weather_agent is not None
        assert agent_system.graph is not None

    @patch('main.web_search_tool')
    def test_query_routing_research(self, mock_search, agent_system):
        """Testa roteamento para pesquisa econômica"""
        # Simular resposta de busca
        mock_search.return_value = "PIB de São Paulo: R$ 100 bilhões"

        # Testar query de pesquisa
        result = agent_system.process_query("Qual o PIB de São Paulo?")

        assert result["success"] is True
        assert "query" in result
        assert result["query"] == "Qual o PIB de São Paulo?"

    def test_query_routing_climate(self, agent_system):
        """Testa roteamento para consultas climáticas"""
        query = "Como está o clima em Brasília?"
        route = agent_system._route_query({"messages": [Mock(content=query)]})

        assert route == "weather"

    def test_query_routing_chart(self, agent_system):
        """Testa roteamento para geração de gráficos"""  
        query = "Crie um gráfico do PIB do Brasil"
        route = agent_system._route_query({"messages": [Mock(content=query)]})

        assert route == "chart"

class TestTools:
    """Testes para as ferramentas"""

    @patch('tools.duckduckgo_search')
    def test_web_search_tool(self, mock_search):
        """Testa ferramenta de busca web"""
        mock_search.run.return_value = "Resultados de busca simulados"

        result = web_search_tool("PIB Brasil 2023")

        assert "RESULTADOS DA BUSCA" in result
        assert "PIB Brasil 2023" in result
        mock_search.run.assert_called_once()

    @patch('tools.repl')  
    def test_python_repl_tool(self, mock_repl):
        """Testa ferramenta de execução Python"""
        mock_repl.run.return_value = "42"

        code = "print(2 + 2)"
        result = python_repl_tool(code)

        assert "Código executado com sucesso" in result
        assert "42" in result
        mock_repl.run.assert_called_once()

    @patch('tools.requests.get')
    def test_ibge_data_tool(self, mock_get):
        """Testa ferramenta de dados do IBGE"""
        # Simular resposta da API
        mock_response = Mock()
        mock_response.json.return_value = [
            {"nome": "São Paulo", "microrregiao": {"nome": "São Paulo"}}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = ibge_data_tool("/v1/localidades/municipios")

        assert "Dados do IBGE obtidos com sucesso" in result
        assert "São Paulo" in result

class TestPromptEngineering:
    """Testes para validar qualidade dos prompts"""

    def test_prompt_structure(self):
        """Testa se prompts têm estrutura adequada"""
        from prompts import RESEARCH_AGENT_PROMPT, CHART_AGENT_PROMPT

        # Verificar elementos essenciais
        assert "PAPEL:" in RESEARCH_AGENT_PROMPT
        assert "INSTRUÇÕES ESPECÍFICAS:" in RESEARCH_AGENT_PROMPT
        assert "FINAL ANSWER" in RESEARCH_AGENT_PROMPT

        assert "PAPEL:" in CHART_AGENT_PROMPT
        assert "matplotlib" in CHART_AGENT_PROMPT
        assert "FINAL ANSWER" in CHART_AGENT_PROMPT

    def test_prompt_clarity(self):
        """Testa clareza e especificidade dos prompts"""
        from prompts import WEATHER_AGENT_PROMPT, ROUTER_AGENT_PROMPT

        # Verificar especificidade 
        assert "clima" in WEATHER_AGENT_PROMPT.lower()
        assert "temperatura" in WEATHER_AGENT_PROMPT.lower()

        assert "roteamento" in ROUTER_AGENT_PROMPT.lower()
        assert "agente" in ROUTER_AGENT_PROMPT.lower()

class TestDataValidation:
    """Testes para validação de dados"""

    def test_search_query_enhancement(self):
        """Testa melhoria de queries de busca"""
        from tools import _enhance_search_query

        # Testar enhancement de query econômica
        enhanced = _enhance_search_query("PIB São Paulo")

        assert "PIB Brasil dados oficiais IBGE" in enhanced
        assert "site:ibge.gov.br" in enhanced or "site:gov.br" in enhanced

    def test_error_handling(self):
        """Testa tratamento de erros"""
        from tools import python_repl_tool

        # Testar código inválido
        result = python_repl_tool("invalid python code %%%")

        assert "Erro na execução" in result

class TestIntegration:
    """Testes de integração"""

    @pytest.mark.integration
    def test_full_query_flow(self):
        """Testa fluxo completo de consulta (requer tokens válidos)"""
        if not os.environ.get("GITHUB_TOKEN"):
            pytest.skip("Token do GitHub não configurado")

        system = BrazilianEconomyAgentSystem()
        result = system.process_query("Teste de integração - PIB Brasil")

        assert "success" in result
        assert "results" in result

# Configuração do pytest
def pytest_configure(config):
    """Configuração do pytest"""
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )

if __name__ == "__main__":
    # Executar testes básicos
    pytest.main([__file__, "-v"])
