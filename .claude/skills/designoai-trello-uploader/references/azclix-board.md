# Quadro AZCLIX (referência da DesignoAI)

Estes IDs foram lidos em 2026-11-09. Cartões podem ser recriados, então confirme
pelo título antes de enviar. Se um ID não existir mais, use o título.

Quadro: "AZCLIX | Conteúdo até 14/11"
ID: 6aefb91d7f27945c83cd49ac

| Título do cartão | ID do cartão | Anexo esperado |
|---|---|---|
| 10/11 · Vídeo V9 · Comentário vira conversa com IA | 6aefb92119e72ee1ead3386d | AZCLIX_V9.mp4 |
| 11/11 · Carrossel C3 · Automação sem programar em 3 passos | 6aefb921d8c462613304990d | C3_card1.png a C3_card4.png |
| 12/11 · Vídeo V5 · A IA que aprende as perguntas repetidas | 6aefb922e7d0f07a593259f1 | AZCLIX_V5.mp4 |
| 14/11 · Vídeo V4 · Sua IA consulta seu banco de dados | 6aefb923b72ca56fc78580d3 | AZCLIX_V4.mp4 |

## Origem dos arquivos

Repositório: `designobr/designoai-reels-media`, branch `azclix-media`, pasta `azclix/`.

- `azclix/AZCLIX_V4.mp4` (8.810.934 bytes)
- `azclix/AZCLIX_V5.mp4` (6.230.811 bytes)
- `azclix/AZCLIX_V9.mp4` (6.934.583 bytes)
- `azclix/carrossel_C3/C3_card1.png` a `C3_card4.png`

Arquivos que não entram em uploads sem pedido explícito:
- `azclix/AZCLIX_V1.mp4`
- `azclix/AZCLIX_V3_equipe_de_IA.mp4`

Não há vídeo do C3: o carrossel é formado por imagens PNG.

## Exemplo de execução

```bash
python3 -I .claude/skills/designoai-trello-uploader/scripts/trello_upload.py \
  --board 6aefb91d7f27945c83cd49ac \
  --item "V4=/caminho/azclix/AZCLIX_V4.mp4" \
  --item "V5=/caminho/azclix/AZCLIX_V5.mp4" \
  --item "V9=/caminho/azclix/AZCLIX_V9.mp4" \
  --item "C3=/caminho/azclix/carrossel_C3/C3_card1.png" \
  --item "C3=/caminho/azclix/carrossel_C3/C3_card2.png" \
  --item "C3=/caminho/azclix/carrossel_C3/C3_card3.png" \
  --item "C3=/caminho/azclix/carrossel_C3/C3_card4.png" \
  --report-dir /caminho/relatorio --dry-run
```

Em um dry-run, o título "V4" casa com "Vídeo V4" e "C3" com "Carrossel C3" porque o
script exige que a referência seja uma palavra inteira no título.
