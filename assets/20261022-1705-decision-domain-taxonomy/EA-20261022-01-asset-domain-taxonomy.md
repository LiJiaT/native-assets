---
asset_id: EA-20261022-01
proposal_id: 20261022-1705-decision-domain-taxonomy
title: 资产分类体系定为 9 领域平铺 + 2 项目正交
form: 决策记忆
secondary_tags: []
domains: []
project: 无
layer: 公共级
ai_form: Memory
source: 2026-10-22 资产化 skill 领域划分决策记录
provenance_status: source-excerpt
provenance_note: 2026-10-22 资产化体系设计决策的摘要；正文中的 v0.5 为决策时点版本，当前对应《AI 公共规范（v0.7 草案）》revision
  5267 的 1.2 节。原始记录未在仓库留存，暂保持 source-excerpt。
owner: AI 平台团队
status: approved
approved_by: LiJiaT
approved_date: '2026-10-22'
implementation:
  ai_infra_repo: eng-asset-ai-components
  package: components/asset-taxonomy.md
  installed: '2026-10-22'
  installed_by: LiJiaT
  notes: 公共级；以受管区块写入 ~/.claude/CLAUDE.md（全局载入点）
  status: installed
schema_version: 2
release_channel: component-library
approval_ref: approvals/EA-20261022-01.json
---
## 内容

**决策**：工程知识资产化体系的分类元数据采用「9 领域平铺 + 2 固定项目 + 四维正交」的自建结构，不引入外部知识收集项目的细粒度标签体系。

- **背景**：为资产化体系设计领域划分时，最初方案是复用外部知识收集项目（论文库 / 公众号 / GitHub radar 三个项目共享）的统一标签体系——8 个顶层主题 + 72 个子标签，期望收集端与资产治理端共用一套标签。
- **选项**：
  1. 复刻外部统一标签体系：与收集侧天然一致，检索粒度最细。
  2. 自建平铺结构：9 个专业领域平铺（架构、设计、验证、时序、DFT、后仿、Firmware、模拟、后端）；项目固定为 LPDDR6、HBM 两个；领域与项目正交（项目横跨多个领域，不做父子嵌套）；资产四维正交——形态 ⊥ 领域 ⊥ 项目 ⊥ 层级。
- **取舍**：选方案 2。外部体系是「知识收集视角」，不是「资产治理视角」，照其细分没有意义；72 个子标签粒度过细，维护成本高、owner 难以指派。细粒度子标签理论上检索更准，但检索收益不及维护成本；团队自定的平铺结构 owner 好指派、好演进。代价是让出细粒度检索精度，换取治理上的可维护与可演进。
- **证据**：该 9 领域划分已写入《AI 公共规范 v0.5》1.2 节，2026-10-22 由团队负责人直接在文档中改定，属团队级既定结构。
- **日期**：2026-10-22（评审结论、最终决策与规范落定同日完成）。

## 出处与理由

<!-- provenance: 来源: 2026-10-22 资产化 skill 领域划分决策记录（单条汇总，437 字符） -->

这是资产治理体系的顶层分类决策，决定了资产库为何只保留 9 个领域枚举、项目为何固定为 2 个且与领域正交、为何设置形态/领域/项目/层级四维正交。后续任何新增领域、项目或维度的提案都需以此为基线，属于典型决策记忆（Decision History）；当前资产库为空，无语义重复。
