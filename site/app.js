(function () {
  "use strict";

  var LOJA = window.LOJA || {};
  var PREVIA = !!window.PREVIA; // prévia de design: pedidos e cadastro desativados
  var LINHAS = window.LINHAS || {};
  var PRODUTOS = window.PRODUTOS || [];
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };

  var moeda = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
  var reais = function (v) { return moeda.format(v); };
  var esc = function (t) {
    return String(t).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  var porId = {};
  PRODUTOS.forEach(function (p) { porId[p.id] = p; });

  /* ======================================================= PACOTE 3D */
  var FOLHA = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 4c9 6 11 20 0 32C9 24 11 10 20 4z" fill="currentColor"/><path d="M20 9v24" stroke="var(--cor)" stroke-width="1.6"/></svg>';

  function rotuloLinha(p) {
    return { chimarrao: "Para chimarrão", composto: "Chimarrão composto", terere: "Para tererê", cha: "Chá mate", fardo: "Fardo" }[p.linha] || "";
  }

  function montarPacote(el, p) {
    var curto = p.rotulo || p.nome;
    el.style.setProperty("--cor", p.cor);
    el.style.setProperty("--txt", p.corTexto);
    el.innerHTML =
      '<div class="face f-frente"><div class="rotulo">' +
        '<div class="rotulo-faixa">Erva-mate</div>' +
        '<div class="rotulo-emblema">' + FOLHA + "</div>" +
        '<div class="rotulo-marca">Timbó</div>' +
        '<div class="rotulo-nome">' + esc(curto) + "</div>" +
        '<div class="rotulo-linha">' + esc(rotuloLinha(p)) + "</div>" +
        (p.peso ? '<div class="rotulo-peso">' + esc(p.peso) + "</div>" : "") +
      "</div></div>" +
      '<div class="face f-costas"><div class="costas">' +
        "<strong>" + esc(curto) + "</strong>" +
        "<span>Conservar em local seco e fresco. Após aberto, manter bem fechado.</span>" +
        '<span class="codigo"></span>' +
      "</div></div>" +
      '<div class="face f-dir"><div class="lateral">Erva Mate Timbó</div></div>' +
      '<div class="face f-esq"><div class="lateral">' + esc(curto) + "</div></div>" +
      '<div class="face f-topo"><div class="dobra"></div></div>' +
      '<div class="face f-base"></div>';
  }

  montarPacote($("#pacote-heroi"), porId["tradicional-1kg"] || PRODUTOS[0]);
  montarPacote($("#pacote-novidades"), porId["capital-1kg"] || PRODUTOS[0]);

  /* ======================================================= CATÁLOGO */
  var grade = $("#grade");
  var filtros = $("#filtros");

  var contagem = {};
  PRODUTOS.forEach(function (p) { contagem[p.linha] = (contagem[p.linha] || 0) + 1; });
  $("#catalogo-resumo").textContent =
    PRODUTOS.length + " produtos: chimarrão tradicional, chimarrão composto, tererê, chá mate e compra em fardos.";

  var botoesFiltro = [{ k: "todas", t: "Todas", n: PRODUTOS.length }].concat(
    Object.keys(LINHAS).filter(function (k) { return contagem[k]; }).map(function (k) {
      return { k: k, t: LINHAS[k], n: contagem[k] };
    })
  );
  filtros.innerHTML = botoesFiltro.map(function (f, i) {
    return '<button class="filtro" type="button" data-filtro="' + f.k + '" aria-pressed="' + (i === 0) + '">' +
      esc(f.t) + "<small>" + f.n + "</small></button>";
  }).join("");

  var temPreco = function (p) { return typeof p.preco === "number"; };

  grade.innerHTML = PRODUTOS.map(function (p) {
    return '<article class="card" data-id="' + p.id + '" data-linha="' + p.linha + '" style="--cor:' + p.cor + '">' +
      '<div class="card-vitrine"><div class="pacote pacote-card"></div></div>' +
      '<p class="card-linha">' + esc(LINHAS[p.linha] || "") + (p.peso ? " · " + esc(p.peso) : "") + "</p>" +
      "<h3>" + esc(p.nome) + "</h3>" +
      '<div class="card-compra">' +
        (temPreco(p)
          ? '<span class="preco">' + reais(p.preco) + '</span><button class="add" type="button">Adicionar</button>'
          : '<span class="preco preco-consulta">Preço sob consulta</span>') +
      "</div>" +
    "</article>";
  }).join("");

  $$(".card", grade).forEach(function (card) { montarPacote($(".pacote", card), porId[card.dataset.id]); });

  grade.addEventListener("click", function (e) {
    var card = e.target.closest(".card");
    if (!card || !e.target.closest(".add")) return;
    adicionar(porId[card.dataset.id]);
  });

  filtros.addEventListener("click", function (e) {
    var b = e.target.closest(".filtro");
    if (!b) return;
    $$(".filtro", filtros).forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
    var k = b.dataset.filtro;
    $$(".card", grade).forEach(function (c) { c.hidden = !(k === "todas" || c.dataset.linha === k); });
    if (window.ScrollTrigger) window.ScrollTrigger.refresh();
  });

  /* ======================================================= SACOLA */
  var CHAVE = "timbo-sacola";
  var sacola = [];
  try { sacola = JSON.parse(localStorage.getItem(CHAVE)) || []; } catch (err) { sacola = []; }
  sacola = sacola.filter(function (i) { return porId[i.id] && temPreco(porId[i.id]) && i.qtd > 0; })
    .map(function (i) { return { id: i.id, qtd: i.qtd }; });

  function salvar() { try { localStorage.setItem(CHAVE, JSON.stringify(sacola)); } catch (err) { /* sem armazenamento */ } }

  function adicionar(p) {
    var item = sacola.find(function (i) { return i.id === p.id; });
    if (item) item.qtd += 1;
    else sacola.push({ id: p.id, qtd: 1 });
    salvar(); desenharSacola();
    var c = $("#contador"); c.classList.remove("pula"); void c.offsetWidth; c.classList.add("pula");
    avisar((p.rotulo || p.nome) + (p.peso ? " (" + p.peso + ")" : "") + " na sacola");
  }

  function total() { return sacola.reduce(function (s, i) { return s + porId[i.id].preco * i.qtd; }, 0); }

  function desenharSacola() {
    var qtd = sacola.reduce(function (s, i) { return s + i.qtd; }, 0);
    $("#contador").textContent = qtd;
    var lista = $("#sacola-itens");
    if (!sacola.length) {
      lista.innerHTML = '<li class="sacola-vazia">Sua sacola está vazia.<br>Bora escolher uma erva?</li>';
    } else {
      lista.innerHTML = sacola.map(function (i, n) {
        var p = porId[i.id];
        return '<li class="item">' +
          '<span class="item-cor" style="background:' + p.cor + '"></span>' +
          '<div><div class="item-nome">' + esc(p.nome) + '</div><div class="item-sub">' + reais(p.preco) + " cada</div>" +
          '<div class="qtd"><button type="button" data-menos="' + n + '" aria-label="Diminuir">−</button><span>' + i.qtd + '</span><button type="button" data-mais="' + n + '" aria-label="Aumentar">+</button></div></div>' +
          '<span class="item-preco">' + reais(p.preco * i.qtd) + "</span></li>";
      }).join("");
    }
    $("#sacola-total").textContent = reais(total());
    $("#finalizar").disabled = !sacola.length;
  }

  $("#sacola-itens").addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    if (b.dataset.mais) sacola[+b.dataset.mais].qtd += 1;
    if (b.dataset.menos) {
      var i = +b.dataset.menos;
      sacola[i].qtd -= 1;
      if (sacola[i].qtd <= 0) sacola.splice(i, 1);
    }
    salvar(); desenharSacola();
  });

  var painel = $("#sacola"), fundo = $("#sacola-fundo");
  function abrir() { painel.classList.add("aberta"); painel.setAttribute("aria-hidden", "false"); fundo.hidden = false; $("#fechar-sacola").focus(); }
  function fechar() { painel.classList.remove("aberta"); painel.setAttribute("aria-hidden", "true"); fundo.hidden = true; }
  $("#abrir-sacola").addEventListener("click", abrir);
  $("#fechar-sacola").addEventListener("click", fechar);
  fundo.addEventListener("click", fechar);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") fechar(); });

  function linkWhats(texto) {
    var num = String(LOJA.whatsapp || "").replace(/\D/g, "");
    return "https://wa.me/" + num + "?text=" + encodeURIComponent(texto);
  }

  $("#finalizar").addEventListener("click", function () {
    if (!sacola.length) return;
    if (PREVIA) { avisar("Prévia: pedidos desativados"); return; }
    var linhas = sacola.map(function (i) {
      return "• " + i.qtd + "× " + porId[i.id].nome + " — " + reais(porId[i.id].preco * i.qtd);
    });
    var msg = "Olá! Quero fazer um pedido na " + (LOJA.nome || "loja") + ":\n\n" + linhas.join("\n") + "\n\nTotal: " + reais(total());
    window.open(linkWhats(msg), "_blank", "noopener");
  });

  desenharSacola();

  /* ======================================================= AVISO */
  var aviso = $("#aviso"), avisoT;
  function avisar(t) {
    aviso.textContent = t; aviso.classList.add("mostra");
    clearTimeout(avisoT); avisoT = setTimeout(function () { aviso.classList.remove("mostra"); }, 2200);
  }

  /* ======================================================= NOVIDADES */
  $("#form-email").addEventListener("submit", function (e) {
    e.preventDefault();
    var email = $("#email").value.trim();
    var msg = $("#form-msg");
    if (PREVIA) { msg.textContent = "Prévia: cadastro desativado."; return; }
    if (LOJA.email) {
      location.href = "mailto:" + LOJA.email + "?subject=" + encodeURIComponent("Quero receber as novidades") +
        "&body=" + encodeURIComponent("Olá! Quero receber as novidades da loja no e-mail " + email + ".");
      msg.textContent = "Abrindo seu e-mail para confirmar…";
    } else if (LOJA.whatsapp) {
      window.open(linkWhats("Olá! Quero receber as novidades da loja. Meu e-mail: " + email), "_blank", "noopener");
      msg.textContent = "Abrindo o WhatsApp para confirmar…";
    } else {
      msg.textContent = "Cadastro de novidades em breve!";
    }
  });

  /* ======================================================= RODAPÉ */
  $("#ano").textContent = new Date().getFullYear();
  $("#rodape-slogan").textContent = LOJA.slogan || "";
  var contatos = [];
  if (LOJA.whatsapp) contatos.push('<a href="https://wa.me/' + String(LOJA.whatsapp).replace(/\D/g, "") + '" target="_blank" rel="noopener">WhatsApp</a>');
  if (LOJA.instagram) contatos.push('<a href="https://instagram.com/' + esc(LOJA.instagram) + '" target="_blank" rel="noopener">@' + esc(LOJA.instagram) + "</a>");
  if (LOJA.telefone) contatos.push("<span>" + esc(LOJA.telefone) + "</span>");
  if (LOJA.email) contatos.push('<a href="mailto:' + esc(LOJA.email) + '">' + esc(LOJA.email) + "</a>");
  if (LOJA.endereco) contatos.push("<span>" + esc(LOJA.endereco) + "</span>");
  if (LOJA.site && !PREVIA) contatos.push("<span>" + esc(LOJA.site) + "</span>");
  $("#rodape-contato").innerHTML = contatos.map(function (c) { return "<li>" + c + "</li>"; }).join("");

  /* ======================================================= TOPO */
  var topo = $(".topo");
  function marcarTopo() { topo.classList.toggle("rolou", window.scrollY > 40); }
  window.addEventListener("scroll", marcarTopo, { passive: true });
  marcarTopo();

  /* ======================================================= ANIMAÇÕES */
  var semMovimento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!window.gsap || !window.ScrollTrigger || semMovimento) return;

  var gsap = window.gsap;
  gsap.registerPlugin(window.ScrollTrigger);
  document.documentElement.classList.add("anim");

  var pacote = $("#pacote-heroi");
  var palco = $("#palco");

  // entrada
  gsap.from(".heroi .titulo-gigante", { yPercent: 40, opacity: 0, duration: 1.1, ease: "power4.out" });
  gsap.from(".heroi .subtitulo, .heroi .kicker, .linha-pontilhada", { y: 30, opacity: 0, duration: .9, delay: .25, stagger: .08, ease: "power3.out" });
  gsap.from("#palco-entra", { y: "60vh", rotationY: -200, duration: 1.6, ease: "power3.out" });

  var mm = gsap.matchMedia();
  mm.add({ largo: "(min-width: 901px)", estreito: "(max-width: 900px)" }, function (ctx) {
    var largo = ctx.conditions.largo;
    gsap.set(pacote, { y: largo ? "22vh" : "4vh", x: 0, rotationX: -8, rotationY: -24, rotationZ: 0, scale: 1 });

    var tl = gsap.timeline({
      defaults: { ease: "none" },
      scrollTrigger: { trigger: "#historia", start: "top top", end: "bottom bottom", scrub: 1 },
    });
    tl.to(pacote, { y: 0, rotationY: 200, rotationX: 12, rotationZ: -12, scale: largo ? 1.2 : 1.05, duration: 1.2 })
      .to(pacote, { x: largo ? "-20vw" : 0, y: largo ? 0 : "-14vh", rotationY: 330, rotationX: -58, rotationZ: 4, scale: .95, duration: 1.2 })
      .to(pacote, { x: largo ? "25vw" : 0, y: largo ? "4vh" : "12vh", rotationY: 384, rotationX: -6, rotationZ: 9, scale: 1.05, duration: 1.2 })
      .to(pacote, { duration: .3 });

    gsap.to(palco, {
      autoAlpha: 0, y: "-25vh", ease: "none",
      scrollTrigger: { trigger: ".faixa", start: "top bottom", end: "top 35%", scrub: true },
    });
  });

  // DESPERTE: linhas entram de lados opostos, eco desloca ao contrário
  var linhasD = $$(".desperte .titulo-gigante .linha-txt");
  gsap.fromTo(linhasD[0], { xPercent: -30 }, { xPercent: 8, ease: "none", scrollTrigger: { trigger: ".desperte", start: "top bottom", end: "bottom top", scrub: true } });
  gsap.fromTo(linhasD[1], { xPercent: 30 }, { xPercent: -8, ease: "none", scrollTrigger: { trigger: ".desperte", start: "top bottom", end: "bottom top", scrub: true } });
  gsap.fromTo(".eco", { yPercent: 12 }, { yPercent: -6, ease: "none", scrollTrigger: { trigger: ".desperte", start: "top bottom", end: "bottom top", scrub: true } });

  // NOVO OLHAR
  gsap.from(".olhar .linha-txt", { xPercent: -12, opacity: 0, stagger: .15, ease: "power3.out", duration: 1,
    scrollTrigger: { trigger: ".olhar", start: "top 65%" } });

  // SEM ATALHOS
  gsap.from(".qualidades li", { x: -40, opacity: 0, stagger: .12, duration: .8, ease: "power3.out", scrollTrigger: { trigger: ".sem", start: "top 60%" } });
  gsap.from(".sem-lista span", { yPercent: 100, opacity: 0, stagger: .15, duration: .9, ease: "power4.out", scrollTrigger: { trigger: ".sem-lista", start: "top 85%" } });

  // títulos genéricos
  $$(".revela").forEach(function (el) {
    if (el.closest(".heroi")) return;
    gsap.from(el, { y: 70, opacity: 0, duration: 1, ease: "power4.out", scrollTrigger: { trigger: el, start: "top 88%" } });
  });

  gsap.from(".processo li", { y: 30, opacity: 0, stagger: .08, duration: .7, ease: "power3.out", scrollTrigger: { trigger: ".processo", start: "top 88%" } });
  gsap.from(".tradicao-ilustra", { rotation: 14, y: 80, opacity: 0, duration: 1.1, ease: "power3.out", scrollTrigger: { trigger: ".tradicao-ilustra", start: "top 85%" } });
  gsap.from(".passos li", { y: 40, opacity: 0, stagger: .1, duration: .8, ease: "power3.out", scrollTrigger: { trigger: ".passos", start: "top 85%" } });

  window.ScrollTrigger.batch(".card", {
    start: "top 92%",
    onEnter: function (els) { gsap.from(els, { y: 50, opacity: 0, stagger: .07, duration: .7, ease: "power3.out", overwrite: true }); },
  });
})();
