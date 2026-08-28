const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');

// 内嵌简单 HTTP 服务器
function startLocalServer(port) {
  const server = http.createServer((req, res) => {
    // CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

    const url = req.url;
    const queryIdx = url.indexOf('?');
    const pathOnly = queryIdx >= 0 ? url.slice(0, queryIdx) : url;
    let filePath = pathOnly === '/' ? '/index.html' : pathOnly;
    // 安全：只允许字母、数字、点、下划线、短横线
    filePath = filePath.replace(/\.\./g, '').replace(/[^\w./-]/g, '');
    const fullPath = path.join(__dirname, filePath);

    // 城市数据代理
    if (filePath.startsWith('/api/')) {
      const citycostHost = 'citycost.cn';
      const citycostPath = filePath;
      const options = {
        hostname: citycostHost,
        port: 443,
        path: citycostPath,
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      };
      const proxyReq = require('https').request(options, (proxyRes) => {
        let data = '';
        proxyRes.on('data', chunk => data += chunk);
        proxyRes.on('end', () => {
          res.writeHead(proxyRes.statusCode, {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          });
          res.end(data);
        });
      });
      proxyReq.on('error', () => {
        res.writeHead(502);
        res.end(JSON.stringify({ error: 'upstream error' }));
      });
      proxyReq.end();
      return;
    }

    try {
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
      }
      const ext = path.extname(fullPath).toLowerCase();
      const mimeTypes = {
        '.html': 'text/html;charset=utf-8',
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.ico': 'image/x-icon',
        '.glb': 'model/gltf-binary',
        '.gltf': 'model/gltf+json',
      };
      const mime = mimeTypes[ext] || 'application/octet-stream';
      const content = fs.readFileSync(fullPath);
      res.writeHead(200, { 'Content-Type': mime });
      res.end(content);
    } catch (e) {
      res.writeHead(404);
      res.end('Not found: ' + filePath);
    }
  });

  return new Promise((resolve) => {
    server.listen(port, '127.0.0.1', () => {
      console.log(`Local server running on http://127.0.0.1:${port}`);
      resolve(server);
    });
  });
}

let mainWindow;
let server;

async function createWindow() {
  const port = 18765;
  server = await startLocalServer(port);

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'Earth Explorer - 地球探索器',
    backgroundColor: '#0a0a1a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false
    }
  });

  const viewParam = process.env.EARTH_VIEW ? `?view=${encodeURIComponent(process.env.EARTH_VIEW)}` : '';
  mainWindow.loadURL(`http://127.0.0.1:${port}/${viewParam}`, {
    extraHeaders: 'Cache-Control: no-cache'
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (server) server.close();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (server) server.close();
});

// 打开外部链接
ipcMain.on('open-external', (event, url) => {
  shell.openExternal(url);
});

// 读取本地文件（Cesium 资源）
ipcMain.handle('get-cesium-path', () => {
  // 开发环境
  const localPath = path.join(__dirname, 'node_modules', 'cesium', 'Build', 'Cesium');
  if (fs.existsSync(localPath)) {
    return 'file://' + localPath;
  }
  // 打包后的路径
  const bundledPath = path.join(process.resourcesPath, 'cesium');
  if (fs.existsSync(bundledPath)) {
    return 'file://' + bundledPath;
  }
  return null;
});
