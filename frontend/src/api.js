/**
 * api.js - 后端 API 通信层
 *
 * @input:  VITE_API_URL 环境变量, 后端HTTP端点
 * @output: fetchScenarios, uploadFile, generatePresentationStream, getOutputUrl, getSpeechScript, generateSpeechScript 等API函数
 * @pos:    前端与后端的桥梁，封装所有HTTP请求和SSE流处理
 *
 * ⚠️ 一旦我被更新，务必更新：
 *    1. 我的头部注释
 *    2. /frontend/src/_FOLDER.md
 */

// API 配置
// 生产环境使用环境变量，开发环境使用本地
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';

// 获取完整的 API URL
export const getApiUrl = (endpoint) => {
    const base = API_BASE.endsWith('/api') ? API_BASE.replace('/api', '') : API_BASE;
    return `${base}${endpoint}`;
};

export const fetchScenarios = async () => {
    const response = await fetch(`${API_BASE}/scenarios`);
    if (!response.ok) throw new Error('Failed to fetch scenarios');
    return response.json();
};

// 🔐 检查管理员状态
export const checkAdminStatus = async (email) => {
    if (!email) return { is_admin: false, models: [] };
    const response = await fetch(`${API_BASE}/admin/check?email=${encodeURIComponent(email)}`);
    if (!response.ok) return { is_admin: false, models: [] };
    return response.json();
};

export const fetchFiles = async () => {
    const response = await fetch(`${API_BASE}/files`);
    if (!response.ok) throw new Error('Failed to fetch files');
    return response.json();
};

// 获取历史输出列表
export const fetchOutputs = async () => {
    const response = await fetch(`${API_BASE}/outputs`);
    if (!response.ok) throw new Error('Failed to fetch outputs');
    return response.json();
};

// 加载指定的历史输出
export const loadOutput = async (outputName) => {
    const response = await fetch(`${API_BASE}/outputs/${encodeURIComponent(outputName)}/load`);
    if (!response.ok) throw new Error('Failed to load output');
    return response.json();
};

export const uploadFile = async (file, userEmail = null, userId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (userEmail) formData.append('user_email', userEmail);
    if (userId) formData.append('user_id', userId);
    const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
    });
    if (!response.ok) throw new Error('Upload failed');
    return response.json();
};

// 同步生成 (向后兼容)
export const generatePresentation = async (data) => {
    const response = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Generation failed');
    return response.json();
};

/**
 * SSE 流式生成 (推荐)
 * @param {object} data - 生成参数
 * @param {function} onProgress - 进度回调 (event) => void
 * @returns {Promise<object>} - 最终结果
 */
// SSE 流式生成 (推荐)
export const generatePresentationStream = (data, onProgress) => {
    return new Promise((resolve, reject) => {
        // 使用 fetch + ReadableStream 来处理 POST 请求的 SSE
        // 根据约定，我们总是使用 V2 API
        // 或者如果需要兼容，可以修改此处
        fetch(`${API_BASE}/generate-v2`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...data, engine: 'v2' }),
        })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`HTTP ${response.status}: ${text}`);
                    });
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                function processText(text) {
                    buffer += text;
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || ''; // 保留最后一个不完整的行

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const event = JSON.parse(line.slice(6));
                                onProgress(event);

                                if (event.stage === 'done') {
                                    resolve(event.result);
                                } else if (event.stage === 'error') {
                                    reject(new Error(event.message));
                                }
                            } catch (e) {
                                console.warn('Failed to parse SSE event:', line);
                            }
                        }
                    }
                }

                function read() {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            // 处理剩余的 buffer
                            if (buffer) processText('');
                            return;
                        }
                        processText(decoder.decode(value, { stream: true }));
                        read();
                    }).catch(reject);
                }

                read();
            })
            .catch(reject);
    });
};

// 获取文件下载 URL
export const getOutputUrl = (path) => {
    if (!path) return '';
    // 提取 output/ 之后的路径
    const match = path.match(/output\/(.+)/);
    if (match) {
        // 使用基础 URL（不带 /api）
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';
        const baseUrl = apiUrl.replace('/api', '');
        return `${baseUrl}/output/${match[1]}`;
    }
    return path;
};

// 获取缓存的演讲稿
export const getSpeechScript = async (outputName) => {
    const response = await fetch(`${API_BASE}/speech/${encodeURIComponent(outputName)}`);
    if (!response.ok) {
        throw new Error('获取演讲稿失败');
    }
    return response.json();
};

// 生成演讲稿
export const generateSpeechScript = async (outputName, userId) => {
    const response = await fetch(`${API_BASE}/generate-speech`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ output_name: outputName, user_id: userId }),
    });
    if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || '演讲稿生成失败');
    }
    return response.json();
};
