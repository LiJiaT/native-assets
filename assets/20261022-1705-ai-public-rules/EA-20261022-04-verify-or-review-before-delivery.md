---
asset_id: EA-20261022-04
proposal_id: 20261022-1705-ai-public-rules
title: 任何产出交付前必须验证或评审
form: 工程规则
secondary_tags: []
domains: []
project: 无
layer: 公共级
ai_form: Rule
source: AI 公共规范 4.4 团队强制规则 2026-10-22
provenance_status: source-excerpt
provenance_note: 摘自《AI 公共规范（v0.7 草案）》revision 5281 的强制规则清单；2026-10-24 复审后由 owner 将完成判定修正为“执行方自查与独立复核同时满足”，未逐条对照规范全文核验。
owner: AI 平台团队
status: approved
approved_by: LiJiaT
approved_date: '2026-10-24'
implementation:
  ai_infra_repo: native-assets-build
  package: rules/verify-or-review-before-delivery.md
  installed: '2026-10-22'
  installed_by: LiJiaT
  notes: ''
  status: installed
schema_version: 2
release_channel: component-library
revision_note: 2026-10-24 owner 修正 R4：删除“或一份评审结论”的替代路径，改为自查与独立复核两类证据必须同时存在。
approval_ref: approvals/EA-20261022-04.json
---
## 内容

**规则**：任何产出在交付前必须同时完成执行方逐项自查与独立复核；不得以验证或评审中的一项替代另一项，也不得省略。

**动作与边界**

1. 适用范围：AI 或人产出的代码、文档、配置、资产提案与结论，交付前一律适用。
2. 自查：执行方必须先按验收清单逐项自查，并给出可复核的检查结果（检查项 + 结论），不得只写"已检查"。
3. 独立复核：执行方自查不能替代独立复核；交付前须由未参与执行的另一方（人，或与执行上下文独立的 AI 复核者）按同一验收清单复核。
4. 不可验证时：确实无法自动验证的产出，必须转为评审，并在交付说明中写明未能验证的部分与原因；评审记录仍须同时包含执行方自查说明与独立复核意见。
5. 判定边界：自查与复核均未完成的产出，不得标记为完成或已交付。

**完成判定**：同时存在可逐项追溯的执行方自查记录与独立复核记录。只有一份评审结论、只有自查、或只有复核，均不满足。

## 出处与理由

来源：AI 公共规范 4.4 第 3 条（团队强制规则，2026-10-22）。原文："任何产出必须经过验证或评审：执行方自查加独立复核，按验收清单逐项检查。"

入库理由：AI 产出的"看起来对"与"确实对"差距很大，这条规则决定了产出能否被信任，且必须在每次交付时强制触发，属 Rule 场景。本资产把原文的一句话展开为自查、独立复核、不可验证时转评审、未完成不得标记完成四条可判定边界，保持原语义不变。层级为公共级：全团队、全领域的产出均适用。
