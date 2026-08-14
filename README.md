# Discord Community Monitor

该仓库通过 GitHub Actions 免费运行四项 Discord 自动化：

- Bug 频道：每 20 分钟检查一次，写入 Lark 表格并按等级通知。
- Suggestions：按配置的整点窗口聚合并推送。
- General + Language Channels：合并进行舆情分析并推送。
- 每日小结：北京时间每天 18:00 汇总并 `@所有人`。

## 安全设计

仓库不保存 Discord Token、Gemini Key、Lark Webhook、飞书应用凭据、频道 ID 或文档 Token。四份运行配置分别保存为 GitHub Actions Secrets：

- `BUG_ENV_B64`
- `SUGGESTIONS_ENV_B64`
- `LANGUAGE_ENV_B64`
- `DAILY_ENV_B64`

Secrets 的内容是对应 `.env` 文件经过 Base64 编码后的文本。工作流仅在临时 runner 中解码，任务结束后 runner 会被销毁。

## 运行方式

四个工作流均支持在 GitHub Actions 页面手动执行。定时执行可能因 GitHub 队列产生几分钟延迟，但统计窗口仍由北京时间整点计算。

Bug 工作流使用 180 分钟重叠查询窗口应对 runner 无本地持久状态的情况；Lark 表格里的 `Source Message ID` 负责去重，不会重复写入同一 Bug。

