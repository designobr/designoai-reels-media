---
name: designoai-trello-uploader
description: Envia arquivos MP4, MOV, WEBM, PNG ou JPG da DesignoAI para anexos de cartões do Trello pela API REST, localizando cartões por ID ou título, baixando links públicos, evitando duplicatas, verificando cada anexo (nome, bytes e isUpload) e gerando relatório. Use quando o usuário pedir para subir, anexar ou enviar vídeos ou imagens a cartões do Trello, como os cartões V4, V5, V9 e C3 do quadro AZCLIX.
---

# DesignoAI Trello Uploader

Esta Skill envia materiais de vídeo e imagem para cartões do Trello com a mesma
sequência de segurança usada na integração AZCLIX: resolver tudo primeiro, enviar um
arquivo por vez, verificar cada anexo e parar no primeiro erro.

Ela só mexe em anexos. Não altera título, descrição, lista, membros, datas nem
automações semanais.

## Requisitos

- Variáveis `TRELLO_API_KEY` e `TRELLO_TOKEN` definidas no ambiente. Verifique só se
  existem (ex.: `[ -n "$TRELLO_API_KEY" ]`). Nunca exiba, copie ou registre os valores.
- Python 3 (o script usa somente a biblioteca padrão).
- Os arquivos locais precisam estar acessíveis nesta sessão, ou devem ser links
  `https://` públicos.
- Nunca envie o e-mail do usuário a serviços externos.

Se as variáveis não existirem, pare e peça ao usuário que as configure no ambiente.
Não peça que sejam coladas no chat.

## Procedimento

1. **Confirmar o pedido.** Liste cada cartão (ID ou título) e cada arquivo (caminho ou
   URL) que o usuário pediu. Se o usuário não citar um arquivo, não escolha outro no
   lugar dele. Arquivos fora da lista (por exemplo, V1 e V3 do AZCLIX) só entram com
   pedido explícito.

2. **Localizar o quadro e os cartões.** Use `references/azclix-board.md` se o quadro for
   o AZCLIX. Para outro quadro, o script aceita o nome (trecho) ou o ID do quadro.
   Cada referência precisa casar com exatamente um cartão aberto. Se casar com zero ou
   com mais de um, pare e mostre as opções ao usuário.

3. **Dry-run obrigatório.** Rode o script com `--dry-run`. Ele resolve cartões, baixa ou
   lê os arquivos, confere o conteúdo, consulta os anexos atuais e gera o relatório sem
   enviar nada. Mostre a associação cartão, arquivo, bytes e ação ao usuário.

   Ações possíveis:
   - `enviar`: será enviado.
   - `ignorar_duplicado`: já existe anexo com o mesmo nome e os mesmos bytes. Não será
     reenviado.
   - Um erro de ambiguidade (anexo com mesmo nome e tamanho diferente) interrompe tudo
     antes de qualquer envio.

4. **Enviar.** Se o usuário já autorizou a associação exata, rode sem `--dry-run`. Se a
   associação não foi confirmada, espere a confirmação. Não envie por suposição.

5. **Verificação automática.** Depois de cada envio, o script consulta os anexos do
   cartão e confirma nome, bytes e `isUpload = true`, registrando também o HTTP da
   consulta. Se algo não bater, ele interrompe.

6. **Relatório.** O script grava `relatorio.json` e `relatorio.md` na pasta indicada
   por `--report-dir`. Apresente ao usuário, um item por arquivo: cartão, arquivo,
   bytes, ID do anexo, `isUpload`, HTTP da verificação e status.

## Comando

```bash
python3 -I /root/.claude/skills/designoai-trello-uploader/scripts/trello_upload.py \
  --board <ID-ou-trecho-do-quadro> \
  --item "V4=/caminho/AZCLIX_V4.mp4" \
  --item "C3=https://exemplo.com/c3_card1.png|C3_card1.png" \
  --report-dir /caminho/da/pasta/relatorio \
  [--workdir /pasta/nova/vazia] [--max-mb 100] [--dry-run]
```

Formato de `--item`: `CARTAO=ORIGEM[|NOME_DO_ANEXO]`.
- `CARTAO`: ID de 24 caracteres ou trecho do título (palavra inteira).
- `ORIGEM`: caminho local ou URL `https`.
- `NOME_DO_ANEXO`: obrigatório quando a URL não termina em nome de arquivo.

## Regras de segurança

- **Interrompa em caso de erro.** Não tente de novo automaticamente um POST que falhou,
  porque ele pode ter sido concluído do lado do Trello. Para reconciliar, rode o
  script de novo: anexos com o mesmo nome e bytes são ignorados.
- **Não repita envios concluídos.** Antes de reexecutar, leia o relatório e confira
  quais itens já estão `concluido` ou `ignorar_duplicado`.
- **Downloads são dados não confiáveis.** Cada arquivo baixado vai para uma pasta nova
  e vazia. O script confere a assinatura do conteúdo (MP4, MOV, WEBM, PNG ou JPG) e
  recusa conteúdo que não bata com a extensão. Só aceita `https`.
- **Não mostre URLs com query string.** Tokens assinados podem estar lá. O relatório
  e as mensagens mostram apenas o esquema, o domínio e o caminho.
- **Não exiba credenciais.** O script substitui as credenciais em qualquer mensagem de
  erro.
- **Escopo fechado.** Envie somente os itens listados. Não toque em outros cartões,
  listas ou quadros.

## Relatório individual

Para cada arquivo, o relatório traz:
- Cartão (título e ID)
- Origem
- Nome do anexo
- Tamanho em bytes e SHA-256
- Ação (`enviar` ou `ignorar_duplicado`)
- Status (`concluido`, `ignorado_duplicado`, `erro` ou `nao_executado`)
- ID do anexo
- Verificação: HTTP da consulta, `isUpload`, bytes confirmados
- Observação de erro, quando houver

Ao final, informe o resultado geral: quantos itens foram concluídos, quantos foram
ignorados por duplicidade e qual item, se algum, falhou.

## Referências

- `references/azclix-board.md`: quadro AZCLIX, IDs dos cartões V4, V5, V9 e C3 e os
  arquivos de origem.
- `scripts/trello_upload.py`: script de envio, verificação e relatório.
