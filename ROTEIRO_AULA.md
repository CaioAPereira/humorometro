# 🎤 Roteiro da aula: Humorômetro (60 min)

Um arquivo só: `humor.py`. A turma digita a **Parte 1** (Seções 1 a 6) junto com você,
na ordem do arquivo. A **Parte 2** (Seções 7 a 9) é só para mostrar no final.

**Como funciona a digitação:** a Seção 2 cria o loop principal. Nele, as linhas marcadas
`# [Seção N]` só são digitadas quando chegarmos na Seção N. Assim o programa
**roda ao fim de cada seção**.

| Parte | Linhas de código | Linhas no arquivo (com comentários) |
|---|---|---|
| Parte 1: núcleo (codar junto) | 146 | ~240 |
| Parte 2: extras (só mostrar) | 94 | ~135 |

## ✅ Antes da aula
- [ ] Pedir que a turma instale tudo antes (seção "Instalação" do README)
- [ ] Rodar uma vez com internet para baixar o `face_landmarker.task`.
      Leve esse arquivo num pendrive para quem não conseguir baixar
- [ ] Testar na sala, com a luz de lá, e **calibrar os limiares** (Seção 1) olhando as barras
- [ ] **Para ganhar tempo:** mandar a Seção 1 (imports e configurações) no grupo da
      turma para eles colarem. Economiza uns 3 minutos de digitação

---

## 0–5 min · 🎬 Abertura
Rode o arquivo completo (`python humor.py`) virado para a turma. Sorria, faça cara de
surpresa, franza a testa, feche os olhos. Chame 2 ou 3 colegas para o "humor da sala".
> "Em uma hora, vocês vão construir isso."

## 5–10 min · Conceitos
- O computador vê a imagem como uma matriz de números (pixels)
- O **MediaPipe** tem um modelo já treinado que acha **478 pontos** no rosto e, além disso,
  dá **52 notas de expressão** (*blendshapes*): `mouthSmileLeft`, `jawOpen`, `browInnerUp`...
- Fluxo: `câmera → IA acha o rosto → notas → regras → humor (emoji)`
- **A pergunta da aula:** ler um sorriso é ler felicidade? (Volte a ela no final)

## 10–13 min · ✍️ Seção 1: importações e configurações (16 linhas)
- Para que serve cada biblioteca
- Configurações no topo: dá para ajustar sem mexer na lógica
- Os limiares são os "botões de calibrar" das regras da Seção 5

## 13–20 min · ✍️ Seção 2: webcam e loop (25 linhas, **sem** as marcadas `[Seção N]`)
- O loop faz, a cada quadro: `ler → espelhar → mostrar → checar tecla`
- Resolução 1280×720: imagem maior acha rostos mais longe (para a sala toda)
- `try/finally`: mesmo que dê erro, a câmera é liberada
- A linha `if __name__ == "__main__": main()` vai no **fim** do arquivo e as próximas
  seções entram **acima** dela
- ▶️ **Rodar:** a webcam aparece espelhada

## 20–29 min · ✍️ Seção 3: a IA encontra o rosto (30 linhas)
- O modelo é baixado só na 1ª vez e lido em memória (evita erro com acentos no caminho)
- `output_face_blendshapes=True` liga as 52 notas; `num_faces` = quantos rostos
- **BGR × RGB:** o OpenCV e o MediaPipe guardam as cores em ordens diferentes
- As coordenadas vêm **de 0 a 1** e é preciso converter para pixels (`para_pixels`)
- No loop: as 4 linhas `[Seção 3]` (detector, detectar, `for` dos rostos, desenhar)
- ▶️ **Rodar:** o contorno do rosto, olhos e boca aparece (teste com 2 pessoas!)

## 29–37 min · ✍️ Seção 4: as notas do rosto (24 linhas). **O coração**
- O resultado vira um dicionário `{nome: nota}`. Juntamos esquerda + direita com a média
- **Suavização:** a cada quadro a nota anda só 30% do caminho até o valor novo
  (sem isso o humor fica "piscando"). Pergunte: o que acontece com `SUAVIZACAO = 1`?
- ▶️ **Rodar:** as barras sobem e descem com as caretas. Deixe a turma brincar 1 minuto

## 37–44 min · ✍️ Seção 5: regras de humor (22 linhas)
- Uma cadeia de `if`: **a ordem importa**. Pergunte: por que SURPRESO vem antes de CANSADO?
  (Resposta: os dois abrem a boca; a sobrancelha é o que separa surpresa de bocejo)
- TRISTE usa `mouthFrown`, que a IA pontua baixo: por isso o limiar dele é só 0,2
- Os limiares vieram de olhar as barras: é assim que se calibra
- ▶️ **Rodar:** o nome do humor aparece embaixo do queixo, colorido

## 44–52 min · ✍️ Seção 6: emoji em cima da cabeça (29 linhas)
- O `cv2.putText` não desenha emoji (nem acentos), então desenhamos com **círculos,
  linhas e elipses**: o arco da boca muda de 0–180° (sorriso) para 180–360° (triste)
- O tamanho segue a largura do rosto (pontos 234 e 454): longe = emoji pequeno
- ▶️ **Rodar:** o projeto do dia está pronto 🎉

## 52–57 min · 👀 Parte 2: mostrar os extras (sem digitar)
- **Seção 7:** humor da sala = média dos pontos de cada rosto → termômetro colorido
- **Seção 8:** gráfico dos últimos 30 s e o aviso **HORA DE UMA PAUSA!** quando mais da
  metade das leituras for CANSADO (feche os olhos uns 10 s para mostrar)
- **Seção 9:** barra do topo, contador de sorrisos e, ao apertar **Q**, o resumo no
  terminal + planilha `humor_....csv` (abra no Excel/LibreOffice)
- A Parte 2 se liga ao núcleo por **uma linha só** (`aplicar_extras`): apague-a e tudo volta ao básico

## 57–60 min · 💬 Fechamento: limites e ética
- Ele mede **expressão**, não emoção: quem pensa franze a testa; dá para "enganar" com careta
- Pergunte: seria justo um sistema assim dar nota de "atenção" para alunos ou funcionários?
- Usos legais: treinar uma apresentação (estou sorrindo?), feedback anônimo da turma
