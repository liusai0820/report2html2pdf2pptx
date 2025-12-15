#!/usr/bin/env node
/**
 * 使用 Browserless.io 云服务将 HTML 转换为 PDF
 * 无需本地 Chrome，性能更好，适合生产环境
 */

const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

// Browserless.io 配置
const BROWSERLESS_URL = process.env.BROWSERLESS_URL || 'wss://chrome.browserless.io?token=YOUR_TOKEN';

async function convertToPDF(htmlPath, pdfPath) {
  const absoluteHtmlPath = path.resolve(htmlPath);
  const absolutePdfPath = path.resolve(pdfPath);

  if (!fs.existsSync(absoluteHtmlPath)) {
    console.error(`❌ HTML文件不存在: ${absoluteHtmlPath}`);
    process.exit(1);
  }

  console.log('🚀 连接到 Browserless 云服务...');
  
  const browser = await puppeteer.connect({
    browserWSEndpoint: BROWSERLESS_URL,
  });

  try {
    console.log('📄 加载HTML文件...');
    const page = await browser.newPage();
    
    await page.setViewport({ width: 1280, height: 720 });
    
    // 读取 HTML 内容并直接设置
    const htmlContent = fs.readFileSync(absoluteHtmlPath, 'utf-8');
    await page.setContent(htmlContent, { 
      waitUntil: 'networkidle0',
      timeout: 60000
    });
    
    // 等待字体加载
    await page.evaluateHandle('document.fonts.ready');
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    console.log('📝 生成PDF...');
    
    const pdfDir = path.dirname(absolutePdfPath);
    if (!fs.existsSync(pdfDir)) {
      fs.mkdirSync(pdfDir, { recursive: true });
    }
    
    await page.pdf({
      path: absolutePdfPath,
      width: '1280px',
      height: '720px',
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 }
    });
    
    const stats = fs.statSync(absolutePdfPath);
    const fileSizeMB = (stats.size / 1024 / 1024).toFixed(2);
    
    console.log(`✅ PDF已生成: ${absolutePdfPath}`);
    console.log(`📦 文件大小: ${fileSizeMB} MB`);
    
  } catch (error) {
    console.error('❌ 生成PDF失败:', error.message);
    process.exit(1);
  } finally {
    await browser.disconnect();
  }
}

const args = process.argv.slice(2);
if (args.length < 2) {
  console.log('用法: node convert_to_pdf_browserless.js <html文件> <pdf文件>');
  process.exit(1);
}

const [htmlPath, pdfPath] = args;
convertToPDF(htmlPath, pdfPath).catch(error => {
  console.error('❌ 错误:', error);
  process.exit(1);
});
