import os
import re
import math
import shutil
import subprocess
import unicodedata
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# CONFIGURAÇÃO FIXA
# ============================================================

QUANTIDADE_VIDEOS = 8
PERGUNTAS_POR_VIDEO = 5
TEMPO_ESCOLHA = 3

VOZ = "pt-BR-AntonioNeural"
VELOCIDADE_VOZ = "+10%"

W = 1080
H = 1920
FPS = 30

DURACAO_MARCATEXTO = 0.90
PAUSA_DEPOIS_RESPOSTA = 0.55

AUDIO_HZ = 48000
AUDIO_CHANNELS = 2

FUSO = ZoneInfo("America/Fortaleza")
DATA_DO_DIA = datetime.now(FUSO).strftime("%Y-%m-%d")

PASTA_RAIZ = Path("output")
PASTA_TMP = Path("_tmp_juhquiz_rosa")
PASTA_SAIDA = PASTA_RAIZ / DATA_DO_DIA

# ============================================================
# 8 TEMAS × 5 PERGUNTAS
# Cada tema = 1 vídeo.
# correta: 0=A, 1=B, 2=C
# ============================================================

QUIZZES = {
    "História do Brasil": [
        {"pergunta": "Em que ano o Brasil declarou sua independência de Portugal?", "alternativas": ["1889", "1822", "1500"], "correta": 1},
        {"pergunta": "Quem proclamou a Independência do Brasil?", "alternativas": ["Tiradentes", "Dom Pedro I", "Dom Pedro II"], "correta": 1},
        {"pergunta": "Qual foi a primeira capital do Brasil?", "alternativas": ["Rio de Janeiro", "Salvador", "Brasília"], "correta": 1},
        {"pergunta": "Em que ano foi proclamada a República no Brasil?", "alternativas": ["1822", "1960", "1889"], "correta": 2},
        {"pergunta": "Qual cidade se tornou a capital do Brasil em 1960?", "alternativas": ["Salvador", "Brasília", "São Paulo"], "correta": 1},
    ],

    "Geografia do Mundo": [
        {"pergunta": "Qual é o maior oceano da Terra?", "alternativas": ["Atlântico", "Pacífico", "Índico"], "correta": 1},
        {"pergunta": "Qual é a capital do Japão?", "alternativas": ["Seul", "Pequim", "Tóquio"], "correta": 2},
        {"pergunta": "Em qual continente fica o Egito?", "alternativas": ["Europa", "África", "Oceania"], "correta": 1},
        {"pergunta": "Qual é o maior país da América do Sul em área?", "alternativas": ["Argentina", "Brasil", "Peru"], "correta": 1},
        {"pergunta": "Qual é a capital da Argentina?", "alternativas": ["Montevidéu", "Buenos Aires", "Santiago"], "correta": 1},
    ],

    "Ciências": [
        {"pergunta": "Qual planeta é conhecido como Planeta Vermelho?", "alternativas": ["Vênus", "Marte", "Júpiter"], "correta": 1},
        {"pergunta": "Qual gás é essencial para a respiração humana?", "alternativas": ["Hélio", "Oxigênio", "Neônio"], "correta": 1},
        {"pergunta": "Qual órgão bombeia o sangue pelo corpo humano?", "alternativas": ["Pulmão", "Estômago", "Coração"], "correta": 2},
        {"pergunta": "Quantos planetas existem no Sistema Solar?", "alternativas": ["7", "8", "9"], "correta": 1},
        {"pergunta": "A água congela a quantos graus Celsius ao nível do mar?", "alternativas": ["100 graus", "0 graus", "10 graus"], "correta": 1},
    ],

    "Animais": [
        {"pergunta": "Qual é o maior animal terrestre atualmente?", "alternativas": ["Girafa", "Elefante-africano", "Rinoceronte"], "correta": 1},
        {"pergunta": "Qual animal é conhecido por mudar de cor para se camuflar?", "alternativas": ["Camaleão", "Pinguim", "Golfinho"], "correta": 0},
        {"pergunta": "Qual destes animais é um mamífero marinho?", "alternativas": ["Tubarão", "Golfinho", "Polvo"], "correta": 1},
        {"pergunta": "Qual animal possui listras pretas e brancas?", "alternativas": ["Zebra", "Girafa", "Leopardo"], "correta": 0},
        {"pergunta": "Qual ave é conhecida por não voar e viver na Antártida?", "alternativas": ["Águia", "Pinguim", "Beija-flor"], "correta": 1},
    ],

    "Corpo Humano": [
        {"pergunta": "Qual é o maior órgão do corpo humano?", "alternativas": ["Fígado", "Pele", "Pulmão"], "correta": 1},
        {"pergunta": "Quantos pulmões uma pessoa normalmente possui?", "alternativas": ["1", "2", "3"], "correta": 1},
        {"pergunta": "Qual órgão é responsável por filtrar o sangue e produzir urina?", "alternativas": ["Rins", "Coração", "Estômago"], "correta": 0},
        {"pergunta": "Qual parte do corpo contém o fêmur?", "alternativas": ["Braço", "Coxa", "Pescoço"], "correta": 1},
        {"pergunta": "Qual órgão está diretamente ligado à visão?", "alternativas": ["Olho", "Ouvido", "Nariz"], "correta": 0},
    ],

    "Curiosidades": [
        {"pergunta": "Qual metal é líquido em temperatura ambiente?", "alternativas": ["Mercúrio", "Ferro", "Alumínio"], "correta": 0},
        {"pergunta": "Qual é o único mamífero capaz de voo verdadeiro?", "alternativas": ["Morcego", "Esquilo", "Coala"], "correta": 0},
        {"pergunta": "Qual país é conhecido pelo formato de uma bota?", "alternativas": ["Itália", "França", "Portugal"], "correta": 0},
        {"pergunta": "Qual é a cor resultante da mistura de azul e amarelo?", "alternativas": ["Roxo", "Verde", "Laranja"], "correta": 1},
        {"pergunta": "Qual instrumento é usado para medir a temperatura?", "alternativas": ["Termômetro", "Barômetro", "Bússola"], "correta": 0},
    ],

    "Espaço": [
        {"pergunta": "Qual estrela está no centro do Sistema Solar?", "alternativas": ["Sol", "Sirius", "Lua"], "correta": 0},
        {"pergunta": "Qual é o maior planeta do Sistema Solar?", "alternativas": ["Saturno", "Júpiter", "Terra"], "correta": 1},
        {"pergunta": "Qual planeta é conhecido por seus anéis?", "alternativas": ["Marte", "Saturno", "Mercúrio"], "correta": 1},
        {"pergunta": "Qual corpo celeste orbita naturalmente a Terra?", "alternativas": ["Lua", "Sol", "Vênus"], "correta": 0},
        {"pergunta": "Qual é o planeta mais próximo do Sol?", "alternativas": ["Vênus", "Mercúrio", "Terra"], "correta": 1},
    ],

    "Cultura Geral": [
        {"pergunta": "Quantos lados tem um hexágono?", "alternativas": ["5", "6", "8"], "correta": 1},
        {"pergunta": "Qual idioma é falado oficialmente no Brasil?", "alternativas": ["Espanhol", "Português", "Inglês"], "correta": 1},
        {"pergunta": "Qual é a capital da França?", "alternativas": ["Paris", "Roma", "Madri"], "correta": 0},
        {"pergunta": "Qual destes é um instrumento de cordas?", "alternativas": ["Violão", "Flauta", "Trompete"], "correta": 0},
        {"pergunta": "Quantos dias possui uma semana?", "alternativas": ["5", "7", "10"], "correta": 1},
    ],
}


# ============================================================
# UTILITÁRIOS
# ============================================================

def slug(texto):
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", texto).strip("_").lower()
    return texto or "video"


def executar(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        print(p.stderr[-5000:])
        raise RuntimeError("Comando retornou erro.")
    return p


def achar_fonte(*candidatos):
    for caminho in candidatos:
        if caminho and os.path.exists(caminho):
            return caminho
    return None


FONT_BOLD = achar_fonte(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
)

FONT_REG = achar_fonte(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
)


def fonte(tamanho, bold=True):
    caminho = FONT_BOLD if bold else FONT_REG
    if caminho:
        return ImageFont.truetype(caminho, int(tamanho))
    return ImageFont.load_default()


def wrap_text(draw, texto, fnt, max_width):
    palavras = str(texto).split()
    linhas = []
    atual = ""

    for palavra in palavras:
        teste = (atual + " " + palavra).strip()
        bb = draw.textbbox((0, 0), teste, font=fnt)
        if (bb[2] - bb[0]) <= max_width:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra

    if atual:
        linhas.append(atual)

    return linhas


def gradient_vertical(size, top_color, bottom_color):
    w, h = size
    faixa = Image.new("RGB", (1, h))
    dados = []
    for y in range(h):
        t = y / max(1, h - 1)
        dados.append(tuple(
            int(top_color[i] * (1 - t) + bottom_color[i] * t)
            for i in range(3)
        ))
    faixa.putdata(dados)
    return faixa.resize((w, h))


def texto_central(draw, xy, texto, fnt, fill):
    x, y = xy
    bb = draw.textbbox((0, 0), texto, font=fnt)
    tw = bb[2] - bb[0]
    draw.text((x - tw / 2, y), texto, font=fnt, fill=fill)


def desenhar_check(draw, cx, cy):
    draw.line(
        [(cx - 11, cy), (cx - 1, cy + 11), (cx + 18, cy - 18)],
        fill=(45, 125, 246),
        width=9
    )


def preparar_layout(perguntas):
    dummy = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(dummy)
    f_q = fonte(38, True)

    paper_x0 = 70
    paper_x1 = W - 70
    x_q = paper_x0 + 100
    max_q_width = paper_x1 - x_q - 130

    y = 370
    itens = []

    for i, q in enumerate(perguntas):
        linhas = wrap_text(draw, f"{i+1}) {q['pergunta']}", f_q, max_q_width)
        line_h = 52
        question_h = len(linhas) * line_h
        alt_top = y + question_h + 20
        alt_h = 46
        total_h = question_h + 20 + (3 * alt_h) + 50

        line_infos = []
        yy = y
        for linha in linhas:
            bb = draw.textbbox((0, 0), linha, font=f_q)
            largura = bb[2] - bb[0]
            line_infos.append({"texto": linha, "x": x_q, "y": yy, "w": largura, "h": 44})
            yy += line_h

        itens.append({
            "index": i,
            "y": y,
            "h": total_h,
            "lines": line_infos,
            "alt_top": alt_top
        })

        y += total_h + 14

    return itens


def calcular_scroll(layout, atual):
    if atual < 0:
        return 0
    return max(0, layout[atual]["y"] - 470)


def draw_marker(draw, x, y):
    body_w = 145
    body_h = 38
    draw.rounded_rectangle(
        [x, y, x + body_w, y + body_h],
        radius=12,
        fill=(255, 226, 61),
        outline=(229, 193, 17),
        width=3
    )
    draw.rounded_rectangle(
        [x + body_w - 35, y, x + body_w, y + body_h],
        radius=9,
        fill=(54, 54, 62)
    )
    draw.polygon(
        [(x - 18, y + 10), (x, y + 5), (x, y + body_h - 5), (x - 18, y + body_h - 10)],
        fill=(239, 221, 100)
    )
    draw.rectangle([x - 25, y + 13, x - 17, y + body_h - 13], fill=(102, 93, 34))


def desenhar_header_papel(draw, tema):
    draw.rectangle([82, 74, W - 88, 345], fill=(255, 254, 251))
    texto_central(draw, (W / 2, 92), "JuhQuiz", fonte(70, True), (255, 82, 148))
    texto_central(
        draw,
        (W / 2, 165),
        "QUIZ RÁPIDO • DESAFIE SEU CÉREBRO",
        fonte(23, True),
        (159, 122, 136)
    )

    tema_txt = f"TEMA: {tema.upper()}"
    bb = draw.textbbox((0, 0), tema_txt, font=fonte(28, True))
    tw = bb[2] - bb[0]
    px0 = W / 2 - tw / 2 - 30
    px1 = W / 2 + tw / 2 + 30

    draw.rounded_rectangle(
        [px0, 220, px1, 278],
        radius=29,
        fill=(255, 239, 247),
        outline=(255, 194, 219),
        width=3
    )
    texto_central(draw, (W / 2, 233), tema_txt, fonte(28, True), (208, 77, 132))


# ============================================================
# RENDER
# ============================================================

def render_frame(tema, perguntas, atual, estado, timer=None, highlight_progress=1.0, mostrar_marker=False):
    img = gradient_vertical((W, H), (255, 219, 233), (255, 196, 219))
    draw = ImageDraw.Draw(img)

    for x in range(0, W, 44):
        draw.line([(x, 0), (x + 90, H)], fill=(255, 255, 255), width=2)

    draw.ellipse([55, 95, 145, 185], fill=(255, 237, 245))
    draw.ellipse([W - 170, 80, W - 80, 170], fill=(255, 237, 245))
    draw.text((80, 110), "♥", font=fonte(56, True), fill=(226, 83, 143))
    draw.text((W - 155, 102), "✦", font=fonte(55, True), fill=(228, 137, 177))

    draw.rounded_rectangle(
        [W - 205, 130, W - 70, 265],
        radius=12,
        fill=(255, 242, 166),
        outline=(238, 215, 103),
        width=2
    )
    texto_central(draw, (W - 138, 168), "BOA", fonte(26, True), (150, 120, 30))
    texto_central(draw, (W - 138, 202), "SORTE!", fonte(26, True), (150, 120, 30))

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([60, 60, W - 45, H - 55], radius=36, fill=(110, 55, 85, 65))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(img)

    paper = [45, 45, W - 65, H - 75]
    draw.rounded_rectangle(
        paper,
        radius=30,
        fill=(255, 254, 251),
        outline=(255, 190, 214),
        width=3
    )

    for yy in range(300, H - 100, 52):
        draw.line([(100, yy), (W - 105, yy)], fill=(255, 228, 238), width=2)

    draw.line([(120, 260), (120, H - 105)], fill=(255, 160, 198), width=3)
    draw.arc([70, 80, 190, 155], start=180, end=355, fill=(198, 143, 165), width=8)

    desenhar_header_papel(draw, tema)

    if estado == "final":
        texto_central(draw, (W / 2, 690), "QUANTAS VOCÊ ACERTOU?", fonte(58, True), (70, 61, 66))
        draw.rounded_rectangle(
            [190, 810, W - 190, 930],
            radius=35,
            fill=(255, 240, 247),
            outline=(255, 185, 213),
            width=4
        )
        texto_central(draw, (W / 2, 840), "COMENTA SUA PONTUAÇÃO", fonte(36, True), (210, 73, 131))
        texto_central(draw, (W / 2, 1010), "@juhquiz", fonte(36, True), (144, 104, 120))
        return img

    layout = preparar_layout(perguntas)
    scroll = calcular_scroll(layout, atual)

    f_q = fonte(38, True)
    f_alt = fonte(34, False)
    f_alt_bold = fonte(34, True)

    respondidos = atual if estado in ("reading", "highlight", "countdown") else atual + 1
    marker_pos = None

    for item in layout:
        idx = item["index"]
        q = perguntas[idx]
        q_y = item["y"] - scroll

        if q_y + item["h"] < 315 or q_y > H - 90:
            continue

        if idx == atual:
            draw.rounded_rectangle(
                [135, q_y - 8, W - 125, q_y + item["h"] - 12],
                radius=22,
                fill=(255, 247, 251)
            )

        total_path = sum(li["w"] for li in item["lines"])
        current_path = max(0.0, min(1.0, float(highlight_progress))) * total_path
        path_acc = 0.0

        for li in item["lines"]:
            lx = li["x"]
            ly = li["y"] - scroll
            lw = li["w"]

            full_mark = idx < respondidos
            if idx == atual and estado in ("countdown", "answer"):
                full_mark = True

            if idx == atual and estado == "highlight":
                faltando = current_path - path_acc
                parcial = max(0, min(lw, faltando))
                if parcial > 0:
                    draw.rounded_rectangle(
                        [lx - 5, ly + 6, lx + parcial + 7, ly + 47],
                        radius=10,
                        fill=(255, 238, 83)
                    )
                    if mostrar_marker and 0 < parcial < lw + 1:
                        marker_pos = (lx + parcial - 15, ly + 8)

            elif full_mark:
                draw.rounded_rectangle(
                    [lx - 5, ly + 6, lx + lw + 7, ly + 47],
                    radius=10,
                    fill=(255, 238, 83)
                )

            draw.text((lx, ly), li["texto"], font=f_q, fill=(48, 48, 48))
            path_acc += lw

        alt_y = item["alt_top"] - scroll
        letras = ["A", "B", "C"]

        for j, alt in enumerate(q["alternativas"]):
            yy = alt_y + j * 46
            cx = 185
            cy = yy + 18

            draw.ellipse(
                [cx - 13, cy - 13, cx + 13, cy + 13],
                outline=(130, 130, 130),
                width=3,
                fill=(255, 255, 255)
            )

            esta_revelada = idx < respondidos or (idx == atual and estado == "answer")
            if esta_revelada and j == int(q["correta"]):
                desenhar_check(draw, cx, cy)
                alt_font = f_alt_bold
                alt_fill = (35, 35, 35)
            else:
                alt_font = f_alt
                alt_fill = (55, 55, 55)

            draw.text((220, yy), f"{letras[j]}) {alt}", font=alt_font, fill=alt_fill)

        if idx == atual and estado == "countdown" and timer is not None:
            tx0, ty0, tx1, ty1 = W - 265, q_y + item["h"] - 75, W - 145, q_y + item["h"] - 20
            draw.rounded_rectangle(
                [tx0, ty0, tx1, ty1],
                radius=27,
                fill=(255, 250, 253),
                outline=(255, 139, 183),
                width=4
            )
            texto_central(
                draw,
                ((tx0 + tx1) / 2, ty0 + 7),
                str(timer),
                fonte(36, True),
                (209, 76, 132)
            )

    if marker_pos is not None:
        draw_marker(draw, marker_pos[0], marker_pos[1])

    desenhar_header_papel(draw, tema)

    texto_central(
        draw,
        (W / 2, H - 120),
        "@juhquiz",
        fonte(25, True),
        (174, 123, 145)
    )

    return img


# ============================================================
# ÁUDIO / FFMPEG
# ============================================================

def limpar_tts(texto):
    return re.sub(r"\s+", " ", str(texto)).strip()


def tts_salvar(texto, caminho):
    caminho = str(caminho)
    if os.path.exists(caminho):
        os.remove(caminho)

    p = subprocess.run(
        [
            "edge-tts",
            "--voice", VOZ,
            "--rate", VELOCIDADE_VOZ,
            "--text", limpar_tts(texto),
            "--write-media", caminho
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if p.returncode != 0:
        print(p.stderr)
        raise RuntimeError("Falha ao gerar voz com Edge TTS.")

    if not os.path.exists(caminho) or os.path.getsize(caminho) < 500:
        raise RuntimeError(f"Áudio não foi criado: {caminho}")


def duracao_audio(caminho):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(caminho)
    ]
    return float(subprocess.check_output(cmd, text=True).strip())


def criar_beep(caminho, frequencia=950):
    caminho = str(caminho)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency={frequencia}:duration=0.14",
        "-af", "volume=0.55,apad=pad_dur=1",
        "-t", "1.0",
        "-c:a", "aac", "-b:a", "160k",
        "-ar", str(AUDIO_HZ),
        "-ac", str(AUDIO_CHANNELS),
        caminho
    ]
    executar(cmd)


def criar_clipe_imagem(img_path, duracao, saida, audio=None):
    img_path = str(img_path)
    saida = str(saida)
    duracao = float(duracao)

    if audio:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", img_path,
            "-i", str(audio),
            "-t", f"{duracao:.3f}",
            "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
            "-af", f"aresample={AUDIO_HZ}:async=1:first_pts=0,apad",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k",
            "-ar", str(AUDIO_HZ), "-ac", str(AUDIO_CHANNELS),
            "-video_track_timescale", "90000",
            "-avoid_negative_ts", "make_zero",
            "-movflags", "+faststart",
            saida
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", img_path,
            "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_HZ}",
            "-t", f"{duracao:.3f}",
            "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k",
            "-ar", str(AUDIO_HZ), "-ac", str(AUDIO_CHANNELS),
            "-shortest",
            "-video_track_timescale", "90000",
            "-avoid_negative_ts", "make_zero",
            "-movflags", "+faststart",
            saida
        ]
    executar(cmd)


def criar_clipe_animacao(frames_dir, numero_frames, fps_frames, saida):
    frames_dir = Path(frames_dir)
    dur = numero_frames / float(fps_frames)

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps_frames),
        "-i", str(frames_dir / "frame_%03d.png"),
        "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_HZ}",
        "-t", f"{dur:.3f}",
        "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-ar", str(AUDIO_HZ), "-ac", str(AUDIO_CHANNELS),
        "-shortest",
        "-video_track_timescale", "90000",
        "-movflags", "+faststart",
        str(saida)
    ]
    executar(cmd)


def juntar_clipes(lista, saida, concat_path):
    # IMPORTANTE:
    # O FFmpeg resolve caminhos relativos a partir da pasta onde está
    # o arquivo concat.txt. Como os segmentos já estão em subpastas de
    # _tmp_juhquiz_rosa, gravamos caminhos ABSOLUTOS para não duplicar
    # o prefixo da pasta.
    concat_path = Path(concat_path).resolve()
    saida = Path(saida).resolve()

    concat_path.parent.mkdir(parents=True, exist_ok=True)
    saida.parent.mkdir(parents=True, exist_ok=True)

    with open(concat_path, "w", encoding="utf-8") as f:
        for p in lista:
            p_abs = Path(p).resolve()
            if not p_abs.exists():
                raise FileNotFoundError(f"Segmento não encontrado: {p_abs}")

            caminho_ffmpeg = str(p_abs).replace("'", "'\\''")
            f.write("file '" + caminho_ffmpeg + "'\n")

    cmd = [
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_path),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-ar", str(AUDIO_HZ), "-ac", str(AUDIO_CHANNELS),
        "-af", f"aresample={AUDIO_HZ}:async=1:first_pts=0",
        "-avoid_negative_ts", "make_zero",
        "-movflags", "+faststart",
        str(saida)
    ]
    executar(cmd)


# ============================================================
# GERAÇÃO
# ============================================================

def validar():
    temas = list(QUIZZES.keys())

    if len(temas) < QUANTIDADE_VIDEOS:
        raise ValueError("Não há temas suficientes para 8 vídeos.")

    for tema in temas[:QUANTIDADE_VIDEOS]:
        perguntas = QUIZZES[tema]
        if len(perguntas) < PERGUNTAS_POR_VIDEO:
            raise ValueError(f"Tema '{tema}' tem menos de 5 perguntas.")

        for q in perguntas[:PERGUNTAS_POR_VIDEO]:
            if len(q["alternativas"]) != 3:
                raise ValueError(f"'{tema}' tem pergunta sem 3 alternativas.")
            if int(q["correta"]) not in (0, 1, 2):
                raise ValueError(f"'{tema}' tem índice de resposta inválido.")


def main():
    validar()

    if PASTA_TMP.exists():
        shutil.rmtree(PASTA_TMP)

    PASTA_TMP.mkdir(parents=True, exist_ok=True)
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    print(f"📅 Pasta do dia: {PASTA_SAIDA}")
    print(f"🎬 Gerando {QUANTIDADE_VIDEOS} vídeos × {PERGUNTAS_POR_VIDEO} perguntas")

    beep_normal = PASTA_TMP / "beep_950.m4a"
    beep_final = PASTA_TMP / "beep_1250.m4a"

    criar_beep(beep_normal, 950)
    criar_beep(beep_final, 1250)

    videos_gerados = []
    temas = list(QUIZZES.keys())[:QUANTIDADE_VIDEOS]

    for video_num, tema in enumerate(temas, start=1):
        perguntas_tema = QUIZZES[tema][:PERGUNTAS_POR_VIDEO]

        print("\n" + "=" * 72)
        print(f"🎬 {video_num:02d}/08 — {tema}")
        print("=" * 72)

        pasta_video = PASTA_TMP / f"video_{video_num:02d}_{slug(tema)}"
        pasta_video.mkdir(parents=True, exist_ok=True)

        segmentos = []

        for idx, pergunta in enumerate(perguntas_tema):
            numero = idx + 1
            print(f" • {numero}/5 — {pergunta['pergunta']}")

            pasta_q = pasta_video / f"q{numero:02d}"
            pasta_q.mkdir(parents=True, exist_ok=True)

            # 1) lê apenas a pergunta
            audio_q = pasta_q / "pergunta.mp3"
            tts_salvar(pergunta["pergunta"], audio_q)
            dur_q = duracao_audio(audio_q) + 0.18

            frame_q = pasta_q / "01_pergunta.png"
            render_frame(
                tema, perguntas_tema,
                atual=idx,
                estado="reading",
                highlight_progress=0
            ).save(frame_q)

            clip_q = pasta_q / "01_pergunta.mp4"
            criar_clipe_imagem(frame_q, dur_q, clip_q, audio=audio_q)
            segmentos.append(clip_q)

            # 2) marca-texto percorre a pergunta toda
            frames_dir = pasta_q / "frames_marcatexto"
            frames_dir.mkdir(exist_ok=True)

            fps_marker = 20
            n_frames = max(8, int(DURACAO_MARCATEXTO * fps_marker))

            for fr in range(n_frames):
                progresso = (fr + 1) / n_frames
                frame = render_frame(
                    tema, perguntas_tema,
                    atual=idx,
                    estado="highlight",
                    highlight_progress=progresso,
                    mostrar_marker=True
                )
                frame.save(frames_dir / f"frame_{fr:03d}.png")

            clip_marker = pasta_q / "02_marcatexto.mp4"
            criar_clipe_animacao(frames_dir, n_frames, fps_marker, clip_marker)
            segmentos.append(clip_marker)

            # 3) contagem com bip
            for segundos in range(TEMPO_ESCOLHA, 0, -1):
                frame_timer = pasta_q / f"timer_{segundos}.png"
                render_frame(
                    tema, perguntas_tema,
                    atual=idx,
                    estado="countdown",
                    timer=segundos,
                    highlight_progress=1
                ).save(frame_timer)

                clip_timer = pasta_q / f"timer_{segundos}.mp4"
                som = beep_final if segundos == 1 else beep_normal
                criar_clipe_imagem(frame_timer, 1.0, clip_timer, audio=som)
                segmentos.append(clip_timer)

            # 4) fala só a resposta e marca correta
            correta = int(pergunta["correta"])
            texto_resposta = pergunta["alternativas"][correta]

            audio_resp = pasta_q / "resposta.mp3"
            tts_salvar(texto_resposta, audio_resp)
            dur_resp = duracao_audio(audio_resp) + PAUSA_DEPOIS_RESPOSTA

            frame_resp = pasta_q / "03_resposta.png"
            render_frame(
                tema, perguntas_tema,
                atual=idx,
                estado="answer",
                highlight_progress=1
            ).save(frame_resp)

            clip_resp = pasta_q / "03_resposta.mp4"
            criar_clipe_imagem(frame_resp, dur_resp, clip_resp, audio=audio_resp)
            segmentos.append(clip_resp)

        # tela final
        frame_final = pasta_video / "final.png"
        render_frame(
            tema, perguntas_tema,
            atual=len(perguntas_tema) - 1,
            estado="final"
        ).save(frame_final)

        clip_final = pasta_video / "final.mp4"
        criar_clipe_imagem(frame_final, 2.0, clip_final)
        segmentos.append(clip_final)

        nome_saida = f"{video_num:02d}_{slug(tema)}_{DATA_DO_DIA}.mp4"
        saida_video = PASTA_SAIDA / nome_saida

        juntar_clipes(segmentos, saida_video, pasta_video / "concat.txt")
        videos_gerados.append(saida_video)

        print("✅ Gerado:", saida_video)

    print("\n✅ FINALIZADO")
    print(f"📁 {PASTA_SAIDA}")
    for p in videos_gerados:
        print(" -", p)


if __name__ == "__main__":
    main()
