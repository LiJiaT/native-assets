#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""资产库持续一致性门禁：records / registry / INDEX / approvals。

用法: python -X utf8 scripts/validate_registry.py [--repo .]

检查：
  1. record 必填字段、枚举、project/layer 组合；
  2. asset_id 全局唯一、registry 与 record 字段一致、path 存在；
  3. approval 文件存在且绑定当前 record 文件 hash + 不可变正文 hash + scope；
  4. INDEX.md 覆盖全部 asset_id；
  5. 生命周期：withdrawn 不得有 installed；synthetic 不得有生产安装；
  6. registry 状态、provenance、release_channel 与 record 一致。
exit 0 = 通过；1 = 失败；2 = 依赖缺失。
"""
import argparse
import glob
import hashlib
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

try:
    import yaml
except ImportError:
    print("[FATAL] 需要 pyyaml: python -m pip install pyyaml")
    sys.exit(2)

LAYERS = {"个人级", "项目级", "领域级", "公共级"}
AI_FORMS = {"Memory", "Rule", "Skill", "Workflow", "Hook", "Prompt"}
PROVENANCE = {"verified", "source-excerpt", "synthetic"}
STATUSES = {"approved", "deprecated", "superseded", "withdrawn"}
LIFECYCLE = {"pending", "implemented", "installed", "withdrawn", "superseded"}
RELEASE = {"component-library", "personal", "test-only"}
REQUIRED = ["asset_id", "proposal_id", "title", "form", "secondary_tags", "domains",
            "layer", "ai_form", "source", "owner", "status", "approved_by",
            "approved_date", "provenance_status", "provenance_note"]


def split(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        return None, text
    try:
        return yaml.safe_load(m.group(1)) or {}, m.group(2)
    except yaml.YAMLError:
        return {"__parse_error__": True}, ""


def sha(path):
    # Git checkout line endings differ by OS; hash canonical LF bytes.
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def content_hash(fm, body):
    payload = {k: v for k, v in fm.items() if k != "implementation"}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str) + "\n---\n" + body
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def projects_of(fm):
    raw = fm.get("projects") if fm.get("projects") not in (None, "") else fm.get("project")
    vals = raw if isinstance(raw, list) else [raw]
    return [x for x in vals if x and x != "无"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    errors = []
    reg = json.load(open(repo / "registry.json", encoding="utf-8"))
    entries = reg.get("assets")
    if not isinstance(entries, list):
        print("❌ registry.json 缺 assets 列表"); return 1
    ids = [e.get("asset_id") for e in entries]
    if len(ids) != len(set(ids)):
        errors.append("registry.json 存在重复 asset_id")
    index = (repo / "INDEX.md").read_text(encoding="utf-8") if (repo / "INDEX.md").exists() else ""
    records = {}
    for p in sorted((repo / "assets").rglob("*.md")):
        fm, body = split(p.read_text(encoding="utf-8"))
        if not fm or not fm.get("asset_id"):
            continue
        aid = fm["asset_id"]
        if aid in records:
            errors.append(f"{aid}: record 重复 {records[aid]} / {p}")
        records[aid] = p
        missing = [k for k in REQUIRED if k not in fm]
        if missing:
            errors.append(f"{aid}: record 缺字段 {missing}")
            continue
        if fm.get("layer") not in LAYERS:
            errors.append(f"{aid}: layer 非法")
        if fm.get("ai_form") not in AI_FORMS:
            errors.append(f"{aid}: ai_form 非法")
        if fm.get("provenance_status") not in PROVENANCE:
            errors.append(f"{aid}: provenance_status 非法")
        if fm.get("status") not in STATUSES:
            errors.append(f"{aid}: status 非法")
        if fm.get("release_channel") not in RELEASE:
            errors.append(f"{aid}: release_channel 非法")
        pr = projects_of(fm)
        if fm.get("layer") == "项目级" and len(pr) != 1:
            errors.append(f"{aid}: 项目级必须且只能有一个项目")
        if len(pr) > 1 and fm.get("layer") not in ("领域级", "公共级"):
            errors.append(f"{aid}: 多项目资产只能领域级/公共级")
        impl = fm.get("implementation") or {}
        if impl.get("status") and impl["status"] not in LIFECYCLE:
            errors.append(f"{aid}: implementation.status 非法")
        if impl.get("status") == "withdrawn" and impl.get("installed"):
            errors.append(f"{aid}: withdrawn 不得保留 installed")
        if fm.get("provenance_status") == "synthetic" and fm.get("release_channel") != "test-only":
            errors.append(f"{aid}: synthetic 必须 release_channel=test-only")

        apath = repo / "approvals" / f"{aid}.json"
        if not apath.is_file():
            errors.append(f"{aid}: 缺 approvals/{aid}.json")
        else:
            try:
                a = json.load(open(apath, encoding="utf-8"))
            except Exception as e:
                errors.append(f"{aid}: approval 解析失败 {e}")
                a = {}
            for k in ("asset_id", "approver", "approved_at", "decision",
                      "record_sha256", "content_sha256", "scope"):
                if k not in a:
                    errors.append(f"{aid}: approval 缺 {k}")
            if a.get("asset_id") != aid:
                errors.append(f"{aid}: approval asset_id 不符")
            if a.get("decision") != "approved":
                errors.append(f"{aid}: approval decision 非 approved")
            if a.get("record_sha256") != sha(p):
                errors.append(f"{aid}: record hash 与审批绑定不一致")
            if a.get("content_sha256") != content_hash(fm, body):
                errors.append(f"{aid}: 不可变正文 hash 与审批绑定不一致")
            scope = a.get("scope") or {}
            for k in ("layer", "ai_form", "owner", "provenance_status"):
                if scope.get(k) != fm.get(k):
                    errors.append(f"{aid}: approval scope.{k} 不一致")
            if sorted(scope.get("projects") or []) != sorted(pr):
                errors.append(f"{aid}: approval scope.projects 不一致")

    for e in entries:
        aid = e.get("asset_id")
        if aid not in records:
            errors.append(f"{aid}: registry 条目找不到 record")
            continue
        fm, body = split(records[aid].read_text(encoding="utf-8"))
        for key in ("proposal_id", "title", "layer", "ai_form", "owner",
                    "provenance_status", "release_channel"):
            if e.get(key) != fm.get(key):
                errors.append(f"{aid}: registry.{key} 与 record 不一致")
        if e.get("path") != records[aid].relative_to(repo).as_posix():
            errors.append(f"{aid}: registry.path 与 record 实际路径不一致")
        if aid not in index:
            errors.append(f"{aid}: INDEX.md 未登记")
        impl = e.get("implementation") or {}
        if impl.get("status") == "withdrawn" and impl.get("installed"):
            errors.append(f"{aid}: registry withdrawn 但仍有 installed")
        if fm.get("provenance_status") == "synthetic" and impl.get("installed"):
            errors.append(f"{aid}: synthetic 不得有生产安装记录")
    for aid in records:
        if aid not in ids:
            errors.append(f"{aid}: record 未登记 registry")

    if errors:
        print("❌ 资产库一致性校验失败：")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✅ 资产库一致：{len(records)} 条 record / {len(entries)} 条 registry / approvals / INDEX")
    return 0


if __name__ == "__main__":
    sys.exit(main())
