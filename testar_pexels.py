"""
Script de teste da integração com Pexels.
Uso: python3 testar_pexels.py SUA_API_KEY_AQUI
"""
import sys
import os

def testar(api_key: str):
    os.environ["PEXELS_API_KEY"] = api_key

    # Recarrega config com a key
    import importlib
    import config
    importlib.reload(config)
    config.PEXELS_API_KEY = api_key

    from src.visual_provider import buscar_pexels_foto, buscar_pexels_video, extrair_frames_video

    print("\n" + "="*60)
    print("  TESTE PEXELS API")
    print("="*60)

    # ── Teste 1: foto ────────────────────────────────────────────
    print("\n[1] Buscando foto: 'chocolate cake close up'")
    foto = buscar_pexels_foto("chocolate cake close up", indice=0)
    if foto:
        size = os.path.getsize(foto) // 1024
        print(f"    ✅ Foto baixada: {foto} ({size} KB)")
    else:
        print("    ❌ Foto não encontrada")

    # ── Teste 2: vídeo ───────────────────────────────────────────
    print("\n[2] Buscando vídeo: 'cooking food kitchen'")
    video = buscar_pexels_video("cooking food kitchen", indice=0)
    if video:
        size = os.path.getsize(video) // 1024
        print(f"    ✅ Vídeo baixado: {video} ({size} KB)")

        # ── Teste 3: extração de frames ──────────────────────────
        print("\n[3] Extraindo frames do vídeo (6 segundos a 30 FPS)...")
        frames = extrair_frames_video(video, duracao_cena=6.0)
        if frames:
            print(f"    ✅ {len(frames)} frames extraídos — tamanho: {frames[0].size}")
            # Salva o primeiro frame como preview
            frames[0].save("/tmp/pexels_preview_frame.jpg")
            print("    📸 Preview salvo em: /tmp/pexels_preview_frame.jpg")
        else:
            print("    ❌ Nenhum frame extraído")
    else:
        print("    ❌ Vídeo não encontrado")

    print("\n" + "="*60)
    print("  Teste concluído!")
    print("  Para usar em produção:")
    print(f"    export PEXELS_API_KEY=\"{api_key}\"")
    print("    python3 app.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 testar_pexels.py SUA_PEXELS_API_KEY")
        print("Obtenha sua key gratuita em: https://www.pexels.com/api/")
        sys.exit(1)

    testar(sys.argv[1])
