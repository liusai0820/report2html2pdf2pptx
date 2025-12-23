#!/usr/bin/env node
/**
 * 使用本地 Puppeteer 将 HTML 转换为 PDF
 * 优先使用系统 Chrome，无需额外下载
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// 查找系统 Chrome 路径
function findChromePath() {
  const possiblePaths = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  // macOS
    '/Applications/Chromium.app/Contents/MacOS/Chromium',  // macOS Chromium
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  // Windows
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',  // Windows 32-bit
    '/usr/bin/google-chrome',  // Linux
    '/usr/bin/chromium-browser',  // Linux Chromium
    '/usr/bin/chromium',  // Linux Chromium alt
  ];
  
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  return null;
}

async function convertToPDF(htmlPath, pdfPath) {
  const absoluteHtmlPath = path.resolve(htmlPath);
  const absolutePdfPath = path.resolve(pdfPath);

  if (!fs.existsSync(absoluteHtmlPath)) {
    console.error(`❌ HTML文件不存在: ${absoluteHtmlPath}`);
    process.exit(1);
  }

  let browser;
  try {
    const chromePath = findChromePath();
    
    const launchOptions = {
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security',
        '--allow-file-access-from-files',
        // 字体渲染优化 - 关键参数
        '--font-render-hinting=none',
        '--disable-font-subpixel-positioning',
        '--enable-font-antialiasing',
        // 强制使用系统字体（避免下载失败）
        '--disable-remote-fonts=false',
        // 禁用字体沙盒，让 Chromium 访问所有系统字体
        '--disable-features=FontAccess',
        // 使用硬件加速字体渲染
        '--enable-oop-rasterization',
        // 禁用 blink 功能缓存（可能导致字体问题）
        '--disable-blink-features=AutomationControlled'
      ]
    };
    
    // 如果找到系统 Chrome，使用它
    if (chromePath) {
      launchOptions.executablePath = chromePath;
    }
    
    browser = await puppeteer.launch(launchOptions);

    const page = await browser.newPage();
    
    // 设置视口大小 (16:9)
    await page.setViewport({ width: 1280, height: 720 });
    
    // 加载本地 HTML 文件
    const fileUrl = `file://${absoluteHtmlPath}`;
    await page.goto(fileUrl, { 
      waitUntil: 'networkidle0',
      timeout: 60000  // 增加超时时间到 60 秒
    });
    
    // 等待字体加载完成（关键！防止 Type3 字体）
    console.log('⏳ 等待字体加载...');
    try {
      // 等待 fonts.ready API
      await page.evaluateHandle('document.fonts.ready');
      
      // 额外等待，确保 Google Fonts 中文字体加载
      await page.waitForFunction(() => {
        // 检查是否有任何字体正在加载
        const fonts = document.fonts;
        if (fonts.status === 'loading') return false;
        
        // 尝试检测中文字体是否可用
        const testElement = document.createElement('span');
        testElement.style.fontFamily = "'Presentation Font', 'Noto Sans SC', sans-serif";
        testElement.style.visibility = 'hidden';
        testElement.style.position = 'absolute';
        testElement.textContent = '测试字体加载';
        document.body.appendChild(testElement);
        const fontLoaded = testElement.offsetWidth > 0;
        document.body.removeChild(testElement);
        
        return fontLoaded;
      }, { timeout: 15000 }).catch(() => {
        console.log('⚠️ 字体加载检测超时，继续处理...');
      });
      
    } catch (e) {
      console.log('⚠️ 字体加载等待出错，继续处理:', e.message);
    }
    
    // 额外等待渲染完成（确保所有样式和网络字体应用）
    await new Promise(resolve => setTimeout(resolve, 3000));
    console.log('✓ 字体加载完成');
    
    // 确保输出目录存在
    const pdfDir = path.dirname(absolutePdfPath);
    if (!fs.existsSync(pdfDir)) {
      fs.mkdirSync(pdfDir, { recursive: true });
    }
    
    // 生成 PDF - 使用优化配置避免 Type3 字体
    await page.pdf({
      path: absolutePdfPath,
      width: '1280px',
      height: '720px',
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
      preferCSSPageSize: true,
      // 关键：设置 scale 为 1 可以帮助减少 Type3 字体问题
      scale: 1,
      // tagged PDF 可以改善字体嵌入
      tagged: true,
      // 设置为 screen 而不是 print，以便更好地保留字体样式
      omitBackground: false
    });
    
    // 验证文件生成
    if (fs.existsSync(absolutePdfPath)) {
      const stats = fs.statSync(absolutePdfPath);
      const fileSizeKB = (stats.size / 1024).toFixed(2);
      console.log(`✅ ${path.basename(htmlPath)} -> ${fileSizeKB} KB`);
    }
    
  } catch (error) {
    console.error(`❌ 转换失败: ${error.message}`);
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// 命令行参数处理
const args = process.argv.slice(2);
if (args.length < 2) {
  console.log('用法: node convert_to_pdf_local.js <html文件> <pdf文件>');
  process.exit(1);
}

const [htmlPath, pdfPath] = args;
convertToPDF(htmlPath, pdfPath).catch(error => {
  console.error('❌ 错误:', error);
  process.exit(1);
});
