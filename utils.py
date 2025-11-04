"""
Utilitários e funções auxiliares para o sistema multi-agente.
"""

import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class QueryClassification:
    """Classificação de uma consulta do usuário"""
    intent: str  # 'research', 'chart', 'weather'
    confidence: float  # 0.0 to 1.0
    entities: List[str]  # Entidades extraídas
    keywords: List[str]  # Palavras-chave relevantes

class QueryAnalyzer:
    """Analisador inteligente de consultas do usuário"""

    # Padrões para classificação de intenções
    INTENT_PATTERNS = {
        'weather': [
            r'\b(clima|tempo|temperatura|chuva|sol|vento)\b',
            r'\b(previsão|meteorol|°c|celsius|fahrenheit)\b',
            r'\b(quente|frio|nublado|ensolarado)\b'
        ],
        'chart': [
            r'\b(gráfico|chart|plotar|visualiz|diagram)\b',
            r'\b(histórico|evolução|tendência|comparar)\b',
            r'\b(linha|barras|pizza|scatter)\b'
        ],
        'research': [
            r'\b(pib|economia|dados|estatística)\b',
            r'\b(município|cidade|estado|região)\b',
            r'\b(ibge|banco\s+central|bcb)\b'
        ]
    }

    # Entidades geográficas brasileiras comuns
    BRAZILIAN_LOCATIONS = [
        'são paulo', 'rio de janeiro', 'brasília', 'salvador',
        'fortaleza', 'belo horizonte', 'manaus', 'curitiba',
        'recife', 'porto alegre', 'belém', 'goiânia'
    ]

    def analyze_query(self, query: str) -> QueryClassification:
        """
        Analisa uma consulta e retorna classificação detalhada.

        Args:
            query: Consulta do usuário

        Returns:
            QueryClassification com análise completa
        """
        query_lower = query.lower()

        # Calcular scores para cada intenção
        intent_scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            intent_scores[intent] = score

        # Determinar intenção principal
        best_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[best_intent]

        # Calcular confiança (normalizada)
        total_score = sum(intent_scores.values())
        confidence = max_score / max(total_score, 1)

        # Extrair entidades e palavras-chave
        entities = self._extract_entities(query_lower)
        keywords = self._extract_keywords(query_lower)

        return QueryClassification(
            intent=best_intent,
            confidence=confidence,
            entities=entities,
            keywords=keywords
        )

    def _extract_entities(self, query: str) -> List[str]:
        """Extrai entidades geográficas da consulta"""
        entities = []
        for location in self.BRAZILIAN_LOCATIONS:
            if location in query:
                entities.append(location.title())
        return entities

    def _extract_keywords(self, query: str) -> List[str]:
        """Extrai palavras-chave relevantes"""
        # Palavras-chave econômicas importantes
        economic_keywords = [
            'pib', 'economia', 'renda', 'população', 'desenvolvimento',
            'crescimento', 'investimento', 'emprego', 'inflação'
        ]

        keywords = []
        for keyword in economic_keywords:
            if keyword in query:
                keywords.append(keyword)

        return keywords

class DataValidator:
    """Validador de dados para garantir qualidade das informações"""

    @staticmethod
    def validate_economic_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida dados econômicos para consistência.

        Args:
            data: Dados econômicos para validação

        Returns:
            Tuple com (is_valid, lista_de_erros)
        """
        errors = []

        # Verificar campos obrigatórios
        required_fields = ['value', 'date', 'source']
        for field in required_fields:
            if field not in data:
                errors.append(f"Campo obrigatório ausente: {field}")

        # Validar valor numérico
        if 'value' in data:
            try:
                value = float(data['value'])
                if value < 0:
                    errors.append("Valor econômico negativo pode indicar erro")
            except (ValueError, TypeError):
                errors.append("Valor não é numérico válido")

        # Validar data
        if 'date' in data:
            try:
                # Aceitar formatos dd/mm/yyyy ou yyyy-mm-dd
                date_str = str(data['date'])
                if '/' in date_str:
                    datetime.strptime(date_str, '%d/%m/%Y')
                else:
                    datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                errors.append("Formato de data inválido")

        return len(errors) == 0, errors

    @staticmethod
    def validate_chart_data(data: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Valida dados para geração de gráficos.

        Args:
            data: Lista de pontos de dados

        Returns:
            Tuple com (is_valid, lista_de_erros)
        """
        errors = []

        # Verificar se há dados suficientes
        if len(data) < 2:
            errors.append("Dados insuficientes para gráfico (mínimo 2 pontos)")

        # Verificar consistência dos dados
        for i, point in enumerate(data):
            if not isinstance(point, dict):
                errors.append(f"Ponto {i} não é um dicionário válido")
                continue

            # Verificar campos essenciais
            if 'x' not in point or 'y' not in point:
                errors.append(f"Ponto {i} missing 'x' or 'y' coordinates")

        return len(errors) == 0, errors

class ResponseFormatter:
    """Formatador de respostas para apresentação consistente"""

    @staticmethod
    def format_economic_data(data: Dict[str, Any], title: str = "") -> str:
        """
        Formata dados econômicos para apresentação.

        Args:
            data: Dados econômicos
            title: Título opcional

        Returns:
            String formatada para apresentação
        """
        output = []

        if title:
            output.append(f"📊 {title}")
            output.append("=" * len(title))

        # Formatar valor principal
        if 'value' in data:
            value = data['value']
            if isinstance(value, (int, float)):
                if value >= 1_000_000_000:
                    formatted_value = f"R$ {value/1_000_000_000:.2f} bilhões"
                elif value >= 1_000_000:
                    formatted_value = f"R$ {value/1_000_000:.2f} milhões"
                else:
                    formatted_value = f"R$ {value:,.2f}"
            else:
                formatted_value = str(value)

            output.append(f"💰 Valor: {formatted_value}")

        # Adicionar data se disponível
        if 'date' in data:
            output.append(f"📅 Data: {data['date']}")

        # Adicionar fonte
        if 'source' in data:
            output.append(f"📝 Fonte: {data['source']}")

        # Adicionar contexto adicional
        if 'context' in data:
            output.append(f"ℹ️  Contexto: {data['context']}")

        return "\n".join(output)

    @staticmethod
    def format_error_message(error: str, context: str = "") -> str:
        """
        Formata mensagens de erro de forma amigável.

        Args:
            error: Mensagem de erro
            context: Contexto adicional

        Returns:
            Mensagem formatada
        """
        output = ["❌ Erro identificado"]

        if context:
            output.append(f"📍 Contexto: {context}")

        output.append(f"🔍 Detalhes: {error}")
        output.append("💡 Dica: Tente reformular sua consulta ou verifique os dados")

        return "\n".join(output)

class CacheManager:
    """Gerenciador de cache simples para otimizar consultas repetidas"""

    def __init__(self, ttl_minutes: int = 30):
        """
        Inicializa o cache manager.

        Args:
            ttl_minutes: Tempo de vida do cache em minutos
        """
        self.cache = {}
        self.ttl_minutes = ttl_minutes

    def get(self, key: str) -> Optional[Any]:
        """
        Recupera item do cache se ainda válido.

        Args:
            key: Chave do cache

        Returns:
            Valor cached ou None se expirado/inexistente
        """
        if key in self.cache:
            data, timestamp = self.cache[key]

            # Verificar se ainda está válido
            if datetime.now() - timestamp < timedelta(minutes=self.ttl_minutes):
                logger.info(f"Cache hit para: {key}")
                return data
            else:
                # Remover item expirado
                del self.cache[key]
                logger.info(f"Cache expirado removido: {key}")

        return None

    def set(self, key: str, value: Any) -> None:
        """
        Armazena item no cache.

        Args:
            key: Chave do cache
            value: Valor para armazenar
        """
        self.cache[key] = (value, datetime.now())
        logger.info(f"Item adicionado ao cache: {key}")

    def clear(self) -> None:
        """Limpa todo o cache"""
        self.cache.clear()
        logger.info("Cache limpo completamente")

# Instância global do cache
cache_manager = CacheManager()

def generate_cache_key(agent_type: str, query: str) -> str:
    """
    Gera chave de cache baseada no tipo de agente e consulta.

    Args:
        agent_type: Tipo do agente ('research', 'chart', 'weather')  
        query: Consulta do usuário

    Returns:
        Chave de cache única
    """
    # Normalizar consulta para cache
    normalized_query = re.sub(r'\s+', ' ', query.lower().strip())

    # Gerar hash simples
    import hashlib
    query_hash = hashlib.md5(normalized_query.encode()).hexdigest()[:8]

    return f"{agent_type}:{query_hash}"

def log_agent_activity(agent_name: str, action: str, details: Dict[str, Any] = None):
    """
    Log estruturado das atividades dos agentes.

    Args:
        agent_name: Nome do agente
        action: Ação realizada
        details: Detalhes adicionais
    """
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'agent': agent_name,
        'action': action,
        'details': details or {}
    }

    logger.info(f"Agent Activity: {json.dumps(log_entry, ensure_ascii=False)}")

# Constantes úteis
BRAZILIAN_STATES = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
}

MAJOR_BRAZILIAN_CITIES = [
    'São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza',
    'Belo Horizonte', 'Manaus', 'Curitiba', 'Recife', 'Porto Alegre',
    'Belém', 'Goiânia', 'Guarulhos', 'Campinas', 'São Luís'
]
