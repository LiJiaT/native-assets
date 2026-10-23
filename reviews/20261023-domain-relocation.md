# 领域级资产归位记录 · 2026-10-23

- 执行人：LiJiaT
- 范围：EA-20261022-08（Rule）、EA-20261022-09（Memory）
- 原因：领域级资产按规范 §3.4.3 的 9 领域目录归口

## 变更

| asset_id | 原位置 | 新位置 |
|---|---|---|
| EA-20261022-08 | eng-asset-ai-components/rules/bist-scan-same-cycle-exclusion.md | ai-native-basic-component/rules/dft/bist-scan-same-cycle-exclusion.md |
| EA-20261022-09 | eng-asset-ai-components/components/hbm3e-stack-level-repair-decision.md | ai-native-basic-component/memory/dft/hbm3e-stack-level-repair-decision.md |

- 对应 record 的 `implementation` 字段与 `registry.json` 已同步。
- 旧 repo 的 `build/` 与 `reviews/` 保留为历史，不随迁。

## 运行时安装位置（不变）

- EA-08：`~/.claude/rules/bist-scan-same-cycle-exclusion.md`
- EA-09：`~/.claude/projects/D--Project/memory/hbm3e-stack-level-repair-decision.md`（HBM 项目建立后迁移）

## 回滚

从 `ai-native-basic-component` 删除两份文件，恢复 `eng-asset-ai-components` 对应路径，并回写 record / registry。
