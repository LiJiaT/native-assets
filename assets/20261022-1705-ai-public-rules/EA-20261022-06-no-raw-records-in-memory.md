---
asset_id: EA-20261022-06
proposal_id: 20261022-1705-ai-public-rules
title: 原始记录不得写入长期记忆
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
  ai_infra_repo: native-assets-build
  package: rules/no-raw-records-in-memory.md
  installed: '2026-10-22'
  installed_by: LiJiaT
  notes: ''
  status: installed
schema_version: 2
release_channel: component-library
approval_ref: approvals/EA-20261022-06.json
---
## 内容

**规则**：不得把原始记录写入长期记忆。

**动作与边界**

1. 长期记忆的范围：会被长期保留、并能被后续任务读取的载体，包括 CLAUDE.md、rules 文件、memory 条目与知识资产正文。
2. 原始记录的范围：会议原文与逐字稿、聊天记录、调试日志、命令输出、临时文件内容。
3. 允许写入的形态：只写提炼后的结论（事实、要求、决策及其理由），并注明出处（材料名 + 日期或位置），使结论可回溯到原始记录，而原始记录本身仍留在原载体。
4. 判定边界：先把原始记录粘贴进正文、再补一句结论，同样属于违规；"只摘录一小段"不构成豁免。
5. 当次使用：原始记录可以在当前任务或会话内作为工作输入使用，但不得沉淀为长期记忆。

**完成判定**：长期记忆载体的每一段内容都能回答"这是提炼后的结论吗"，原始记录仅以出处引用（材料名 + 日期/位置）形式出现。

## 出处与理由

来源：AI 公共规范 4.4 第 5 条（团队强制规则，2026-10-22）。原文："不得把原始记录（会议、聊天、调试日志）写入长期记忆。"

入库理由：长期记忆一旦被原始记录污染，会持续占用上下文并在后续任务中反复被误用，且难以清理，属于必须每次写入前强制的约束，故仍按工程规则（而非"仅当前任务有效"的上下文）成案。本资产划清了"长期记忆"与"原始记录"两个范围，并给出"结论 + 出处引用"这一可执行的替代写法；其正文本身是提炼后的规则文本，不含任何会议、聊天或日志原文，不违反本条自身。
