# Earth Explorer 更新日志

## [Unreleased] — 2026-08-28

### ✨ 新增:11 个宇宙尺度视图模式
- 🌌 **全天主要星系分布**:Mollweide 投影,49,573 颗 SIMBAD 真实星系,交互式浏览器
- ✨ **拉尼亚凯亚(5万颗 SIMBAD 真实数据)**:z<0.08,3 亿光年范围,真实坐标映射
- ✨ **拉尼亚凯亚(示意)**:Tully 2014 长丝 + 巨引源 + 4 节点星系团
- 🌃 **本星系群**:银河系(棒旋) + M31(侧向 + 尘埃带) + M33 + 矮星系
- 🔭 **室女座星系团**:M87 cD 星系 + 相对论性喷流 + 1300+ 星系
- 🧱 **史隆长城**:13.8 亿光年长的宇宙大尺度结构
- 🔭 **哈勃深空场**:1995 年 HDF 模拟,远近星系混合 + 醒目星系
- 🌡️ **宇宙微波背景辐射**:Planck 卫星观测模拟,冷暖区起伏

### 🛠️ 技术改进
- `gen_universe.py`(8 KB):宇宙大尺度结构示意图生成器,4 种尺度
- `gen_allsky.py`(7 KB):全天 Mollweide 投影 + SIMBAD TAP 集成
- `gen_laniakea_real.py`(7 KB):拉尼亚凯亚 5万颗真实数据渲染
- `gen_cosmos.py`(5 KB):哈勃深空场 + CMB 生成器
- `cesium-renderer.js`:扩展 `setViewMode()` 支持全部宇宙模式
- **交互式全天星系浏览器**:点击 5000 颗 SIMBAD 星系查详情 (名称 / 红移 / 距离 / SIMBAD 跳转)

### 📚 数据源
- 接入 [SIMBAD TAP Service](https://simbad.cds.unistra.fr/simbad/sim-tap) 获取真实河外星系列表
- Tully et al. 2014 拉尼亚凯亚定义(直径 5.2 亿光年,10 万星系)
- SDSS 巡天数据用于史隆长城
- Planck 卫星 CMB 观测数据模拟

### 📤 部署
- 仓库创建: https://github.com/wzirong/earth-explorer
- macOS DMG: `dist/Earth Explorer-1.0.0-arm64.dmg`

---

## [1.0.0] — 2026-08-15

### 🎉 首次发布

#### 核心功能
- 🌍 Cesium 3D 地球(1400×900 macOS App,534MB .app)
- 🛰️ 6 类 NASA GIBS 卫星图层:
  - VIIRS 真彩
  - Black Marble 夜灯
  - MODIS 地表温度
  - IMERG 实时降水
  - AOD 空气质量
  - Blue Marble
- 🏙️ 548 城市光点 + 城市详情面板(人口、天气、介绍、外链)
- 🌃 昼夜分界线 + 实时太阳光照 + 国家/省界 + 时区线
- ☀️ 太阳系 3D 视图(Solar Walk 风格)
- 🌌 银河系俯视图 + 银心 / 太阳点击详情
- 🌞 太阳系模式(Solar Walk 风格,8 大行星 + 卫星)

#### 技术栈
- Electron 33 + Cesium 1.117 + Three.js 0.185
- Node.js HTTP Server (127.0.0.1:18765) + CORS 代理
- electron-builder 25(macOS DMG + Windows NSIS)
- JavaScript ES2020

#### 项目大小
- 源文件:1455 行 cesium-renderer.js + 169 行 index.html + 163 行 main.js
- 打包体积:534 MB(macOS arm64)
- node_modules:392 个包

#### 性能优化记录
- ✅ 城市数据从 19MB 压缩到 208KB(`cities_top1500.json` 选 1500 重点城市)
- ✅ 宇宙尺度 overlay img 默认 `display:none`,首次不加载 PNG (减少初始带宽)
- ✅ 内嵌 HTTP server 缓存 Cesium 资源 (避免重复请求)
- ✅ Cesium 卫星图层按需加载 (init 只取 VIIRS)