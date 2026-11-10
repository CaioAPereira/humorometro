"""
HUMORÔMETRO - Mede o humor do rosto pela webcam

A webcam enxerga o rosto, a IA do MediaPipe dá 52 "notas" para ele (de 0 a 1:
quanto a boca sorri, quanto a sobrancelha sobe...) e regras simples
transformam essas notas em um humor, com emoji, barras e gráfico.

  😄 FELIZ          sorriso alto
  😮 SURPRESO       boca aberta + sobrancelhas para cima
  😢 TRISTE         cantos da boca para baixo
  😠 BRAVO/CONFUSO  sobrancelhas franzidas
  😴 CANSADO        olhos fechando ou bocejo
  😐 NEUTRO         nada disso

Atenção: ele lê a EXPRESSÃO do rosto, não o que a pessoa sente de verdade.

PARTE 1 (Seções 1 a 6): núcleo, codado junto na aula.
PARTE 2 (Seções 7 a 9): extras, mostrados se der tempo.

Rodar: python humor.py            Q = sair
"""

# ##########################################################################
#  PARTE 1 - NÚCLEO (codar junto)
# ##########################################################################

# ==========================================================================
# SEÇÃO 1 - Importações e configurações
# ==========================================================================
import os
import time
import urllib.request

import cv2                      # OpenCV: câmera, imagens e desenhos
import mediapipe as mp          # MediaPipe: IA que encontra o rosto
from mediapipe.tasks.python import BaseOptions, vision

CAMERA = 0                # 0 = webcam padrão (troque para 1 se tiver outra)
NUM_ROSTOS = 4            # quantos rostos a IA procura ao mesmo tempo
SUAVIZACAO = 0.3          # 0 a 1: menor = notas mais estáveis (e mais lentas)

# Limiares das regras de humor (Seção 5): calibre olhando as barras na tela
LIMIAR_SORRISO = 0.5      # sorriso acima disso = FELIZ
LIMIAR_BOCA = 0.3         # boca aberta...
LIMIAR_SOBRANCELHA = 0.3  # ...com sobrancelhas para cima = SURPRESO
LIMIAR_TRISTE = 0.1      # cantos da boca para baixo = TRISTE (a IA dá notas baixas aqui)
LIMIAR_BRAVO = 0.4        # sobrancelhas franzidas = BRAVO/CONFUSO
LIMIAR_OLHOS = 0.5        # olhos fechando = CANSADO
LIMIAR_BOCEJO = 0.6       # boca muito aberta sem surpresa = bocejo = CANSADO


# ==========================================================================
# SEÇÃO 2 - Webcam e loop principal
# As linhas marcadas [Seção N] são digitadas quando chegarmos na Seção N.
# ==========================================================================
def main():
    backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY  # Windows abre mais rápido
    camera = cv2.VideoCapture(CAMERA, backend)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)     # imagem maior: acha rostos mais longe
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    detector = carregar_detector()                                   # [Seção 3]
    estado = {"notas": {}}      # o que o programa "lembra" de um quadro para o outro
    inicio = time.time()

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("Não consegui ler a webcam (troque CAMERA na Seção 1).")
                break
            frame = cv2.flip(frame, 1)      # espelha: fica igual a um espelho
            agora = time.time()
            humores = []                    # um humor para cada rosto encontrado

            resultado = detectar_rostos(detector, frame, int((agora - inicio) * 1000))  # [Seção 3]
            for i, pontos in enumerate(resultado.face_landmarks):                     # [Seção 3]
                desenhar_rosto(frame, pontos)                                         # [Seção 3]
                notas = ler_notas(resultado.face_blendshapes[i], i, estado)           # [Seção 4]
                if i == 0:                                                            # [Seção 4]
                    desenhar_barras(frame, notas)                                     # [Seção 4]
                humor = classificar_humor(notas)                                      # [Seção 5]
                humores.append(humor)                                                 # [Seção 5]
                escrever_humor(frame, humor, pontos)                                  # [Seção 5]
                desenhar_emoji(frame, humor, pontos)                                  # [Seção 6]

            aplicar_extras(frame, humores, estado, agora)   # [Parte 2] apague para desligar
            cv2.imshow("Humorometro", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()            # haja o que houver: libera a câmera
        cv2.destroyAllWindows()


# ==========================================================================
# SEÇÃO 3 - IA encontra o rosto (e desenhamos o contorno)
# ==========================================================================
URL_MODELO = ("https://storage.googleapis.com/mediapipe-models/face_landmarker/"
              "face_landmarker/float16/latest/face_landmarker.task")
ARQUIVO_MODELO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_landmarker.task")


def carregar_detector():
    if not os.path.exists(ARQUIVO_MODELO):          # baixa o modelo treinado só na 1ª vez
        print("Baixando o modelo de rostos (~4 MB)...")
        urllib.request.urlretrieve(URL_MODELO, ARQUIVO_MODELO)
    with open(ARQUIVO_MODELO, "rb") as arquivo:     # ler em memória evita erro com acentos na pasta
        modelo = arquivo.read()
    opcoes = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_buffer=modelo),
        running_mode=vision.RunningMode.VIDEO,      # VIDEO: aproveita o quadro anterior
        output_face_blendshapes=True,               # as 52 "notas" de expressão
        num_faces=NUM_ROSTOS)
    return vision.FaceLandmarker.create_from_options(opcoes)


def detectar_rostos(detector, frame, tempo_ms):
    """Retorna, para cada rosto, 478 pontos (x e y de 0 a 1) e as 52 notas."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    # OpenCV usa BGR, MediaPipe usa RGB
    imagem = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    return detector.detect_for_video(imagem, tempo_ms)


def para_pixels(ponto, frame):
    """Converte coordenada de 0 a 1 em pixel da imagem."""
    altura, largura = frame.shape[:2]
    return int(ponto.x * largura), int(ponto.y * altura)


def desenhar_rosto(frame, pontos, cor=(0, 255, 0)):
    # CONTOURS = contorno do rosto, olhos, sobrancelhas e boca (pares de pontos a ligar)
    for conexao in vision.FaceLandmarksConnections.FACE_LANDMARKS_CONTOURS:
        cv2.line(frame, para_pixels(pontos[conexao.start], frame),
                 para_pixels(pontos[conexao.end], frame), cor, 1, cv2.LINE_AA)

# Pontos úteis: 10 = alto da testa | 152 = queixo | 234 e 454 = laterais do rosto


# ==========================================================================
# SEÇÃO 4 - As "notas" do rosto (blendshapes)
# ==========================================================================
def ler_notas(categorias, i, estado):
    """Pega as notas que importam e suaviza (tira a tremedeira de um quadro para o outro)."""
    cru = {c.category_name: c.score for c in categorias}   # ex.: {"jawOpen": 0.12, ...}

    def media(nome):                                        # lado esquerdo e direito juntos
        return (cru[nome + "Left"] + cru[nome + "Right"]) / 2

    atual = {"sorriso": media("mouthSmile"),
             "boca_aberta": cru["jawOpen"],
             "sobrancelha_cima": cru["browInnerUp"],
             "sobrancelha_baixo": media("browDown"),
             "boca_triste": media("mouthFrown"),
             "olhos_fechando": media("eyeBlink")}
    # Média móvel: anda só uma fração do caminho até o valor novo
    anterior = estado["notas"].get(i, atual)
    suave = {nome: anterior[nome] + (atual[nome] - anterior[nome]) * SUAVIZACAO for nome in atual}
    estado["notas"][i] = suave
    return suave


def desenhar_barras(frame, notas):
    cv2.rectangle(frame, (0, 60), (290, 60 + 24 * len(notas)), (30, 30, 30), -1)   # fundo escuro
    for linha, (nome, valor) in enumerate(notas.items()):
        y = 80 + linha * 24
        cv2.putText(frame, nome, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.rectangle(frame, (160, y - 12), (160 + int(valor * 120), y), (0, 200, 255), -1)
        cv2.rectangle(frame, (160, y - 12), (280, y), (255, 255, 255), 1)


# ==========================================================================
# SEÇÃO 5 - Regras: das notas para o humor
# ==========================================================================
# Cores em BGR (Azul, Verde, Vermelho). O cv2.putText não escreve acentos.
CORES = {"FELIZ": (0, 220, 120), "SURPRESO": (255, 200, 0), "TRISTE": (230, 140, 40),
         "BRAVO/CONFUSO": (60, 60, 255), "CANSADO": (200, 120, 160), "NEUTRO": (200, 200, 200)}


def classificar_humor(notas):
    # A ORDEM importa: a primeira regra que bater decide
    if notas["sorriso"] > LIMIAR_SORRISO:
        return "FELIZ"
    if notas["boca_aberta"] > LIMIAR_BOCA and notas["sobrancelha_cima"] > LIMIAR_SOBRANCELHA:
        return "SURPRESO"
    if notas["boca_triste"] > LIMIAR_TRISTE:
        return "TRISTE"
    if notas["sobrancelha_baixo"] > LIMIAR_BRAVO:
        return "BRAVO/CONFUSO"
    if notas["olhos_fechando"] > LIMIAR_OLHOS or notas["boca_aberta"] > LIMIAR_BOCEJO:
        return "CANSADO"
    return "NEUTRO"


def escrever_humor(frame, humor, pontos):
    x, y = para_pixels(pontos[152], frame)          # embaixo do queixo
    (largura_texto, _), _ = cv2.getTextSize(humor, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)
    cv2.putText(frame, humor, (x - largura_texto // 2, y + 35), cv2.FONT_HERSHEY_DUPLEX, 0.8,
                CORES[humor], 2, cv2.LINE_AA)


# ==========================================================================
# SEÇÃO 6 - Emoji desenhado em cima da cabeça (só com círculos e linhas)
# ==========================================================================
def desenhar_emoji(frame, humor, pontos):
    altura, largura = frame.shape[:2]
    r = max(int(abs(pontos[454].x - pontos[234].x) * largura * 0.3), 15)  # tamanho segue o rosto
    x = int(pontos[10].x * largura)
    y = max(int(pontos[10].y * altura) - r - 15, r + 55)  # acima da testa, sem entrar na barra do topo
    preto = (0, 0, 0)
    cv2.circle(frame, (x, y), r, (0, 215, 255), -1, cv2.LINE_AA)     # cara amarela
    cv2.circle(frame, (x, y), r, preto, 2, cv2.LINE_AA)

    for olho_x in (x - r // 3, x + r // 3):                          # olhos
        if humor == "CANSADO":
            cv2.line(frame, (olho_x - r // 7, y - r // 4), (olho_x + r // 7, y - r // 4), preto, 3)
        else:
            cv2.circle(frame, (olho_x, y - r // 4), r // 5 if humor == "SURPRESO" else r // 9, preto, -1)
    if humor == "BRAVO/CONFUSO":                                     # sobrancelhas em V
        cv2.line(frame, (x - r // 2, y - r // 2), (x - r // 8, y - r // 3), preto, 3)
        cv2.line(frame, (x + r // 2, y - r // 2), (x + r // 8, y - r // 3), preto, 3)
    if humor == "TRISTE":                                            # lágrima azul
        cv2.ellipse(frame, (x - r // 3, y + r // 8), (r // 10, r // 6), 0, 0, 360, (255, 150, 50), -1)
    if humor == "CANSADO":
        cv2.putText(frame, "z", (x + r, y - r // 2), cv2.FONT_HERSHEY_DUPLEX, r / 30, (255, 255, 255), 2)

    if humor == "FELIZ":                                             # boca
        cv2.ellipse(frame, (x, y + r // 6), (r // 2, r // 3), 0, 0, 180, preto, 3)    # arco sorrindo
    elif humor == "SURPRESO":
        cv2.ellipse(frame, (x, y + r // 3), (r // 6, r // 4), 0, 0, 360, preto, -1)   # boca em "O"
    elif humor in ("BRAVO/CONFUSO", "TRISTE"):
        cv2.ellipse(frame, (x, y + r // 2), (r // 3, r // 5), 0, 180, 360, preto, 3)  # arco triste
    else:
        cv2.line(frame, (x - r // 3, y + r // 3), (x + r // 3, y + r // 3), preto, 3)  # boca reta


# ##########################################################################
#  PARTE 2 - EXTRAS (mostrar se der tempo; o núcleo funciona sem isto)
#  Para desligar tudo: apague a linha marcada [Parte 2] na Seção 2.
# ##########################################################################

# ==========================================================================
# SEÇÃO 7 - Humor da sala: média de todos os rostos num termômetro
# ==========================================================================
import atexit
import csv
from collections import Counter, deque
from datetime import datetime

PONTOS_HUMOR = {"FELIZ": 1.0, "SURPRESO": 0.8, "NEUTRO": 0.5, "BRAVO/CONFUSO": 0.25, "TRISTE": 0.15,
                "CANSADO": 0.0}


def humor_da_sala(humores):
    """De 0 (sala cansada) a 1 (sala feliz). None se não há ninguém."""
    if not humores:
        return None
    return sum(PONTOS_HUMOR[h] for h in humores) / len(humores)


def cor_termometro(valor):
    return (0, int(255 * valor), int(255 * (1 - valor)))    # vermelho -> amarelo -> verde (BGR)


def desenhar_termometro(frame, valor):
    altura, largura = frame.shape[:2]
    x1, x2, topo, base = largura - 55, largura - 25, 80, altura - 130
    cv2.rectangle(frame, (x1, topo), (x2, base), (60, 60, 60), -1)
    if valor is not None:
        nivel = int(base - (base - topo) * valor)
        cv2.rectangle(frame, (x1, nivel), (x2, base), cor_termometro(valor), -1)
        cv2.putText(frame, f"{valor * 100:.0f}%", (x1 - 10, base + 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.rectangle(frame, (x1, topo), (x2, base), (255, 255, 255), 1)
    cv2.putText(frame, "SALA", (x1 - 5, topo - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)


# ==========================================================================
# SEÇÃO 8 - Gráfico do humor no tempo + aviso de pausa
# ==========================================================================
JANELA_GRAFICO = 30       # segundos mostrados no gráfico
LIMIAR_PAUSA = 0.5        # se mais da metade dos rostos ficou CANSADO na janela -> pausa
TEMPO_MINIMO_PAUSA = 10   # segundos de histórico antes de poder avisar


def desenhar_grafico(frame, historico, agora):
    altura, largura = frame.shape[:2]
    x1, x2, topo, base = 10, largura - 80, altura - 100, altura - 10
    cv2.rectangle(frame, (x1, topo), (x2, base), (30, 30, 30), -1)
    pontos = [(int(x2 - (agora - t) / JANELA_GRAFICO * (x2 - x1)), int(base - v * (base - topo)))
              for t, v, _ in historico if v is not None]
    for a, b in zip(pontos, pontos[1:]):
        cv2.line(frame, a, b, cor_termometro((base - b[1]) / (base - topo)), 2, cv2.LINE_AA)
    cv2.putText(frame, f"humor nos ultimos {JANELA_GRAFICO} s", (x1 + 5, topo + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)


def precisa_de_pausa(historico, agora):
    todos = [h for _, _, humores in historico for h in humores]
    if not todos or agora - historico[0][0] < TEMPO_MINIMO_PAUSA:
        return False
    return todos.count("CANSADO") / len(todos) > LIMIAR_PAUSA


# ==========================================================================
# SEÇÃO 9 - Painel (HUD), resumo ao sair e planilha CSV
# ==========================================================================
def escrever_centralizado(frame, texto, y, cor=(255, 255, 255)):
    (largura_texto, _), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)
    x = (frame.shape[1] - largura_texto) // 2
    cv2.putText(frame, texto, (x, y), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 7, cv2.LINE_AA)  # contorno
    cv2.putText(frame, texto, (x, y), cv2.FONT_HERSHEY_DUPLEX, 1.5, cor, 3, cv2.LINE_AA)


def mostrar_resumo(estado):
    """Roda sozinho quando o programa fecha (atexit)."""
    total = sum(estado["contagem"].values())
    if total == 0:
        return
    minutos, segundos = divmod(int(time.time() - estado["comeco"]), 60)
    print("\n========== RESUMO DO HUMORÔMETRO ==========")
    print(f"Tempo: {minutos} min {segundos} s | Você sorriu {estado['sorrisos']} vezes")
    for humor in PONTOS_HUMOR:
        parte = estado["contagem"][humor] / total
        print(f"{humor:<14} {parte * 100:5.1f}% {'#' * round(parte * 30)}")
    nome = datetime.now().strftime("humor_%Y%m%d_%H%M%S.csv")
    with open(nome, "w", newline="", encoding="utf-8") as arquivo:   # abre no Excel/LibreOffice
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["hora", "rostos", "humor_da_sala_%", "humores"])
        escritor.writerows(estado["linhas"])
    print(f"Planilha salva: {nome}")


def aplicar_extras(frame, humores, estado, agora):
    if "historico" not in estado:               # 1ª vez: prepara a memória dos extras
        estado.update(historico=deque(), contagem=Counter(), sorrisos=0, primeiro_humor=None,
                      linhas=[], ultima_linha=0.0, comeco=agora, fps=0.0, ultimo_quadro=agora)
        cv2.namedWindow("Humorometro", cv2.WINDOW_NORMAL)   # janela que dá para maximizar
        atexit.register(mostrar_resumo, estado)
    altura, largura = frame.shape[:2]
    valor = humor_da_sala(humores)

    # Memória: histórico do gráfico, contagem de humores e sorrisos do 1º rosto
    estado["historico"].append((agora, valor, humores))
    while agora - estado["historico"][0][0] > JANELA_GRAFICO:
        estado["historico"].popleft()
    estado["contagem"].update(humores)
    primeiro = humores[0] if humores else None
    if primeiro == "FELIZ" and estado["primeiro_humor"] != "FELIZ":
        estado["sorrisos"] += 1                 # contou na hora em que o sorriso começou
    estado["primeiro_humor"] = primeiro
    if agora - estado["ultima_linha"] >= 1.0 and humores:   # uma linha por segundo na planilha
        estado["linhas"].append([datetime.now().strftime("%H:%M:%S"), len(humores),
                                 round(valor * 100), " ".join(humores)])
        estado["ultima_linha"] = agora

    # Desenhos: termômetro (Seção 7), gráfico (Seção 8) e barra superior
    desenhar_termometro(frame, valor)
    desenhar_grafico(frame, estado["historico"], agora)
    cv2.rectangle(frame, (0, 0), (largura, 50), (30, 30, 30), -1)
    cv2.putText(frame, "HUMOROMETRO", (15, 34), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 215, 255), 2, cv2.LINE_AA)
    estado["fps"] = 0.9 * estado["fps"] + 0.1 / max(agora - estado["ultimo_quadro"], 1e-6)
    estado["ultimo_quadro"] = agora
    cv2.putText(frame, f"{len(humores)} rosto(s) | sorrisos: {estado['sorrisos']} | {estado['fps']:.0f} FPS",
                (largura - 360, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)

    if not humores:
        escrever_centralizado(frame, "PROCURANDO ROSTOS...", altura // 2)
    elif precisa_de_pausa(estado["historico"], agora) and int(agora * 2) % 2:   # pisca
        escrever_centralizado(frame, "HORA DE UMA PAUSA!", altura // 2, CORES["CANSADO"])


# ==========================================================================
# SEMPRE A ÚLTIMA LINHA DO ARQUIVO: inicia o programa.
# (Digite na Seção 2 e escreva as próximas seções ACIMA dela.)
# ==========================================================================
if __name__ == "__main__":
    main()
