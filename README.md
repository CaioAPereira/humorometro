# 😄 Humorômetro: o medidor de humor pela webcam

Projeto de visão computacional em Python. A webcam enxerga o rosto, a IA do
MediaPipe dá **52 "notas"** para ele (de 0 a 1: quanto a boca sorri, quanto a
sobrancelha sobe, quanto o olho fecha...) e regras simples transformam essas
notas em um humor, com emoji, barras, termômetro da sala e gráfico.

| Expressão | Humor |
|---|---|
| 😄 Sorriso | FELIZ |
| 😮 Boca aberta + sobrancelhas para cima | SURPRESO |
| 😢 Cantos da boca para baixo | TRISTE |
| 😠 Sobrancelhas franzidas | BRAVO/CONFUSO |
| 😴 Olhos fechando ou bocejo | CANSADO |
| 😐 Nada disso | NEUTRO |

Ele reconhece até 4 rostos ao mesmo tempo e calcula o **humor da sala**. Se o
CANSADO dominar por um tempo, ele avisa: **HORA DE UMA PAUSA!** Ao sair, mostra um
resumo (quantas vezes você sorriu, % de cada humor) e salva uma planilha `.csv`.

> ⚠️ Ele lê a **expressão** do rosto, não o que a pessoa sente de verdade.
> Quem está concentrado pode franzir a testa sem estar bravo.

## Arquivos

| Arquivo | O que é |
|---|---|
| `humor.py` | O projeto inteiro. **Parte 1** (Seções 1–6): núcleo, codado junto na aula. **Parte 2** (Seções 7–9): extras |
| `ROTEIRO_AULA.md` | Roteiro do apresentador, com o tempo de cada seção |

## Instalação

### Windows
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Ubuntu
```bash
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

(Este projeto não controla mouse nem teclado, então funciona tanto no Xorg quanto no Wayland.)

## Como rodar
```bash
python humor.py
```
Na primeira execução o modelo da IA (~4 MB) é baixado automaticamente.
Na janela da câmera, **Q** sai (e mostra o resumo no terminal).

## Ajustes (Seção 1 do `humor.py`)

Olhe as barras no canto da tela enquanto faz as caretas: elas mostram as notas
que as regras usam. Se um humor dispara fácil ou difícil demais, mude o limiar dele.

| Problema | Solução |
|---|---|
| "Não consegui ler a webcam" | Mude `CAMERA = 0` para `1` |
| Fica FELIZ com qualquer sorrisinho | Aumente `LIMIAR_SORRISO` |
| Fica CANSADO à toa | Aumente `LIMIAR_OLHOS` |
| Fica BRAVO/CONFUSO à toa | Aumente `LIMIAR_BRAVO` |
| TRISTE nunca aparece (ou aparece demais) | Diminua (ou aumente) `LIMIAR_TRISTE` |
| Humor muda rápido demais | Diminua `SUAVIZACAO` |
| Muito lento (FPS baixo) | Diminua `NUM_ROSTOS` |
