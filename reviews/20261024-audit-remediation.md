# 审计整改记录 · 2026-10-24

- 执行人：AI 平台团队（owner 授权）
- 范围：eng-knowledge-assets / eng-asset-ai-components / ai-native-basic-component
- 依据：`eng-audit-20261023/audit-report.md`（F01–F39）

## 本次变更

1. **审批绑定（F18/F19）**：新增 `approvals/<asset_id>.json` 与 `scripts/validate_registry.py`、CI；9 条既有 owner 批准回溯绑定到当前 record 文件 hash、不可变正文 hash 与 scope。内容变更即失效。
2. **生命周期（F11/F21/F24）**：record/registry 增加 `schema_version`、`release_channel`、`implementation.status`、`withdrawn_at`。EA-07/08/09 为 synthetic，`release_channel=test-only`，`implementation.status=withdrawn`，保留 `previous_installed` 历史。
3. **多项目与未映射（F06/F07）**：schema 支持 `projects[]`；`ai_form: null` 时要求 `mapping_status=unmapped|deferred` 与 `mapping_reason`。
4. **可移植性（F23/K11）**：技能文档改为 `$ENG_ASSETS_REPO` 输入，不再硬编码作者机器路径。
5. **来源版本（F39/D02）**：规则与记忆的 `provenance_note` 更新为 v0.7 revision 5267；规范侧补追踪矩阵。

## 回滚

- 删除 `approvals/` 与 `scripts/`、回退 `registry.json` / records 的本次字段；
- EA-07/08/09 若需恢复，必须先由 owner 核验来源并从 test-only 重新审批；不得直接改回 installed。
