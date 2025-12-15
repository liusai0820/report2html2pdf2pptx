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
        '--allow-file-access-from-files'
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
      timeout: 30000
    });
    
    // 等待字体加载
    try {
      await page.evaluateHandle('document.fonts.ready');
    } catch (e) {
      // 忽略字体加载错误
    }
    
    // 等待渲染完成
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 确保输出目录存在
    const pdfDir = path.dirname(absolutePdfPath);
    if (!fs.existsSync(pdfDir)) {
      fs.mkdirSync(pdfDir, { recursive: true });
    }
    
    // 生成 PDF
    await page.pdf({
      path: absolutePdfPath,
      width: '1280px',
      height: '720px',
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
      preferCSSPageSize: true
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
