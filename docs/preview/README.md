# 🌍 Earth Explorer — 多尺度宇宙可视化桌面应用

> Google Earth 风格的 macOS 桌面端 App,集成 NASA GIBS 卫星图层、城市检索,从地球尺度一路**无缝放大到宇宙大尺度结构**(银河系、本星系群、室女座星系团、拉尼亚凯亚超星系团、史隆长城、可观测宇宙全天星系)。

---

## ✨ 9 个视图模式

### 行星尺度

| 视图 | 说明 | 截图 |
|---|---|---|
| 🌍 **地球** | Cesium 3D 球体,6 类 NASA GIBS 卫星图层(VIIRS / Black Marble / MODIS 温度 / IMERG 降水 / AOD 空气质量 / Blue Marble)+ 548 城市光点 + 昼夜分界线 | (App 内) |
| ☀️ **太阳系** | 真实 3D 行星系统(Solar Walk 风格),全部行星 + 时间流速控制 | `../solar-system-view.html` |

### 银河 / 本星系群尺度

| 视图 | 直径 | 截图 |
|---|---|---|
| 🌌 **银河系** | 10万光年 | [`galaxy_diagram.png`](./galaxy_diagram.png) |
| 🌃 **本星系群** | 1000万光年 | [`local_group.png`](./local_group.png) |

### 星系团 / 超星系团尺度

| 视图 | 直径 | 截图 |
|---|---|---|
| 🔭 **室女座星系团** | 600万光年(M87 + 喷流) | [`virgo_cluster.png`](./virgo_cluster.png) |
| ✨ **拉尼亚凯亚超星系团(示意)** | 5.2亿光年(巨引源+长丝) | [`laniakea.png`](./laniakea.png) |
| ✨ **拉尼亚凯亚(5万颗 SIMBAD 真实数据)** | 3亿光年(z<0.08) | [`laniakea_real.png`](./laniakea_real.png) |
| 🧱 **史隆长城** | 13.8亿光年(已知最大结构) | [`sloan_great_wall.png`](./sloan_great_wall.png) |

### 全天尺度

| 视图 | 数据量 | 截图 |
|---|---|---|
| 🌌 **全天主要星系分布** | 49,573 颗 SIMBAD 星系(Mollweide 投影) | [`allsky_galaxies.png`](./allsky_galaxies.png) |

---

## 📊 数据源

| 类别 | 数据 | 来源 |
|---|---|---|
| 卫星图层 | VIIRS / Black Marble / MODIS / IMERG / AOD | [NASA EOSDIS GIBS](https://gibs.earthdata.nasa.gov/) |
| 城市数据 | 548 个主要城市 | GeoNames + 自整理 |
| 国界/省界 | 中国 34 省 + 全球 200+ 国家 | 中国/世界 GeoJSON |
| 太阳系 | 行星 + 卫星 | Three.js 程序化 |
| 银河系 | 10万光年盘 | PIL 程序化生成 |
| 大尺度结构(示意图) | 长丝 / 节点 / 巨引源 | PIL 程序化(`gen_universe.py`) |
| **全天星系(真实)** | **49,573 颗 z<0.08 SIMBAD 星系** | [SIMBAD TAP Service](https://simbad.cds.unistra.fr/simbad/sim-tap) |
| **拉尼亚凯亚(真实)** | **49,990 颗 z<0.08 SIMBAD 星系** | 同上 |

---

## 🚀 运行

```bash
cd earth-explorer
npm install
npm start
```

构建 macOS .app:
```bash
npm run build:mac
# 输出: dist/mac-arm64/Earth Explorer.app
```

---

## 🛠️ 技术栈

- **前端**:HTML5 + CSS3 + JavaScript (ES2020)
- **3D 渲染**:Cesium 1.117 + Three.js 0.185
- **桌面壳**:Electron 33
- **打包**:electron-builder 25(macOS DMG + Windows NSIS)
- **本地服务**:Node.js HTTP Server (127.0.0.1:18765) + CORS 代理
- **图像生成**:Python 3.9 + PIL / ImageDraw(用于宇宙大尺度结构示意图)

---

## 📁 项目结构

```
earth-explorer/
├── main.js                 # Electron 主进程 + HTTP server
├── preload.js              # 安全 IPC 桥
├── index.html              # 主界面(视图模式 + 图层面板 + 城市面板)
├── cesium-renderer.js      # Cesium 主渲染逻辑 (1455 行)
├── solar-system-view.html  # 独立太阳系视图
├── renderer.js             # 旧版 Three.js (备用)
├── gen_universe.py         # 宇宙大尺度结构示意图生成器(4 张)
├── gen_allsky.py           # 全天星系分布图生成器(Mollweide)
├── gen_laniakea_real.py    # 拉尼亚凯亚真实星系图生成器
├── data/                   # 城市 GeoJSON + 宇宙图 PNG
├── cesium/                 # Cesium SDK (Workers + Widgets)
├── textures/               # 地球 + 行星纹理
└── docs/preview/           # 截图档(本目录)
```

---

## 🎯 设计要点

1. **9 尺度无缝切换**:地球 → 太阳系 → 银河 → 本星系群 → 室女团 → 拉尼亚凯亚(示意)→ 拉尼亚凯亚(真实) → 史隆长城 → 全天星系,按 Esc 一键返回
2. **真实科学数据**:全天星系和拉尼亚凯亚视图用 SIMBAD TAP 服务的真实红移测量值,**不是合成数据**
3. **离线可用**:除卫星图层外,所有功能 100% 离线;NASA GIBS 通过 WMTS 实时加载
4. **跨平台打包**:`electron-builder` 一键生成 macOS DMG + Windows NSIS

---

## 📜 License

MIT © 2026 lvcheng

---

> Built with ❤️ by 王梓荣 — 一个自学转型的开发者