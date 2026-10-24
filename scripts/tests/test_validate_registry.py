#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_registry 回归：schema/枚举/审批/registry 漂移/损坏 record。"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
PY = sys.executable
FAILS = []


def check(name, cond, detail=""):
    if cond:
        print(f"  OK {name}")
    else:
        FAILS.append(name)
        print(f"  FAIL {name} {detail}")


def run(repo):
    return subprocess.run([PY, "-X", "utf8", str(REPO / "scripts/validate_registry.py"),
                           "--repo", str(repo)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def split(text):
    m = __import__("re").match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, __import__("re").S)
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def dump(fm, body):
    return ("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).rstrip()
            + "\n---\n" + body)


def content_hash(fm, body):
    payload = {k: v for k, v in fm.items() if k != "implementation"}
    return hashlib.sha256((json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                      default=str) + "\n---\n" + body).encode()).hexdigest()


def fresh(root, tag):
    dst = root / tag
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return dst


def rebind_approval(repo, aid, record_path, fm, body):
    ap = json.load(open(repo / "approvals" / f"{aid}.json", encoding="utf-8"))
    ap["record_sha256"] = sha(record_path)
    ap["content_sha256"] = content_hash(fm, body)
    ap["scope"].update({"ai_form": fm.get("ai_form"), "domains": fm.get("domains") or [],
                        "projects": []})
    (repo / "approvals" / f"{aid}.json").write_text(
        json.dumps(ap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_deferred(repo):
    src = repo / "assets/20261022-1705-decision-domain-taxonomy/EA-20261022-01-asset-domain-taxonomy.md"
    fm, body = split(src.read_text(encoding="utf-8"))
    fm.update({"asset_id": "EA-20261022-99", "proposal_id": "prop-test",
               "title": "暂不映射测试", "ai_form": None, "mapping_status": "deferred",
               "mapping_reason": "当前阶段不 AI 化，等待领域 owner 决定"})
    fm.pop("implementation", None)
    p = repo / "assets/test/EA-20261022-99.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dump(fm, body), encoding="utf-8")
    ap = json.load(open(repo / "approvals/EA-20261022-01.json", encoding="utf-8"))
    ap.update({"asset_id": "EA-20261022-99", "proposal_id": "prop-test",
               "record_path": p.relative_to(repo).as_posix()})
    (repo / "approvals/EA-20261022-99.json").write_text(
        json.dumps(ap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rebind_approval(repo, "EA-20261022-99", p, fm, body)
    reg = json.load(open(repo / "registry.json", encoding="utf-8"))
    e = json.loads(json.dumps(reg["assets"][0]))
    e.update({"asset_id": "EA-20261022-99", "proposal_id": "prop-test",
              "title": fm["title"], "ai_form": None,
              "path": p.relative_to(repo).as_posix(),
              "approval_ref": "approvals/EA-20261022-99.json",
              "provenance_note": fm["provenance_note"]})
    e.pop("implementation", None)
    reg["assets"].append(e)
    (repo / "registry.json").write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8")
    idx = repo / "INDEX.md"
    idx.write_text(idx.read_text(encoding="utf-8") + "\n- EA-20261022-99\n", encoding="utf-8")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        base = fresh(root, "base")
        r = run(base)
        check("baseline pass", r.returncode == 0, r.stdout[-300:])

        d = fresh(root, "deferred"); add_deferred(d)
        r = run(d)
        check("deferred/unmapped record accepted", r.returncode == 0, r.stdout[-400:])

        d = fresh(root, "drift")
        reg = json.load(open(d / "registry.json", encoding="utf-8"))
        reg["assets"][0]["status"] = "withdrawn"
        (d / "registry.json").write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8")
        r = run(d)
        check("registry status drift rejected", r.returncode != 0, r.stdout[-300:])

        d = fresh(root, "impl-drift")
        reg = json.load(open(d / "registry.json", encoding="utf-8"))
        reg["assets"][0].setdefault("implementation", {})["package"] = "other.md"
        (d / "registry.json").write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8")
        r = run(d)
        check("registry implementation drift rejected", r.returncode != 0, r.stdout[-300:])

        d = fresh(root, "bad-enum")
        p = next((d / "assets").rglob("EA-20261022-04*.md"))
        fm, body = split(p.read_text(encoding="utf-8"))
        fm.update({"form": "NOT_A_FORM", "domains": ["NOT_A_DOMAIN"],
                   "project": "NOT_A_PROJECT", "approved_date": "NOT_A_DATE",
                   "ai_form": "NOT_A_FORM"})
        p.write_text(dump(fm, body), encoding="utf-8")
        rebind_approval(d, "EA-20261022-04", p, fm, body)
        r = run(d)
        check("invalid enums/date rejected", r.returncode != 0, r.stdout[-300:])

        d = fresh(root, "bad-extra")
        (d / "assets/bad.md").write_text("---\nasset_id: [\n---\n# bad\n", encoding="utf-8")
        r = run(d)
        check("malformed extra record rejected", r.returncode != 0, r.stdout[-300:])

        d = fresh(root, "empty-approver")
        ap = json.load(open(d / "approvals/EA-20261022-01.json", encoding="utf-8"))
        ap["approver"] = ""; ap["approved_at"] = ""
        (d / "approvals/EA-20261022-01.json").write_text(
            json.dumps(ap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        r = run(d)
        check("empty approver/date rejected", r.returncode != 0, r.stdout[-300:])

        d = fresh(root, "scope-drift")
        ap = json.load(open(d / "approvals/EA-20261022-08.json", encoding="utf-8"))
        ap["scope"]["domains"] = ["架构"]
        (d / "approvals/EA-20261022-08.json").write_text(
            json.dumps(ap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        r = run(d)
        check("approval scope domains drift rejected", r.returncode != 0, r.stdout[-300:])

        d = fresh(root, "withdrawn-installed")
        p = next((d / "assets").rglob("EA-20261022-01*.md"))
        fm, body = split(p.read_text(encoding="utf-8"))
        fm["status"] = "withdrawn"
        fm.setdefault("implementation", {})["status"] = "installed"
        p.write_text(dump(fm, body), encoding="utf-8")
        reg = json.load(open(d / "registry.json", encoding="utf-8"))
        for e in reg["assets"]:
            if e["asset_id"] == "EA-20261022-01":
                e["status"] = "withdrawn"
        (d / "registry.json").write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8")
        rebind_approval(d, "EA-20261022-01", p, fm, body)
        r = run(d)
        check("withdrawn record + installed implementation rejected",
              r.returncode != 0, r.stdout[-300:])

        d = fresh(root, "mutable-impl")
        p = next((d / "assets").rglob("EA-20261022-01*.md"))
        fm, body = split(p.read_text(encoding="utf-8"))
        fm.setdefault("implementation", {})["notes"] = "2026-10-24 部署状态写回"
        p.write_text(dump(fm, body), encoding="utf-8")
        rebind_approval(d, "EA-20261022-01", p, fm, body)
        r = run(d)
        check("implementation notes writeback accepted without reapproval",
              r.returncode == 0, r.stdout[-400:])

    if FAILS:
        print(f"FAILED: {len(FAILS)}")
        return 1
    print("PASS: asset registry schema / approval / drift regression")
    return 0


if __name__ == "__main__":
    sys.exit(main())
