import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { AuthProvider } from './contexts/AuthContext.jsx'

// 🔒 生产环境禁用 console 输出，防止敏感信息泄露
if (import.meta.env.PROD) {
  const noop = () => {};
  ['log', 'debug', 'info', 'warn'].forEach(method => {
    console[method] = noop;
  });
  // 保留 console.error 以便调试关键错误
}
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
