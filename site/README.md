# Site — Erva Mate Timbó

Site de uma página, com pacotes de erva-mate em 3D que giram conforme a página rola.

## Como abrir

Abra `index.html` no navegador. Se as animações não aparecerem, sirva a pasta:

```bash
cd site
python3 -m http.server 8000
# depois abra http://localhost:8000
```

Tudo funciona offline. As animações (GSAP) e as fontes (Anton e Archivo) já estão dentro da pasta.

## Trocar os produtos

Edite **só o arquivo `produtos.js`**:

- `window.LOJA` guarda o nome, o slogan, o **WhatsApp** (só dígitos, com 55 + DDD), o Instagram, o e-mail e o endereço.
- `window.PRODUTOS` guarda a lista de pacotes. Cada um tem nome, linha, descrição, intensidade, moagem, selo, cores do pacote e tamanhos com preço.

> ⚠️ Os produtos e preços atuais são **exemplos**. Troque pelos pacotes reais da loja antes de publicar.

Os pacotes 3D são desenhados com o nome e as cores de cada produto, então não é preciso ter fotos.

## O que tem no site

1. **Abertura** com "Sabor forte" e o pacote 3D.
2. **Desperte a tradição / Um novo olhar sobre o mate**, onde o pacote gira e atravessa o texto ao rolar.
3. **Sem aditivos. Sem atalhos. Sem pressa.**: diferenciais da erva.
4. **Tradição & Origem**: as etapas da produção.
5. **Todas as nossas ervas**: catálogo com filtros (chimarrão, compostas, tererê, chá mate, kits), escolha de tamanho e sacola.
6. **Bora matear**: como preparar o chimarrão.
7. **Novidades + 10% off**: chamada de cadastro.

A sacola fica salva no navegador. O botão **Finalizar pelo WhatsApp** monta a mensagem com o pedido e o total.
Se `whatsapp` estiver vazio, o WhatsApp abre e a pessoa escolhe para quem enviar.

O formulário de novidades não tem servidor. Ele abre um e-mail para `LOJA.email`, ou, se não houver, uma mensagem no WhatsApp.
