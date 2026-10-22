---
asset_id: EA-20261022-02
proposal_id: 20261022-1705-ai-public-rules
title: Verilog 文件变更必须同步 filelist
form: 工程规则
secondary_tags: []
domains: []
project: 无
layer: 公共级
ai_form: Rule
source: AI 公共规范 4.4 团队强制规则 2026-10-22
owner: AI 平台团队
status: approved
approved_by: LiJiaT
approved_date: '2026-10-22'
implementation:
---
## 内容

**规则**：模块的 Verilog 文件发生新增或更新时，必须在同一次变更中同步更新该模块的 filelist。

**动作与边界**

1. 触发：本次变更触及模块内任一 Verilog 文件的新增或更新，即触发本规则。
2. 同步：filelist 的更新与代码变更属于同一次变更，不得拆成两次提交，也不得"先提交代码、稍后补 filelist"。
3. 一致：更新后的 filelist 必须与目录中实际存在的 Verilog 文件集合一致——新增的文件必须被登记，已不存在的文件不得继续保留在清单中。
4. 校验：提交前必须通过 hook 对 filelist 与目录一致性的校验；校验不通过即视为变更未完成，须先补齐 filelist 再提交。
5. 不触发：本次变更完全不涉及 Verilog 文件时（例如只改文档或脚本），本规则不适用。

**完成判定**：hook 一致性校验通过，即为本规则的完成标准。

## 出处与理由

来源：AI 公共规范 4.4 第 1 条（团队强制规则，2026-10-22）。原文："新增或更新模块的 Verilog 文件时，必须同步更新 filelist。由 hook 校验 filelist 与目录的一致性。"

入库理由：filelist 与代码不同步会造成编译/仿真漏文件，且这类问题在 review 中很难看出，属于每次改动都要执行的强制约束，适合以 Rule 形态在 AI 协作中强制。原文只有一句原则，本资产补齐了触发条件、同次变更、一致性口径与校验判定，可直接落成 rules markdown。层级为公共级：该约束对所有涉及 Verilog 的项目与领域一致适用，不归属任何单一专业领域。
