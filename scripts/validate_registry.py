#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""资产库持续一致性门禁：records / registry / INDEX / approvals。

用法: python -X utf8 scripts/validate_registry.py [--repo .]

检查：
  1. 每条 record 执行 asset-record schema + 枚举/类型/日期/占位符；
  2. asset_id 全局唯一，registry 与 record 全字段一致，path 存在；
  3. approval 执行 approval schema、非空审批人/日期、record_path/proposal_id/
     record+正文 hash、scope（含 domains/release_channel）一致；配置 allowed_signers
     时还验证 SSH 签名；
  4. INDEX.md 覆盖全部 asset_id；
  5. 生命周期：withdrawn 不得有 installed；synthetic 只能 test-only 且不得生产安装；
  6. 额外/损坏的 record 文件、非法枚举、registry 漂移均失败。
exit 0 = 通过；1 = 失败；2 = 依赖缺失。
"""
import argparse
import glob
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
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
PROJECTS = {"LPDDR6", "HBM"}
DOMAINS = {"架构", "设计", "验证", "时序", "DFT", "后仿", "Firmware", "模拟", "后端"}
PLACEHOLDERS = {"", "-", "--", "...", "…", "待填", "待定", "待补充", "todo", "tbd",
                "n/a", "na", "xxx", "示例", "<待填>"}


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


def projects_of(fm, errors=None, aid=""):
    if "projects" in fm and not isinstance(fm.get("projects"), list):
        if errors is not None:
            errors.append(f"{aid}: projects 必须是列表")
        return []
    raw = fm.get("projects") if fm.get("projects") not in (None, "") else fm.get("project")
    vals = raw if isinstance(raw, list) else [raw]
    out = []
    for x in vals:
        if x in (None, "", "无"):
            continue
        if not isinstance(x, str):
            if errors is not None:
                errors.append(f"{aid}: project 元素必须是字符串")
            continue
        out.append(x)
    if len(out) != len(set(out)) and errors is not None:
        errors.append(f"{aid}: project 重复 {out}")
    return out


def valid_date(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:[T ][0-9:.+Z-]+)?", text):
        return False
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def is_placeholder(value):
    return value is None or not isinstance(value, str) or value.strip().lower() in PLACEHOLDERS


def validate_schema(value, schema, path="$"):
    errors = []
    if not isinstance(schema, dict):
        return errors
    if "oneOf" in schema:
        matched = sum(1 for s in schema["oneOf"] if not validate_schema(value, s, path))
        if matched != 1:
            errors.append(f"{path}: oneOf 匹配 {matched} 个分支")
        return errors
    if "anyOf" in schema:
        if not any(not validate_schema(value, s, path) for s in schema["anyOf"]):
            errors.append(f"{path}: anyOf 无匹配分支")
        return errors
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: 应为常量 {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} 不在枚举 {schema['enum']}")
    typ = schema.get("type")
    if typ:
        types = typ if isinstance(typ, list) else [typ]
        py_types = {"object": dict, "array": list, "string": str, "integer": int,
                    "number": (int, float), "boolean": bool, "null": type(None)}
        if not any(isinstance(value, py_types.get(t, object)) and
                   not (t in ("integer", "number") and isinstance(value, bool)) for t in types):
            errors.append(f"{path}: 类型应为 {typ}，实际 {type(value).__name__}")
            return errors
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: 长度小于 {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: 不匹配 {schema['pattern']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: 项数少于 {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: 项数多于 {schema['maxItems']}")
        if isinstance(schema.get("items"), dict):
            for i, item in enumerate(value):
                errors += validate_schema(item, schema["items"], f"{path}[{i}]")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: 缺必填 {key}")
        props = schema.get("properties") or {}
        for key, sub in props.items():
            if key in value:
                errors += validate_schema(value[key], sub, f"{path}.{key}")
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(props))
            if extra:
                errors.append(f"{path}: 不允许的额外字段 {extra}")
    return errors


def load_schema(repo, name):
    try:
        return json.load(open(repo / "schemas" / name, encoding="utf-8"))
    except Exception as e:
        return {"__schema_error__": str(e)}


def verify_signature(repo, aid, approval, raw_bytes):
    signers = repo / "approvals" / "allowed_signers"
    if not signers.is_file():
        return None
    sig = repo / "approvals" / f"{aid}.sig"
    if not sig.is_file():
        return False
    try:
        r = subprocess.run(
            ["ssh-keygen", "-Y", "verify", "-f", str(signers),
             "-I", str(approval.get("approver", "")), "-n", "asset-approval",
             "-s", str(sig)], input=raw_bytes, capture_output=True, timeout=15)
        return r.returncode == 0
    except Exception:
        return False


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
    record_schema = load_schema(repo, "asset-record.schema.json")
    approval_schema = load_schema(repo, "approval.schema.json")
    for name, schema in (("asset-record.schema.json", record_schema),
                         ("approval.schema.json", approval_schema)):
        if "__schema_error__" in schema:
            errors.append(f"{name} 读取失败: {schema['__schema_error__']}")

    records = {}
    for p in sorted((repo / "assets").rglob("*.md")):
        fm, body = split(p.read_text(encoding="utf-8"))
        if not fm or fm.get("__parse_error__") or not fm.get("asset_id"):
            errors.append(f"{p.relative_to(repo)}: record 无法解析或缺 asset_id")
            continue
        aid = fm["asset_id"]
        if aid in records:
            errors.append(f"{aid}: record 重复 {records[aid]} / {p}")
        records[aid] = p
        missing = [k for k in REQUIRED if k not in fm]
        if missing:
            errors.append(f"{aid}: record 缺字段 {missing}")
            continue
        schema_errors = validate_schema(fm, record_schema)
        if schema_errors:
            errors.append(f"{aid}: record schema 失败 {schema_errors}")
        for key in ("asset_id", "proposal_id", "title", "source", "owner",
                    "approved_by", "provenance_note"):
            if is_placeholder(fm.get(key)):
                errors.append(f"{aid}: {key} 为空或占位符")
        if fm.get("ai_form") is None:
            if fm.get("mapping_status") not in ("unmapped", "deferred"):
                errors.append(f"{aid}: ai_form 为空时必须声明 mapping_status=unmapped|deferred")
            if is_placeholder(fm.get("mapping_reason")):
                errors.append(f"{aid}: ai_form 未映射时必须给出非空 mapping_reason")
        if fm.get("layer") not in LAYERS:
            errors.append(f"{aid}: layer 非法")
        if fm.get("ai_form") is not None and fm.get("ai_form") not in AI_FORMS:
            errors.append(f"{aid}: ai_form 非法")
        if fm.get("provenance_status") not in PROVENANCE:
            errors.append(f"{aid}: provenance_status 非法")
        if fm.get("status") not in STATUSES:
            errors.append(f"{aid}: status 非法")
        if fm.get("release_channel") not in RELEASE:
            errors.append(f"{aid}: release_channel 非法")
        if not valid_date(fm.get("approved_date")):
            errors.append(f"{aid}: approved_date 不是有效日期")
        if not isinstance(fm.get("domains"), list):
            errors.append(f"{aid}: domains 必须是列表")
        else:
            bad_domains = [d for d in fm["domains"] if d not in DOMAINS]
            if bad_domains:
                errors.append(f"{aid}: domains 非法 {bad_domains}")
            if len(fm["domains"]) > 3:
                errors.append(f"{aid}: domains 超过 3 个")
        if not isinstance(fm.get("secondary_tags"), list):
            errors.append(f"{aid}: secondary_tags 必须是列表")
        pr = projects_of(fm, errors, aid)
        if fm.get("layer") == "项目级" and len(pr) != 1:
            errors.append(f"{aid}: 项目级必须且只能有一个项目")
        if len(pr) > 1 and fm.get("layer") not in ("领域级", "公共级"):
            errors.append(f"{aid}: 多项目资产只能领域级/公共级")
        impl = fm.get("implementation") or {}
        if impl.get("status") and impl["status"] not in LIFECYCLE:
            errors.append(f"{aid}: implementation.status 非法")
        if impl.get("status") == "withdrawn" and impl.get("installed"):
            errors.append(f"{aid}: withdrawn 不得保留 installed")
        if fm.get("provenance_status") == "synthetic":
            if fm.get("release_channel") != "test-only":
                errors.append(f"{aid}: synthetic 必须 release_channel=test-only")
            if impl.get("installed"):
                errors.append(f"{aid}: synthetic 不得有生产安装记录")

        apath = repo / "approvals" / f"{aid}.json"
        if not apath.is_file():
            errors.append(f"{aid}: 缺 approvals/{aid}.json")
        else:
            try:
                raw = apath.read_bytes()
                a = json.loads(raw.decode("utf-8"))
            except Exception as e:
                errors.append(f"{aid}: approval 解析失败 {e}")
                a = {}
            schema_errors = validate_schema(a, approval_schema)
            if schema_errors:
                errors.append(f"{aid}: approval schema 失败 {schema_errors}")
            if not isinstance(a.get("approver"), str) or len(a.get("approver", "").strip()) < 2:
                errors.append(f"{aid}: approval approver 为空或过短")
            if not valid_date(a.get("approved_at")):
                errors.append(f"{aid}: approval approved_at 不是有效日期")
            if a.get("asset_id") != aid:
                errors.append(f"{aid}: approval asset_id 不符")
            if a.get("proposal_id") != fm.get("proposal_id"):
                errors.append(f"{aid}: approval proposal_id 与 record 不一致")
            if a.get("decision") != "approved":
                errors.append(f"{aid}: approval decision 非 approved")
            if a.get("record_path") != records[aid].relative_to(repo).as_posix():
                errors.append(f"{aid}: approval record_path 与 record 实际路径不一致")
            if a.get("record_sha256") != sha(records[aid]):
                errors.append(f"{aid}: record hash 与审批绑定不一致")
            if a.get("content_sha256") != content_hash(fm, body):
                errors.append(f"{aid}: 不可变正文 hash 与审批绑定不一致")
            scope = a.get("scope") or {}
            for k in ("layer", "ai_form", "owner", "provenance_status"):
                if scope.get(k) != fm.get(k):
                    errors.append(f"{aid}: approval scope.{k} 不一致")
            if sorted(scope.get("projects") or []) != sorted(pr):
                errors.append(f"{aid}: approval scope.projects 不一致")
            if sorted(scope.get("domains") or []) != sorted(fm.get("domains") or []):
                errors.append(f"{aid}: approval scope.domains 不一致")
            if scope.get("release_channel") != fm.get("release_channel") or \
                    a.get("release_channel") != fm.get("release_channel"):
                errors.append(f"{aid}: approval release_channel 与 record 不一致")
            signed = verify_signature(repo, aid, a, raw)
            if signed is False:
                errors.append(f"{aid}: approval 签名缺失或无效")

    for e in entries:
        aid = e.get("asset_id")
        if aid not in records:
            errors.append(f"{aid}: registry 条目找不到 record")
            continue
        fm, body = split(records[aid].read_text(encoding="utf-8"))
        pr = projects_of(fm)
        checks = {
            "proposal_id": fm.get("proposal_id"), "title": fm.get("title"),
            "form": fm.get("form"), "layer": fm.get("layer"),
            "ai_form": fm.get("ai_form"), "owner": fm.get("owner"),
            "status": fm.get("status"), "approved_by": fm.get("approved_by"),
            "approved_date": fm.get("approved_date"),
            "provenance_status": fm.get("provenance_status"),
            "provenance_note": fm.get("provenance_note"),
            "release_channel": fm.get("release_channel"),
        }
        for key, expected in checks.items():
            if e.get(key) != expected:
                errors.append(f"{aid}: registry.{key} 与 record 不一致")
        if sorted(e.get("domains") or []) != sorted(fm.get("domains") or []):
            errors.append(f"{aid}: registry.domains 与 record 不一致")
        reg_projects = sorted(projects_of(e))
        if reg_projects != sorted(pr):
            errors.append(f"{aid}: registry.projects 与 record 不一致")
        if e.get("path") != records[aid].relative_to(repo).as_posix():
            errors.append(f"{aid}: registry.path 与 record 实际路径不一致")
        if aid not in index:
            errors.append(f"{aid}: INDEX.md 未登记")
        impl_r = e.get("implementation") or {}
        impl_f = fm.get("implementation") or {}
        for key in ("status", "package", "ai_infra_repo", "installed", "installed_by"):
            if impl_r.get(key) != impl_f.get(key):
                errors.append(f"{aid}: registry.implementation.{key} 与 record 不一致")
        if impl_r.get("status") == "withdrawn" and impl_r.get("installed"):
            errors.append(f"{aid}: registry withdrawn 但仍有 installed")
        if fm.get("provenance_status") == "synthetic" and impl_r.get("installed"):
            errors.append(f"{aid}: synthetic 不得有生产安装记录")
    for aid in records:
        if aid not in ids:
            errors.append(f"{aid}: record 未登记 registry")
    if len(records) != len(entries):
        errors.append(f"record 数 {len(records)} 与 registry 条目数 {len(entries)} 不一致")

    if errors:
        print("❌ 资产库一致性校验失败：")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✅ 资产库一致：{len(records)} 条 record / {len(entries)} 条 registry / approvals / INDEX")
    return 0


if __name__ == "__main__":
    sys.exit(main())
