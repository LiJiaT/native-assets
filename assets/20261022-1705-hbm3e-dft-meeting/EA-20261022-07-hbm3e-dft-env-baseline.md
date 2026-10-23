---
asset_id: EA-20261022-07
proposal_id: 20261022-1705-hbm3e-dft-meeting
title: HBM3E DFT 环境基线：V0.9 工具链与修复资源
form: 知识库
secondary_tags: []
domains:
- DFT
project: HBM
layer: 项目级
ai_form: Memory
source: HBM3E DFT debug 复盘会议纪要 2026-10-20
owner: HBM 项目负责人
status: approved
approved_by: LiJiaT
approved_date: '2026-10-22'
implementation:
  ai_infra_repo: eng-asset-ai-components
  package: components/hbm3e-dft-env-baseline.md
  installed: '2026-10-22'
  installed_by: LiJiaT
  notes: HBM 项目目录本机不存在，先落到 D--Project 项目 memory；建 HBM 项目后迁移
---
## 内容

HBM3E 项目当前 DFT debug 所依据的环境基线，共三个参数（截至 2026-10-20）：

- **工具链版本：V0.9**。该版本下 `bist_collars` 数量受限——MBIST collar 的可用数量由工具链版本决定，不能按理论最大并发去规划 MBIST 配置或覆盖率目标。
- **TSV 通道修复资源：2 个 spare row**。HBM TSV 通道 repair 只有 2 个 spare row，修复能力上限由 spare row 数量决定。
- **PHY 侧修复粒度：1:4**。修复资源按"1 份修复资源对应 4 个单元"的粒度划分，评估 PHY 侧可修复比例时必须按该粒度折算，不能按单 lane 粒度估算。

使用约束：

1. 任何针对 HBM3E 的 MBIST 覆盖率评估、fault sim 配置、repair 方案讨论，都必须以这三个参数为前提；脱离该基线的结论不可比。
2. 三个参数均绑定当前工具链版本与当前 die 配置。工具链升级、spare row 数量变化或 PHY 修复粒度调整后，本基线需重新核实，旧结论不得直接沿用。

## 出处与理由

- 来源：2026-10-20 HBM3E DFT debug 复盘会议纪要「环境现状」条目（V0.9 工具链、bist_collars 受限、2 个 spare row、PHY 修复粒度 1:4）。
- 为什么值得入库：这三个参数是后续所有覆盖率评估与 repair 方案取舍的隐含前提。不知道资源上限，容易把环境能力不足误判成修复算法缺陷，重复走一遍无效排查。
- 为什么是项目级：参数取值绑定该 HBM3E 项目当前的工具链版本与 die 配置，换项目或换工具链即失效，对 DFT 领域不具备跨项目通用性，因此 project=HBM、layer=项目级。
