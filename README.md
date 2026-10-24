# 工程知识资产库（eng-knowledge-assets）

技能 A「工程知识资产化」的入库落地仓库。存放 **approved asset record**、资产索引、registry entry 与评审记录。

对应规范：《AI 公共规范》§2.4（资产化落地）（飞书文档 `SlsGd0bKQo6pVNxxxNAcrF1tnIg`）。

## 链路位置

```
原始材料 → 技能A（资产化）→ 本 repo 入库申请 issue/PR → owner 批准 → approved asset record
        → 技能B（资产AI化，见 eng-asset-ai-components）→ 实现申请 → owner 批准 → 合入/分发
```

## 目录结构

```
assets/        # approved asset records（按提案批次一个子目录：<proposal_id>/）
approvals/     # 审批绑定：record 文件 hash + 不可变正文 hash + scope
schemas/       # record / approval JSON Schema 契约
scripts/       # validate_registry.py：records/registry/INDEX/approvals 一致性门禁
INDEX.md       # 资产索引：asset_id | proposal_id | 领域 | 一行摘要（去重依据）
registry.json  # registry entry：机器可读的资产登记表（含生命周期/release_channel）
reviews/       # 评审记录：入库申请的审批结论
.github/workflows/validate.yml            # CI：每次 push/PR 跑一致性门禁
.github/ISSUE_TEMPLATE/asset-intake.md   # 入库申请 issue 模板
```

## 入库流程

1. 技能 A 在本地生成 proposal package（proposal.md + assets/ + manifest.json）并通过质量门校验；
2. 以本 repo 的 [入库申请 issue 模板](.github/ISSUE_TEMPLATE/asset-intake.md) 提交申请，附 proposal package 与 manifest；
3. **GitHub owner 批准后**合入 `assets/`，同时更新 `INDEX.md`、`registry.json` 与 `approvals/<asset_id>.json`，形成 approved asset record；
4. 技能只负责生成申请内容与校验材料；**push / merge / 关闭 issue 由人执行**（或经人明确授权的自动化执行）。

## 来源可信度

approved asset record 的 `provenance_status` 标记内容来源可信度，与 `registry.json` 同名字段一致：

- `verified`：已对照原始来源逐条核验；
- `source-excerpt`：真实来源的节选/摘要，尚未全文核验；
- `synthetic`：构造材料，仅用于流程验证，不代表真实事实。

## 一致性门禁

```bash
python -X utf8 scripts/validate_registry.py --repo .
```

检查 record 必填字段/枚举、asset_id 唯一、registry 与 record 对账、path 存在、INDEX 覆盖、审批绑定（文件 hash + 不可变正文 hash + scope）、生命周期（withdrawn 不得有 installed；synthetic 不得生产安装）。CI 在 push/PR 时自动执行；失败即不得合入。

## 生命周期

record `status`：`approved` → `deprecated` / `superseded` / `withdrawn`。registry/implementation 另记 `pending` / `implemented` / `installed` / `withdrawn` / `superseded`。修正走新提案并标 `supersedes`；旧实现、分发副本与安装登记必须同步处理，不能只删新文件。

`synthetic` 资产必须 `release_channel: test-only`，不得有生产安装记录。EA-07/08/09 已撤出安装点，组件移入 `ai-native-basic-component/samples/synthetic/`。

## 纪律（R3 / R9）

- 技能不得自行关闭 issue、批准 PR 或合并；批准与合并权限只属于 owner。
- 申请单至少包含：资产 ID、来源提案 ID、目标层级/领域/项目、owner、变更内容、验收清单、回滚方式。
- 审批必须绑定当前内容 hash；内容变更后旧批准自动失效，需重新审批。
