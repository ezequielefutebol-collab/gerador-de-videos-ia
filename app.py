"""
Interface web do Gerador de Vídeos de Receitas.
Acesse http://localhost:5000 após iniciar.
"""
import os
import sys
import json
import threading
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template_string

sys.path.insert(0, os.path.dirname(__file__))
import config
from src.pipeline import executar_pipeline

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB

# Armazena status dos jobs em andamento
JOBS = {}

# ─────────────────────────────────────────────────────────────
# HTML DA INTERFACE (embutido para facilidade de uso)
# ─────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gerador de Vídeos de Receitas</title>
<style>
  :root {
    --bg: #0a0a0f;
    --surface: #13131a;
    --surface2: #1c1c28;
    --accent: #ff6b35;
    --accent2: #ffd700;
    --text: #f0f0f0;
    --text-muted: #888;
    --success: #4caf50;
    --radius: 16px;
  }

  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .hero {
    width: 100%;
    padding: 60px 20px 40px;
    text-align: center;
    background: linear-gradient(135deg, #0a0a0f 0%, #1a0f05 50%, #0a0a0f 100%);
    border-bottom: 1px solid #2a2a3a;
  }

  .hero h1 {
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 900;
    background: linear-gradient(135deg, #ff6b35, #ffd700, #ff6b35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 12px;
  }

  .hero p {
    color: var(--text-muted);
    font-size: 1.1rem;
    max-width: 500px;
    margin: 0 auto;
  }

  .container {
    width: 100%;
    max-width: 760px;
    padding: 40px 20px;
  }

  .card {
    background: var(--surface);
    border: 1px solid #2a2a3a;
    border-radius: var(--radius);
    padding: 32px;
    margin-bottom: 24px;
  }

  .input-group {
    display: flex;
    gap: 12px;
    margin-top: 20px;
    flex-wrap: wrap;
  }

  .input-group input {
    flex: 1;
    min-width: 200px;
    background: var(--surface2);
    border: 2px solid #2a2a3a;
    border-radius: 12px;
    padding: 16px 20px;
    color: var(--text);
    font-size: 1.05rem;
    outline: none;
    transition: border-color 0.2s;
  }

  .input-group input:focus {
    border-color: var(--accent);
  }

  .input-group input::placeholder {
    color: var(--text-muted);
  }

  .btn {
    background: linear-gradient(135deg, var(--accent), #e55a2b);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 16px 28px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255,107,53,0.4); }
  .btn:active { transform: translateY(0); }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

  .btn-secondary {
    background: var(--surface2);
    border: 2px solid #3a3a4a;
  }
  .btn-secondary:hover { border-color: var(--accent); box-shadow: none; }

  .sugestoes {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 16px;
  }

  .sugestao {
    background: var(--surface2);
    border: 1px solid #3a3a4a;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;
    color: var(--text-muted);
  }

  .sugestao:hover {
    border-color: var(--accent2);
    color: var(--accent2);
  }

  .progress-section {
    display: none;
  }

  .progress-section.ativo {
    display: block;
  }

  .progress-bar-bg {
    background: var(--surface2);
    border-radius: 100px;
    height: 8px;
    margin: 16px 0 8px;
    overflow: hidden;
  }

  .progress-bar-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    width: 0%;
    transition: width 0.4s ease;
  }

  .etapas {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .etapa {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--text-muted);
    font-size: 0.95rem;
    padding: 10px 14px;
    border-radius: 10px;
    background: var(--surface2);
    transition: all 0.3s;
  }

  .etapa.ativa {
    color: var(--accent2);
    background: rgba(255, 215, 0, 0.08);
    border: 1px solid rgba(255, 215, 0, 0.2);
  }

  .etapa.concluida {
    color: var(--success);
    background: rgba(76, 175, 80, 0.08);
  }

  .etapa-icon {
    font-size: 1.2rem;
    min-width: 24px;
    text-align: center;
  }

  .resultado-section {
    display: none;
  }

  .resultado-section.ativo {
    display: block;
  }

  .video-wrapper {
    position: relative;
    width: 100%;
    max-width: 340px;
    margin: 0 auto;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
  }

  .video-wrapper video {
    width: 100%;
    display: block;
    aspect-ratio: 9/16;
    background: #000;
  }

  .resultado-info {
    text-align: center;
    margin-top: 20px;
  }

  .resultado-titulo {
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--accent2);
    margin-bottom: 8px;
  }

  .resultado-meta {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 24px;
  }

  .botoes-resultado {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .erro-section {
    display: none;
    background: rgba(255, 50, 50, 0.1);
    border: 1px solid rgba(255, 50, 50, 0.3);
    border-radius: 12px;
    padding: 20px;
    color: #ff8080;
  }

  .erro-section.ativo {
    display: block;
  }

  .config-info {
    background: rgba(255, 215, 0, 0.05);
    border: 1px solid rgba(255, 215, 0, 0.2);
    border-radius: 12px;
    padding: 20px;
    margin-top: 16px;
    font-size: 0.9rem;
    color: var(--text-muted);
  }

  .config-info strong { color: var(--accent2); }
  .config-info a { color: var(--accent); }

  .api-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 12px;
  }

  .api-row label {
    min-width: 110px;
    font-weight: 600;
    color: var(--text);
    font-size: 0.9rem;
  }

  .api-row input[type="text"],
  .api-row input[type="password"] {
    flex: 1;
    background: var(--surface2);
    border: 1px solid #3a3a4a;
    border-radius: 8px;
    padding: 9px 12px;
    color: var(--text);
    font-size: 0.85rem;
    font-family: monospace;
    outline: none;
  }

  .api-row input:focus { border-color: var(--accent2); }

  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .badge-ok  { background: rgba(76,175,80,0.2); color: #81c784; border: 1px solid #4caf50; }
  .badge-off { background: rgba(255,255,255,0.05); color: #888; border: 1px solid #444; }

  .btn-sm {
    padding: 8px 14px;
    font-size: 0.82rem;
    border-radius: 8px;
    white-space: nowrap;
  }

  .spinner {
    display: inline-block;
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255,107,53,0.3);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-right: 8px;
    vertical-align: middle;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .msg-status {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.95rem;
    min-height: 24px;
    margin-top: 4px;
  }

  h2 { font-size: 1.3rem; margin-bottom: 4px; }
  .sub { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 8px; }

  footer {
    padding: 40px 20px;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.85rem;
  }
</style>
</head>
<body>

<div class="hero">
  <h1>🎬 Gerador de Vídeos</h1>
  <p>Digite o nome de uma receita e gere um vídeo profissional para TikTok, Reels e Shorts</p>
</div>

<div class="container">

  <!-- CARD DE ENTRADA -->
  <div class="card" id="card-entrada">
    <h2>Nova receita</h2>
    <p class="sub">Qual receita você quer transformar em vídeo?</p>

    <div class="input-group">
      <input type="text" id="input-receita"
             placeholder="Ex: Bolo de chocolate, Lasanha, Pizza..."
             maxlength="80"
             onkeydown="if(event.key==='Enter') gerarVideo()">
      <button class="btn" id="btn-gerar" onclick="gerarVideo()">
        🎬 Gerar Vídeo
      </button>
    </div>

    <div class="sugestoes">
      <span style="color:var(--text-muted); font-size:0.85rem; align-self:center;">Sugestões:</span>
      <div class="sugestao" onclick="usarSugestao(this)">Bolo de chocolate</div>
      <div class="sugestao" onclick="usarSugestao(this)">Hambúrguer artesanal</div>
      <div class="sugestao" onclick="usarSugestao(this)">Pizza caseira</div>
      <div class="sugestao" onclick="usarSugestao(this)">Frango crocante</div>
      <div class="sugestao" onclick="usarSugestao(this)">Pudim</div>
      <div class="sugestao" onclick="usarSugestao(this)">Lasanha à bolonhesa</div>
    </div>

    <div class="config-info">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px; flex-wrap:wrap">
        <strong>⚡ Modo atual:</strong>
        <span id="modo-atual" style="color:var(--text)">Verificando...</span>
      </div>

      <!-- Pexels API Key -->
      <div class="api-row">
        <label>
          <span id="badge-pexels" class="badge badge-off">OFF</span>
          Pexels
        </label>
        <input type="password" id="input-pexels" placeholder="Cole sua Pexels API Key aqui...">
        <button class="btn btn-sm" onclick="salvarKey('pexels')">Ativar</button>
      </div>
      <div style="font-size:0.78rem; margin:4px 0 10px 120px; color:#666">
        Vídeos e fotos reais de alta qualidade ·
        <a href="https://www.pexels.com/api/" target="_blank">pexels.com/api</a> (gratuito)
      </div>

      <!-- Claude API Key -->
      <div class="api-row">
        <label>
          <span id="badge-claude" class="badge badge-off">OFF</span>
          Claude AI
        </label>
        <input type="password" id="input-claude" placeholder="Cole sua Anthropic API Key aqui...">
        <button class="btn btn-sm" onclick="salvarKey('claude')">Ativar</button>
      </div>
      <div style="font-size:0.78rem; margin:4px 0 0 120px; color:#666">
        Receitas geradas por IA para qualquer prato ·
        <a href="https://console.anthropic.com/" target="_blank">console.anthropic.com</a>
      </div>

      <div id="msg-config" style="margin-top:10px; font-size:0.85rem; min-height:18px; color:var(--success)"></div>
    </div>
  </div>

  <!-- CARD DE PROGRESSO -->
  <div class="card progress-section" id="card-progresso">
    <h2><span class="spinner" id="spinner"></span>Produzindo vídeo...</h2>
    <p class="sub" id="nome-receita-ativo"></p>

    <div class="progress-bar-bg">
      <div class="progress-bar-fill" id="progress-bar"></div>
    </div>
    <div class="msg-status" id="msg-progresso">Iniciando...</div>

    <div class="etapas" id="etapas-lista">
      <div class="etapa" id="etapa-1"><span class="etapa-icon">📝</span> Criando receita e roteiro</div>
      <div class="etapa" id="etapa-2"><span class="etapa-icon">🎙️</span> Gerando narração por voz</div>
      <div class="etapa" id="etapa-3"><span class="etapa-icon">🎵</span> Compondo trilha sonora</div>
      <div class="etapa" id="etapa-4"><span class="etapa-icon">🎥</span> Baixando vídeos/fotos (Pexels)</div>
      <div class="etapa" id="etapa-5"><span class="etapa-icon">✂️</span> Editando e sincronizando</div>
      <div class="etapa" id="etapa-6"><span class="etapa-icon">🎬</span> Renderizando vídeo final</div>
    </div>
  </div>

  <!-- CARD DE ERRO -->
  <div class="erro-section" id="card-erro">
    <h3>❌ Erro ao gerar vídeo</h3>
    <p id="msg-erro" style="margin-top:8px"></p>
    <button class="btn btn-secondary" onclick="resetar()" style="margin-top:16px">Tentar novamente</button>
  </div>

  <!-- CARD DE RESULTADO -->
  <div class="card resultado-section" id="card-resultado">
    <div class="resultado-info">
      <div class="resultado-titulo" id="resultado-titulo"></div>
      <div class="resultado-meta" id="resultado-meta"></div>
    </div>

    <div class="video-wrapper">
      <video id="video-player" controls playsinline>
        Seu navegador não suporta vídeo HTML5.
      </video>
    </div>

    <div class="botoes-resultado" style="margin-top:24px">
      <a id="btn-download" class="btn" download>
        ⬇️ Baixar Vídeo
      </a>
      <button class="btn btn-secondary" onclick="resetar()">
        🔄 Gerar outra receita
      </button>
    </div>
  </div>

</div>

<footer>
  Gerador de Vídeos de Receitas · Powered by Claude AI + Edge TTS + FFmpeg
</footer>

<script>
let jobId = null;
let pollTimer = null;

async function verificarModo() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    document.getElementById('modo-atual').textContent =
      d.modo_descricao || 'modo básico';

    // Atualiza badges
    const bp = document.getElementById('badge-pexels');
    const bc = document.getElementById('badge-claude');
    if (d.tem_pexels) {
      bp.textContent = 'ON';
      bp.className = 'badge badge-ok';
    } else {
      bp.textContent = 'OFF';
      bp.className = 'badge badge-off';
    }
    if (d.tem_claude) {
      bc.textContent = 'ON';
      bc.className = 'badge badge-ok';
    } else {
      bc.textContent = 'OFF';
      bc.className = 'badge badge-off';
    }
  } catch(e) {}
}

async function salvarKey(tipo) {
  const campo = tipo === 'pexels'
    ? document.getElementById('input-pexels')
    : document.getElementById('input-claude');

  const val = campo.value.trim();
  if (!val) { campo.focus(); return; }

  const body = tipo === 'pexels'
    ? { pexels_key: val }
    : { anthropic_key: val };

  try {
    const r = await fetch('/api/configurar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const d = await r.json();
    if (d.ok) {
      campo.value = '';
      campo.placeholder = '✓ Key salva!';
      setTimeout(() => {
        campo.placeholder = tipo === 'pexels'
          ? 'Cole sua Pexels API Key aqui...'
          : 'Cole sua Anthropic API Key aqui...';
      }, 3000);
      document.getElementById('msg-config').textContent =
        `✅ ${tipo === 'pexels' ? 'Pexels' : 'Claude AI'} ativado com sucesso!`;
      await verificarModo();
    }
  } catch(e) {
    document.getElementById('msg-config').textContent = '❌ Erro ao salvar key.';
  }
}

function usarSugestao(el) {
  document.getElementById('input-receita').value = el.textContent;
  document.getElementById('input-receita').focus();
}

async function gerarVideo() {
  const receita = document.getElementById('input-receita').value.trim();
  if (!receita) {
    document.getElementById('input-receita').focus();
    return;
  }

  // Reset estado
  document.getElementById('card-erro').classList.remove('ativo');
  document.getElementById('card-resultado').classList.remove('ativo');

  // Mostra progresso
  document.getElementById('card-progresso').classList.add('ativo');
  document.getElementById('btn-gerar').disabled = true;
  document.getElementById('nome-receita-ativo').textContent = receita;

  // Reset etapas
  for (let i=1; i<=6; i++) {
    document.getElementById(`etapa-${i}`).className = 'etapa';
  }

  try {
    const resp = await fetch('/api/gerar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ receita })
    });
    const data = await resp.json();
    jobId = data.job_id;
    pollTimer = setInterval(verificarProgresso, 1200);
  } catch(e) {
    mostrarErro('Falha ao conectar com o servidor: ' + e.message);
  }
}

async function verificarProgresso() {
  if (!jobId) return;
  try {
    const resp = await fetch(`/api/progresso/${jobId}`);
    const data = await resp.json();

    atualizarUI(data);

    if (data.status === 'concluido' || data.status === 'erro') {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  } catch(e) {
    console.error(e);
  }
}

function atualizarUI(data) {
  const p = data.progresso || 0;
  document.getElementById('progress-bar').style.width = (p * 100) + '%';
  document.getElementById('msg-progresso').textContent = data.mensagem || '';

  // Destaca etapa atual
  const etapas = [
    [0.0, 0.08],
    [0.08, 0.22],
    [0.22, 0.32],
    [0.32, 0.72],
    [0.72, 0.85],
    [0.85, 1.0],
  ];
  for (let i=0; i<etapas.length; i++) {
    const el = document.getElementById(`etapa-${i+1}`);
    const [min, max] = etapas[i];
    if (p >= max) {
      el.className = 'etapa concluida';
      el.querySelector('.etapa-icon').textContent = '✅';
    } else if (p >= min) {
      el.className = 'etapa ativa';
    }
  }

  if (data.status === 'concluido') {
    document.getElementById('card-progresso').classList.remove('ativo');
    document.getElementById('spinner').style.display = 'none';
    mostrarResultado(data);
  } else if (data.status === 'erro') {
    document.getElementById('card-progresso').classList.remove('ativo');
    mostrarErro(data.erro || 'Erro desconhecido');
  }
}

function mostrarResultado(data) {
  document.getElementById('card-resultado').classList.add('ativo');
  document.getElementById('resultado-titulo').textContent = data.titulo || 'Vídeo criado!';

  const dur = data.duracao ? Math.round(data.duracao) + 's' : '';
  document.getElementById('resultado-meta').textContent =
    `✅ Vídeo gerado com sucesso! ${dur ? '• Duração: ' + dur : ''}`;

  const videoUrl = `/api/video/${data.filename}`;
  const player = document.getElementById('video-player');
  player.src = videoUrl;
  player.load();

  const dl = document.getElementById('btn-download');
  dl.href = videoUrl;
  dl.download = data.filename;
}

function mostrarErro(msg) {
  document.getElementById('card-erro').classList.add('ativo');
  document.getElementById('msg-erro').textContent = msg;
  document.getElementById('btn-gerar').disabled = false;
}

function resetar() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
  jobId = null;
  document.getElementById('card-progresso').classList.remove('ativo');
  document.getElementById('card-resultado').classList.remove('ativo');
  document.getElementById('card-erro').classList.remove('ativo');
  document.getElementById('btn-gerar').disabled = false;
  document.getElementById('progress-bar').style.width = '0%';
  document.getElementById('spinner').style.display = '';
  document.getElementById('input-receita').value = '';
  document.getElementById('input-receita').focus();
}

// Inicializa
verificarModo();
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────
# ROTAS DA API
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/status")
def api_status():
    tem_claude = bool(config.ANTHROPIC_API_KEY)
    tem_pexels = bool(config.PEXELS_API_KEY)

    if tem_claude and tem_pexels:
        modo = "IA completa — Claude AI + vídeos/fotos Pexels"
    elif tem_claude:
        modo = "Claude AI ativo — sem imagens Pexels"
    elif tem_pexels:
        modo = "Imagens Pexels ativas — sem Claude AI"
    else:
        modo = "modo básico — configure as API keys para qualidade máxima"

    return jsonify({
        "tem_claude": tem_claude,
        "tem_pexels": tem_pexels,
        "modo_descricao": modo
    })


@app.route("/api/configurar", methods=["POST"])
def api_configurar():
    """Define API keys em runtime sem reiniciar o servidor."""
    data = request.get_json() or {}

    if "pexels_key" in data:
        nova = data["pexels_key"].strip()
        config.PEXELS_API_KEY = nova
        os.environ["PEXELS_API_KEY"] = nova

    if "anthropic_key" in data:
        nova = data["anthropic_key"].strip()
        config.ANTHROPIC_API_KEY = nova
        os.environ["ANTHROPIC_API_KEY"] = nova

    return jsonify({"ok": True})


@app.route("/api/gerar", methods=["POST"])
def api_gerar():
    data = request.get_json()
    nome_receita = (data or {}).get("receita", "").strip()

    if not nome_receita:
        return jsonify({"erro": "Nome da receita não informado"}), 400

    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {
        "status": "processando",
        "progresso": 0.0,
        "mensagem": "Iniciando...",
        "titulo": nome_receita,
        "filename": None,
        "duracao": 0,
        "erro": None
    }

    # Executa em thread separada
    t = threading.Thread(
        target=_executar_job,
        args=(job_id, nome_receita),
        daemon=True
    )
    t.start()

    return jsonify({"job_id": job_id})


@app.route("/api/progresso/<job_id>")
def api_progresso(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"status": "erro", "erro": "Job não encontrado"}), 404
    return jsonify(job)


@app.route("/api/video/<filename>")
def api_video(filename):
    # Segurança: apenas arquivos MP4 do diretório output
    if not filename.endswith(".mp4") or "/" in filename or ".." in filename:
        return "Arquivo inválido", 400

    video_path = os.path.join(config.OUTPUT_DIR, filename)
    if not os.path.exists(video_path):
        return "Vídeo não encontrado", 404

    return send_file(video_path, mimetype="video/mp4")


def _executar_job(job_id: str, nome_receita: str):
    """Executa o pipeline em background e atualiza JOBS."""

    def callback(mensagem: str, progresso: float):
        JOBS[job_id]["mensagem"] = mensagem
        JOBS[job_id]["progresso"] = round(progresso, 3)

    resultado = executar_pipeline(nome_receita, callback=callback)

    if resultado["sucesso"]:
        JOBS[job_id].update({
            "status": "concluido",
            "progresso": 1.0,
            "mensagem": "Vídeo criado com sucesso!",
            "titulo": resultado.get("titulo", nome_receita),
            "filename": resultado.get("video_filename"),
            "duracao": round(resultado.get("duracao", 0), 1)
        })
    else:
        JOBS[job_id].update({
            "status": "erro",
            "progresso": 0,
            "erro": resultado.get("erro", "Erro desconhecido")
        })


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🎬 GERADOR DE VÍDEOS DE RECEITAS")
    print("="*60)
    print(f"  Acesse: http://localhost:5000")
    print(f"  API Keys: ANTHROPIC={bool(config.ANTHROPIC_API_KEY)}, PEXELS={bool(config.PEXELS_API_KEY)}")
    print(f"  Vídeos salvos em: {config.OUTPUT_DIR}")
    print("="*60 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
