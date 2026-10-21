#!/usr/bin/env python3 -I
"""
ProFase — Vídeo Institucional (30 s)
Execução: python3 -I videos/institucional_profase/montar.py
  (a partir da raiz do estúdio, com FilmCraft aberto)

Etapas automatizadas:
  1. Baixar clipes Mixkit (videoFree — comercial)
  2. Baixar trilha "Digital Clouds" (Mixkit)
  3. Gerar narração Kokoro pf_dora
  4. Montar e exportar via ferramentas/fc.py
"""

import sys, os, subprocess
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
RAIZ   = Path(__file__).resolve().parent.parent.parent   # raiz do estúdio
FERRAM = RAIZ / "ferramentas"
PROJ   = Path(__file__).resolve().parent
MIDIA  = PROJ / "midia"
EXPORT = PROJ / "export"
MIDIA.mkdir(exist_ok=True)
EXPORT.mkdir(exist_ok=True)

sys.path.insert(0, str(FERRAM))
import fc  # ferramentas/fc.py — wrapper FilmCraft

# ── Constantes ─────────────────────────────────────────────────────────────
SEC   = 254_016_000_000          # ticks por segundo no FilmCraft
def t(s): return int(s * SEC)    # segundos → ticks
FPS   = 30
W, H  = 1920, 1080

# Cores ProFase
ROSA  = "#FF007F"
CIANO = "#00E5FF"
BRNCO = "#FFFFFF"
PRETO = "#000000"

CONTATO = "fredner@profase.com.br  ·  (11) 91915-6525"

# ── Clips Mixkit (videoFree — licença comercial confirmada) ─────────────────
# Licença: https://mixkit.co/license/#videoFree
CLIPS_MIXKIT = {
    "mic":       "https://mixkit.co/free-stock-video/close-up-shot-of-a-professional-condenser-microphone-44049/",
    "comercial": "https://mixkit.co/free-stock-video/behind-the-scenes-of-a-man-doing-a-commercial-44062/",
    "camera":    "https://mixkit.co/free-stock-video/close-shot-on-a-dslr-camera-44076/",
    "stage":     "https://mixkit.co/free-stock-video/experienced-drummer-performing-on-stage-with-lights-41315/",
    "podcast":   "https://mixkit.co/free-stock-video/people-recording-a-podcast-in-a-studio-2948/",
}
TRILHA_PAGE = "https://mixkit.co/free-stock-music/play/digital-clouds-442/"

NARRACAO_TXT = (
    "ProFase — consultoria e projeto de audiovisual. "
    "Do levantamento técnico à entrega final, "
    "áudio — cada detalhe sonoro calculado com precisão. "
    "Vídeo — câmeras, switchers e telões sob medida. "
    "Iluminação — luz que transforma palcos e auditórios. "
    "ProFase. São Paulo."
)

# ══════════════════════════════════════════════════════════════════════════════
# 1. DOWNLOAD
# ══════════════════════════════════════════════════════════════════════════════

def _pip(*pkgs):
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *pkgs], check=True)

def baixar_clips():
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        _pip("requests", "beautifulsoup4")
        import requests
        from bs4 import BeautifulSoup

    HDR = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

    def _check_livre(soup, url):
        """Aborta se o clip não for videoFree (uso comercial)."""
        texto = soup.get_text(" ")
        if "videoFree" in str(soup) or "commercial or personal" in texto:
            return
        raise RuntimeError(
            f"\n❌ Clip NÃO é videoFree — uso comercial não permitido.\n   {url}\n"
            "   Substitua por um clip com licença Stock Video Free License."
        )

    def _baixar_video(nome, page_url):
        dest = MIDIA / f"{nome}.mp4"
        if dest.exists():
            print(f"  ✓ {dest.name} (cache)")
            return dest
        import requests
        from bs4 import BeautifulSoup
        r = requests.get(page_url, timeout=30, headers=HDR)
        soup = BeautifulSoup(r.text, "html.parser")
        _check_livre(soup, page_url)
        og = soup.find("meta", property="og:video")
        if not og or not og.get("content"):
            raise RuntimeError(f"og:video não encontrado em {page_url}")
        vid_url = og["content"]
        print(f"  ↓ {nome}: {vid_url}")
        r2 = requests.get(vid_url, stream=True, timeout=120, headers=HDR)
        r2.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r2.iter_content(1 << 16):
                f.write(chunk)
        print(f"  ✓ {dest.name}")
        return dest

    def _baixar_audio(nome, page_url):
        dest = MIDIA / f"{nome}.mp3"
        if dest.exists():
            print(f"  ✓ {dest.name} (cache)")
            return dest
        import requests
        from bs4 import BeautifulSoup
        r = requests.get(page_url, timeout=30, headers=HDR)
        soup = BeautifulSoup(r.text, "html.parser")
        # og:audio ou og:url com type=audio/mpeg
        tag = (soup.find("meta", property="og:audio") or
               soup.find("meta", attrs={"name": "twitter:player:stream"}))
        if not tag or not tag.get("content"):
            # fallback: procurar URL .mp3 em qualquer href/src
            import re
            mp3 = re.search(r'(https://[^\s"\']+\.mp3)', r.text)
            if not mp3:
                raise RuntimeError(f"URL de áudio não encontrada em {page_url}")
            audio_url = mp3.group(1)
        else:
            audio_url = tag["content"]
        print(f"  ↓ trilha: {audio_url}")
        r2 = requests.get(audio_url, stream=True, timeout=120, headers=HDR)
        r2.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r2.iter_content(1 << 16):
                f.write(chunk)
        print(f"  ✓ {dest.name}")
        return dest

    print("── 1. Baixando clipes ────────────────────────────────────────")
    caminhos = {}
    for nome, url in CLIPS_MIXKIT.items():
        caminhos[nome] = str(_baixar_video(nome, url))
    caminhos["trilha"] = str(_baixar_audio("digital_clouds", TRILHA_PAGE))
    return caminhos


# ══════════════════════════════════════════════════════════════════════════════
# 2. NARRAÇÃO  (Kokoro pf_dora)
# ══════════════════════════════════════════════════════════════════════════════

def gerar_narracao():
    dest = MIDIA / "narracao.wav"
    if dest.exists():
        print(f"  ✓ {dest.name} (cache)")
        return str(dest)

    print("── 2. Gerando narração (Kokoro pf_dora) ─────────────────────")
    try:
        from kokoro import KPipeline
        import soundfile as sf
        import numpy as np
    except ImportError:
        _pip("kokoro>=0.9.4", "soundfile", "numpy")
        from kokoro import KPipeline
        import soundfile as sf
        import numpy as np

    pipeline = KPipeline(lang_code="p")
    samples = []
    for chunk in pipeline(NARRACAO_TXT, voice="pf_dora", speed=0.93):
        audio = getattr(chunk, "audio", None)
        if audio is not None:
            samples.append(audio)

    if not samples:
        raise RuntimeError("Kokoro não gerou áudio — verifique instalação.")

    audio = np.concatenate(samples)
    peak = float(np.max(np.abs(audio)))
    if peak > 0:
        audio = audio / peak * (10 ** (-1 / 20))   # normalizar -1 dBFS peak

    sf.write(str(dest), audio, 24000)
    print(f"  ✓ narracao.wav ({len(audio)/24000:.1f} s)")
    return str(dest)


# ══════════════════════════════════════════════════════════════════════════════
# 3. MONTAGEM FilmCraft
# ══════════════════════════════════════════════════════════════════════════════

def montar(caminhos):
    print("── 3. Montando no FilmCraft ─────────────────────────────────")

    proj = fc.new_project(
        name="ProFase_Institucional_v1",
        width=W, height=H, fps=FPS,
        duration=t(30),
    )

    # ── Track map ─────────────────────────────────────────────────────────
    # 0 → vídeo fundo
    # 1 → overlay texto / logo
    # 2 → narração
    # 3 → trilha musical

    # ─ CENA 1: ABERTURA 0–5 s (fundo preto + logo) ────────────────────────
    fc.add_solid(proj, color=PRETO, track=0, start=t(0), end=t(5))

    fc.add_text(proj, text="PROFASE",
                font="Outfit", weight=600, size=96,
                color=BRNCO, letter_spacing=0.22,
                track=1, start=t(0.5), end=t(4.5),
                fade_in=t(0.8), fade_out=t(0.5),
                x=0.50, y=0.45, align="center")

    fc.add_text(proj, text="CONSULTORIA E PROJETO DE AUDIOVISUAL",
                font="Outfit", weight=300, size=26,
                color=CIANO, letter_spacing=0.14,
                track=1, start=t(1.2), end=t(4.5),
                fade_in=t(0.6),
                x=0.50, y=0.57, align="center")

    # ─ CENA 2: CONSULTORIA 5–10 s ──────────────────────────────────────────
    fc.add_clip(proj, path=caminhos["comercial"],
                track=0, start=t(5), end=t(10),
                clip_start=t(0), opacity=0.65)

    fc.add_text(proj, text="SÃO PAULO, SP",
                font="Outfit", weight=200, size=22,
                color=CIANO,
                track=1, start=t(5.5), end=t(9.5),
                fade_in=t(0.5),
                x=0.50, y=0.63, align="center")

    # ─ CENA 3: ÁUDIO 10–16 s ──────────────────────────────────────────────
    fc.add_clip(proj, path=caminhos["mic"],
                track=0, start=t(10), end=t(13),
                clip_start=t(0))

    fc.add_clip(proj, path=caminhos["podcast"],
                track=0, start=t(13), end=t(16),
                clip_start=t(0))

    fc.add_text(proj, text="ÁUDIO",
                font="Outfit", weight=600, size=80,
                color=ROSA,
                track=1, start=t(10.3), end=t(15.7),
                fade_in=t(0.5), fade_out=t(0.4),
                x=0.50, y=0.35, align="center")

    # ─ CENA 4: VÍDEO 16–21 s ──────────────────────────────────────────────
    fc.add_clip(proj, path=caminhos["camera"],
                track=0, start=t(16), end=t(19),
                clip_start=t(0))

    fc.add_clip(proj, path=caminhos["comercial"],
                track=0, start=t(19), end=t(21),
                clip_start=t(2))

    fc.add_text(proj, text="VÍDEO",
                font="Outfit", weight=600, size=80,
                color=CIANO,
                track=1, start=t(16.3), end=t(20.7),
                fade_in=t(0.5), fade_out=t(0.4),
                x=0.50, y=0.35, align="center")

    # ─ CENA 5: ILUMINAÇÃO 21–26 s ─────────────────────────────────────────
    fc.add_clip(proj, path=caminhos["stage"],
                track=0, start=t(21), end=t(26),
                clip_start=t(0))

    fc.add_text(proj, text="ILUMINAÇÃO",
                font="Outfit", weight=600, size=72,
                color=BRNCO,
                track=1, start=t(21.3), end=t(25.7),
                fade_in=t(0.5), fade_out=t(0.4),
                x=0.50, y=0.35, align="center")

    # ─ CENA 6: FECHAMENTO 26–30 s ─────────────────────────────────────────
    fc.add_solid(proj, color=PRETO, track=0, start=t(26), end=t(30))

    fc.add_gradient_bar(proj,
                        colors=[ROSA, CIANO],
                        direction="horizontal", height_px=3,
                        track=1, start=t(26), end=t(30),
                        y=0.99)

    fc.add_text(proj, text="PROFASE",
                font="Outfit", weight=600, size=72,
                color=BRNCO, letter_spacing=0.22,
                track=1, start=t(26.5), end=t(30),
                fade_in=t(0.6),
                x=0.50, y=0.42, align="center")

    fc.add_text(proj, text=CONTATO,
                font="Outfit", weight=300, size=20,
                color=CIANO,
                track=1, start=t(27.2), end=t(30),
                fade_in=t(0.4),
                x=0.50, y=0.62, align="center")

    # ─ Transições cross-fade (12 frames = 0.4 s) entre cenas ──────────────
    for corte in (t(5), t(10), t(16), t(21), t(26)):
        fc.add_transition(proj,
                          type="crossfade",
                          track=0,
                          at=corte,
                          duration=t(12 / 30))

    # ─ Áudio ──────────────────────────────────────────────────────────────
    fc.add_audio(proj, path=caminhos["narracao"],
                 track=2, start=t(1), end=t(27),
                 volume=0.90)

    fc.add_audio(proj, path=caminhos["trilha"],
                 track=3, start=t(0), end=t(30),
                 volume=0.28)

    # ─ Export ─────────────────────────────────────────────────────────────
    saida = str(EXPORT / "profase_institucional_v1.mp4")
    print(f"  Exportando → {saida}")
    fc.export(proj,
              path=saida,
              codec="h264",
              width=W, height=H, fps=FPS,
              bitrate=16_000_000,
              audio_codec="aac",
              lufs=-14)

    print(f"\n✅  Concluído: {saida}")
    return saida


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════╗")
    print("║  ProFase — Vídeo Institucional  (montagem automática)║")
    print("╚══════════════════════════════════════════════════════╝\n")

    caminhos = baixar_clips()
    caminhos["narracao"] = gerar_narracao()
    montar(caminhos)
