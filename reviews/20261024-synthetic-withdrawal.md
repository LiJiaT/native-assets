# synthetic 资产撤出生产安装点 · 2026-10-24

- 资产：EA-20261022-07、EA-20261022-08、EA-20261022-09
- 原因：审计 IMPL-01/F11/K08；synthetic 构造材料不得作为真实工程基线分发或安装。
- 处置：
  - 最终组件移入 `eng-asset-ai-components/samples/synthetic/` 与 `ai-native-basic-component/samples/synthetic/dft/`；
  - `release_channel=test-only`、`install_target=test-sandbox`；
  - record/registry `implementation.status=withdrawn`，保留 `previous_installed`；
  - 运行时安装点（`~/.claude/rules/`、`~/.claude/projects/D--Project/memory/`）由 owner 撤出。
- 转正条件：重新核对真实来源、补 `verified/source-excerpt` 证据、走技能 A/B 与 owner 审批；不得直接改标签。

## 回滚

从 `samples/synthetic/` 恢复文件并把 `implementation.status` 改回 `installed` **不合法**；必须重新审批。
