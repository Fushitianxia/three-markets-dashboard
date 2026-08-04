# 🏯 三国演义 · 全球三市数据可视化系统

> **A股 · 港股 · 美股** 三市合一的智能投资决策平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-teal.svg)](https://fastapi.tiangolo.com/)

---

## 📋 目录

- [系统架构](#系统架构)
- [核心功能](#核心功能)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [API 文档](#api-文档)
- [数据源](#数据源)
- [部署指南](#部署指南)
- [配置说明](#配置说明)

---

## 🏗 系统架构

```
┌─────────────────────────────────────────────────────┐
│                   📊 前端展示层                        │
│        Next.js + React + Tailwind + Recharts         │
│     Dashboard │ 行情中心 │ 信号中心 │ 分析报告         │
└──────────────────────┬──────────────────────────────┘
                       │ REST API
┌──────────────────────┴──────────────────────────────┐
│                   🔧 后端引擎层                        │
│             FastAPI + Celery + APScheduler           │
│  ┌──────────┬──────────┬──────────┬───────────┐     │
│  │数据采集器│ 趋势分析 │ 信号工厂 │ 投资引擎  │     │
│  │A/HK/US   │ MA/MACD  │ 龙虎榜   │ 多因子    │     │
│  │三市统一  │ RSI/BOLL │ 北向资金 │ 评分模型  │     │
│  └──────────┴──────────┴──────────┴───────────┘     │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                   💾 数据层                           │
│         PostgreSQL + Redis + SQLite (Dev)           │
│              每日数据池 · 历史追溯                    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                   📡 数据源层                         │
│  A股: mootdx + 腾讯 + 东财 + 同花顺 + iwencai       │
│  港股: yfinance + Alpha Vantage                     │
│  美股: yfinance + Finnhub + SEC EDGAR + FRED        │
│  宏观: FRED + World Bank                            │
└─────────────────────────────────────────────────────┘
```

### 3+1+1 架构

| 层级 | 说明 |
|------|------|
| **3** 个市场模块 | A股 / 港股 / 美股，各自独立采集器 |
| **1** 个核心引擎 | 数据采集 + 趋势分析 + 信号生成 + 量化评分 |
| **1** 个输出层 | 邮件推送 + 交互式仪表盘 + GitHub Pages |

---

## ✨ 核心功能

### 📊 模块一：行情数据中心
- 三市实时行情查询（价格/涨跌幅/PE/PB/市值/换手率）
- 多周期K线数据（日线/周线/月线）
- 主要指数实时监控（上证/恒生/标普500/纳斯达克）
- 跨市场股票搜索

### 📈 模块二：市场趋势分析
- 多周期均线系统（MA5/10/20/60/120）
- MACD 金叉/死叉检测
- RSI 超买/超卖判断
- 布林带突破信号
- KDJ 指标分析
- 支撑位/阻力位计算
- 成交量异常检测

### 🚨 模块三：信号工厂
- **北向资金**：沪股通/深股通实时流向
- **龙虎榜**：每日上榜股票 + 席位分析
- **热门概念**：同花顺概念板块 + 题材归因
- **行业排名**：东财行业涨跌排名
- 技术信号自动生成（7大类信号）

### 🎯 模块四：个股追踪系统
- 自定义追踪股票列表
- 目标买入价/卖出价/止损价设置
- 涨跌幅预警（可配置阈值）
- 量比预警
- 价格触发自动通知
- 追踪仪表盘（趋势+因子+信号一页全览）

### 📐 模块五：量化因子分析
**五大因子维度，25+量化指标：**

| 因子类别 | 核心指标 |
|----------|----------|
| **估值因子** | PE(TTM) / PB / PS / PEG / EV/EBITDA / 5年PE分位 |
| **成长因子** | 营收增速 / 利润增速 / ROE / ROA / 毛利率 / 净利率 |
| **动量因子** | 1/3/6/12月收益 / Alpha / Beta / Sharpe比率 |
| **波动因子** | 20/60日波动率 / 最大回撤 |
| **资金面** | 北向资金 / 机构持仓 / 融资融券 |

### 💡 模块六：投资建议引擎
- **四维评分系统**：技术面(30%) + 基本面(30%) + 情绪面(15%) + 宏观面(25%)
- 自动生成操作建议：买入 → 加仓 → 持有 → 减仓 → 卖出
- 目标价位 + 止损价位计算
- 仓位管理建议
- 投资周期判断（短/中/长）
- 风险因素识别与提示
- 关键催化剂梳理
- 完整分析报告生成

### 🗄 模块七：数据池与可视化
- 每日交易数据自动持久化
- 历史数据追溯查询
- 交互式K线图表（支持MA叠加）
- 热门概念动态排行
- 信号多空比可视化
- 北向资金流向图
- 龙虎榜数据表格

### 📧 模块八：邮件推送服务
- **QQ邮箱 SMTP 集成**
- 每日市场报告自动推送
- 交易信号实时预警
- 追踪股票价格触发通知
- 投资建议定期推送
- 推送时间可配置
- 发送日志追溯

---

## 🛠 技术栈

### 前端
| 技术 | 用途 |
|------|------|
| Next.js 14 | React 框架，App Router，SSG导出 |
| React 18 | UI 组件 |
| Tailwind CSS | 样式系统，暗色模式 |
| Recharts | 数据可视化图表 |
| Lucide React | 图标库 |
| Framer Motion | 动画 |
| Zustand | 状态管理 |
| Sonner | Toast 通知 |

### 后端
| 技术 | 用途 |
|------|------|
| FastAPI | REST API 框架 |
| SQLAlchemy | ORM |
| PostgreSQL | 生产数据库 |
| Redis | 缓存 + Celery 消息队列 |
| Celery | 异步任务队列 |
| APScheduler | 定时任务调度 |
| mootdx | A股TCP行情 |
| yfinance | 全球股票数据 |
| NumPy / SciPy | 量化计算 |
| stockstats | 技术指标 |

### DevOps
| 技术 | 用途 |
|------|------|
| Docker Compose | 容器编排 |
| Nginx | 反向代理 |
| GitHub Actions | CI/CD |
| GitHub Pages | 前端静态部署 |

---

## 🚀 快速开始

### 前置条件

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (可选)

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/three-markets-dashboard.git
cd three-markets-dashboard

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入QQ邮箱授权码和API Keys

# 3. 启动所有服务
docker-compose up -d

# 4. 访问
# 前端: http://localhost:3000
# API文档: http://localhost:8000/docs
```

### 方式二：本地开发

```bash
# 1. 后端
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env  # 编辑配置
uvicorn app.main:app --reload --port 8000

# 2. 前端（新终端）
cd frontend
npm install
npm run dev

# 3. 访问 http://localhost:3000
```

---

## 📁 项目结构

```
three-markets-dashboard/
├── README.md                    # 项目文档
├── docker-compose.yml           # Docker 编排
├── .env.example                 # 环境变量模板
├── .github/workflows/           # CI/CD
│   └── deploy.yml
│
├── backend/                     # Python FastAPI 后端
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # 应用入口
│       ├── config.py            # 配置管理
│       ├── database.py          # 数据库连接
│       ├── models/              # SQLAlchemy 数据模型
│       │   └── market.py        # 12个数据表
│       ├── api/                 # REST API 路由
│       │   ├── routes.py        # 路由聚合
│       │   ├── market.py        # 行情API
│       │   ├── analysis.py      # 分析API
│       │   ├── signals.py       # 信号API
│       │   ├── tracking.py      # 追踪API
│       │   ├── recommendation.py # 投资建议API
│       │   └── email.py         # 邮件API
│       ├── services/            # 业务逻辑
│       │   ├── data_collectors/ # 数据采集器
│       │   │   ├── a_stock.py   # A股采集器 (7层)
│       │   │   ├── hk_stock.py  # 港股采集器
│       │   │   └── us_stock.py  # 美股采集器 (8层)
│       │   ├── analyzers/       # 分析引擎
│       │   │   ├── trend.py     # 趋势分析
│       │   │   ├── signals.py   # 信号工厂
│       │   │   └── quantitative.py # 量化因子
│       │   ├── recommenders/    # 投资引擎
│       │   │   └── engine.py    # 综合评分+决策
│       │   └── email_service.py # 邮件服务
│       └── scheduler/           # 定时任务
│           └── jobs.py          # 4个调度任务
│
├── frontend/                    # Next.js 前端
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   └── src/
│       ├── app/                 # 页面 (App Router)
│       │   ├── layout.tsx       # 根布局
│       │   ├── page.tsx         # 仪表盘首页
│       │   ├── globals.css      # 全局样式
│       │   ├── market/          # 行情中心
│       │   ├── signals/         # 信号中心
│       │   ├── tracking/        # 个股追踪
│       │   ├── analysis/        # 量化分析
│       │   └── settings/        # 系统设置
│       ├── components/          # 组件
│       │   ├── layout/          # Sidebar + Header
│       │   ├── charts/          # 图表组件
│       │   └── dashboard/       # 仪表盘组件
│       └── lib/                 # 工具库
│           ├── api.ts           # API客户端
│           └── utils.ts         # 工具函数
│
├── docker/                      # Docker 配置
│   ├── nginx/nginx.conf
│   └── postgres/init.sql
│
└── data/                        # 数据存储目录
```

---

## 📡 API 文档

启动后端后访问 `http://localhost:8000/docs` 查看完整 Swagger 文档。

### 核心端点速览

```bash
# 行情
GET  /api/v1/market/overview              # 三市概览
GET  /api/v1/market/quote/{market}/{sym}  # 实时行情
GET  /api/v1/market/kline/{market}/{sym}  # K线数据
GET  /api/v1/market/search?q=关键词       # 搜索股票

# 分析
GET  /api/v1/analysis/trend/{market}/{sym}     # 趋势分析
GET  /api/v1/analysis/factors/{market}/{sym}   # 量化因子

# 信号
GET  /api/v1/signals/technical/{market}/{sym}  # 技术信号
GET  /api/v1/signals/north-flow               # 北向资金
GET  /api/v1/signals/dragon-tiger             # 龙虎榜
GET  /api/v1/signals/hot-concepts             # 热门概念

# 追踪
GET    /api/v1/tracking/              # 追踪列表
POST   /api/v1/tracking/              # 添加追踪
DELETE /api/v1/tracking/{id}          # 删除追踪
GET    /api/v1/tracking/{id}/dashboard # 追踪仪表盘

# 投资建议
POST /api/v1/recommendations/generate/{market}/{sym}  # 生成建议
GET  /api/v1/recommendations/daily/{market}           # 每日建议

# 邮件
POST /api/v1/email/config    # 配置邮箱
POST /api/v1/email/test      # 发送测试邮件
```

---

## 📊 数据源

### A股（7层数据架构）
| 层级 | 数据源 | 数据内容 |
|------|--------|----------|
| 行情层 | mootdx + 腾讯 + 百度 | K线/盘口/PE/PB/市值 |
| 研报层 | 东财 + 同花顺 + iwencai | 研报/EPS/评级 |
| 信号层 | 同花顺 + 东财 | 热点/北向/龙虎榜/解禁 |
| 资金面 | 东财 + datacenter | 融资融券/大宗/股东 |
| 新闻层 | 东财 + 财联社 | 个股新闻/快讯 |
| 基础数据 | mootdx + 新浪 | 财务/F10/三表 |
| 公告层 | 巨潮 | 公告全文 |

### 全球市场（8层数据架构）
| 层级 | 数据源 | 数据内容 |
|------|--------|----------|
| 行情层 | yfinance + Alpha Vantage + Finnhub | OHLCV/多周期 |
| 基本面 | yfinance + FMP | 三表/关键指标/DCF |
| 研报层 | yfinance + Finnhub | 分析师/目标价 |
| 信号层 | Finnhub + yfinance | 内幕交易/异常/做空 |
| 资金面 | yfinance + SEC EDGAR | 机构持仓/13F |
| 新闻层 | Finnhub + Benzinga | 新闻/情绪 |
| 公告层 | SEC EDGAR | 10-K/10-Q/8-K |
| 宏观层 | FRED + World Bank | GDP/CPI/利率/汇率 |

---

## 📧 QQ邮箱配置

1. 登录 QQ 邮箱 → 设置 → 账户 → POP3/SMTP服务
2. 开启 SMTP 服务，获取**授权码**
3. 在 `.env` 中配置：
```env
QQ_EMAIL_SENDER=your_qq@qq.com
QQ_EMAIL_AUTH_CODE=你的授权码
```
4. 启动系统后在「系统设置」页面填写邮箱并测试

---

## 🌐 部署指南

### GitHub Pages（前端）

1. 在 GitHub 仓库设置中启用 Pages
2. 选择 `gh-actions` 作为构建源
3. Push 到 `main` 分支，GitHub Actions 自动部署

### 后端部署（VPS/云服务器）

```bash
# 服务器上
git clone <repo>
cd three-markets-dashboard
cp .env.example .env && vim .env  # 填入生产配置
docker-compose -f docker-compose.yml up -d
```

---

## ⚙️ 定时任务

| 任务 | 时间 | 说明 |
|------|------|------|
| 数据采集 | 每个交易日 15:30 | 采集当日三市交易数据 |
| 信号生成 | 每个交易日 15:45 | 为追踪股票生成交易信号 |
| 每日报告 | 每个交易日 16:00 | 推送每日市场报告邮件 |
| 预警检查 | 交易日 9:00-15:30，每30分钟 | 检查追踪股票预警条件 |

---

## 🎨 UI/BI 设计

- **三国演义主题**：中国红 + 帝王金 + 水墨黑
- **暗色模式**：完整支持 Light/Dark 切换
- **响应式布局**：桌面端为主，平板适配
- **可折叠侧边栏**：最大化数据可视区域
- **玻璃态卡片**：现代化毛玻璃效果
- **实时状态指示**：市场连接状态一目了然

---

## 📝 开发路线图

- [x] 三市数据采集器
- [x] 技术指标分析引擎
- [x] 量化因子评分模型
- [x] 投资建议生成引擎
- [x] QQ邮箱推送
- [x] 仪表盘 Dashboard
- [x] 个股追踪系统
- [x] Docker 容器化
- [x] GitHub Actions CI/CD
- [ ] 回测系统
- [ ] 实时WebSocket推送
- [ ] 移动端适配
- [ ] AI 大模型研报解读

---

## ⚠️ 免责声明

本系统由AI辅助生成，所有数据来自公开API，分析结果仅供参考，**不构成任何投资建议**。投资有风险，入市需谨慎。过去的表现不代表未来的收益。

---

## 📄 License

MIT License

---

<p align="center">
  <b>三国演义 · 全球三市数据可视化系统</b><br>
  <sub>Made with ❤️ by AI + Claude Code</sub>
</p>
