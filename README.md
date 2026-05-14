```markdown
# 🎯 OfferGenius - AI 求职辅导平台

AI 驱动的简历诊断 + 模拟面试工具，帮助求职者提升面试通过率。

## ✨ 功能

- **简历诊断**：上传简历，AI 分析岗位匹配度，给出评分和修改建议
- **模拟面试**：根据简历和岗位生成定制化面试题
- **智能点评**：按 STAR 法则评价回答，提供优化框架
- **复盘报告**：生成能力雷达图和 7 天行动计划

## 🛠 技术栈

- 前端：React
- 后端：FastAPI (Python)
- AI：DeepSeek API
- 数据库：SQLite + JSON

## 🚀 快速开始

### 1. 安装依赖

后端：
```bash
pip install -r requirements.txt
```

前端：
```bash
cd frontend
npm install
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key
```

### 3. 运行

后端：
```bash
python api_server.py
```

前端（新开终端）：
```bash
cd frontend
npm start
```

访问 `http://localhost:3000`

## 📁 项目结构

```
code/
├── frontend/          # React 前端
├── engine/            # 业务逻辑
├── ai/                # AI 调用
├── api_server.py      # FastAPI 入口
├── app.py             # Streamlit 版本
└── requirements.txt   # Python 依赖
```

## 📄 说明

- 需要有效的 DeepSeek API Key
- 后端先启动，前端再启动                    
