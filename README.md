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

四个工作流均支持在 GitHub Actions 页面手动执行。为降低 GitHub 定时任务延迟或漏触发的影响，工作流会在每小时多个非整点分钟冗余唤醒；程序仍通过持久化状态保证 Bug 实际检查间隔不短于 20 分钟、整点报告不重复、每日小结每天只发送一次。下一次成功运行会从上次成功边界继续补齐。

四项状态分别保存在独立的 GitHub 状态分支；分支中只有时间戳，没有 Discord 消息或密钥：

- `state-bug`
- `state-suggestions`
- `state-language`
- `state-daily`

Bug 工作流在变量缺失时使用 7 天紧急回看窗口；Lark 表格里的 `Source Message ID` 负责去重，不会重复写入同一 Bug。
