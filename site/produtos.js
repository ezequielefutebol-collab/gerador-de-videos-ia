/*
 * ===================================================================
 *  CATÁLOGO DA LOJA — edite só este arquivo para trocar os produtos.
 * ===================================================================
 *
 *  Nomes copiados das páginas de lojaervamatetimbo.com.br indexadas
 *  pelo buscador (nov/2026). Os preços preenchidos vieram dos trechos
 *  do buscador e podem estar desatualizados; os marcados com null não
 *  apareceram em nenhum trecho e mostram "Preço sob consulta".
 *  CONFIRA cada preço na loja antes de publicar.
 *
 *  Campos de cada produto:
 *    id        identificador único, sem espaços
 *    nome      nome do produto, como está na loja
 *    rotulo    nome curto impresso no pacote 3D
 *    linha     "chimarrao" | "composto" | "terere" | "cha" | "fardo"
 *    peso      peso/quantidade
 *    preco     preço em reais (número) ou null se não souber
 *    cor       cor principal do pacote (hex)
 *    corTexto  cor do texto no pacote (hex)
 */

window.LOJA = {
  nome: "Erva Mate Timbó",
  slogan: "Erva-mate para chimarrão e tererê. Desde 1980, vendendo para todo o Brasil.",
  // Número do WhatsApp com DDI + DDD, só dígitos (ex.: "5547999999999").
  whatsapp: "",
  telefone: "(47) 3622-4558", // telefone de revenda que aparece nas páginas da loja
  instagram: "",
  email: "",
  endereco: "",
  site: "www.lojaervamatetimbo.com.br",
};

window.LINHAS = {
  chimarrao: "Chimarrão Tradicional",
  composto: "Chimarrão Composto",
  terere: "Tererê",
  cha: "Chá mate",
  fardo: "Compra em Fardos",
};

window.PRODUTOS = [
  // ------------------------------------------------ CHIMARRÃO TRADICIONAL
  { id: "tradicional-1kg", nome: "Erva Mate Chimarrão Tradicional 1kg", rotulo: "Tradicional",
    linha: "chimarrao", peso: "1 kg", preco: 13.5, cor: "#2f7d32", corTexto: "#e9f56b" },
  { id: "tradicional-500g", nome: "Erva Mate Chimarrão Tradicional 500g", rotulo: "Tradicional",
    linha: "chimarrao", peso: "500 g", preco: 7.0, cor: "#2f7d32", corTexto: "#e9f56b" },
  { id: "moida-grossa-1kg", nome: "Erva Mate Chimarrão Moída Grossa 1kg", rotulo: "Moída Grossa",
    linha: "chimarrao", peso: "1 kg", preco: 13.5, cor: "#1f5c2a", corTexto: "#f4d35e" },
  { id: "grossa-1kg", nome: "Erva-Mate Chimarrão Grossa 1kg", rotulo: "Grossa",
    linha: "chimarrao", peso: "1 kg", preco: 10.6, cor: "#3f7a2a", corTexto: "#fff3c4" },
  { id: "capital-1kg", nome: "Erva Mate Chimarrão Capital 1kg", rotulo: "Capital",
    linha: "chimarrao", peso: "1 kg", preco: 12.7, cor: "#123d1c", corTexto: "#c9f26b" },

  // ------------------------------------------------ CHIMARRÃO COMPOSTO
  { id: "composto-500g", nome: "Erva Mate Chimarrão Composto 500g", rotulo: "Composto",
    linha: "composto", peso: "500 g", preco: 11.0, cor: "#3c6e47", corTexto: "#ffe9a8" },
  { id: "magrimate-500g", nome: "Composto de Erva-Mate Magrimate 500g", rotulo: "Magrimate",
    linha: "composto", peso: "500 g", preco: 13.0, cor: "#c2185b", corTexto: "#fff0f5" },
  { id: "menta-500g", nome: "Composto de Erva Mate Sabor Menta - 500g", rotulo: "Sabor Menta",
    linha: "composto", peso: "500 g", preco: 12.4, cor: "#1e8a6e", corTexto: "#eafff4" },
  { id: "citrus-500g", nome: "Composto de Erva-Mate Citrus 500g", rotulo: "Citrus",
    linha: "composto", peso: "500 g", preco: null, cor: "#f2b705", corTexto: "#1f3a12" },

  // ------------------------------------------------ TERERÊ
  { id: "terere-natural-500g", nome: "Composto de Tererê Natural 500g", rotulo: "Tererê Natural",
    linha: "terere", peso: "500 g", preco: 8.5, cor: "#3f9b3a", corTexto: "#fdf6e3" },
  { id: "terere-limao-menta-500g", nome: "Composto de Tererê Limão e Menta 500g", rotulo: "Tererê Limão e Menta",
    linha: "terere", peso: "500 g", preco: null, cor: "#c7e83a", corTexto: "#123d1c" },
  { id: "terere-abacaxi-500g", nome: "Composto de Tererê Abacaxi 500g", rotulo: "Tererê Abacaxi",
    linha: "terere", peso: "500 g", preco: null, cor: "#f2a900", corTexto: "#1f3a12" },
  { id: "terere-boldo-menta-500g", nome: "Composto de Tererê Boldo e Menta 500g", rotulo: "Tererê Boldo e Menta",
    linha: "terere", peso: "500 g", preco: null, cor: "#25b49a", corTexto: "#06302a" },
  { id: "combo-terere", nome: "Combo 2 Unidades - Composto de Tererê Abacaxi + Composto de Tererê Limão e Menta 500g",
    rotulo: "Combo Tererê", linha: "terere", peso: "2 × 500 g", preco: null, cor: "#ff6b2c", corTexto: "#1b1206" },

  // ------------------------------------------------ CHÁ MATE
  { id: "cha-mate-tostado", nome: "Chá mate Tostado Timbó", rotulo: "Chá Mate Tostado",
    linha: "cha", peso: "", preco: null, cor: "#7a3e14", corTexto: "#ffd88a" },

  // ------------------------------------------------ COMPRA EM FARDOS
  { id: "fardo-tradicional", nome: "Erva-Mate Chimarrão Tradicional - Fardo com 10x1Kg", rotulo: "Tradicional",
    linha: "fardo", peso: "10 × 1 kg", preco: null, cor: "#2f7d32", corTexto: "#e9f56b" },
  { id: "fardo-grossa", nome: "Erva-Mate Chimarrão Grossa - Fardo com 5x1Kg", rotulo: "Grossa",
    linha: "fardo", peso: "5 × 1 kg", preco: null, cor: "#3f7a2a", corTexto: "#fff3c4" },
  { id: "fardo-moida-grossa", nome: "Erva Mate Chimarrão Moída Grossa - Fardo com 10x500g", rotulo: "Moída Grossa",
    linha: "fardo", peso: "10 × 500 g", preco: null, cor: "#1f5c2a", corTexto: "#f4d35e" },
  { id: "fardo-safra-inverno", nome: "Erva Mate Chimarrão Safra de Inverno - Fardo com 10x1Kg", rotulo: "Safra de Inverno",
    linha: "fardo", peso: "10 × 1 kg", preco: null, cor: "#1b3a5c", corTexto: "#e6f1ff" },
  { id: "fardo-composto", nome: "Combo 10 Unidades - Erva Mate Chimarrão Composto 10 x 500g", rotulo: "Composto",
    linha: "fardo", peso: "10 × 500 g", preco: null, cor: "#3c6e47", corTexto: "#ffe9a8" },
  { id: "fardo-citrus", nome: "Composto de Erva-Mate Citrus - 10 Unidades x 500g", rotulo: "Citrus",
    linha: "fardo", peso: "10 × 500 g", preco: null, cor: "#f2b705", corTexto: "#1f3a12" },
  { id: "fardo-menta", nome: "Composto de Erva-Mate Sabor Menta 10 Unidades x 500g", rotulo: "Sabor Menta",
    linha: "fardo", peso: "10 × 500 g", preco: 120.0, cor: "#1e8a6e", corTexto: "#eafff4" },
  { id: "fardo-terere-limao-menta", nome: "Composto de Tererê Limão e Menta - Fardo com 10x500g", rotulo: "Tererê Limão e Menta",
    linha: "fardo", peso: "10 × 500 g", preco: null, cor: "#c7e83a", corTexto: "#123d1c" },
  { id: "fardo-terere-abacaxi", nome: "Composto de Tererê Abacaxi - Fardo com 10x500g", rotulo: "Tererê Abacaxi",
    linha: "fardo", peso: "10 × 500 g", preco: null, cor: "#f2a900", corTexto: "#1f3a12" },
];
