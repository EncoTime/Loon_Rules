# Loon_Rules

Loon 代理规则订阅仓库 —— CoffeeOwl 维护，多上游自动聚合。

## 规则列表

| 规则 | 订阅链接 |
|------|----------|
| [bybit](bybit/) | `https://raw.githubusercontent.com/EncoTime/Loon_Rules/main/bybit/bybit.list` |
| [meta](meta/) | `https://raw.githubusercontent.com/EncoTime/Loon_Rules/main/meta/meta.list` |
| [google](google/) | `https://raw.githubusercontent.com/EncoTime/Loon_Rules/main/google/google.list` |

## 工作方式

- 每天北京时间凌晨 5 点（GitHub Actions，`cron 0 21 * * *` UTC）自动运行
- 拉取各上游名单 → 清洗（剔广告/追踪/第三方域）→ 合并去重 → 生成 Loon 格式 `.list`
- 有变化才提交；单个上游失败不影响其余上游
- Loon 中添加远程规则，指向上面的订阅链接，策略组自选