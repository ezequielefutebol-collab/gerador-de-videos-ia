"""
Gerador de receitas e roteiros usando Claude AI.
Se não houver API key, usa banco de receitas embutido.
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


RECIPE_PROMPT = """Você é um chef profissional e roteirista de vídeos culinários para redes sociais.

Dado o nome de uma receita, crie um JSON completo com:
1. A receita detalhada
2. Um roteiro para vídeo vertical (TikTok/Reels/Shorts) de 45 a 75 segundos

RETORNE APENAS JSON VÁLIDO, sem texto adicional, no formato:
{
  "titulo": "Nome do prato",
  "descricao_curta": "Frase de impacto para o gancho (máx 15 palavras)",
  "tempo_total_min": 30,
  "porcoes": 4,
  "dificuldade": "Fácil",
  "ingredientes": [
    {"item": "farinha de trigo", "quantidade": "2 xícaras"},
    {"item": "ovos", "quantidade": "3 unidades"}
  ],
  "cenas": [
    {
      "id": 1,
      "tipo": "gancho",
      "duracao_seg": 5,
      "narracao": "Texto falado pelo narrador nesta cena",
      "descricao_visual": "O que deve aparecer na tela (para busca de imagens)",
      "busca_visual": "palavras-chave em inglês para buscar imagem/vídeo (ex: chocolate cake slice)",
      "efeito_sonoro": "nome do som (opcional: knife_cutting, frying, mixing, water_pour, etc)"
    }
  ],
  "musica_estilo": "upbeat cooking",
  "hashtags": ["#receita", "#comida", "#facil"]
}

Tipos de cena possíveis: gancho, ingredientes, preparacao, processo, detalhe, finalizacao, resultado, encerramento

A narração deve ser natural, animada e em português brasileiro.
Crie entre 6 e 10 cenas bem distribuídas.
Cada cena deve ter narração correspondente à ação visual.
"""


def gerar_receita_com_ia(nome_receita: str) -> dict:
    """Usa Claude para gerar a receita e roteiro."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": f"{RECIPE_PROMPT}\n\nReceita: {nome_receita}"
                }
            ]
        )

        texto = message.content[0].text.strip()
        # Remove markdown code blocks se presentes
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        if texto.endswith("```"):
            texto = texto.rsplit("```", 1)[0]

        return json.loads(texto.strip())

    except Exception as e:
        print(f"[IA] Erro ao gerar com Claude: {e}. Usando receita padrão.")
        return gerar_receita_fallback(nome_receita)


def gerar_receita_fallback(nome_receita: str) -> dict:
    """Receita padrão quando não há API key."""
    nome = nome_receita.strip().title()

    receitas_base = {
        "bolo de chocolate": {
            "titulo": "Bolo de Chocolate Irresistível",
            "descricao_curta": "O bolo de chocolate mais fácil e gostoso que você já viu!",
            "tempo_total_min": 50,
            "porcoes": 8,
            "dificuldade": "Fácil",
            "ingredientes": [
                {"item": "farinha de trigo", "quantidade": "2 xícaras"},
                {"item": "açúcar", "quantidade": "2 xícaras"},
                {"item": "cacau em pó", "quantidade": "3/4 xícara"},
                {"item": "ovos", "quantidade": "3 unidades"},
                {"item": "leite", "quantidade": "1 xícara"},
                {"item": "óleo", "quantidade": "1/2 xícara"},
                {"item": "água quente", "quantidade": "1 xícara"},
                {"item": "fermento em pó", "quantidade": "2 colheres de chá"}
            ],
            "cenas": [
                {
                    "id": 1, "tipo": "gancho", "duracao_seg": 5,
                    "narracao": "Olha só esse bolo de chocolate perfeito! Hoje você vai aprender a fazer em casa.",
                    "descricao_visual": "Fatia de bolo de chocolate com cobertura brilhante",
                    "busca_visual": "chocolate cake slice dark background",
                    "efeito_sonoro": ""
                },
                {
                    "id": 2, "tipo": "ingredientes", "duracao_seg": 6,
                    "narracao": "Você vai precisar de farinha, açúcar, cacau, ovos, leite, óleo e fermento. Bem simples!",
                    "descricao_visual": "Ingredientes organizados na bancada",
                    "busca_visual": "baking ingredients flat lay flour eggs",
                    "efeito_sonoro": ""
                },
                {
                    "id": 3, "tipo": "preparacao", "duracao_seg": 7,
                    "narracao": "Misture todos os secos: farinha, açúcar e cacau.",
                    "descricao_visual": "Peneirando farinha e cacau em uma tigela",
                    "busca_visual": "sifting flour cocoa powder mixing bowl",
                    "efeito_sonoro": "mixing"
                },
                {
                    "id": 4, "tipo": "processo", "duracao_seg": 7,
                    "narracao": "Adicione os ovos, o leite e o óleo. Misture bem até ficar homogêneo.",
                    "descricao_visual": "Quebrando ovos na tigela com massa escura",
                    "busca_visual": "adding eggs chocolate cake batter mixing",
                    "efeito_sonoro": "mixing"
                },
                {
                    "id": 5, "tipo": "processo", "duracao_seg": 6,
                    "narracao": "Por último, a água quente. Vai deixar a massa super úmida e fofinha!",
                    "descricao_visual": "Derramando água quente na massa de chocolate",
                    "busca_visual": "pouring water chocolate batter dark",
                    "efeito_sonoro": "water_pour"
                },
                {
                    "id": 6, "tipo": "detalhe", "duracao_seg": 7,
                    "narracao": "Despeje na forma untada e leve ao forno a 180 graus por 35 minutos.",
                    "descricao_visual": "Massa sendo despejada na forma de bolo",
                    "busca_visual": "chocolate cake batter pan oven ready",
                    "efeito_sonoro": ""
                },
                {
                    "id": 7, "tipo": "resultado", "duracao_seg": 7,
                    "narracao": "Veja que lindo! Chocolate derretido por cima deixa perfeito.",
                    "descricao_visual": "Cobertura de chocolate sendo derramada sobre o bolo",
                    "busca_visual": "chocolate ganache pouring over cake",
                    "efeito_sonoro": ""
                },
                {
                    "id": 8, "tipo": "encerramento", "duracao_seg": 5,
                    "narracao": "Salva essa receita e tenta em casa! Conta nos comentários como ficou!",
                    "descricao_visual": "Fatia de bolo no prato com garfo",
                    "busca_visual": "chocolate cake slice fork plate beautiful",
                    "efeito_sonoro": ""
                }
            ],
            "musica_estilo": "upbeat cooking background",
            "hashtags": ["#boloDeChocolate", "#receita", "#facil", "#chocolate"]
        }
    }

    chave = nome_receita.lower().strip()
    if chave in receitas_base:
        return receitas_base[chave]

    # Receita genérica para qualquer nome
    return {
        "titulo": nome,
        "descricao_curta": f"Aprenda a fazer {nome} em poucos minutos!",
        "tempo_total_min": 30,
        "porcoes": 4,
        "dificuldade": "Fácil",
        "ingredientes": [
            {"item": "ingrediente principal", "quantidade": "a gosto"},
            {"item": "temperos", "quantidade": "a gosto"},
            {"item": "acompanhamentos", "quantidade": "a gosto"}
        ],
        "cenas": [
            {
                "id": 1, "tipo": "gancho", "duracao_seg": 5,
                "narracao": f"Hoje vou te ensinar a fazer {nome} incrível! Fica do começo ao fim.",
                "descricao_visual": f"Prato de {nome} apetitoso",
                "busca_visual": f"{nome.lower()} food dish beautiful",
                "efeito_sonoro": ""
            },
            {
                "id": 2, "tipo": "ingredientes", "duracao_seg": 6,
                "narracao": "Veja os ingredientes que você vai precisar. Tudo bem simples!",
                "descricao_visual": "Ingredientes frescos organizados",
                "busca_visual": "fresh cooking ingredients kitchen counter",
                "efeito_sonoro": ""
            },
            {
                "id": 3, "tipo": "preparacao", "duracao_seg": 8,
                "narracao": "Começamos preparando todos os ingredientes. Capricha no corte!",
                "descricao_visual": "Preparação dos ingredientes",
                "busca_visual": "chef knife cutting vegetables kitchen",
                "efeito_sonoro": "knife_cutting"
            },
            {
                "id": 4, "tipo": "processo", "duracao_seg": 8,
                "narracao": "Agora vem a parte mais importante. Presta atenção nessa técnica.",
                "descricao_visual": "Cozinhando na panela",
                "busca_visual": "cooking pan stove heat food preparation",
                "efeito_sonoro": "frying"
            },
            {
                "id": 5, "tipo": "detalhe", "duracao_seg": 6,
                "narracao": "Veja esse detalhe. É o segredo para ficar perfeito!",
                "descricao_visual": "Detalhe do preparo",
                "busca_visual": "cooking detail close up food texture",
                "efeito_sonoro": ""
            },
            {
                "id": 6, "tipo": "resultado", "duracao_seg": 7,
                "narracao": f"Pronto! Olha que {nome} incrível! Ficou perfeito!",
                "descricao_visual": f"{nome} finalizado e pronto para servir",
                "busca_visual": f"{nome.lower()} finished plate served restaurant",
                "efeito_sonoro": ""
            },
            {
                "id": 7, "tipo": "encerramento", "duracao_seg": 5,
                "narracao": "Salva essa receita! Me conta nos comentários se ficou bom!",
                "descricao_visual": "Prato finalizado com apresentação perfeita",
                "busca_visual": "beautiful food plating close up",
                "efeito_sonoro": ""
            }
        ],
        "musica_estilo": "upbeat cooking music",
        "hashtags": [f"#{nome.replace(' ', '')}", "#receita", "#comida", "#facil"]
    }


def gerar_receita(nome_receita: str) -> dict:
    """Ponto de entrada principal."""
    if config.ANTHROPIC_API_KEY:
        print(f"[Receita] Gerando com Claude AI: {nome_receita}")
        return gerar_receita_com_ia(nome_receita)
    else:
        print(f"[Receita] Usando banco de receitas: {nome_receita}")
        return gerar_receita_fallback(nome_receita)
