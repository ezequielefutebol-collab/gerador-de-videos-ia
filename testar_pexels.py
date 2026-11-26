"""
Script de teste das APIs de imagens (Pixabay e Pexels).

Uso:
  python3 testar_pexels.py pixabay SUA_PIXABAY_KEY
  python3 testar_pexels.py pexels  SUA_PEXELS_KEY

Obtenha a key do Pixabay (gratuita, sem fila):
  https://pixabay.com/api/docs/

Obtenha a key do Pexels (gratuita, novas chaves pausadas em nov/2026):
  https://www.pexels.com/api/
"""
import sys
import os


def testar_pixabay(api_key: str):
    os.environ["PIXABAY_API_KEY"] = api_key
    import importlib, config
    importlib.reload(config)
    config.PIXABAY_API_KEY = api_key

    from src.visual_provider import buscar_pixabay_foto, buscar_pixabay_video, extrair_frames_video

    print("\n" + "="*60)
    print("  TESTE PIXABAY API")
    print("="*60)

    print("\n[1] Buscando foto: 'chocolate cake'")
    foto = buscar_pixabay_foto("chocolate cake", indice=0)
    if foto:
        print(f"    ✅ Foto: {foto} ({os.path.getsize(foto)//1024} KB)")
    else:
        print("    ❌ Foto não encontrada")

    print("\n[2] Buscando vídeo: 'cooking food kitchen'")
    video = buscar_pixabay_video("cooking food kitchen", indice=0)
    if video:
        print(f"    ✅ Vídeo: {video} ({os.path.getsize(video)//1024} KB)")

        print("\n[3] Extraindo frames (6s a 30fps)...")
        frames = extrair_frames_video(video, duracao_cena=6.0)
        if frames:
            print(f"    ✅ {len(frames)} frames extraídos — tamanho: {frames[0].size}")
            frames[0].save("/tmp/pixabay_preview.jpg")
            print("    📸 Preview: /tmp/pixabay_preview.jpg")
        else:
            print("    ❌ Nenhum frame extraído")
    else:
        print("    ❌ Vídeo não encontrado")

    _mostrar_instrucoes("pixabay", api_key)


def testar_pexels(api_key: str):
    os.environ["PEXELS_API_KEY"] = api_key
    import importlib, config
    importlib.reload(config)
    config.PEXELS_API_KEY = api_key

    from src.visual_provider import buscar_pexels_foto, buscar_pexels_video, extrair_frames_video

    print("\n" + "="*60)
    print("  TESTE PEXELS API")
    print("="*60)

    print("\n[1] Buscando foto: 'chocolate cake close up'")
    foto = buscar_pexels_foto("chocolate cake close up", indice=0)
    if foto:
        print(f"    ✅ Foto: {foto} ({os.path.getsize(foto)//1024} KB)")
    else:
        print("    ❌ Foto não encontrada")

    print("\n[2] Buscando vídeo: 'cooking food kitchen'")
    video = buscar_pexels_video("cooking food kitchen", indice=0)
    if video:
        print(f"    ✅ Vídeo: {video} ({os.path.getsize(video)//1024} KB)")

        print("\n[3] Extraindo frames (6s a 30fps)...")
        frames = extrair_frames_video(video, duracao_cena=6.0)
        if frames:
            print(f"    ✅ {len(frames)} frames extraídos — tamanho: {frames[0].size}")
            frames[0].save("/tmp/pexels_preview.jpg")
            print("    📸 Preview: /tmp/pexels_preview.jpg")
        else:
            print("    ❌ Nenhum frame extraído")
    else:
        print("    ❌ Vídeo não encontrado")

    _mostrar_instrucoes("pexels", api_key)


def _mostrar_instrucoes(provedor: str, key: str):
    var = "PIXABAY_API_KEY" if provedor == "pixabay" else "PEXELS_API_KEY"
    print("\n" + "="*60)
    print("  Para usar em produção:")
    print(f'    export {var}="{key}"')
    print("    python3 app.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    provedor = sys.argv[1].lower()
    key = sys.argv[2]

    if provedor == "pixabay":
        testar_pixabay(key)
    elif provedor == "pexels":
        testar_pexels(key)
    else:
        print(f"Provedor inválido: {provedor!r}. Use 'pixabay' ou 'pexels'.")
        sys.exit(1)
