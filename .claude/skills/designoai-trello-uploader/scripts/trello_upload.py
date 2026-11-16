#!/usr/bin/env python3
"""DesignoAI Trello Uploader.

Anexa arquivos (MP4, MOV, WEBM, PNG, JPG) a cartões do Trello pela API REST.
Usa somente os endpoints de quadros, cartões e anexos. Não altera título,
descrição, lista, membros ou qualquer outro dado do cartão.

Uso:
  python3 -I trello_upload.py --board AZCLIX \
      --item "V4=/caminho/AZCLIX_V4.mp4" \
      --item "C3=https://exemplo.com/c3_card1.png|C3_card1.png" \
      --report-dir /caminho/relatorio [--dry-run]

Formato de --item:  CARTAO=ORIGEM[|NOME_DO_ANEXO]
  CARTAO  ID do cartão (24 caracteres hexadecimais) ou trecho do título que
          aparece em exatamente um cartão aberto do quadro.
  ORIGEM  caminho local ou URL https pública.
  NOME    obrigatório para URLs que não terminam em nome de arquivo.

Fluxo:
  1. Resolve o quadro e os cartões (erro se houver ambiguidade).
  2. Baixa ou lê cada arquivo e confere o conteúdo com a extensão.
  3. Consulta os anexos atuais de cada cartão e marca duplicatas.
  4. Só então envia. Qualquer erro interrompe a execução.
  5. Após cada envio, confere nome, bytes e isUpload no próprio Trello.

Códigos de saída: 0 = concluído (ou dry-run), 1 = interrompido por erro.
"""

import argparse
import hashlib
import json
import os
import pathlib
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone

API = "https://api.trello.com/1"
UA = "DesignoAI-Trello-Uploader/1.0"
DEFAULT_MAX_MB = 100
HEX24 = re.compile(r"[0-9a-f]{24}")
CHUNK = 1 << 20


class Stop(Exception):
    """Erro que interrompe a execução sem novos envios."""


def redact_url(url):
    """Remove a query string (pode conter tokens assinados) antes de mostrar a URL."""
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


class Trello:
    def __init__(self):
        self.key = os.environ.get("TRELLO_API_KEY", "")
        self.token = os.environ.get("TRELLO_TOKEN", "")
        if not self.key or not self.token:
            raise Stop("TRELLO_API_KEY e/ou TRELLO_TOKEN não estão definidas no ambiente.")

    def _scrub(self, text):
        for secret in (self.key, self.token):
            if secret:
                text = text.replace(secret, "***")
        return text

    def call(self, method, path, params=None, body=None, content_type=None):
        query = {"key": self.key, "token": self.token}
        if params:
            query.update(params)
        url = f"{API}{path}?{urllib.parse.urlencode(query)}"
        req = urllib.request.Request(url, data=body, method=method,
                                     headers={"User-Agent": UA})
        if content_type:
            req.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as e:
            detail = self._scrub(e.read(500).decode("utf-8", "replace"))
            raise Stop(f"{method} {path} retornou HTTP {e.code}: {detail}") from None
        except urllib.error.URLError as e:
            raise Stop(f"falha de rede em {method} {path}: {self._scrub(str(e.reason))}") from None


def safe_name(name):
    return re.sub(r"[^A-Za-z0-9._ -]", "_", name)


def sniff(path, upload_name):
    """Confere se o conteúdo corresponde à extensão do arquivo."""
    ext = pathlib.PurePosixPath(upload_name).suffix.lower()
    with open(path, "rb") as f:
        head = f.read(16)
    if ext in (".mp4", ".mov", ".m4v"):
        ok = head[4:8] in (b"ftyp", b"moov", b"mdat", b"wide")
    elif ext == ".webm":
        ok = head[:4] == b"\x1a\x45\xdf\xa3"
    elif ext == ".png":
        ok = head[:8] == b"\x89PNG\r\n\x1a\n"
    elif ext in (".jpg", ".jpeg"):
        ok = head[:3] == b"\xff\xd8\xff"
    else:
        raise Stop(f"extensão não permitida para anexo: '{ext}' ({upload_name})")
    if not ok:
        raise Stop(f"o conteúdo de {upload_name} não corresponde à extensão {ext}")


def prepare(source, name, workdir, max_bytes):
    """Retorna (caminho_local, nome_do_anexo, tamanho, sha256) validados."""
    if re.match(r"https?://", source, re.IGNORECASE):
        if not source.lower().startswith("https://"):
            raise Stop("somente links https são aceitos")
        upload_name = name or pathlib.PurePosixPath(urllib.parse.urlsplit(source).path).name
        if not upload_name:
            raise Stop(f"a URL {redact_url(source)} não tem nome de arquivo; informe com |NOME")
        upload_name = safe_name(upload_name)
        dest = workdir / upload_name
        req = urllib.request.Request(source, headers={"User-Agent": UA})
        total = 0
        try:
            with urllib.request.urlopen(req, timeout=600) as resp, open(dest, "wb") as out:
                while True:
                    chunk = resp.read(CHUNK)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise Stop(f"download maior que o limite de {max_bytes} bytes")
                    out.write(chunk)
        except urllib.error.HTTPError as e:
            raise Stop(f"download de {redact_url(source)} retornou HTTP {e.code}") from None
        except urllib.error.URLError as e:
            raise Stop(f"falha no download de {redact_url(source)}: {e.reason}") from None
        path = dest
    else:
        path = pathlib.Path(source).expanduser().resolve()
        if not path.is_file():
            raise Stop(f"arquivo local não encontrado: {source}")
        if path.stat().st_size > max_bytes:
            raise Stop(f"arquivo maior que o limite de {max_bytes} bytes: {path.name}")
        upload_name = name or path.name

    sniff(path, upload_name)
    size = path.stat().st_size
    if size == 0:
        raise Stop(f"arquivo vazio: {upload_name}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, upload_name, size, digest


def multipart(upload_name, data):
    boundary = uuid.uuid4().hex
    fname = re.sub(r'[\r\n"]', "_", upload_name)
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="name"\r\n\r\n{upload_name}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8")
    tail = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return head + data + tail, f"multipart/form-data; boundary={boundary}"


def resolve_board(tr, ref):
    _, boards = tr.call("GET", "/members/me/boards", {"fields": "name,closed"})
    open_boards = [b for b in boards if not b["closed"]]
    if HEX24.fullmatch(ref):
        found = [b for b in open_boards if b["id"] == ref]
    else:
        found = [b for b in open_boards if ref.lower() in b["name"].lower()]
    if len(found) != 1:
        options = "; ".join(f"{b['name']} ({b['id']})" for b in open_boards)
        raise Stop(f"quadro '{ref}' encontrou {len(found)} resultados (esperado 1). Disponíveis: {options}")
    return found[0]


def resolve_card(ref, cards):
    if HEX24.fullmatch(ref):
        found = [c for c in cards if c["id"] == ref]
    else:
        pattern = re.compile(
            r"(?<![0-9A-Za-zÀ-ÿ])" + re.escape(ref) + r"(?![0-9A-Za-zÀ-ÿ])",
            re.IGNORECASE,
        )
        found = [c for c in cards if pattern.search(c["name"])]
    if len(found) != 1:
        titles = "; ".join(c["name"] for c in found) or "nenhum"
        raise Stop(f"cartão '{ref}' encontrou {len(found)} cartões abertos (esperado 1): {titles}")
    return found[0]


def write_report(report_dir, meta, items):
    report_dir.mkdir(parents=True, exist_ok=True)
    payload = {"gerado_em_utc": datetime.now(timezone.utc).isoformat(), **meta, "itens": items}
    (report_dir / "relatorio.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Relatório de uploads no Trello",
        "",
        f"Quadro: {meta.get('quadro', '')}",
        f"Resultado geral: {meta.get('resultado', '')}",
        "",
    ]
    for n, it in enumerate(items, 1):
        lines += [
            f"## {n}. {it.get('arquivo', '')}",
            f"- Cartão: {it.get('cartao_titulo', '')} ({it.get('cartao_id', '')})",
            f"- Origem: {it.get('origem', '')}",
            f"- Tamanho: {it.get('bytes', '')} bytes",
            f"- SHA-256: {it.get('sha256', '')}",
            f"- Ação: {it.get('acao', '')}",
            f"- Status: {it.get('status', '')}",
            f"- ID do anexo: {it.get('anexo_id', '') or '-'}",
            f"- Verificação: HTTP {it.get('verificacao_http', '-')}, isUpload={it.get('isUpload', '-')}, bytes confirmados={it.get('bytes_confirmados', '-')}",
            f"- Observação: {it.get('erro', '') or '-'}",
            "",
        ]
    (report_dir / "relatorio.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Anexa arquivos a cartões do Trello.")
    ap.add_argument("--board", required=True, help="Nome (trecho) ou ID do quadro.")
    ap.add_argument("--item", action="append", required=True, help="CARTAO=ORIGEM[|NOME]")
    ap.add_argument("--report-dir", required=True)
    ap.add_argument("--workdir", help="Pasta de trabalho para downloads (nova e vazia).")
    ap.add_argument("--max-mb", type=int, default=DEFAULT_MAX_MB)
    ap.add_argument("--dry-run", action="store_true", help="Resolve tudo e gera relatório, sem enviar.")
    args = ap.parse_args()

    report_dir = pathlib.Path(args.report_dir).expanduser().resolve()
    workdir = pathlib.Path(args.workdir).expanduser().resolve() if args.workdir else pathlib.Path(tempfile.mkdtemp(prefix="trello-upload-"))
    workdir.mkdir(parents=True, exist_ok=True)
    max_bytes = args.max_mb * 1024 * 1024

    meta = {"quadro": "", "modo": "simulacao" if args.dry_run else "envio", "resultado": ""}
    items = []
    current = None
    try:
        tr = Trello()
        board = resolve_board(tr, args.board)
        meta["quadro"] = f"{board['name']} ({board['id']})"
        _, all_cards = tr.call("GET", f"/boards/{board['id']}/cards", {"fields": "name,closed"})
        cards = [c for c in all_cards if not c["closed"]]

        # Fase 1: resolver tudo e checar duplicatas antes de qualquer envio.
        seen = set()
        for raw in args.item:
            if "=" not in raw:
                raise Stop(f"item inválido (use CARTAO=ORIGEM): {raw}")
            ref, rest = raw.split("=", 1)
            ref, rest = ref.strip(), rest.strip()
            source, name = (rest.rsplit("|", 1) if "|" in rest else (rest, None))
            card = resolve_card(ref, cards)
            path, upload_name, size, digest = prepare(source, name, workdir, max_bytes)

            key = (card["id"], upload_name)
            if key in seen:
                raise Stop(f"o mesmo arquivo ({upload_name}) foi pedido duas vezes para o cartão {card['name']}")
            seen.add(key)

            _, atts = tr.call("GET", f"/cards/{card['id']}/attachments",
                              {"fields": "id,name,bytes,isUpload"})
            same_name = [a for a in atts if a["name"] == upload_name]
            if any(int(a["bytes"]) == size for a in same_name):
                acao = "ignorar_duplicado"
            elif same_name:
                raise Stop(f"o cartão '{card['name']}' já tem um anexo '{upload_name}' com outro tamanho. Resolva antes de enviar.")
            else:
                acao = "enviar"

            items.append({
                "cartao_id": card["id"], "cartao_titulo": card["name"],
                "arquivo": upload_name, "origem": redact_url(source) if source.lower().startswith("http") else source,
                "bytes": size, "sha256": digest, "acao": acao,
                "status": "simulado" if args.dry_run else "pendente",
                "_path": str(path),
            })

        if args.dry_run:
            for it in items:
                it["status"] = "simulado"
            meta["resultado"] = "simulacao concluida, nada foi enviado"
        else:
            # Fase 2: enviar, um por vez, verificando cada anexo.
            for it in items:
                if it["acao"] == "ignorar_duplicado":
                    it["status"] = "ignorado_duplicado"
                    continue
                current = it
                data = pathlib.Path(it["_path"]).read_bytes()
                body, ctype = multipart(it["arquivo"], data)
                _, resp = tr.call("POST", f"/cards/{it['cartao_id']}/attachments",
                                  body=body, content_type=ctype)
                it["anexo_id"] = (resp or {}).get("id")
                code, atts = tr.call("GET", f"/cards/{it['cartao_id']}/attachments",
                                     {"fields": "id,name,bytes,isUpload"})
                match = [a for a in atts if a["id"] == it["anexo_id"]]
                if not match:
                    raise Stop(f"anexo {it['arquivo']} não apareceu na verificação do cartão")
                a = match[0]
                it["verificacao_http"] = code
                it["isUpload"] = a.get("isUpload")
                it["bytes_confirmados"] = a.get("bytes")
                if a["name"] != it["arquivo"] or int(a["bytes"]) != it["bytes"] or a.get("isUpload") is not True:
                    raise Stop(f"verificação falhou para {it['arquivo']}: nome, bytes ou isUpload não conferem")
                it["status"] = "concluido"
            meta["resultado"] = "todos os itens concluídos e verificados"
    except Stop as e:
        # Marca o envio que falhou e o que ficou sem executar; preserva o relatório parcial.
        if current is not None and current.get("status") == "pendente":
            current["status"] = "erro"
            current["erro"] = str(e)
        for it in items:
            if it.get("status") == "pendente":
                it["status"] = "nao_executado"
        meta["resultado"] = f"INTERROMPIDO: {e}. Itens já concluídos permanecem no Trello; reexecute para reconciliar (anexos iguais são ignorados)."
        for it in items:
            it.pop("_path", None)
        write_report(report_dir, meta, items)
        print(f"ERRO: {e}", file=sys.stderr)
        print(f"Relatório parcial: {report_dir}", file=sys.stderr)
        sys.exit(1)

    for it in items:
        it.pop("_path", None)
    write_report(report_dir, meta, items)
    for it in items:
        print(f"{it['status']:<20} {it['cartao_titulo'][:45]:<45} {it['arquivo']} ({it['bytes']} bytes)")
    print(f"Relatório: {report_dir}")


if __name__ == "__main__":
    main()
