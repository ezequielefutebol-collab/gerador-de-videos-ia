/*
 * ===================================================================
 *  CATÁLOGO DA LOJA — edite só este arquivo para trocar os produtos.
 * ===================================================================
 *
 *  ATENÇÃO: os produtos e preços abaixo são EXEMPLOS. Troque pelos
 *  pacotes e preços reais da loja antes de publicar o site.
 *
 *  Campos de cada produto:
 *    id          identificador único, sem espaços
 *    nome        nome que aparece no pacote e no card
 *    linha       "chimarrao" | "composta" | "terere" | "cha" | "kit"
 *    descricao   uma ou duas frases
 *    intensidade 1 (suave) a 5 (forte)
 *    moagem      texto livre (ex.: "Fina", "Grossa", "Folha")
 *    selo        etiqueta opcional no card (ex.: "Mais vendida") ou ""
 *    cor         cor principal do pacote (hex)
 *    corTexto    cor do texto no pacote (hex)
 *    tamanhos    lista de { peso, preco } — preco em reais (número)
 */

window.LOJA = {
  nome: "Erva Mate Timbó",
  slogan: "Erva-mate de verdade, do pé à cuia.",
  // Número do WhatsApp com DDI + DDD, só dígitos (ex.: "5547999999999").
  // Se ficar vazio, o pedido abre no WhatsApp para a pessoa escolher o contato.
  whatsapp: "",
  instagram: "",   // ex.: "lojaervamatetimbo"
  email: "",       // ex.: "contato@lojaervamatetimbo.com.br"
  endereco: "",    // ex.: "Rua Exemplo, 123 — Timbó/SC"
  site: "www.lojaervamatetimbo.com.br",
};

window.LINHAS = {
  chimarrao: "Chimarrão",
  composta: "Compostas",
  terere: "Tererê",
  cha: "Chá mate",
  kit: "Kits",
};

window.PRODUTOS = [
  // ---------------------------------------------------------- CHIMARRÃO
  {
    id: "tradicional",
    nome: "Tradicional",
    linha: "chimarrao",
    descricao: "A clássica do dia a dia: verde vivo, amargor equilibrado e espuma firme na cuia.",
    intensidade: 3, moagem: "Fina", selo: "Mais vendida",
    cor: "#2f7d32", corTexto: "#e9f56b",
    tamanhos: [{ peso: "500 g", preco: 14.9 }, { peso: "1 kg", preco: 24.9 }],
  },
  {
    id: "moida-grossa",
    nome: "Moída Grossa",
    linha: "chimarrao",
    descricao: "Mais folha e talo, entope menos a bomba e rende mais rodadas de chimarrão.",
    intensidade: 3, moagem: "Grossa", selo: "",
    cor: "#1f5c2a", corTexto: "#f4d35e",
    tamanhos: [{ peso: "500 g", preco: 15.9 }, { peso: "1 kg", preco: 26.9 }],
  },
  {
    id: "pura-folha",
    nome: "Pura Folha",
    linha: "chimarrao",
    descricao: "Só folhas selecionadas, sem palito. Sabor intenso e marcante do começo ao fim.",
    intensidade: 5, moagem: "Folha", selo: "Premium",
    cor: "#123d1c", corTexto: "#c9f26b",
    tamanhos: [{ peso: "500 g", preco: 19.9 }, { peso: "1 kg", preco: 34.9 }],
  },
  {
    id: "nativa",
    nome: "Nativa de Sombra",
    linha: "chimarrao",
    descricao: "Erva cultivada à sombra da mata: mais macia, adocicada e aromática.",
    intensidade: 2, moagem: "Média", selo: "",
    cor: "#4f8a3b", corTexto: "#fff3c4",
    tamanhos: [{ peso: "500 g", preco: 18.9 }, { peso: "1 kg", preco: 32.9 }],
  },
  {
    id: "suave",
    nome: "Suave",
    linha: "chimarrao",
    descricao: "Amargor leve para quem está começando a matear ou gosta de cuia o dia inteiro.",
    intensidade: 1, moagem: "Fina", selo: "",
    cor: "#8cc04b", corTexto: "#163b17",
    tamanhos: [{ peso: "500 g", preco: 13.9 }, { peso: "1 kg", preco: 23.9 }],
  },
  {
    id: "barbaqua",
    nome: "Barbaquá",
    linha: "chimarrao",
    descricao: "Secagem lenta na fumaça da lenha, do jeito antigo. Sabor tostado e defumado.",
    intensidade: 4, moagem: "Média", selo: "Artesanal",
    cor: "#5b3a1e", corTexto: "#f4d35e",
    tamanhos: [{ peso: "500 g", preco: 22.9 }, { peso: "1 kg", preco: 39.9 }],
  },
  {
    id: "organica",
    nome: "Orgânica",
    linha: "chimarrao",
    descricao: "Cultivo sem agrotóxicos, colheita manual. Leve, limpa e muito fresca.",
    intensidade: 2, moagem: "Fina", selo: "Orgânica",
    cor: "#6c9a2f", corTexto: "#fdf6e3",
    tamanhos: [{ peso: "500 g", preco: 24.9 }],
  },

  // ---------------------------------------------------------- COMPOSTAS
  {
    id: "composta-hortela",
    nome: "Composta Hortelã",
    linha: "composta",
    descricao: "Erva-mate com folhas de hortelã: refrescante e perfumada.",
    intensidade: 2, moagem: "Fina", selo: "",
    cor: "#1e8a6e", corTexto: "#eafff4",
    tamanhos: [{ peso: "500 g", preco: 16.9 }],
  },
  {
    id: "composta-camomila",
    nome: "Camomila & Erva-doce",
    linha: "composta",
    descricao: "Mistura calmante para o mate da noite, com notas florais e adocicadas.",
    intensidade: 1, moagem: "Fina", selo: "",
    cor: "#d9a521", corTexto: "#2b1d05",
    tamanhos: [{ peso: "500 g", preco: 16.9 }],
  },
  {
    id: "composta-ervas",
    nome: "Composta Ervas da Serra",
    linha: "composta",
    descricao: "Boldo, carqueja e cidreira com erva-mate. A receita da casa da vó.",
    intensidade: 3, moagem: "Fina", selo: "",
    cor: "#3c6e47", corTexto: "#ffe9a8",
    tamanhos: [{ peso: "500 g", preco: 17.9 }],
  },

  // ---------------------------------------------------------- TERERÊ
  {
    id: "terere-limao",
    nome: "Tererê Limão",
    linha: "terere",
    descricao: "Para tomar com água gelada: cítrico, refrescante e perfeito para o calor.",
    intensidade: 2, moagem: "Grossa", selo: "Verão",
    cor: "#c7e83a", corTexto: "#123d1c",
    tamanhos: [{ peso: "500 g", preco: 15.9 }],
  },
  {
    id: "terere-menta",
    nome: "Tererê Menta",
    linha: "terere",
    descricao: "Menta gelada com erva-mate grossa. Refresca de verdade.",
    intensidade: 2, moagem: "Grossa", selo: "",
    cor: "#25b49a", corTexto: "#06302a",
    tamanhos: [{ peso: "500 g", preco: 15.9 }],
  },
  {
    id: "terere-abacaxi",
    nome: "Tererê Abacaxi & Hortelã",
    linha: "terere",
    descricao: "Toque tropical de abacaxi com hortelã. Combina com suco gelado.",
    intensidade: 2, moagem: "Grossa", selo: "Novo",
    cor: "#f2b705", corTexto: "#1f3a12",
    tamanhos: [{ peso: "500 g", preco: 16.9 }],
  },
  {
    id: "terere-natural",
    nome: "Tererê Natural",
    linha: "terere",
    descricao: "Erva-mate pura em moagem grossa, sem aromas. Para montar o seu tererê.",
    intensidade: 3, moagem: "Grossa", selo: "",
    cor: "#3f9b3a", corTexto: "#fdf6e3",
    tamanhos: [{ peso: "500 g", preco: 14.9 }, { peso: "1 kg", preco: 25.9 }],
  },

  // ---------------------------------------------------------- CHÁ MATE
  {
    id: "cha-mate-tostado",
    nome: "Chá Mate Tostado",
    linha: "cha",
    descricao: "Folhas tostadas para chá quente ou gelado. Sabor encorpado, lembra café.",
    intensidade: 3, moagem: "Folha tostada", selo: "",
    cor: "#7a3e14", corTexto: "#ffd88a",
    tamanhos: [{ peso: "250 g", preco: 12.9 }],
  },
  {
    id: "cha-mate-limao",
    nome: "Chá Mate Limão",
    linha: "cha",
    descricao: "Mate tostado com raspas de limão. Clássico gelado da praia.",
    intensidade: 2, moagem: "Folha tostada", selo: "",
    cor: "#b5651d", corTexto: "#fff6cc",
    tamanhos: [{ peso: "250 g", preco: 13.9 }],
  },

  // ---------------------------------------------------------- KITS
  {
    id: "kit-degustacao",
    nome: "Kit Degustação",
    linha: "kit",
    descricao: "Quatro pacotes de 250 g (Tradicional, Pura Folha, Nativa e Barbaquá) para descobrir a sua favorita.",
    intensidade: 3, moagem: "Variada", selo: "Presente",
    cor: "#14301c", corTexto: "#e9f56b",
    tamanhos: [{ peso: "4 × 250 g", preco: 44.9 }],
  },
  {
    id: "kit-terere",
    nome: "Kit Tererê",
    linha: "kit",
    descricao: "Limão, Menta e Abacaxi & Hortelã, 500 g cada. O verão inteiro garantido.",
    intensidade: 2, moagem: "Grossa", selo: "",
    cor: "#ff6b2c", corTexto: "#1b1206",
    tamanhos: [{ peso: "3 × 500 g", preco: 42.9 }],
  },
];
