import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useState } from 'react';
import axios from 'axios';
import './App.css';

import HomePage from './HomePage';

const API_URL = 'http://localhost:8000/api';

// 简历诊断页面（你已有的，我精简了一下）
function DiagnosePage() {
  const [resumeText, setResumeText] = useState('');
  const [targetJob, setTargetJob] = useState('数据分析师');
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleDiagnose = async () => {
    if (!resumeText.trim()) {
      alert('请填写简历内容');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/diagnose`, {
        resume_text: resumeText,
        target_job: targetJob
      });
      setDiagnosis(response.data);
    } catch (error) {
      alert('诊断失败，请确保后端已启动');
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>📄 简历诊断</h2>
      
      <select value={targetJob} onChange={(e) => setTargetJob(e.target.value)}>
        <option>数据分析师</option>
        <option>产品经理</option>
        <option>后端开发</option>
        <option>前端开发</option>
      </select>

      <textarea
        rows={8}
        value={resumeText}
        onChange={(e) => setResumeText(e.target.value)}
        placeholder="粘贴你的简历内容..."
        style={{ width: '100%', marginTop: 10, padding: 8 }}
      />

      <button onClick={handleDiagnose} disabled={loading}>
        {loading ? '诊断中...' : '开始诊断'}
      </button>

      {diagnosis && (
        <div style={{ marginTop: 30 }}>
          <h3>诊断结果</h3>
          <p>总分：<strong>{diagnosis.total_score}</strong></p>
          <p>关键词得分：{diagnosis.keyword_score}</p>
          <p>结构得分：{diagnosis.structure_score}</p>
          
          <h4>✅ 优势</h4>
          <ul>{diagnosis.strengths?.map((s, i) => <li key={i}>{s}</li>)}</ul>
          
          <h4>⚠️ 待优化</h4>
          <ul>{diagnosis.weaknesses?.map((w, i) => <li key={i}>{w}</li>)}</ul>
        </div>
      )}
    </div>
  );
}

// 面试题生成页面（新增）
function InterviewPage() {
  const [resumeText, setResumeText] = useState('');
  const [targetJob, setTargetJob] = useState('数据分析师');
  const [targetCompany, setTargetCompany] = useState('字节跳动');
  const [difficulty, setDifficulty] = useState('中等');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);

  const generateQuestions = async () => {
    if (!resumeText.trim()) {
      alert('请填写简历内容');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/generate_questions`, {
        resume_text: resumeText,
        target_job: targetJob,
        target_company: targetCompany,
        difficulty: difficulty,
        count: 3
      });
      setQuestions(response.data.questions);
    } catch (error) {
      alert('生成失败，请确保后端已启动');
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>🎙️ 模拟面试</h2>
      
      <div>
        <label>目标岗位：</label>
        <input value={targetJob} onChange={(e) => setTargetJob(e.target.value)} />
      </div>
      
      <div>
        <label>目标公司：</label>
        <input value={targetCompany} onChange={(e) => setTargetCompany(e.target.value)} />
      </div>
      
      <div>
        <label>难度：</label>
        <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
          <option>基础</option><option>中等</option><option>困难</option>
        </select>
      </div>
      
      <div>
        <label>简历内容：</label>
        <textarea rows={6} value={resumeText} onChange={(e) => setResumeText(e.target.value)} />
      </div>
      
      <button onClick={generateQuestions} disabled={loading}>
        {loading ? '生成中...' : '生成面试题'}
      </button>

      {questions.length > 0 && (
        <div>
          <h3>面试题</h3>
          {questions.map((q, i) => (
            <div key={i} style={{ background: '#f5f5f5', padding: 10, margin: 10 }}>
              <strong>第{i+1}题：</strong> {q}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// 主 App 组件（带导航栏）
function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <nav className="nav-bar">
          <Link to="/" className="nav-link">🏠 首页</Link>
          <Link to="/diagnose" className="nav-link">📄 简历诊断</Link>
          <Link to="/interview" className="nav-link">🎙️ 模拟面试</Link>
        </nav>

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/diagnose" element={<DiagnosePage />} />
          <Route path="/interview" element={<InterviewPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;