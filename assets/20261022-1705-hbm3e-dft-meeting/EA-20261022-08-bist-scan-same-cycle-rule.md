---
asset_id: EA-20261022-08
proposal_id: 20261022-1705-hbm3e-dft-meeting
title: bist_en 与 scan_en 禁止同周期拉高
form: 工程规则
secondary_tags:
- 知识库
domains:
- DFT
- 时序
project: HBM
layer: 领域级
ai_form: Rule
source: HBM3E DFT debug 复盘会议纪要 2026-10-20
provenance_status: synthetic
provenance_note: 由构造的 HBM3E DFT 会议纪要生成，仅用于验证资产化流程，不代表真实项目结论
owner: DFT 领域 owner
status: approved
approved_by: LiJiaT
approved_date: '2026-10-22'
implementation:
  ai_infra_repo: eng-asset-ai-components
  package: rules/bist-scan-same-cycle-exclusion.md
  installed: '2026-10-22'
  installed_by: LiJiaT
  notes: ''
---
## 内容

**规则**：在同时包含 MBIST（bist）与 scan 的 DFT 时序约束中，`bist_en` 与 `scan_en` 不得在同一周期同时拉高，二者必须保持周期级互斥。

**适用范围**：所有在 OCC（on-chip clock controller）切换窗口内需要并存 repair/MBIST 时钟与 scan 时钟的 DFT 设计。该规则的来源场景是 HBM 堆叠 die 的 MBIST 修复，但机制不依赖具体项目。

**违反后果**：repair clock 与 scan clock 在 OCC 期间发生冲突，会导致该窗口内 bist 部分失效，表现为 MBIST 结果异常、修复覆盖率上不去。该症状与"修复算法有缺陷"高度相似，会把排查引向错误方向，代价是大量无效的 fault sim。

**检查方式**：在 OCC 使能窗口内检查 `bist_en` / `scan_en` 波形，确认两者不存在同周期高电平重叠；新增或修改 DFT 时序约束时，把该互斥关系作为必检项逐条确认。

**边界**：规则只约束"同周期拉高"，不禁止 bist 与 scan 在时间上分段使用。需要二者交替工作时，切换边界必须由 OCC 时序保证落在不同周期。

## 出处与理由

- 来源：2026-10-20 HBM3E DFT debug 复盘会议纪要第 2 条结论——「HBM 的 DFT 时序约束里 bist_en 与 scan_en 不能同周期拉高」。
- 为什么值得入库：这是带强制语气的时序约束，违反即出事（OCC 期间 bist 失效、修复覆盖率异常），且误诊成本极高。固化为规则后可在约束评审阶段拦截，而不是等覆盖率上不去再回头查。
- 为什么是领域级：冲突机制来自 OCC 结构本身（repair clock 与 scan clock 争用），凡是 MBIST 与 scan 共享 OCC 的设计都会遇到，不随项目变化。project 仅记录来源项目 HBM，共享范围按 DFT 领域计。
- 副标签说明：主标签为工程规则，同时承载"为什么不能同周期"的机理知识（知识库），供规则解释与培训引用。
