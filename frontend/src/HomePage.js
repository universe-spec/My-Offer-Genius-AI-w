import { Link } from 'react-router-dom';

function HomePage() {
  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: 20 }}>
      
      {/* 标题区域 */}
      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <h1 style={{ fontSize: 48, marginBottom: 10, color: '#1a1a2e' }}>🎯 OfferGenius</h1>
        <p style={{ fontSize: 20, color: '#333' }}>AI 驱动的求职辅导平台</p>
        <p style={{ color: '#555', marginTop: 10 }}>让每一次面试都更有底气</p>
      </div>

      {/* 按钮区域 */}
      <div style={{ display: 'flex', gap: 20, justifyContent: 'center', marginBottom: 50 }}>
        <Link to="/diagnose">
          <button style={{ padding: '12px 30px', fontSize: 18, background: '#0066cc', color: 'white', border: 'none', borderRadius: 30, cursor: 'pointer' }}>
            📄 开始简历诊断
          </button>
        </Link>
        <Link to="/interview">
          <button style={{ padding: '12px 30px', fontSize: 18, background: '#00aa55', color: 'white', border: 'none', borderRadius: 30, cursor: 'pointer' }}>
            🎙️ 开始模拟面试
          </button>
        </Link>
      </div>

      {/* 内容区域 - 没有滚动框，整个页面自然滚动 */}
      
      {/* 核心功能 */}
      <div style={{ background: '#f0f7ff', padding: 25, borderRadius: 16, marginBottom: 25 }}>
        <h2 style={{ marginTop: 0, color: '#1a1a2e' }}>✨ 核心功能</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          <div>
            <h3 style={{ color: '#1a1a2e' }}>📄 简历诊断</h3>
            <p style={{ color: '#333' }}>上传简历 + 选择目标岗位，AI 自动分析匹配度，给出关键词、结构、量化成果等多维度评分，并提供改写建议。</p>
          </div>
          <div>
            <h3 style={{ color: '#1a1a2e' }}>🎙️ 模拟面试</h3>
            <p style={{ color: '#333' }}>根据你的简历和岗位，AI 生成定制化面试题，难度可选基础、中等、困难、压力面。</p>
          </div>
          <div>
            <h3 style={{ color: '#1a1a2e' }}>💬 智能点评</h3>
            <p style={{ color: '#333' }}>你的每个回答都会得到 AI 点评，包括得分、亮点、问题，以及按 STAR 法则优化的答案框架。</p>
          </div>
          <div>
            <h3 style={{ color: '#1a1a2e' }}>📊 复盘报告</h3>
            <p style={{ color: '#333' }}>面试结束后生成雷达图、能力维度得分、高频问题分析，以及 7 天针对性行动计划。</p>
          </div>
        </div>
      </div>

      {/* 适用人群 */}
      <div style={{ background: '#fff4e6', padding: 25, borderRadius: 16, marginBottom: 25 }}>
        <h2 style={{ marginTop: 0, color: '#1a1a2e' }}>👥 适用人群</h2>
        <ul style={{ fontSize: 16, lineHeight: 1.8, color: '#333' }}>
          <li><strong>🎓 应届毕业生</strong> —— 缺乏面试经验，想提前模拟练习</li>
          <li><strong>💼 职场跳槽者</strong> —— 准备转行或冲击大厂，需要针对性训练</li>
          <li><strong>🏫 高校就业办</strong> —— 为学生提供 AI 面试辅导工具</li>
          <li><strong>🚀 创业团队</strong> —— 快速验证 AI+教育赛道 MVP</li>
        </ul>
      </div>

      {/* 产品亮点 */}
      <div style={{ background: '#e6ffe6', padding: 25, borderRadius: 16, marginBottom: 25 }}>
        <h2 style={{ marginTop: 0, color: '#1a1a2e' }}>⭐ 产品亮点</h2>
        <ul style={{ fontSize: 16, lineHeight: 1.8, color: '#333' }}>
          <li><strong>🤖 真 AI 驱动</strong> —— 接入 DeepSeek 大模型，不是规则匹配</li>
          <li><strong>📱 响应式设计</strong> —— 电脑、平板、手机都能用</li>
          <li><strong>🔐 数据本地化</strong> —— 简历和对话记录存在本地，隐私安全</li>
          <li><strong>📥 报告导出</strong> —— 支持下载 Markdown 格式的复盘报告</li>
        </ul>
      </div>

      {/* 技术栈 */}
      <div style={{ background: '#f3e8ff', padding: 25, borderRadius: 16, marginBottom: 25 }}>
        <h2 style={{ marginTop: 0, color: '#1a1a2e' }}>🛠️ 技术栈</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 15 }}>
          <span style={{ background: '#0066cc', color: 'white', padding: '5px 15px', borderRadius: 20 }}>React</span>
          <span style={{ background: '#00aa55', color: 'white', padding: '5px 15px', borderRadius: 20 }}>FastAPI</span>
          <span style={{ background: '#764ba2', color: 'white', padding: '5px 15px', borderRadius: 20 }}>DeepSeek API</span>
          <span style={{ background: '#ff8800', color: 'white', padding: '5px 15px', borderRadius: 20 }}>Streamlit</span>
          <span style={{ background: '#333', color: 'white', padding: '5px 15px', borderRadius: 20 }}>SQLite</span>
        </div>
        <p style={{ marginTop: 15, color: '#333' }}>前后端分离架构，RESTful API 设计，数据驱动 UI。</p>
      </div>

      {/* 如何开始 */}
      <div style={{ background: '#e6f0fa', padding: 25, borderRadius: 16, marginBottom: 25 }}>
        <h2 style={{ marginTop: 0, color: '#1a1a2e' }}>🚀 如何开始</h2>
        <div style={{ display: 'flex', gap: 15, flexWrap: 'wrap' }}>
          <div style={{ background: 'white', padding: 15, borderRadius: 12, flex: 1, minWidth: 150, textAlign: 'center' }}>
            <div style={{ fontSize: 28 }}>1️⃣</div>
            <strong>上传简历</strong>
            <p style={{ fontSize: 14, color: '#555' }}>粘贴或上传 PDF</p>
          </div>
          <div style={{ background: 'white', padding: 15, borderRadius: 12, flex: 1, minWidth: 150, textAlign: 'center' }}>
            <div style={{ fontSize: 28 }}>2️⃣</div>
            <strong>选择岗位</strong>
            <p style={{ fontSize: 14, color: '#555' }}>数据分析/产品/开发</p>
          </div>
          <div style={{ background: 'white', padding: 15, borderRadius: 12, flex: 1, minWidth: 150, textAlign: 'center' }}>
            <div style={{ fontSize: 28 }}>3️⃣</div>
            <strong>开始诊断</strong>
            <p style={{ fontSize: 14, color: '#555' }}>获取匹配度分析</p>
          </div>
          <div style={{ background: 'white', padding: 15, borderRadius: 12, flex: 1, minWidth: 150, textAlign: 'center' }}>
            <div style={{ fontSize: 28 }}>4️⃣</div>
            <strong>模拟面试</strong>
            <p style={{ fontSize: 14, color: '#555' }}>AI 出题 + 智能点评</p>
          </div>
        </div>
      </div>

      {/* 关于项目 */}
      <div style={{ background: '#fafafa', padding: 25, borderRadius: 16, marginBottom: 25 }}>
        <h2 style={{ marginTop: 0, color: '#1a1a2e' }}>💡 关于项目</h2>
        <p style={{ color: '#333' }}>OfferGenius 是一个面向求职者的 AI 面试训练平台，最初作为全栈原型项目开发。它展示了如何用现代 Web 技术快速构建一个可用的 AI 应用。</p>
        <p style={{ marginTop: 10, color: '#333' }}>本项目采用前后端分离架构，前端使用 React，后端使用 FastAPI，AI 能力来自 DeepSeek 大模型。代码已开源，欢迎学习和交流。</p>
      </div>

    </div>
  );
}

export default HomePage;