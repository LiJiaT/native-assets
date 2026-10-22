---
name: 资产入库申请
about: 技能 A（工程知识资产化）产出 proposal package 后，向本 repo 提交入库申请
title: "[资产入库] <提案slug> · <日期>"
labels: asset-intake
---

# 资产入库申请

> 由技能 A 生成本申请单内容；提交动作由人执行或经人明确授权的自动化执行。批准与合并权限属于 owner。

## 必填字段

- **资产 ID**：
- **来源提案 ID**：
- **目标层级 / 领域 / 项目**：层级（个人级/项目级/领域级/公共级）· 领域 · 项目（LPDDR6/HBM/无）
- **owner**：
- **变更内容**：（新增/修改哪些 asset record，附 proposal package 路径与 manifest）
- **验收清单**：（- [ ] 项，来自 proposal 质量门）
- **回滚方式**：（revert 此 PR / 删除对应 assets/ 子目录 / INDEX 与 registry 同步回退）

## 附件

- proposal package 路径：
- manifest.json：
- 质量门校验结果（validate exit code）：

## 审批

- [ ] owner 批准（批准后合入 assets/ 并更新 INDEX.md 与 registry.json）
