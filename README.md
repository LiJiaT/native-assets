# 工程知识资产库（eng-knowledge-assets）

技能 A「工程知识资产化」的入库落地仓库。存放 **approved asset record**、资产索引、registry entry 与评审记录。

对应规范：《AI Native 工程规范》§3.4（飞书文档 `SlsGd0bKQo6pVNxxxNAcrF1tnIg`）。

## 链路位置

```
原始材料 → 技能A（资产化）→ 本 repo 入库申请 issue/PR → owner 批准 → approved asset record
        → 技能B（资产AI化，见 eng-asset-ai-components）→ 实现申请 → owner 批准 → 合入/分发
```

## 目录结构

```
assets/        # approved asset records（按提案批次一个子目录：<proposal_id>/，即 <YYYYMMDD-HHmm>-<slug>/）
INDEX.md       # 资产索引：proposal_id | 领域 | 一行摘要（去重依据）
registry.json  # registry entry：机器可读的资产登记表
reviews/       # 评审记录：入库申请的审批结论
.github/ISSUE_TEMPLATE/asset-intake.md   # 入库申请 issue 模板
```

## 入库流程

1. 技能 A 在本地生成 proposal package（proposal.md + assets/ + manifest.json）并通过质量门校验；
2. 以本 repo 的 [入库申请 issue 模板](.github/ISSUE_TEMPLATE/asset-intake.md) 提交申请，附 proposal package 与 manifest；
3. **GitHub owner 批准后**合入 `assets/`，同时更新 `INDEX.md` 与 `registry.json`，形成 approved asset record；
4. 技能只负责生成申请内容与校验材料；**push / merge / 关闭 issue 由人执行**（或经人明确授权的自动化执行）。

## 纪律（R3 / R9）

- 技能不得自行关闭 issue、批准 PR 或合并；批准与合并权限只属于 owner。
- 申请单至少包含：资产 ID、来源提案 ID、目标层级/领域/项目、owner、变更内容、验收清单、回滚方式。
