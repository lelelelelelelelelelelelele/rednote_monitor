# xiaohongshu-mcp 风控风险备忘录

> 维护者: lele | 最后更新: 2026-05-14
>
> 本文档记录 M1 Scraper 依赖的 xiaohongshu-mcp 的风控现状、替代工具调研、以及安全采集策略。所有 partner 在调整采集逻辑前应先阅读本文。

---

## 一、现状：风控已经加强

2026-03-10 小红书正式发布打击 AI 托管账号的公告。随后风控系统明显收紧：

- **只读浏览也会触发警告** —— [xpzouying/xiaohongshu-mcp#668](https://github.com/xpzouying/xiaohongshu-mcp/issues/668) 确认，用户仅浏览不发帖，第一天被警告，第二天封号 3 天
- 风控周期从过去约 14 天缩短，现在更敏感
- Cookie 有效期也在缩短，需更频繁更新

---

## 二、xiaohongshu-mcp 的风控检测维度

| 检测层面 | 具体方法 |
|---------|---------|
| **内容特征** | AI 生成内容的固有特征（高频噪声、统一段落组织） |
| **端侧行为** | 设备绑定多账号、完成普通人无法完成的操作 |
| **网络环境** | IP 地址稳定性、地理位置一致性 |
| **请求频率** | 短时间内连续请求、固定周期的定时任务 |
| **Cookie 异常** | 异地使用、多设备混用、过期 cookie |

---

## 三、替代工具调研结论

2026-05-14 对 3 个候选工具做了调研，**没有一个明显比 xiaohongshu-mcp 更安全**：

| 工具 | 实现方式 | 安全性评估 |
|------|---------|-----------|
| **xhs-mcp (jobsonlook)** | JS 逆向直接请求 HTTP 接口，**无 Playwright** | **可能更差** —— 没有真实浏览器指纹，每次请求签名更像脚本，更容易被识别为爬虫 |
| **XHS-Downloader** | 浏览器自动化 + 可选 MCP 模式 | **同级风险** —— GitHub Issue #321 有制裁案例，官方明确警告自动滚动功能会触发风控 |
| **Agent-Reach / xiaohongshu-cli** | 底层**就是 xiaohongshu-mcp**，套壳 | **完全一样** —— 腾讯云 SkillHub 检测：科恩实验室安全，云鼎实验室标"可疑" |

### 核心判断

xiaohongshu-mcp 使用 **Playwright（真实 Chromium 浏览器）**，请求带的是**真实浏览器指纹**。JS 逆向方案虽然没有浏览器环境，但"请求指纹是脚本"这个特征反而更容易被抓。**在现有选项中，xiaohongshu-mcp 已经是相对安全的选择。**

---

## 四、安全采集策略

### 4.1 底线原则

1. **ManualScraper 永远是兜底** —— 自动采集挂了，手贴进 `data/raw/manual/`
2. **用小号做采集，主号不冒险**
3. **老号权重高，收敛用法比换工具更有效**

### 4.2 具体用法约束

| 项 | 约束 | 说明 |
|---|---|---|
| 每日搜索轮次 | ≤ 1 轮（4 个 keyword） | 够了，我们只需要每天产 4 行 DailyMetric |
| `get_feed_detail` 间隔 | ≥ 5-10 秒随机延迟 | 避免连续请求 |
| 运行时间 | 随机时段，不固定 | 不要用 crontab 的精确时间 |
| Cookie 更新周期 | 每 2-3 周检查一次 | 小红书在缩短有效期 |
| 部署位置 | 本地日常机器 + 日常网络 | **不要**放到云服务器上跑 |
| 养号 | 同账号日常手动刷小红书 | 保持正常的点赞、收藏、浏览行为 |

### 4.3 紧急处理

如果收到警告：

1. **立即停止**所有自动化采集，停 3-5 天让警告冷却
2. 检查是否踩了上面的约束（频率太高？cookie 过期？部署在云上？）
3. 恢复后按约束重新运行
4. 如果封号，切小号，ManualScraper 兜底

---

## 五、相关链接

- [xiaohongshu-mcp GitHub](https://github.com/xpzouying/xiaohongshu-mcp)
- [Issue #668 - 封号（只读也被风控）](https://github.com/xpzouying/xiaohongshu-mcp/issues/668)
- [Issue #680 - 违规问题](https://github.com/xpzouying/xiaohongshu-mcp/issues/680)
- [Issue #674 - 反检测机制建议](https://github.com/xpzouying/xiaohongshu-mcp/issues/674)
- [XHS-Downloader Issue #321 - 账号疑似被制裁](https://github.com/JoeanAmier/XHS-Downloader/issues/321)
