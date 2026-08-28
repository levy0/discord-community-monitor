# Discord Community Monitor

该仓库通过 GitHub Actions 免费运行四项 Discord 自动化：

- Bug 频道：每 20 分钟检查一次，写入 Lark 表格并按等级通知。
- Suggestions：北京时间 08:10～22:10 运行，统计边界保持整点；08:00 窗口从前一日 22:00 开始。
- General + Language Channels：同样在北京时间 08:10～22:10 合并分析，自动补齐上次成功边界后的消息。
- 每日小结：北京时间每天 18:10 运行，统计范围固定为昨日 18:00～今日 18:00，并 `@所有人`。

## 安全设计

仓库不保存 Discord Token、Gemini Key、Lark Webhook、飞书应用凭据、频道 ID 或文档 Token。四份运行配置分别保存为 GitHub Actions Secrets：

- `BUG_ENV_B64`
- `SUGGESTIONS_ENV_B64`
- `LANGUAGE_ENV_B64`
- `DAILY_ENV_B64`

Secrets 的内容是对应 `.env` 文件经过 Base64 编码后的文本。工作流仅在临时 runner 中解码，任务结束后 runner 会被销毁。

## 运行方式

四个工作流均支持在 GitHub Actions 页面手动执行。定时触发避开每小时第 0 分钟的高负载时段；即使 GitHub 延迟或漏掉某次触发，下一次成功运行也会从持久化的上次成功边界继续补齐。

四项状态分别保存在 GitHub Actions Variables：

- `BUG_LAST_CHECKED_AT_UTC`
- `SUGGESTIONS_LAST_END_UTC`
- `LANGUAGE_LAST_END_UTC`
- `DAILY_LAST_REPORTED_DATE`

Bug 工作流在变量缺失时使用 7 天紧急回看窗口；Lark 表格里的 `Source Message ID` 负责去重，不会重复写入同一 Bug。
