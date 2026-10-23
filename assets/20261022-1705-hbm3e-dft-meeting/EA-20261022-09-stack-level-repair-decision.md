---
asset_id: EA-20261022-09
proposal_id: 20261022-1705-hbm3e-dft-meeting
title: HBM3E 修复层级决策：选 stack-level
form: 决策记忆
secondary_tags:
- 工程规则
- 知识库
domains:
- DFT
- 设计
project: HBM
layer: 领域级
ai_form: Memory
source: HBM3E DFT debug 复盘会议纪要 2026-10-20
provenance_status: synthetic
provenance_note: 由构造的 HBM3E DFT 会议纪要生成，仅用于验证资产化流程，不代表真实项目结论
owner: DFT 领域 owner
status: approved
approved_by: LiJiaT
approved_date: '2026-10-22'
implementation:
  ai_infra_repo: eng-asset-ai-components
  package: components/hbm3e-stack-level-repair-decision.md
  installed: '2026-10-22'
  installed_by: LiJiaT
  notes: 领域级载体未定义，先落到 D--Project 项目 memory；owner 指定领域级载体后迁移
---
## 内容

**背景**：HBM3E 堆叠 die 的 MBIST 修复覆盖率上不去，团队就修复动作放在哪一层发生争论：是由 controller 统一控制各 die 的修复资源，还是把修复下沉到 stack 内部完成。当时的环境前提是 V0.9 工具链（`bist_collars` 数量受限）、TSV 通道 repair 仅 2 个 spare row、PHY 侧修复粒度 1:4。

**选项**：

- 方案 A，controller-level repair：controller 统一控制堆叠各 die 的修复资源，测试入口单一、控制集中。
- 方案 B，stack-level repair：修复在 stack 内部完成，controller 只发起测试。

**取舍**：最终选方案 B（stack-level）。判断依据三条：

1. **可达性**：PHY 侧 spare row 在 controller level 无法访问。controller-level 方案触达不到这部分修复资源，PHY 侧可修复单元形成覆盖率天花板，方案 A 在结构上就不成立。
2. **协议一致性**：stack-level 与 base die 的测试协议一致，不需要为 repair 额外引入一套跨层控制协议。
3. **既有证据**：此前 HBM3 项目走过 stack-level 这条路，修复覆盖率达到 98%+。

放弃的是 controller-level 的集中控制与单一测试入口；换来的是对 PHY 侧 spare row 的真实可达性，以及与 base die 测试协议的一致性。

**证据**：PHY 侧 spare row 在 controller level 不可访问（结构性限制）；stack-level 路径与 base die 测试协议一致；HBM3 项目 stack-level 实测修复覆盖率 98%+。

**生效条件与复核点**：本决策建立在"PHY 侧 spare row 必须由 stack 自身修复逻辑访问"这一结构前提上。若后续 PHY 修复资源、修复粒度（当前 1:4）或 controller 访问路径发生变化，需重新评估该前提是否仍成立，不得直接沿用本结论。

**日期**：2026-10-20（HBM3E DFT debug 复盘会）。

## 出处与理由

- 来源：2026-10-20 HBM3E DFT debug 复盘会议纪要第 3 条决策及其理由（PHY spare row 不可达、与 base die 测试协议一致、HBM3 项目 98%+ 验证）。
- 为什么值得入库：这是"为什么 repair 放在 stack 侧"的完整来龙去脉，属于只有亲历者才知道的决策上下文。没有它，后来者看到 stack-level 架构只会当成既定事实，遇到控制器侧访问受限时可能反向推翻并重走一轮争论。
- 为什么是领域级：决策证据虽然来自 HBM，但"修复资源在哪一层可访问，就把 repair 放在哪一层"是可迁移到其他堆叠 die 项目的取舍原则；project 记录来源项目 HBM，共享范围按 DFT 领域计。
- 副标签说明：主体是决策记忆，其中"可达性优先于控制集中度"可复用为工程规则（副标签工程规则）；PHY spare row 不可达、base die 协议一致性等机理部分具备知识库性质（副标签知识库）。
