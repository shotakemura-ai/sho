#!/usr/bin/env python3
"""ntfy の「⏰後で」タップをクラウド側（朝刊Routine）で拾い、daily/carryover.json に追記する。

背景（2026-09-07 3層通知設計）:
  PC は夜間・週末に落ちており、ntfy.sh のメッセージキャッシュは約12時間。
  PC の 5分毎ポーリングが取りこぼす 18:00〜翌06:00 と週末のタップを、
  毎朝 06:00 のクラウド朝刊がこのスクリプトで再取得して同じファイルへ書く（二重受信・ID で冪等）。

必要な環境変数（Routine の environment_variables に設定。repo には置かない）:
  NTFY_REPLY_TOPIC  応答トピック（"<id>:snooze" が届く）
  NTFY_TOPIC        通知トピック（題名・詳細URLの補完に使う。無くても可）

使い方: python3 ntfy_carryover.py [--since 13h] [--dry-run]
出力:   "CARRY +N件 / 未処理M件"。標準ライブラリのみ。失敗しても exit 0（朝刊本体を止めない）。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

NTFY_BASE = "https://ntfy.sh/"
CARRY = Path(__file__).resolve().parent / "daily" / "carryover.json"


def fetch(topic: str, since: str) -> list[dict]:
    url = f"{NTFY_BASE}{topic}/json?poll=1&since={since}"
    out: list[dict] = []
    try:
        with urllib.request.urlopen(urllib.request.Request(url), timeout=30) as resp:
            for raw in resp.read().decode("utf-8", "replace").splitlines():
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    m = json.loads(raw)
                except ValueError:
                    continue
                if m.get("event") == "message":
                    out.append(m)
    except Exception as err:  # noqa: BLE001
        print(f"FETCH FAILED {topic[:12]}…: {type(err).__name__}: {err}", file=sys.stderr)
    return out


def load() -> dict:
    if CARRY.exists():
        try:
            d = json.loads(CARRY.read_text(encoding="utf-8"))
            if isinstance(d, dict) and isinstance(d.get("items"), list):
                return d
        except (ValueError, OSError):
            pass
    return {"items": []}


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--since", default="13h")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)

    reply_topic = os.environ.get("NTFY_REPLY_TOPIC")
    if not reply_topic:
        print("CARRY SKIP: NTFY_REPLY_TOPIC 未設定")
        return 0
    main_topic = os.environ.get("NTFY_TOPIC")

    # 応答: "<id>:snooze" だけを拾う（approve/reject は PC 側の責務）
    snoozed: dict[str, int] = {}
    for m in fetch(reply_topic, a.since):
        body = (m.get("message") or "").strip()
        rid, _, verdict = body.partition(":")
        if verdict.strip().lower() == "snooze" and rid.strip():
            snoozed.setdefault(rid.strip(), int(m.get("time") or time.time()))

    # 補完: 通知トピックから同じ ID のボタンを持つ通知を探し、題名と詳細URLを得る
    meta: dict[str, dict] = {}
    if snoozed and main_topic:
        for m in fetch(main_topic, "13h"):   # ntfy.sh のキャッシュは約12h（"d" 単位は 400 になる）
            for act in m.get("actions") or []:
                body = str(act.get("body") or "")
                rid = body.split(":", 1)[0]
                if rid in snoozed and rid not in meta:
                    meta[rid] = {"title": m.get("title") or "", "detail_url": m.get("click") or ""}

    d = load()
    known = {it.get("id") for it in d["items"]}
    added = 0
    for rid, ts in snoozed.items():
        if rid in known:
            continue
        info = meta.get(rid, {})
        d["items"].append({
            "id": rid,
            "title": info.get("title") or f"通知 {rid[:4]}（題名不明・PC側で補完）",
            "kind": "notice",
            "detail_url": info.get("detail_url") or None,
            "snoozed_at": time.strftime("%Y-%m-%d %H:%M", time.gmtime(ts + 9 * 3600)),
            "source": "cloud",
            "shown": 0,
            "resolved": False,
        })
        added += 1

    open_n = sum(1 for it in d["items"] if not it.get("resolved"))
    if added and not a.dry_run:
        CARRY.parent.mkdir(parents=True, exist_ok=True)
        CARRY.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CARRY +{added}件 / 未処理{open_n}件" + ("（dry-run）" if a.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
