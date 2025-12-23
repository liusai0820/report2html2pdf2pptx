// API 配置
// 生产环境使用环境变量，开发环境使用本地
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';

export const fetchScenarios = async () => {
    const response = await fetch(`${API_BASE}/scenarios`);
    if (!response.ok) throw new Error('Failed to fetch scenarios');
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

export const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
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
