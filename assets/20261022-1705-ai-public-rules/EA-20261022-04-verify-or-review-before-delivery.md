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
provenance_note: 摘自《AI 公共规范（v0.7 草案）》revision 5267 的强制规则清单（原记录写 v0.5，2026-10-24 对齐当前基线），未逐条对照规范全文核验。
owner: AI 平台团队
status: approved
approved_by: LiJiaT
approved_date: '2026-10-22'
implementation:
  ai_infra_repo: eng-asset-ai-components
  package: rules/verify-or-review-before-delivery.md
  installed: '2026-10-22'
  installed_by: LiJiaT
  notes: ''
  status: installed
schema_version: 2
release_channel: component-library
approval_ref: approvals/EA-20261022-04.json
---
## 内容

**规则**：任何产出在交付前必须经过验证或评审，二者至少完成其一，不得省略。

**动作与边界**

1. 适用范围：AI 或人产出的代码、文档、配置、资产提案与结论，交付前一律适用。
2. 自查：执行方必须先按验收清单逐项自查，并给出可复核的检查结果（检查项 + 结论），不得只写"已检查"。
3. 独立复核：执行方自查不能替代独立复核；交付前须由未参与执行的另一方（人，或与执行上下文独立的 AI 复核者）按同一验收清单复核。
4. 不可验证时：确实无法自动验证的产出，必须转为评审，并在交付说明中写明未能验证的部分与原因。
5. 判定边界：自查与复核均未完成的产出，不得标记为完成或已交付。

**完成判定**：存在可逐项追溯的自查记录与独立复核记录，或存在与交付物对应的评审结论。

## 出处与理由

来源：AI 公共规范 4.4 第 3 条（团队强制规则，2026-10-22）。原文："任何产出必须经过验证或评审：执行方自查加独立复核，按验收清单逐项检查。"

入库理由：AI 产出的"看起来对"与"确实对"差距很大，这条规则决定了产出能否被信任，且必须在每次交付时强制触发，属 Rule 场景。本资产把原文的一句话展开为自查、独立复核、不可验证时转评审、未完成不得标记完成四条可判定边界，保持原语义不变。层级为公共级：全团队、全领域的产出均适用。
