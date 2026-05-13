// HomePage.js
function HomePage() {
  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 20 }}>
      <h1>🎯 OfferGenius</h1>
      <p style={{ fontSize: 18, color: '#666' }}>
        AI 驱动的求职辅导平台
      </p>

      <div style={{
        background: '#f0f7ff',
        padding: 20,
        borderRadius: 10,
        marginTop: 30
      }}>
        <h3>✨ 核心功能</h3>
        <ul>
          <li>📄 简历诊断：分析简历与岗位匹配度</li>
          <li>🎙️ 模拟面试：AI 生成定制化面试题</li>
          <li>📊 复盘报告：能力维度分析和改进建议</li>
        </ul>
      </div>

      <div style={{ marginTop: 30 }}>
        <h3>🚀 技术栈</h3>
        <p>React + FastAPI + DeepSeek 大模型</p>
      </div>
    </div>
  );
}

export default HomePage;