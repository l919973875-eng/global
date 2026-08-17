# 项目状态 · v0.3

## 当前定位

**全球涉华早期信号（China-related Early Signals）**，不再是单纯新闻标题库。

## 已完成

- GitHub Actions + GitHub Pages，无需自建服务器；
- 主巡检每天一次 + 随时手动运行；
- 每新闻源默认最多 5 条候选；
- 311 个原有新闻/智库/官方来源继续保留；
- GDELT 继续作为全球补充；
- direct / indirect / potential 变得更严格；
- 来源 Tier；
- 同事件标题聚类；
- publisher family 独立来源计算；
- WorldMonitor 风格 importance：严重性 / 来源 / 多源 / 新鲜度；
- 本项目 Priority：涉华关联 / 严重性 / 新鲜度 / 多源 / 跨平台；
- Confidence 与 Priority 分离；
- 首页只展示最近24小时约40个重点事件；
- 原始文章、社交苗头、事件、首页数据分开存储；
- X 官方 API 接口；
- X Twikit 实验接口；
- Telegram Telethon 接口；
- RSS/RSSHub 社交桥接；
- 小红书/抖音/微博 MediaCrawler 外部实验工作流；
- 单平台失败不阻断主系统；
- 社交苗头无需媒体报道即可展示。

## 下一步真正值得做的

1. 对中国利益地图继续补项目级实体，而不是继续无限加新闻媒体；
2. 逐步建立高价值 X / Telegram / 小红书 / 抖音账号白名单；
3. 给社交苗头增加图片/视频可定位信息；
4. 统计“哪些苗头后来演变成重大事件”，形成自己的历史预警模型；
5. 如果 GitHub 云 IP 对国内平台风控太强，再把社交采集换到自托管 runner，主网站架构不用变。
