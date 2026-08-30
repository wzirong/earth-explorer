// Earth Explorer - Cesium 版本
// NASA GIBS 卫星图层 + 548 城市光点 + Google Earth 风格 UI

// ── Cesium 初始化 ────────────────────────────────────────
Cesium.Ion.defaultAccessToken = '';  // 不使用 Ion

const viewer = new Cesium.Viewer('cesiumContainer', {
  // 禁用 Cesium 默认的 Bing 影像(避免访问 Ion)
  baseLayer: false,
  // 禁用默认 UI 控件
  animation: false,
  timeline: false,
  geocoder: false,
  homeButton: false,
  sceneModePicker: false,
  baseLayerPicker: false,
  navigationHelpButton: false,
  fullscreenButton: false,
  infoBox: false,
  selectionIndicator: false,
  // 自定义
  shouldAnimate: true,
  requestRenderMode: false,
  contextOptions: { webgl: { alpha: false } }
});

// 关闭底部 credit 容器(避免遮挡)
viewer.cesiumWidget.creditContainer.style.display = 'none';

// 隐藏默认 Cesium logo(可选)
// viewer.cesiumWidget.creditContainer.parentNode.style.display = 'none';

// 暗色大气 / 太空背景
viewer.scene.backgroundColor = Cesium.Color.BLACK;
viewer.scene.skyAtmosphere = new Cesium.SkyAtmosphere();
viewer.scene.globe.enableLighting = true;   // 实时光照 (昼夜明暗, 用真实太阳位置)
// 注意: 不手动设置 scene.light, 让 Cesium 默认用 scene.sun (基于 clock 真实时间的太阳)
viewer.scene.globe.atmosphereLightIntensity = 12;
viewer.scene.globe.showGroundAtmosphere = true;
// galaxy 模式开关
window.__galaxyMode = false;
viewer.scene.globe.baseColor = Cesium.Color.fromCssColorString('#1a3a52');  // fallback 颜色（贴图没加载时）

// ── NASA GIBS 图层 ──────────────────────────────────────
const NASA_GIBS_BASE = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best';

function yesterday() {
  const d = new Date(Date.now() - 86400000);
  return d.toISOString().slice(0, 10);
}

const T_YESTERDAY = yesterday();

const LAYERS = {
  viirs: {
    label: 'VIIRS 真彩色',
    credit: 'NASA EOSDIS GIBS',
    provider: () => new Cesium.UrlTemplateImageryProvider({
      url: `${NASA_GIBS_BASE}/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/${T_YESTERDAY}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg`,
      maximumLevel: 9, tileWidth: 256, tileHeight: 256
    })
  },
  blueMarble: {
    label: 'Blue Marble',
    credit: 'NASA Blue Marble',
    provider: () => new Cesium.UrlTemplateImageryProvider({
      url: `${NASA_GIBS_BASE}/BlueMarble_NextGeneration/default/2004-08-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg`,
      maximumLevel: 8, tileWidth: 256, tileHeight: 256
    })
  },
  blackMarble: {
    label: '夜灯 (Black Marble)',
    credit: 'NASA Black Marble',
    provider: () => new Cesium.UrlTemplateImageryProvider({
      url: `${NASA_GIBS_BASE}/VIIRS_Black_Marble/default/2016-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg`,
      maximumLevel: 8, tileWidth: 256, tileHeight: 256
    })
  },
  tempDay: {
    label: '气温 (白天地表温度)',
    credit: 'NASA MODIS',
    provider: () => new Cesium.UrlTemplateImageryProvider({
      url: `${NASA_GIBS_BASE}/MODIS_Terra_Land_Surface_Temp_Day/default/${T_YESTERDAY}/GoogleMapsCompatible_Level7/{z}/{y}/{x}.jpg`,
      maximumLevel: 7, tileWidth: 256, tileHeight: 256
    })
  },
  precipitation: {
    label: '降水 (IMERG)',
    credit: 'NASA GPM',
    provider: () => new Cesium.UrlTemplateImageryProvider({
      url: `${NASA_GIBS_BASE}/IMERG_Precipitation_Rate/default/${T_YESTERDAY}/GoogleMapsCompatible_Level6/{z}/{y}/{x}.png`,
      maximumLevel: 6, tileWidth: 256, tileHeight: 256
    })
  },
  aod: {
    label: '空气质量 (AOD 气象仪光学深度)',
    credit: 'NASA VIIRS',
    provider: () => new Cesium.UrlTemplateImageryProvider({
      url: `${NASA_GIBS_BASE}/VIIRS_SNPP_AOD_Deep_Blue_Land_Ocean/default/${T_YESTERDAY}/GoogleMapsCompatible_Level6/{z}/{y}/{x}.png`,
      maximumLevel: 6, tileWidth: 256, tileHeight: 256
    })
  },
  none: { label: '无图层（纯色）', provider: () => false }
};

let currentLayer = null;
function setLayer(key) {
  if (currentLayer) viewer.imageryLayers.remove(currentLayer);
  const cfg = LAYERS[key];
  if (!cfg) return;
  const provider = cfg.provider();
  if (provider === false) {
    document.getElementById('img-source').textContent = '无图层';
    currentLayer = null;
    console.log('Layer set to none');
    return;
  }
  currentLayer = viewer.imageryLayers.addImageryProvider(provider);
  document.getElementById('img-source').textContent = `NASA GIBS / ${cfg.label}`;
}

// 默认 Blue Marble
setLayer('blueMarble');

// ── 大洲导航 / 视图跳转 ─────────────────────────────────
const CONTINENT_VIEW = {
  '全部':    { lon: 105, lat: 20,  height: 20000000 },
  '亚洲':    { lon: 105, lat: 35,  height: 8000000 },
  '欧洲':    { lon: 10,  lat: 50,  height: 6000000 },
  '北美洲': { lon: -100, lat: 40, height: 8000000 },
  '南美洲': { lon: -60, lat: -15, height: 8000000 },
  '非洲':    { lon: 20,  lat: 0,   height: 9000000 },
  '大洋洲': { lon: 135, lat: -25, height: 8000000 },
  '中国':    { lon: 105, lat: 35,  height: 5000000 },
  // English aliases
  'all':    { lon: 105, lat: 20,  height: 20000000 },
  'asia':   { lon: 105, lat: 35,  height: 8000000 },
  'europe': { lon: 10,  lat: 50,  height: 6000000 },
  'namerica': { lon: -100, lat: 40, height: 8000000 },
  'samerica': { lon: -60, lat: -15, height: 8000000 },
  'africa': { lon: 20,  lat: 0,   height: 9000000 },
  'oceania': { lon: 135, lat: -25, height: 8000000 },
  'china':  { lon: 105, lat: 35,  height: 5000000 },
};

function flyTo(lat, lon, height = 5000000, duration = 1.5) {
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(lon, lat, height),
    duration: duration
  });
}

function flyContinent(name) {
  const v = CONTINENT_VIEW[name];
  if (v) flyTo(v.lat, v.lon, v.height, 1.5);
}

// ── 加载城市数据 + 添加 Cesium Entity ──────────────────
let allCities = [];
let filteredCities = [];
let activeContinent = '全部';

async function loadCityData() {
  try {
    const [cnRes, globalRes, geoRes] = await Promise.all([
      fetch('/api/cities.json'),
      fetch('/api/global.json'),
      fetch('/cities_geo.json')
    ]);
    const cnData = cnRes.ok ? await cnRes.json() : null;
    const globalData = globalRes.ok ? await globalRes.json() : null;
    const geoData = geoRes.ok ? await geoRes.json() : null;
    const geoMap = (geoData && geoData.cities) || {};
    const cities = [];

    if (cnData && cnData.cities) {
      Object.entries(cnData.cities).forEach(([name, d]) => {
        const g = geoMap[name] || {};
        cities.push({
          name, name_en: g.en_name || name,
          country: '中国', continent: '亚洲',
          lat: g.lat, lon: g.lon,
          salary: d['平均税后月薪'] || d['税后月薪'],
          rent: d['市中心一居室月租'] || d['一居室月租'],
          meal: d['普通餐厅一餐'],
          restaurant: d['普通餐厅一餐'],
          price_per_sqm: d['二手房均价'] || d['新房均价'],
          wiki: `https://en.wikipedia.org/wiki/${encodeURIComponent(g.en_name || name)}`,
        });
      });
    }
    if (globalData && globalData.cities) {
      globalData.cities.forEach(d => {
        const countryCN = d.country_zh || '';
        const continent = COUNTRY_TO_CONTINENT[countryCN] || '其他';
        const g = geoMap[d.city_en] || {};
        cities.push({
          name: d.city_zh || d.city_en || '',
          name_en: d.city_en || '',
          country: countryCN, continent,
          lat: g.lat, lon: g.lon,
          salary: d.rent_1br_cny ? d.rent_1br_cny * 0.8 : null,
          rent: d.rent_1br_cny,
          meal: d.meal_cny,
          restaurant: d.meal_cny ? d.meal_cny * 2 : null,
          price_per_sqm: null,
          wiki: `https://en.wikipedia.org/wiki/${encodeURIComponent(d.city_en || '')}`,
        });
      });
    }
    // 中国其他地级市
    const existingCN = new Set(cities.filter(c => c.country === '中国').map(c => c.name));
    Object.entries(geoMap).forEach(([zh, g]) => {
      if (g.country_zh !== '中国') return;
      if (existingCN.has(zh)) return;
      cities.push({
        name: zh, name_en: g.en_name || zh,
        country: '中国', continent: '亚洲',
        lat: g.lat, lon: g.lon,
        salary: null, rent: null, meal: null, restaurant: null, price_per_sqm: null,
        description: '该城市的成本数据待补充。',
        wiki: `https://en.wikipedia.org/wiki/${encodeURIComponent(g.en_name || zh)}`,
      });
    });
    allCities = cities;
  } catch (e) {
    console.warn('API load failed', e);
  }
  filteredCities = filterCities();
  updateCityCount();
  addCityMarkers();
}

function filterCities() {
  if (activeContinent === '全部') return [...allCities];
  if (activeContinent === '中国') return allCities.filter(c => c.country === '中国');
  return allCities.filter(c => c.continent === activeContinent);
}

function updateCityCount() {
  document.getElementById('city-count').textContent = filteredCities.length + ' 个城市';
}

// ── Entity 添加光点 ────────────────────────────────────
let cityEntities = [];
function clearCityMarkers() {
  cityEntities.forEach(e => viewer.entities.remove(e));
  cityEntities = [];
}

function addCityMarkers() {
  clearCityMarkers();
  // 统一颜色（暖白灯光），按数据完整性区分大小/透明度
  filteredCities.forEach(city => {
    if (city.lat == null || city.lon == null) return;
    const hasData = city.salary != null || city.rent != null || city.meal != null;
    // 有数据:大+实心;无数据:小+半透明
    const pixelSize = hasData ? 8 : 5;
    const alpha = hasData ? 0.95 : 0.55;
    const entity = viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(city.lon, city.lat),
      point: {
        pixelSize,
        color: Cesium.Color.fromCssColorString('#ffeb3b').withAlpha(alpha),
        outlineColor: Cesium.Color.WHITE.withAlpha(hasData ? 0.7 : 0.4),
        outlineWidth: 1,
        scaleByDistance: new Cesium.NearFarScalar(1.5e5, 1.4, 1.5e7, 0.6),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
      },
      properties: { city }
    });
    cityEntities.push(entity);
  });
  setupClickHandler();
}

// ── 点击城市 Entity 弹出面板 ────────────────────────────
let clickHandler;
function setupClickHandler() {
  if (clickHandler) clickHandler.destroy();
  clickHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
  clickHandler.setInputAction((click) => {
    const picked = viewer.scene.pick(click.position);
    if (!picked || !picked.id || !picked.id.properties) return;
    const props = picked.id.properties;
    // 城市
    if (props.city) {
      const city = props.city.getValue();
      flyTo(city.lat, city.lon, 500000, 1.2);
      showCityPanel(city);
      return;
    }
    // 天体 (太阳/月球/行星)
    if (props.bodyType) {
      const type = props.bodyType;
      const data = props.bodyData ? (props.bodyData.getValue ? props.bodyData.getValue() : props.bodyData) : null;
      if (data) showBodyPanel(type, data);
      return;
    }
    // 银河系元素
    if (props.galaxy) {
      const g = props.galaxy.getValue ? props.galaxy.getValue() : props.galaxy;
      showGalaxyPanel(g);
      return;
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
  // hover tooltip
  const tooltip = document.createElement('div');
  tooltip.style.cssText = 'position:fixed;background:rgba(32,33,36,0.95);color:#fff;padding:6px 10px;border-radius:6px;font-size:12px;pointer-events:none;display:none;z-index:200;border:1px solid rgba(255,255,255,0.15);';
  document.body.appendChild(tooltip);
  clickHandler.setInputAction((m) => {
    const picked = viewer.scene.pick(m.endPosition);
    if (picked && picked.id && picked.id.properties) {
      const props = picked.id.properties;
      let label = '';
      if (props.city) {
        const c = props.city.getValue();
        label = `${c.name}${c.country ? ' · ' + c.country : ''}`;
      } else if (props.bodyData) {
        const d = props.bodyData.getValue ? props.bodyData.getValue() : props.bodyData;
        label = d.name || '天体';
      } else if (props.galaxy) {
        const g = props.galaxy.getValue ? props.galaxy.getValue() : props.galaxy;
        label = g.name || '银河系元素';
      }
      if (label) {
        tooltip.style.display = 'block';
        tooltip.textContent = label;
        tooltip.style.left = (m.endPosition.x + 12) + 'px';
        tooltip.style.top = (m.endPosition.y - 8) + 'px';
        viewer.scene.canvas.style.cursor = 'pointer';
        return;
      }
    }
    tooltip.style.display = 'none';
    viewer.scene.canvas.style.cursor = 'default';
  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);
}

// ── 城市面板 ───────────────────────────────────────────
function showCityPanel(city) {
  const isCN = city.country === '中国';
  const fmt = n => n != null ? '¥' + Math.round(n).toLocaleString() : '—';
  const fmtSqm = n => n != null ? '¥' + Math.round(n).toLocaleString() + '/㎡' : '—';

  // 优先使用 citycost API 拉取的实时数据 (中文城市名)
  const costMap = citycostData || {};
  const cn = isCN ? city.name : null;
  let cost = costMap[cn] || costMap[city.name] || costMap[city.name_en] || {};

  // citycost 字段映射到面板字段
  // API 返回的字段可能是长名(全量)或短名(简化版)
  const merged = {
    salary: cost['平均税后月薪'] ?? cost['salary'] ?? city.salary,
    rent: cost['市中心一居室月租'] ?? cost['rent'] ?? city.rent,
    meal: cost['普通餐厅一餐'] ?? cost['meal'] ?? city.meal,
    restaurant: cost['麦当劳套餐'] ?? cost['restaurant'] ?? city.restaurant,
    price_per_sqm: cost['二手房均价(元/㎡,房天下)'] ?? cost['二手房均价'] ?? cost['price_per_sqm'] ?? city.price_per_sqm,
    bus: cost['公交月票'] ?? cost['bus'] ?? null,
    beer_local: cost['国产啤酒(0.5L)'] ?? cost['beer_local'] ?? null,
    coffee: cost['卡布奇诺'] ?? cost['coffee'] ?? null,
    new_home_price: cost['新房均价(元/㎡,房天下)'] ?? cost['新房均价'] ?? cost['new_home_price'] ?? null,
    cpi_idx_new: cost['新建住宅同比指数(统计局)'] ?? cost['cpi_idx_new'] ?? null,
  };

  const hasData = merged.salary != null || merged.rent != null || merged.meal != null || merged.price_per_sqm != null;
  const dataSource = (cn && costMap[cn]) ? 'citycost.cn (实时)' : '本地数据';
  const costSection = hasData ? `
    <div class="panel-section">
      <div class="panel-section-title">💰 生活成本${dataSource ? ` <span style="font-size:11px;color:rgba(255,255,255,0.4);font-weight:400;">· ${dataSource}</span>` : ''}</div>
      <div class="stat-grid">
        <div class="stat-item"><div class="stat-label">平均月薪</div><div class="stat-value">${fmt(merged.salary)}</div></div>
        <div class="stat-item"><div class="stat-label">一居室月租</div><div class="stat-value">${fmt(merged.rent)}</div></div>
        <div class="stat-item"><div class="stat-label">快餐/人均</div><div class="stat-value">${fmt(merged.meal)}</div></div>
        <div class="stat-item"><div class="stat-label">麦当劳套餐</div><div class="stat-value">${fmt(merged.restaurant)}</div></div>
        <div class="stat-item"><div class="stat-label">二手房均价</div><div class="stat-value">${fmtSqm(merged.price_per_sqm)}</div></div>
        <div class="stat-item"><div class="stat-label">新房均价</div><div class="stat-value">${fmtSqm(merged.new_home_price)}</div></div>
        <div class="stat-item"><div class="stat-label">公交月票</div><div class="stat-value">${fmt(merged.bus)}</div></div>
        <div class="stat-item"><div class="stat-label">国产啤酒</div><div class="stat-value">${fmt(merged.beer_local)}</div></div>
        <div class="stat-item"><div class="stat-label">卡布奇诺</div><div class="stat-value">${fmt(merged.coffee)}</div></div>
        ${merged.cpi_idx_new != null ? `<div class="stat-item full"><div class="stat-label">新建住宅同比指数</div><div class="stat-value">${merged.cpi_idx_new}</div></div>` : ''}
      </div>
    </div>` : `
    <div class="panel-section">
      <div class="panel-section-title">💰 生活成本</div>
      <div class="panel-desc" style="color: rgba(255,255,255,0.5);">📊 该城市的成本数据待补充。点击下方维基百科了解更多信息。</div>
    </div>`;
  document.getElementById('panel-content').innerHTML = `
    <div class="panel-header">
      <div class="panel-city-name">${city.name}</div>
      <div class="panel-country">${city.country}${city.name_en && city.name_en !== city.name ? ' · ' + city.name_en : ''}</div>
      <span class="panel-badge">📍 ${hasData ? '有成本数据 · ' + dataSource : '数据待补充'}</span>
    </div>
    ${costSection}
    <div class="panel-section">
      <div class="panel-section-title">🔗 链接</div>
      ${city.wiki ? `<a class="panel-link" href="${city.wiki}" target="_blank" rel="noopener">📚 Wikipedia</a>` : ''}
      <a class="panel-link" href="https://citycost.cn" target="_blank" rel="noopener">💰 citycost.cn 生活成本</a>
    </div>`;
  document.getElementById('city-panel').classList.add('open');
}
document.getElementById('panel-close').onclick = () => document.getElementById('city-panel').classList.remove('open');

// ── 天体面板（太阳/月球/行星）──────────────────────────
function showBodyPanel(type, data) {
  const emoji = type === 'star' ? '☀️' : (type === 'moon' ? '🌙' : '🪐');
  const fields = [];
  if (data.category)  fields.push(['类型', data.category]);
  if (data.radius)    fields.push(['半径', data.radius]);
  if (data.mass)      fields.push(['质量', data.mass]);
  if (data.surfaceTemp) fields.push(['表面温度', data.surfaceTemp]);
  if (data.coreTemp)  fields.push(['核心温度', data.coreTemp]);
  if (data.temp)      fields.push(['平均温度', data.temp]);
  if (data.distanceFromEarth) fields.push(['距地距离', data.distanceFromEarth]);
  if (data.orbitalPeriod) fields.push(['公转周期', data.orbitalPeriod]);
  if (data.age)       fields.push(['年龄', data.age]);
  if (data.remainingLife) fields.push(['剩余寿命', data.remainingLife]);
  if (data.composition) fields.push(['主要成分', data.composition]);
  const wiki = data.en ? `https://zh.wikipedia.org/wiki/${encodeURIComponent(data.en)}` : '';
  document.getElementById('panel-content').innerHTML = `
    <div class="panel-header">
      <div class="panel-city-name">${emoji} ${data.name}${data.isDwarf ? ' (矮行星)' : ''}</div>
      <div class="panel-country">${data.en || ''}</div>
      <span class="panel-badge">🛰️ 太阳系天体</span>
    </div>
    <div class="panel-section">
      <div class="panel-section-title">📊 物理参数</div>
      <div class="stat-grid">
        ${fields.map(([k, v]) => `<div class="stat-item full"><div class="stat-label">${k}</div><div class="stat-value" style="font-size:13px;">${v}</div></div>`).join('')}
      </div>
    </div>
    ${data.fact ? `<div class="panel-section">
      <div class="panel-section-title">💡 冷知识</div>
      <div class="panel-desc" style="color:rgba(255,255,255,0.85);line-height:1.6;">${data.fact}</div>
    </div>` : ''}
    <div class="panel-section">
      <div class="panel-section-title">🔗 链接</div>
      ${wiki ? `<a class="panel-link" href="${wiki}" target="_blank" rel="noopener">📚 维基百科</a>` : ''}
    </div>`;
  document.getElementById('city-panel').classList.add('open');
}

// ── 银河系面板 ─────────────────────────────────────────
function showGalaxyPanel(g) {
  document.getElementById('panel-content').innerHTML = `
    <div class="panel-header">
      <div class="panel-city-name">${g.emoji || '🌌'} ${g.name}</div>
      <div class="panel-country">${g.en || ''}</div>
      <span class="panel-badge">🌌 银河系</span>
    </div>
    <div class="panel-section">
      <div class="panel-section-title">📊 信息</div>
      <div class="stat-grid">
        ${Object.entries(g.fields || {}).map(([k, v]) => `<div class="stat-item full"><div class="stat-label">${k}</div><div class="stat-value" style="font-size:13px;">${v}</div></div>`).join('')}
      </div>
    </div>
    ${g.desc ? `<div class="panel-section">
      <div class="panel-section-title">💡 描述</div>
      <div class="panel-desc" style="color:rgba(255,255,255,0.85);line-height:1.6;">${g.desc}</div>
    </div>` : ''}
    ${g.wiki ? `<div class="panel-section">
      <div class="panel-section-title">🔗 链接</div>
      <a class="panel-link" href="${g.wiki}" target="_blank" rel="noopener">📚 维基百科</a>
    </div>` : ''}`;
  document.getElementById('city-panel').classList.add('open');
}

// ── 状态条：实时显示相机海拔/经纬度 ──────────────────
function updateStatusBar() {
  const cart = viewer.camera.positionCartographic;
  if (cart) {
    document.getElementById('cam-height').textContent = (cart.height / 1000).toFixed(1) + ' km';
    document.getElementById('cam-lon').textContent = Cesium.Math.toDegrees(cart.longitude).toFixed(3) + '°';
    document.getElementById('cam-lat').textContent = Cesium.Math.toDegrees(cart.latitude).toFixed(3) + '°';
  }
}
viewer.scene.postRender.addEventListener(updateStatusBar);

// ── 大洲按钮事件 ───────────────────────────────────────
document.querySelectorAll('.cont-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.cont-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeContinent = btn.dataset.continent;
    filteredCities = filterCities();
    updateCityCount();
    addCityMarkers();
    flyContinent(activeContinent);
  });
});

// ── 图层按钮事件 ───────────────────────────────────────
document.querySelectorAll('.layer-row').forEach(row => {
  row.addEventListener('click', () => {
    document.querySelectorAll('.layer-row').forEach(r => r.classList.remove('active'));
    row.classList.add('active');
    setLayer(row.dataset.layer);
  });
});

// ── 搜索 ──────────────────────────────────────────────
document.getElementById('search-input').addEventListener('input', e => {
  const q = e.target.value.trim().toLowerCase();
  if (!q) return;
  const hit = allCities.find(c =>
    c.name.toLowerCase().includes(q) ||
    (c.name_en && c.name_en.toLowerCase().includes(q)) ||
    c.country.toLowerCase().includes(q)
  );
  if (hit) {
    flyTo(hit.lat, hit.lon, 500000, 1.2);
    showCityPanel(hit);
  }
});

// ── 大洲/国家映射（沿用原版）───────────────────────
const COUNTRY_TO_CONTINENT = {
  "葡萄牙":"欧洲","西班牙":"欧洲","法国":"欧洲","德国":"欧洲","英国":"欧洲",
  "意大利":"欧洲","荷兰":"欧洲","瑞士":"欧洲","奥地利":"欧洲","比利时":"欧洲",
  "希腊":"欧洲","瑞典":"欧洲","挪威":"欧洲","丹麦":"欧洲","芬兰":"欧洲",
  "爱尔兰":"欧洲","捷克":"欧洲","波兰":"欧洲","匈牙利":"欧洲","罗马尼亚":"欧洲",
  "克罗地亚":"欧洲","爱沙尼亚":"欧洲","立陶宛":"欧洲","拉脱维亚":"欧洲","斯洛伐克":"欧洲",
  "斯洛文尼亚":"欧洲","保加利亚":"欧洲","塞尔维亚":"欧洲","波黑":"欧洲","黑山":"欧洲",
  "北马其顿":"欧洲","阿尔巴尼亚":"欧洲","格鲁吉亚":"欧洲","亚美尼亚":"欧洲","摩尔多瓦":"欧洲",
  "白俄罗斯":"欧洲","冰岛":"欧洲","卢森堡":"欧洲","马耳他":"欧洲","塞浦路斯":"欧洲",
  "巴西":"南美洲","阿根廷":"南美洲","哥伦比亚":"南美洲","秘鲁":"南美洲","智利":"南美洲",
  "巴拉圭":"南美洲","乌拉圭":"南美洲","厄瓜多尔":"南美洲","玻利维亚":"南美洲","委内瑞拉":"南美洲",
  "美国":"北美洲","加拿大":"北美洲","墨西哥":"北美洲","哥斯达黎加":"北美洲",
  "巴拿马":"北美洲","多米尼加":"北美洲","古巴":"北美洲",
  "澳大利亚":"大洋洲","新西兰":"大洋洲","斐济":"大洋洲",
  "埃及":"非洲","南非":"非洲","摩洛哥":"非洲","肯尼亚":"非洲","尼日利亚":"非洲",
  "坦桑尼亚":"非洲","加纳":"非洲","埃塞俄比亚":"非洲","塞内加尔":"非洲","卢旺达":"非洲",
  "纳米比亚":"非洲","突尼斯":"非洲","毛里求斯":"非洲","塞舌尔":"非洲",
  "日本":"亚洲","韩国":"亚洲","中国":"亚洲","新加坡":"亚洲",
  "香港":"亚洲","台湾":"亚洲","泰国":"亚洲","越南":"亚洲",
  "印尼":"亚洲","马来西亚":"亚洲","菲律宾":"亚洲","印度":"亚洲",
  "阿联酋":"亚洲","土耳其":"亚洲","卡塔尔":"亚洲","以色列":"亚洲",
  "沙特阿拉伯":"亚洲","科威特":"亚洲","巴林":"亚洲","阿曼":"亚洲",
  "约旦":"亚洲","黎巴嫩":"亚洲","斯里兰卡":"亚洲","尼泊尔":"亚洲",
  "缅甸":"亚洲","老挝":"亚洲","柬埔寨":"亚洲",
};

// ── 昼夜分界线（晨昏线）────────────────────────────────
// 计算太阳直射点（每日更新）
function subsolarPoint() {
  const now = new Date();
  const jd = now.getTime() / 86400000 + 2440587.5;
  const T = (jd - 2451545.0) / 36525;
  // 太阳平黄经
  const L0 = (280.46646 + 36000.76983 * T) % 360;
  const M = (357.52910 + 35999.05030 * T) % 360;
  const C = (1.914602 - 0.004817 * T) * Math.sin(M * Math.PI / 180)
          + (0.019993 - 0.000101 * T) * Math.sin(2 * M * Math.PI / 180);
  const lambda = (L0 + C) % 360;
  // 太阳赤纬
  const eps = 23.439291 - 0.0130042 * T;  // 近似黄赤交角
  const delta = Math.asin(Math.sin(eps * Math.PI / 180) * Math.sin(lambda * Math.PI / 180)) * 180 / Math.PI;
  // 太阳时角（格林威治子午线正午为0）
  const gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0)) % 360;
  const subsolarLon = (gmst - (L0 + C - 180)) % 360 - 180;
  return { lat: delta, lon: subsolarLon };
}

// 画晨昏线（解析公式 + 球面插值，避免折线伪影）
let terminatorEntity = null;
function updateTerminator(visible) {
  if (terminatorEntity) { viewer.entities.remove(terminatorEntity); terminatorEntity = null; }
  if (!visible) return;
  const sp = subsolarPoint();
  const decRad = sp.lat * Math.PI / 180;  // 太阳赤纬（弧度）
  // 晨昏线解析公式：tan(φ) = -cos(λ) / tan(δ)
  // λ 是与直射点的经度差，φ 是纬度
  const pts = [];
  const N = 720;  // 720 个点足够平滑
  const R = 6378137;  // 地球半径
  // 先算出 721 个解析点 (lon, lat)
  const cartesians = [];
  for (let i = 0; i <= N; i++) {
    // 在直射点两侧各扫 180°
    const offset = (i / N) * 360 - 180;  // -180° → +180°
    const lon = sp.lon + offset;
    // tan(φ) = -cos(offset°) / tan(δ)
    let lat;
    if (Math.abs(decRad) < 1e-6) {
      // 赤度 = 0：春分秋分，晨昏线沿赤道，东西经都是 0°
      lat = 0;
    } else {
      const phi = Math.atan(-Math.cos(offset * Math.PI / 180) / Math.tan(decRad));
      lat = phi * 180 / Math.PI;
    }
    cartesians.push(Cesium.Cartesian3.fromDegrees(lon, lat));
  }
  // 球面线性插值（slerp）加强平滑，避免拐角伪影
  // 顺序连接，但中间用 normalize 保证起点位于 R 半径
  for (let i = 0; i < cartesians.length; i++) {
    cartesians[i] = Cesium.Cartesian3.normalize(cartesians[i], new Cesium.Cartesian3());
    cartesians[i] = Cesium.Cartesian3.multiplyByScalar(cartesians[i], R, cartesians[i]);
  }
  terminatorEntity = viewer.entities.add({
    polyline: {
      positions: cartesians,
      width: 2,
      material: new Cesium.PolylineGlowMaterialProperty({
        glowPower: 0.3,
        color: Cesium.Color.fromCssColorString('#2196f3').withAlpha(0.7)
      }),
      clampToGround: false,
      arcType: Cesium.ArcType.GEODESIC  // 球面插值
    }
  });
}

// ── 太阳系（太阳 + 月球 + 八大行星）───────────────────────
// 所有距离/大小按对数缩放，方便在同一视场下看清。
// 实际尺度（1 AU = 1.496e11 m），地球半径 6.378e6 m。
// 月球距离 384400 km = 60 R⊕，太阳距离 1.496e8 km = 23455 R⊕
// 下面都用象征性坐标（单位: 地球半径），让 8 颗行星在球面上都能看见。
const SOLAR_SYSTEM_SCALE = 6.378e6; // 米 → 地球半径 1
// 太阳系整体偏移到远离地球的位置 (避免与地球场景重叠)
// 放在 Z 轴 8e8 m (80万km) 高空, 相机飞过去看
const SOLAR_ORIGIN = new Cesium.Cartesian3(0, 0, 8e8);
const SOLAR_SYSTEM = [
  // {name, color, radiusR, distanceR, orbitalPeriodDays, color: 色温}
  { name: '水星', en: 'Mercury', radiusR: 0.38,  distanceR: 100,  period: 88,   color: '#a3a3a3' },
  { name: '金星', en: 'Venus',   radiusR: 0.95,  distanceR: 130,  period: 225,  color: '#e6c485' },
  { name: '地球', en: 'Earth',   radiusR: 1.0,   distanceR: 0,    period: 365,  color: '#4f8fd1', skip: true },  // 跳过自身
  { name: '火星', en: 'Mars',    radiusR: 0.53,  distanceR: 180,  period: 687,  color: '#c1502e' },
  { name: '木星', en: 'Jupiter', radiusR: 11.0,  distanceR: 350,  period: 4333, color: '#c7a17a' },
  { name: '土星', en: 'Saturn',  radiusR: 9.2,   distanceR: 550,  period: 10759,color: '#e0c896' },
  { name: '天王星', en: 'Uranus', radiusR: 4.0,  distanceR: 750,  period: 30687,color: '#a8d5e2' },
  { name: '海王星', en: 'Neptune',radiusR: 3.9,  distanceR: 1000, period: 60190,color: '#3f54ba' },
  { name: '冥王星', en: 'Pluto', radiusR: 0.18, distanceR: 1300, period: 90560, color: '#b8a89c', dwarf: true },
];

// J2000 (2000-01-01 12:00 UTC) 起算的参考平黄道轨道元素（近似，仅用于可视化）
// 来源：NASA 行星实况手册（简化版）
const PLANET_ELEMENTS = {
  Mercury: { a: 0.387, e: 0.205, i: 7.0,  L: 252.25, longPeri: 77.46, longNode: 48.33, period: 87.97 },
  Venus:   { a: 0.723, e: 0.007, i: 3.4,  L: 181.73, longPeri: 131.53,longNode: 76.68, period: 224.7 },
  Earth:   { a: 1.000, e: 0.017, i: 0.0,  L: 100.47, longPeri: 102.95,longNode: 0.0,   period: 365.26 },
  Mars:    { a: 1.524, e: 0.093, i: 1.85, L: -4.6,   longPeri: -23.92,longNode: 49.56, period: 687.0 },
  Jupiter: { a: 5.203, e: 0.048, i: 1.3,  L: 34.4,   longPeri: 14.73, longNode: 100.29,period: 4332.6 },
  Saturn:  { a: 9.537, e: 0.054, i: 2.49, L: 49.94,  longPeri: 92.6,  longNode: 113.64,period: 10759 },
  Uranus:  { a: 19.19, e: 0.047, i: 0.77, L: 313.23, longPeri: 170.96,longNode: 73.96, period: 30688 },
  Neptune: { a: 30.07, e: 0.009, i: 1.77, L: -55.12, longPeri: 44.97, longNode: 131.79,period: 60182 },
};

// 天体信息字典 (Solar Walk 风格面板)
function getPlanetInfo(p) {
  const data = {
    Mercury: { category: '类地行星', radius: '2,439 km (0.383 × 地球)', mass: '0.055 × 地球', temp: '-173°C ~ 427°C', fact: '太阳系最小行星，昼夜温差极大。' },
    Venus:   { category: '类地行星', radius: '6,051 km (0.949 × 地球)', mass: '0.815 × 地球', temp: '462°C (平均)', fact: '最热的行星。浓厚二氧化碳大气，表面压强是地球的92倍。' },
    Earth:   { category: '类地行星', radius: '6,371 km', mass: '5.972 × 10²⁴ kg', temp: '15°C (平均)', fact: '我们居住的星球。目前已知唯一存在生命的行星。' },
    Mars:    { category: '类地行星', radius: '3,389 km (0.532 × 地球)', mass: '0.107 × 地球', temp: '-87°C ~ -5°C', fact: '红色星球。有太阳系最大火山奥林匹斯山。' },
    Jupiter: { category: '气态巨行星', radius: '69,911 km (10.97 × 地球)', mass: '317.8 × 地球', temp: '-145°C (云顶)', fact: '太阳系最大行星。大红斑是已持续350+年的风暴。' },
    Saturn:  { category: '气态巨行星', radius: '58,232 km (9.14 × 地球)', mass: '95.16 × 地球', temp: '-178°C', fact: '以壮观的环系闻名。密度低于水。' },
    Uranus:  { category: '冰巨行星', radius: '25,362 km (3.98 × 地球)', mass: '14.54 × 地球', temp: '-224°C', fact: '躺着转的行星，自转轴几乎平行于公转面。' },
    Neptune: { category: '冰巨行星', radius: '24,622 km (3.86 × 地球)', mass: '17.15 × 地球', temp: '-218°C', fact: '太阳系最远的行星。风速可达 2,100 km/h。' },
    Pluto:   { category: '矮行星', radius: '1,188 km (0.187 × 地球)', mass: '0.0022 × 地球', temp: '-229°C', fact: '2006 年被 IAU 降级为矮行星。柯伊伯带天体。' },
  };
  const d = data[p.en] || {};
  return {
    name: p.name || p.en, en: p.en,
    category: d.category,
    radius: d.radius,
    mass: d.mass,
    temp: d.temp,
    isDwarf: p.dwarf || false,
    fact: d.fact
  };
}

// 计算行星到地球的当前方向（赤道坐标系 → 经纬度）
// 返回 {lon, lat, distanceR}，lon/lat 为地球看到的角度
function planetPosition(name, date) {
  const el = PLANET_ELEMENTS[name];
  if (!el) return null;
  // J2000 起算天数
  const jd = date.getTime() / 86400000 - 10957.5;  // 2000-01-01
  // 行星平黄经
  const M = ((el.L + 360 * jd / el.period) % 360) * Math.PI / 180;
  // 求解开普勒方程 M = E - e*sin(E)，牛顿迭代 5 次
  let E = M;
  for (let k = 0; k < 5; k++) E = E - (E - el.e * Math.sin(E) - M) / (1 - el.e * Math.cos(E));
  // 真黄经
  const xv = el.a * (Math.cos(E) - el.e);
  const yv = el.a * Math.sqrt(1 - el.e * el.e) * Math.sin(E);
  const v = Math.atan2(yv, xv);  // 真近点角
  // 日心黄道坐标（AU）
  const xh = el.a * (Math.cos(E) - el.e);
  const yh = el.a * Math.sqrt(1 - el.e * el.e) * Math.sin(E);
  // 偏心黄经
  const lonecl = v + el.longPeri * Math.PI / 180;
  const incl  = el.i * Math.PI / 180;
  const longNode = el.longNode * Math.PI / 180;
  // 转赤道坐标（黄赤交角 ε ≈ 23.44°）
  const eps = 23.44 * Math.PI / 180;
  const xeq = xh * (Math.cos(longNode) * Math.cos(lonecl) - Math.sin(longNode) * Math.sin(lonecl) * Math.cos(eps))
            - yh * (Math.sin(longNode) * Math.cos(lonecl) + Math.cos(longNode) * Math.sin(lonecl) * Math.cos(eps));
  const yeq = xh * (Math.cos(longNode) * Math.sin(lonecl) + Math.sin(longNode) * Math.cos(lonecl) * Math.cos(eps))
            + yh * (-Math.sin(longNode) * Math.sin(lonecl) + Math.cos(longNode) * Math.cos(lonecl) * Math.cos(eps));
  const zeq = xh * (Math.sin(longNode) * Math.sin(eps)) + yh * (Math.cos(longNode) * Math.sin(eps));
  // 转换为象征性坐标
  const distAU = Math.sqrt(xeq * xeq + yeq * yeq + zeq * zeq);
  // lon: 从地球看行星的赤经方向（赤道平面内投影）
  const lon = (Math.atan2(yeq, xeq) * 180 / Math.PI + 360) % 360;
  const lat = Math.atan2(zeq, Math.sqrt(xeq*xeq + yeq*yeq)) * 180 / Math.PI;
  // 缩放到可视范围：1 AU = 200 R⊕
  const distanceR = distAU * 200;
  return { lon, lat, distanceR };
}

let solarSystemEntities = [];
let solarSystemVisible = false;
let solarSystemTickCallback = null;

// Solar Walk 风格: 真实纹理 billboard + 轨道线 + 时间动画
const PLANET_TEXTURES = {
  Mercury: 'textures/planets/mercury.jpg',
  Venus:   'textures/planets/venus.jpg',
  Earth:   'textures/planets/earth.jpg',
  Mars:    'textures/planets/mars.jpg',
  Jupiter: 'textures/planets/jupiter.jpg',
  Saturn:  'textures/planets/saturn.jpg',
  Uranus:  'textures/planets/uranus.jpg',
  Neptune: 'textures/planets/neptune.jpg',
  Moon:    'textures/planets/moon.jpg',
  Sun:     'textures/planets/sun.jpg',
};

// 轨道半径 (象征性, 单位: 地球半径 R⊕=6378km), 对数排列保证可见
const ORBIT_R = {
  Mercury: 95, Venus: 125, Earth: 155, Mars: 195,
  Jupiter: 280, Saturn: 380, Uranus: 500, Neptune: 640, Pluto: 800
};
// 行星显示尺寸 (billboard 像素)
const PLANET_SIZE = {
  Mercury: 18, Venus: 24, Earth: 26, Mars: 22,
  Jupiter: 52, Saturn: 46, Uranus: 30, Neptune: 30, Pluto: 12
};
// 轨道倾角 (度)
const ORBIT_INCL = {
  Mercury: 7, Venus: 3.4, Earth: 0, Mars: 1.9,
  Jupiter: 1.3, Saturn: 2.5, Uranus: 0.8, Neptune: 1.8, Pluto: 17.2
};

// 计算行星在轨道上的位置 (基于当前时间, 近似开普勒)
// 返回 {x, y, z} 单位 R⊕, 以太阳为原点
function planetOrbitPos(name, date) {
  const el = PLANET_ELEMENTS[name];
  if (!el) return null;
  const jd = date.getTime() / 86400000 - 10957.5; // J2000 起
  const M = ((el.L + 360 * jd / el.period) % 360) * Math.PI / 180;
  let E = M;
  for (let k = 0; k < 5; k++) E = E - (E - el.e * Math.sin(E) - M) / (1 - el.e * Math.cos(E));
  // 轨道平面位置 (真近点角)
  const xv = el.a * (Math.cos(E) - el.e);
  const yv = el.a * Math.sqrt(1 - el.e * el.e) * Math.sin(E);
  const v = Math.atan2(yv, xv);
  const r = el.a * (1 - el.e * Math.cos(E));
  // 近日点经度 + 升交点
  const argPeri = (el.longPeri - el.longNode) * Math.PI / 180;
  const node = el.longNode * Math.PI / 180;
  const incl = el.i * Math.PI / 180;
  // 真黄经
  const u = v + argPeri;
  // 日心黄道坐标
  const xh = r * (Math.cos(node) * Math.cos(u) - Math.sin(node) * Math.sin(u) * Math.cos(incl));
  const yh = r * (Math.sin(node) * Math.cos(u) + Math.cos(node) * Math.sin(u) * Math.cos(incl));
  const zh = r * Math.sin(u) * Math.sin(incl);
  // 缩放: 1 AU = ORBIT_R.Earth R⊕
  const scale = ORBIT_R.Earth / 1.0;
  return { x: xh * scale, y: yh * scale, z: zh * scale * 0.5 };
}

// 画椭圆轨道 (在黄道面, 用 polyline)
function orbitEllipsePoints(name, segments = 100) {
  const el = PLANET_ELEMENTS[name];
  if (!el) return [];
  const a = el.a * ORBIT_R.Earth; // 半长轴 (R⊕)
  const e = el.e;
  const b = a * Math.sqrt(1 - e * e);
  const pts = [];
  for (let i = 0; i <= segments; i++) {
    const th = i / segments * 2 * Math.PI;
    const x = a * Math.cos(th);
    const y = b * Math.sin(th);
    pts.push(x, y);
  }
  return pts;
}

function updateSolarSystem(visible) {
  if (visible === solarSystemVisible && solarSystemEntities.length > 0) return;
  solarSystemEntities.forEach(e => viewer.entities.remove(e));
  solarSystemEntities = [];
  if (solarSystemTickCallback) {
    viewer.clock.onTick.removeEventListener(solarSystemTickCallback);
    solarSystemTickCallback = null;
  }
  solarSystemVisible = visible;
  if (!visible) return;

  // 太阳: 在原点, 用真实纹理 billboard + 光晕
  const sunPos = SOLAR_ORIGIN;
  const sunEntity = viewer.entities.add({
    position: sunPos,
    billboard: {
      image: PLANET_TEXTURES.Sun,
      width: 90, height: 90,
      scaleByDistance: new Cesium.NearFarScalar(1e6, 1.0, 5e9, 0.3)
    },
    point: {
      pixelSize: 45,
      color: Cesium.Color.fromCssColorString('#ff9800').withAlpha(0.15),
      outlineColor: Cesium.Color.TRANSPARENT,
      outlineWidth: 0
    },
    label: {
      text: '☀️ 太阳',
      font: 'bold 14px sans-serif',
      fillColor: Cesium.Color.fromCssColorString('#ffeb3b'),
      outlineColor: Cesium.Color.BLACK, outlineWidth: 3,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      pixelOffset: new Cesium.Cartesian2(0, -52),
      distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 5e10)
    },
    properties: {
      bodyType: 'star',
      bodyData: {
        name: '太阳', en: 'Sun',
        category: 'G2V 型主序星',
        radius: '696,340 km (109 × 地球)',
        mass: '1.989 × 10³⁰ kg (333,000 × 地球)',
        surfaceTemp: '5,500°C', coreTemp: '1,500 万°C',
        age: '约 46 亿年', remainingLife: '约 50 亿年',
        composition: '氢 73.46% · 氘 24.85% · 氧 0.77% · 碳 0.29% · 铁 0.16%',
        fact: '太阳占太阳系总质量的 99.86%。地球生命的唯一能源。'
      }
    }
  });
  solarSystemEntities.push(sunEntity);

  // 轨道线: 每条行星一个椭圆环 (在黄道面高度 0)
  Object.keys(ORBIT_R).forEach(name => {
    const el = PLANET_ELEMENTS[name];
    if (!el) return;
    const a = el.a * ORBIT_R.Earth;
    const e = el.e;
    const b = a * Math.sqrt(1 - e * e);
    const incl = ORBIT_INCL[name] * Math.PI / 180;
    const node = el.longNode * Math.PI / 180;
    // 生成椭圆点 (3D)
    const pts = [];
    for (let i = 0; i <= 120; i++) {
      const th = i / 120 * 2 * Math.PI;
      const x = a * Math.cos(th);
      const y = b * Math.sin(th);
      // 旋转到升交点 + 倾角
      const xr = x * Math.cos(node) - y * Math.sin(node);
      const yr = x * Math.sin(node) + y * Math.cos(node);
      const zr = y * Math.sin(incl);
      pts.push(new Cesium.Cartesian3(
        SOLAR_ORIGIN.x + xr * SOLAR_SYSTEM_SCALE,
        SOLAR_ORIGIN.y + yr * SOLAR_SYSTEM_SCALE,
        SOLAR_ORIGIN.z + zr * SOLAR_SYSTEM_SCALE * 0.5
      ));
    }
    const isEarth = name === 'Earth';
    solarSystemEntities.push(viewer.entities.add({
      polyline: {
        positions: pts,
        width: isEarth ? 1.5 : 1,
        material: Cesium.Color.fromCssColorString(isEarth ? '#4fc3f7' : '#888888').withAlpha(isEarth ? 0.5 : 0.3),
        arcType: Cesium.ArcType.NONE
      }
    }));
  });

  // 行星 billboard 实体 (位置每帧更新)
  const planetNames = Object.keys(ORBIT_R);
  planetNames.forEach(name => {
    const size = PLANET_SIZE[name] || 16;
    const isEarth = name === 'Earth';
    const entity = viewer.entities.add({
      position: new Cesium.Cartesian3(0, 0, 0), // 初始占位, tick 更新
      billboard: {
        image: PLANET_TEXTURES[name],
        width: size, height: size,
        disableDepthTestDistance: Number.POSITIVE_INFINITY
      },
      label: {
        text: (name === 'Earth' ? '🌍 地球' : name) + (name === 'Pluto' ? ' (矮行星)' : ''),
        font: (isEarth ? 'bold ' : '') + '12px sans-serif',
        fillColor: Cesium.Color.fromCssColorString(isEarth ? '#4fc3f7' : '#ffffff'),
        outlineColor: Cesium.Color.BLACK, outlineWidth: 2,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        pixelOffset: new Cesium.Cartesian2(0, -size / 2 - 8),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 5e10)
      },
      properties: {
        bodyType: 'planet',
        bodyData: getPlanetInfo({ en: name, name: name === 'Earth' ? '地球' : name, dwarf: name === 'Pluto' })
      }
    });
    solarSystemEntities.push(entity);
  });

  // 月球: 绕地球转, 也用纹理
  const moonEntity = viewer.entities.add({
    position: new Cesium.Cartesian3(0, 0, 0),
    billboard: {
      image: PLANET_TEXTURES.Moon,
      width: 14, height: 14,
      disableDepthTestDistance: Number.POSITIVE_INFINITY
    },
    label: {
      text: '🌙 月球',
      font: '12px sans-serif',
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK, outlineWidth: 2,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      pixelOffset: new Cesium.Cartesian2(0, -18),
      distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 5e10)
    },
    properties: {
      bodyType: 'moon',
      bodyData: {
        name: '月球', en: 'Moon',
        category: '天然卫星',
        radius: '1,737 km (0.273 × 地球)',
        mass: '7.342 × 10²² kg (0.012 × 地球)',
        surfaceTemp: '-173°C ~ 127°C',
        distanceFromEarth: '384,400 km',
        orbitalPeriod: '27.32 天',
        age: '约 45.3 亿年',
        fact: '月球是地球唯一的天然卫星。潮汐主因。唯一被人类登过的地外天体。'
      }
    }
  });
  solarSystemEntities.push(moonEntity);

  // 每帧更新位置: 行星沿轨道运动
  solarSystemTickCallback = () => {
    if (!solarSystemVisible) return;
    const now = new Date();
    // 行星位置 (日心 → 地心 Cesium 坐标, 太阳在原点)
    planetNames.forEach((name, idx) => {
      const pos = planetOrbitPos(name, now);
      if (!pos) return;
      const entity = solarSystemEntities[1 + Object.keys(ORBIT_R).length + idx]; // 轨道线之后
      if (entity) {
        entity.position = new Cesium.Cartesian3(
          SOLAR_ORIGIN.x + pos.x * SOLAR_SYSTEM_SCALE,
          SOLAR_ORIGIN.y + pos.y * SOLAR_SYSTEM_SCALE,
          SOLAR_ORIGIN.z + pos.z * SOLAR_SYSTEM_SCALE
        );
      }
    });
    // 月球: 绕地球 (地球在 posEarth)
    const earthPos = planetOrbitPos('Earth', now);
    if (earthPos) {
      const moonAngle = (now.getTime() / 86400000 / 27.32) * 2 * Math.PI;
      const moonR = 30; // 30 R⊕ 距离 (象征)
      const moonEntity = solarSystemEntities[solarSystemEntities.length - 1];
      if (moonEntity) {
        moonEntity.position = new Cesium.Cartesian3(
          SOLAR_ORIGIN.x + (earthPos.x + moonR * Math.cos(moonAngle)) * SOLAR_SYSTEM_SCALE,
          SOLAR_ORIGIN.y + (earthPos.y + moonR * Math.sin(moonAngle)) * SOLAR_SYSTEM_SCALE,
          SOLAR_ORIGIN.z + earthPos.z * SOLAR_SYSTEM_SCALE
        );
      }
    }
  };
  viewer.clock.onTick.addEventListener(solarSystemTickCallback);

  console.log(`太阳系 (Solar Walk 风格) ${solarSystemEntities.length} 个实体`);
}

// 每分钟刷新太阳系
setInterval(() => { if (solarSystemVisible) updateSolarSystem(true); }, 60000);

// ── 太阳光照（Cesium globe.enableLighting）────────────────
document.getElementById('toggle-lighting')?.addEventListener('change', e => {
  viewer.scene.globe.enableLighting = e.target.checked;  // 用真实太阳光照
});


// ── 银河系（10万光年视角）───────────────────────────────
// 银河系直径 10万光年。本应用采用"象征性缩放":1光年 = 100km
// 银河系盘 10万光年 = 1000万km = 1e10m
// 相机距离银心 3-5e10 m(3000-5000万km)看到整个盘
const GAL_SCALE = 100;  // 1 ly = 100 m (象征性,保持 Cesium 渲染精度)
let galaxyEntities = [];
let galaxyActive = false;
let earthWasVisible = true;

function clearGalaxy(skipEarthReset) {
  galaxyEntities.forEach(e => viewer.entities.remove(e));
  galaxyEntities = [];
  galaxyActive = false;
  if (earthWasVisible) viewer.scene.globe.show = true;
  viewer.scene.skyAtmosphere.show = true;
  const overlay = document.getElementById('galaxy-overlay');
  if (overlay) overlay.style.display = 'none';
  // 停止银河系旋转
  const spinEl = document.getElementById('galaxy-spin');
  if (spinEl) spinEl.style.animation = 'none';
  // 还原 sgr/sun 标签默认 css, 避免切到其他视图时还残留 z-index/position
  const sgrLabel = document.getElementById('galaxy-sgr-label');
  if (sgrLabel) sgrLabel.style.cssText = 'position:absolute;left:50%;top:51%;transform:translate(-50%,-50%);color:rgba(255,255,255,0.92);font:600 13px sans-serif;text-shadow:0 1px 4px rgba(0,0,0,0.95), 0 0 12px rgba(0,0,0,0.7);cursor:pointer;text-align:center;';
  const sunLabel = document.getElementById('galaxy-sun-label');
  if (sunLabel) sunLabel.style.cssText = 'position:absolute;left:63%;top:38%;transform:translate(-50%,-50%);color:rgba(255,255,255,0.92);font:600 13px sans-serif;text-shadow:0 1px 4px rgba(0,0,0,0.95), 0 0 12px rgba(0,0,0,0.7);cursor:pointer;text-align:center;';
  // 同步视图模式按钮 (切回地球) — buildGalaxy 内部调用时跳过, 避免把模式重置回 earth
  if (currentViewMode === 'galaxy' && !skipEarthReset) setViewMode('earth');
}
function buildGalaxy() {
  clearGalaxy(true);
  earthWasVisible = viewer.scene.globe.show;

  // 用 HTML overlay 显示银河系示意图 (比 Cesium 3D 远距离渲染可靠)
  const overlay = document.getElementById('galaxy-overlay');
  overlay.style.display = 'block';

  // ── 银心/太阳 圆点创建 (挂到 overlay 内, overlay 隐藏自动隐藏) ──
  const spin = document.getElementById('galaxy-spin');
  let sgrDot = document.getElementById('galaxy-dot-sgr');
  if (!sgrDot) {
    sgrDot = document.createElement('div');
    sgrDot.id = 'galaxy-dot-sgr';
    spin.appendChild(sgrDot);
  }
  let sunDot = document.getElementById('galaxy-dot-sun');
  if (!sunDot) {
    sunDot = document.createElement('div');
    sunDot.id = 'galaxy-dot-sun';
    spin.appendChild(sunDot);
  }
  function drawGalaxyDot(dot, x, y, color, glow) {
    // x/y 可为像素或百分比, 统一拼接
    dot.style.cssText = `position:absolute;left:${x};top:${y};width:7px;height:7px;margin:-3.5px 0 0 -3.5px;border-radius:50%;background:${color};box-shadow:0 0 4px ${color},0 0 12px ${glow};z-index:54;cursor:pointer;`;
  }

  // ── 动态定位标记 (基于图片实际显示区域, 而非窗口百分比) ──
  // 图片内坐标: 核球质心 (49.6%, 50.6%), 太阳 (63%, 38%) — 已用像素分析实测
  function positionGalaxyMarkers() {
    const img = document.getElementById('galaxy-img');
    if (!img) return;
    const rect = img.getBoundingClientRect();
    if (rect.width === 0) return;
    // spin 容器 = 图片显示区域的 70% (保证旋转时四角不超出屏幕被裁剪; 0.7×√2≈0.99<1 安全)
    const spin = document.getElementById('galaxy-spin');
    if (spin) {
      const scale = 0.7;
      const sw = rect.width * scale, sh = rect.height * scale;
      spin.style.cssText = `position:fixed;left:${rect.left + (rect.width - sw) / 2}px;top:${rect.top + (rect.height - sh) / 2}px;width:${sw}px;height:${sh}px;display:flex;align-items:center;justify-content:center;transform-origin:52% 40%;will-change:transform;animation:galaxySpin 600s linear infinite;`;
    }
    // 银心/太阳 位置: NASA Spitzer 图实测 (银心 52%, 40%; 太阳 52%, 69%)
    const pct = (x, y) => `position:absolute;left:${x}%;top:${y}%;`;
    const sgr = document.getElementById('galaxy-sgr');
    const sgrLabel = document.getElementById('galaxy-sgr-label');
    const sun = document.getElementById('galaxy-sun');
    const sunLabel = document.getElementById('galaxy-sun-label');
    // 把标签移进 spin 容器, 跟随图片旋转
    [sgr, sgrLabel, sun, sunLabel].forEach(el => { if (el && el.parentElement !== spin) spin.appendChild(el); });

    if (sgr) sgr.style.cssText = pct(52, 40) + 'width:0;height:0;display:none;';
    if (sgrLabel) sgrLabel.style.cssText = pct(52, 40) + 'transform:translate(-50%,18px);color:rgba(255,235,180,0.98);font:600 13px sans-serif;text-shadow:0 1px 5px rgba(0,0,0,0.98), 0 0 12px rgba(0,0,0,0.9);cursor:pointer;text-align:center;';
    if (sun) { sun.innerHTML = ''; sun.style.cssText = pct(52, 69) + 'width:0;height:0;display:none;'; }
    if (sunLabel) sunLabel.style.cssText = pct(52, 69) + 'transform:translate(-50%,18px);color:rgba(255,235,180,0.98);font:600 13px sans-serif;text-shadow:0 1px 5px rgba(0,0,0,0.98), 0 0 12px rgba(0,0,0,0.9);cursor:pointer;text-align:center;';

    // 银心/太阳 圆点标记
    if (sgrDot) drawGalaxyDot(sgrDot, '52%', '40%', 'rgba(255, 90, 60, 0.95)', 'rgba(255, 120, 60, 0.5)');
    if (sunDot) drawGalaxyDot(sunDot, '52%', '69%', 'rgba(100, 180, 255, 0.95)', 'rgba(100, 180, 255, 0.5)');
  }
  // 图片加载后定位 + 窗口变化时重定位 (只绑定一次)
  const gimg = document.getElementById('galaxy-img');
  console.log('[galaxy] gimg.complete=', gimg && gimg.complete, 'naturalWidth=', gimg && gimg.naturalWidth);
  if (gimg && gimg.complete && gimg.naturalWidth > 0) positionGalaxyMarkers();
  else if (gimg) gimg.addEventListener('load', positionGalaxyMarkers);
  // 即使 complete 为 false 也延迟 100ms 试一次(防缓存图片)
  setTimeout(() => positionGalaxyMarkers(), 200);
  setTimeout(() => positionGalaxyMarkers(), 1000);
  if (!window.__galaxyResizeBound) {
    window.addEventListener('resize', () => {
      if (document.getElementById('galaxy-overlay').style.display !== 'none') {
        positionGalaxyMarkers();
      }
    });
    window.__galaxyResizeBound = true;
  }

  // 绑定 Sgr A* 黑洞点击
  const sgr = document.getElementById('galaxy-sgr');
  const sgrLabel = document.getElementById('galaxy-sgr-label');
  const showSgr = () => showGalaxyPanel({
    name: '银心黑洞 (Sgr A*)',
    en: 'Sagittarius A*',
    emoji: '',
    fields: {
      '类型': '超大质量黑洞',
      '质量': '约 431 万倍太阳质量',
      '距太阳': '约 26,673 光年',
      '史瓦西半径': '约 1,200 万 km (0.08 AU)',
      '影像': '2022 年 5 月 EHT 公布首张照片',
      '发现': '1974 年 Bruce Balick 和 Robert Brown 发现'
    },
    desc: 'Sgr A* 是位于银河系中心的超大质量黑洞，质量约为太阳的 431 万倍。\n\n🔬 关于"中心黄光"：图中央的亮黄色辉光是核球中数十亿颗老年恒星的发 + 周围被黑洞引力加热的稀薄气体（吸积盘），不是黑洞本身在发光。黑洞本体（事件视界）确实完全黑暗——光都逃不出来，但它被发光的恒星/气体包围。EHT 2022 年发布的银河系中心照片清晰显示了"黑色阴影 + 橙色光环"——这正是本图想呈现的。',
    wiki: 'https://zh.wikipedia.org/wiki/人马座A*'
  });
  sgr.onclick = showSgr;
  sgrLabel.onclick = showSgr;

  // 绑定太阳点击
  const sun = document.getElementById('galaxy-sun');
  const sunLabel = document.getElementById('galaxy-sun-label');
  const showSun = () => showGalaxyPanel({
    name: '太阳系 (在银河系中的位置)',
    en: 'Solar System in Milky Way',
    emoji: '',
    fields: {
      '位置': '猎户臂 (Orion-Cygnus Arm)',
      '距银心': '约 26,673 光年',
      '距银盘面': '约 20 光年 (略偏北)',
      '公转速度': '约 220 km/s',
      '公转周期': '约 2.3 亿年 (1 个银河年)',
      '上次在此位置': '恐龙时代 (~2亿年前)'
    },
    desc: '太阳位于猎户臂内侧，距银心约 2.67 万光年。太阳绕银心一周需要 2.3 亿年（一个"银河年"）。上一次太阳处于现在的位置时，恐龙还在地球上。',
    wiki: 'https://zh.wikipedia.org/wiki/太阳在银河系中的位置'
  });
  sun.onclick = showSun;
  sunLabel.onclick = showSun;

  // 返回地球按钮
  const backBtn = document.getElementById('galaxy-back');
  if (backBtn) {
    backBtn.onclick = (e) => {
      e.stopPropagation();
      window.__backToEarth();
      setViewMode('earth');
    };
  }

  // ── 黑洞阴影 div (覆盖 ESO 图核球, 让中心呈现为黑) ──
  // (已移除手绘黑洞暗影 — ESO 原图核球中心已有真实暗区, 画蛇添足)

  // 银河系本体信息 (点击标题才弹)
  overlay.onclick = (e) => {
    if (e.target.id === 'galaxy-title' || e.target.id === 'galaxy-scale') {
      showGalaxyPanel({
        name: '银河系 (Milky Way)',
        en: 'Milky Way Galaxy',
        emoji: '🌌',
        fields: {
          '类型': '棒旋星系 (SBbc)',
          '直径': '约 10 万光年',
          '恒星数': '约 1,000-4,000 亿颗',
          '总质量': '约 1.5 × 10¹² 倍太阳质量',
          '年龄': '约 136 亿年',
          '太阳位置': '猎户臂，距银心 2.67 万光年'
        },
        desc: '银河系是包含太阳系的棒旋星系。盘内有 5 条主要旋臂：英仙臂、猎户臂（太阳所在）、天蝎臂、人马臂、盾牌-半人马臂。',
        wiki: 'https://zh.wikipedia.org/wiki/银河系'
      });
    }
  };

  galaxyActive = true;
  console.log('[galaxy] overlay shown');
}

// ── 返回地球视角 ──────────────────────────────────────
window.__backToEarth = function() {
  clearGalaxy();
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(105, 35, 5000000),
    duration: 2
  });
};

// ── 太阳系 3D 视图 (Solar Walk 风格, Three.js iframe) ──
let solarIframe = null;
let currentViewMode = 'earth';

function openSolarSystemView() {
  if (solarIframe) { solarIframe.style.display = 'block'; return; }
  const solarParams = [];
  if (window.__solarFocus) solarParams.push('focus=' + window.__solarFocus);
  if (window.__solarClickEarth) solarParams.push('clickEarth=1');
  solarIframe = document.createElement('iframe');
  solarIframe.src = '/solar-system-view.html' + (solarParams.length ? '?' + solarParams.join('&') : '');
  solarIframe.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;border:none;z-index:60;background:#000;';
  document.body.appendChild(solarIframe);
}
function closeSolarSystemView() {
  if (solarIframe) solarIframe.remove();
  solarIframe = null;
  viewer.scene.globe.show = true;
}

// 宇宙大尺度 overlay 切换
function showCosmosOverlay(which) {
  // 隐藏所有宇宙 overlay
  document.querySelectorAll('.cosmos-overlay').forEach(el => el.style.display = 'none');
  // 显示目标
  const el = document.getElementById(which + '-overlay');
  if (el) el.style.display = 'block';
}
function hideCosmosOverlays() {
  document.querySelectorAll('.cosmos-overlay').forEach(el => el.style.display = 'none');
}

function setViewMode(mode) {
  currentViewMode = mode;
  document.querySelectorAll('.view-mode-btn').forEach(b => {
    const active = b.dataset.view === mode;
    b.classList.toggle('active', active);
    if (active) {
      b.style.background = 'rgba(79,195,247,0.2)';
      b.style.borderColor = '#4fc3f7';
      b.style.color = '#4fc3f7';
    } else {
      b.style.background = 'rgba(255,255,255,0.06)';
      b.style.borderColor = 'rgba(255,255,255,0.15)';
      b.style.color = 'rgba(255,255,255,0.75)';
    }
  });
  if (mode === 'earth') {
    closeSolarSystemView();
    clearGalaxy();
    hideCosmosOverlays();
    showCesium();
    viewer.scene.globe.show = true;
    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(105, 35, 5000000),
      duration: 1.5
    });
  } else if (mode === 'solar') {
    clearGalaxy();
    hideCosmosOverlays();
    showCesium();
    openSolarSystemView();
  } else if (mode === 'galaxy') {
    closeSolarSystemView();
    hideCosmosOverlays();
    showCesium();
    buildGalaxy();
  } else if (mode === 'localgroup' || mode === 'andromeda' || mode === 'virgo' || mode === 'laniakea' || mode === 'sloan' || mode === 'allsky' || mode === 'observable' || mode === 'hubble' || mode === 'cmb'  || mode === 'pisces-cetus' || mode === 'giant-arc' || mode === 'huge-lqg' || mode === 'giant-grb-ring' || mode === 'hercules-corona') {
    closeSolarSystemView();
    clearGalaxy();
    // 宇宙视图是纯 2D overlay: 隐藏 Cesium 画布, 避免 globe.show=false 时
    // Cesium 触发 'RangeError: Invalid array length' 渲染崩溃 + 错误弹窗遮挡图片
    hideCesium();
    viewer.scene.globe.show = false;
    showCosmosOverlay(mode);
  }
}

// —— 隐藏/恢复 Cesium 画布 (宇宙 2D overlay 视图复用) ——
function hideCesium() {
  const c = document.getElementById('cesiumContainer');
  if (c) c.style.display = 'none';
}
function showCesium() {
  const c = document.getElementById('cesiumContainer');
  if (c) c.style.display = '';
}

// 绑定宇宙 overlay 返回按钮
document.querySelectorAll('.cosmos-back').forEach(btn => {
  btn.addEventListener('click', () => {
    const which = btn.dataset.cosmosBack;
    document.getElementById(which + '-overlay').style.display = 'none';
    setViewMode('earth');
  });
});

// ── 全天星系图交互式浏览器 ──
let allskyData = null;
let allskyLoaded = false;

async function loadAllskyData() {
  if (allskyLoaded) return allskyData;
  try {
    const r = await fetch('/data/allsky_galaxies_data.json');
    allskyData = await r.json();
    allskyLoaded = true;
    console.log(`[allsky] loaded ${allskyData.length} galaxies for browsing`);
  } catch(e) {
    console.warn('[allsky] data load failed', e);
  }
  return allskyData;
}

// 加载交互数据 (在交互模式启动时调用)
loadAllskyData();

function findNearestGalaxy(mouseX, mouseY, imgRect, data) {
  // Mollweide 反投影: 像素 → 赤经/赤纬
  // 画布原始 4096×2048, img 使用 object-fit:contain 可能产生变换
  // 简化: 假设图片填满 (imgRect.width / imgRect.height ≈ 2:1)
  const imgW = 4096, imgH = 2048;
  const scale = Math.min(imgRect.width / imgW, imgRect.height / imgH);
  const drawW = imgW * scale, drawH = imgH * scale;
  const offX = (imgRect.width - drawW) / 2;
  const offY = (imgRect.height - drawH) / 2;
  // 鼠标相对图片原始像素
  const px = (mouseX - imgRect.left - offX) / scale;
  const py = (mouseY - imgRect.top - offY) / scale;
  if (px < 0 || px > imgW || py < 0 || py > imgH) return null;
  // 查最近星系 (数据结构: [{main_id, ra, dec, x, y, z, ...}])
  let nearest = null;
  let minDist = Infinity;
  for (const g of data) {
    const dx = g.x - px;
    const dy = g.y - py;
    const d = dx * dx + dy * dy;
    if (d < minDist) {
      minDist = d;
      nearest = g;
    }
  }
  // 只接受 25 像素以内的星系
  if (minDist > 625) return null;
  return nearest;
}

let allskyHighlighted = null;

function setupAllskyInteraction() {
  const img = document.getElementById('allsky-img');
  const tooltip = document.getElementById('allsky-tooltip');
  const panel = document.getElementById('allsky-panel');
  if (!img) return;

  let mousePos = { x: 0, y: 0 };
  img.addEventListener('mousemove', async (e) => {
    mousePos.x = e.clientX;
    mousePos.y = e.clientY;
    if (!allskyData) return;
    const rect = img.getBoundingClientRect();
    const nearest = findNearestGalaxy(e.clientX, e.clientY, rect, allskyData);
    if (nearest) {
      tooltip.style.display = 'block';
      tooltip.style.left = (e.clientX + 12) + 'px';
      tooltip.style.top = (e.clientY + 12) + 'px';
      tooltip.innerHTML = `<div style="font-weight:600;color:#4fc3f7;">${nearest.main_id}</div><div style="font-size:11px;color:rgba(255,255,255,0.6);margin-top:2px;">z = ${nearest.z.toFixed(4)}</div>`;
    } else {
      tooltip.style.display = 'none';
    }
  });

  img.addEventListener('mouseleave', () => {
    tooltip.style.display = 'none';
  });

  img.addEventListener('click', async (e) => {
    if (!allskyData) return;
    const rect = img.getBoundingClientRect();
    const nearest = findNearestGalaxy(e.clientX, e.clientY, rect, allskyData);
    if (!nearest) return;
    // 计算距离 (z → 距离)
    // z < 0.1 用哈勃定律 v = cz, d = v / H0 (H0 = 70 km/s/Mpc)
    // d = z * c / H0 (Mpc) = z * 300000/70 = z * 4286 Mpc = z * 13.98 亿光年
    const distGly = (nearest.z * 13.98).toFixed(2);  // Gly
    const distMpc = (nearest.z * 4286).toFixed(1);  // Mpc
    // 类型 (粗略): z > 0.5 可能是类星体 / 亮红外星系
    let type = 'Galaxy';
    if (nearest.z > 1) type = 'High-z Galaxy / Quasar';
    else if (nearest.z > 0.2) type = 'Distant Galaxy';
    else if (nearest.z < 0.01) type = 'Nearby Galaxy';
    // 填充面板
    document.getElementById('allsky-panel-name').textContent = nearest.main_id.replace(/"/g, '');
    document.getElementById('allsky-panel-id').textContent = `RA ${nearest.ra.toFixed(2)}° / Dec ${nearest.dec.toFixed(2)}°`;
    document.getElementById('allsky-panel-type').textContent = type;
    document.getElementById('allsky-panel-dist').textContent = `${distGly} 亿光年`;
    document.getElementById('allsky-panel-z').textContent = nearest.z.toFixed(4);
    document.getElementById('allsky-panel-v').textContent = 'N/A';
    document.getElementById('allsky-panel-desc').innerHTML = `<div>这是一个来自 SIMBAD 数据库的真实星系, 距我们 ${distGly} 亿光年 (${distMpc} Mpc)。</div><div style="margin-top:8px;">在交互模式下点击任意星系都能查信息。</div>`;
    const link = document.getElementById('allsky-panel-link');
    link.href = `https://simbad.cds.unistra.fr/simbad/sim-id?Ident=${encodeURIComponent(nearest.main_id.replace(/"/g, ''))}&NbIdent=1&Radius=10&Radius.unit=arcsec&submit=submit+id`;
    panel.style.display = 'block';
  });
}
setupAllskyInteraction();

document.querySelectorAll('.view-mode-btn').forEach(btn => {
  btn.addEventListener('click', () => setViewMode(btn.dataset.view));
});

// 太阳系 iframe 关闭时同步按钮状态
window.addEventListener('message', (ev) => {
  if (ev.data && ev.data.type === 'close-solar-system') {
    closeSolarSystemView();
    setViewMode('earth');
  }
});

// ── 国界/省界 GeoJSON ─────────────────────────────────
let bordersChinaProv = null;
let bordersCountries = null;

function addBorders() {
  // 中国省级边界
  fetch('/data/china_provinces.json').then(r => r.json()).then(geo => {
    geo.features.forEach(f => {
      f.geometry.coordinates.forEach(poly => {
        const ring = poly[0].map(c => Cesium.Cartesian3.fromDegrees(c[0], c[1]));
        viewer.entities.add({
          polyline: {
            positions: ring,
            width: 1,
            material: Cesium.Color.fromCssColorString('#ffffff').withAlpha(0.35),
            clampToGround: true
          }
        });
      });
    });
  }).catch(() => {});
  // 全球国家边界
  fetch('/data/countries.geojson').then(r => r.json()).then(geo => {
    geo.features.forEach(f => {
      if (!f.geometry) return;
      const ring = f.geometry.coordinates[0][0].map(c => Cesium.Cartesian3.fromDegrees(c[0], c[1]));
      viewer.entities.add({
        polyline: {
          positions: ring,
          width: 0.8,
          material: Cesium.Color.fromCssColorString('#aaaaaa').withAlpha(0.25),
          clampToGround: true
        }
      });
    });
  }).catch(() => {});
}

// ── 时区线（每 15° 一条）───────────────────────────────
let tzLines = [];
function addTimezoneLines() {
  for (let lon = -180; lon <= 180; lon += 15) {
    const isMain = lon % 90 === 0;
    const pts = [];
    for (let lat = -90; lat <= 90; lat += 2) {
      pts.push(Cesium.Cartesian3.fromDegrees(lon, lat));
    }
    tzLines.push(viewer.entities.add({
      polyline: {
        positions: pts,
        width: isMain ? 1.5 : 0.6,
        material: Cesium.Color.fromCssColorString(isMain ? '#ff9800' : '#ff9800').withAlpha(isMain ? 0.5 : 0.25),
        clampToGround: true
      }
    }));
  }
}

// ── 叠加层开关 UI 绑定 ───────────────────────────────
// 昼夜分界线
let daynightVisible = true;
document.getElementById('toggle-daynight')?.addEventListener('change', e => {
  daynightVisible = e.target.checked;
  updateTerminator(daynightVisible);
});
updateTerminator(daynightVisible);

// 国界
let bordersVisible = true;
document.getElementById('toggle-borders')?.addEventListener('change', e => {
  if (e.target.checked && !bordersCountries) addBorders();
  // Cesium 不支持动态 show 关掉，简单重启 entity
  bordersVisible = e.target.checked;
});
// 预加载边界（异步，不阻塞）
setTimeout(addBorders, 3000);

// 时区线
let tzVisible = false;
document.getElementById('toggle-timezones')?.addEventListener('change', e => {
  if (e.target.checked && tzLines.length === 0) addTimezoneLines();
  tzVisible = e.target.checked;
  tzLines.forEach(e => e.show = tzVisible);
});

// ── GeoNames 全球搜索 ────────────────────────────────
let gnData = null;
let gnReady = false;

// citycost API 生活成本数据 (从 https://citycost.cn/api/cities.json 拉取)
let citycostData = null;
let citycostReady = false;

async function loadGeoNames() {
  try {
    const r = await fetch('/data/cities_top1500.json');
    const d = await r.json();
    gnData = d.cities;
    gnReady = true;
    console.log(`GeoNames loaded ${gnData.length} cities`);
  } catch(e) { console.warn('GeoNames load failed', e); }
}
loadGeoNames();

// 从 citycost API 拉取生活成本数据, 合并到城市对象上
async function loadCitycost() {
  // 多个备选 URL (开发服务器 vs 生产服务器 vs 本地)
  const urls = [
    'https://citycost.cn/api/cities.json',       // 生产 (citycost.cn)
    'http://citycost.cn/api/cities.json',       // 生产 http 备选
    '/data/cities_cost.json'                    // 本地 fallback (打包在 App 里)
  ];
  for (const url of urls) {
    try {
      const r = await fetch(url, { mode: 'cors' });
      if (!r.ok) continue;
      const d = await r.json();
      if (d && d.cities) {
        citycostData = d.cities;
        citycostReady = true;
        console.log(`[citycost] loaded ${Object.keys(d.cities).length} cities from ${url}`);
        return;
      }
    } catch(e) {
      console.warn(`[citycost] ${url} failed`, e.message);
    }
  }
  console.warn('[citycost] no source available, will use local fallback');
}
loadCitycost();

// 重写搜索逻辑：GeoNames 优先，内部城市次之
const origSearchHandler = document.getElementById('search-input').oninput;
document.getElementById('search-input').addEventListener('input', e => {
  const q = e.target.value.trim().toLowerCase();
  if (!q) return;

  // 1. 先在 allCities（内部城市，有成本数据）搜索
  const hit1 = allCities.find(c =>
    c.name.toLowerCase().includes(q) ||
    (c.name_en && c.name_en.toLowerCase().includes(q)) ||
    c.country.toLowerCase().includes(q)
  );
  if (hit1) {
    flyTo(hit1.lat, hit1.lon, 500000, 1.2);
    showCityPanel(hit1);
    return;
  }

  // 2. 在 GeoNames 搜索（全球任何地点）
  if (gnReady && gnData) {
    // 模糊匹配：名字或拼音首字母
    const scores = gnData.map(c => {
      const nm = (c.name || '').toLowerCase();
      const ascii = (c.ascii || '').toLowerCase();
      const alts = (c.alt_names || []).map(a => a.toLowerCase());
      let score = 0;
      if (nm === q || ascii === q) score = 100;
      else if (nm.startsWith(q) || ascii.startsWith(q)) score = 80;
      else if (nm.includes(q) || ascii.includes(q)) score = 60;
      else if (alts.some(a => a === q || a.startsWith(q))) score = 70;
      return { c, score };
    }).filter(x => x.score > 0).sort((a, b) => b.score - a.score);

    if (scores.length > 0) {
      const best = scores[0].c;
      // 创建一个临时"虚拟城市"对象
      const fakeCity = {
        name: best.name,
        name_en: best.ascii || best.name,
        country: best.country,
        lat: best.lat, lon: best.lon,
        salary: null, rent: null, meal: null,
        description: `人口约 ${best.pop ? best.pop.toLocaleString() : '—'}`,
        wiki: `https://en.wikipedia.org/wiki/${encodeURIComponent(best.ascii || best.name)}`,
      };
      flyTo(best.lat, best.lon, 800000, 1.2);
      showCityPanel(fakeCity);
    }
  }
});

// ── 每分钟更新昼夜分界线 ─────────────────────────────
setInterval(() => updateTerminator(daynightVisible), 60000);


// ── 启动 ──────────────────────────────────────────────
// 保证 loading 屏幕最终一定消失
setTimeout(() => document.getElementById('loading')?.classList.add('hidden'), 8000);
viewer.scene.globe.tileLoadProgressEvent.addEventListener((queueLength) => {
  if (queueLength === 0) {
    setTimeout(() => document.getElementById('loading')?.classList.add('hidden'), 800);
  }
});
loadCityData();

// URL 参数支持
setTimeout(() => {
  const params = new URLSearchParams(window.location.search);
  const view = params.get('view');
  if (view) {
    // view 可能是大洲名（如 china）或地球坐标 'lat,lon,height'
    if (view.includes(',')) {
      const [lat, lon, h] = view.split(',').map(Number);
      flyTo(lat, lon, h || 5000000, 1.5);
    } else {
      const v = CONTINENT_VIEW[view];
      if (v) flyTo(v.lat, v.lon, v.height, 1.5);
    }
    // 同步大洲按钮
    const btn = document.querySelector(`.cont-btn[data-continent="${view}"]`);
    if (btn) {
      document.querySelectorAll('.cont-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeContinent = view;
      filteredCities = filterCities();
      updateCityCount();
      addCityMarkers();
    }
  }
  // 太阳能开关参数
  if (params.get('solar')) {
    if (params.get('solarFocus')) window.__solarFocus = params.get('solarFocus');
    if (params.get('clickEarth')) window.__solarClickEarth = true;
    setViewMode('solar');
  }
  if (params.get('lighting')) {
    const cb = document.getElementById('toggle-lighting');
    cb.checked = true;
    cb.dispatchEvent(new Event('change'));
  }
  if (params.get('galaxy')) {
    setTimeout(() => {
      console.log('[galaxy] auto-trigger');
      setViewMode('galaxy');
      // 可选: 自动弹出 Sgr A* 信息面板验证点击功能
      if (params.get('panel') === 'sgr') {
        setTimeout(() => {
          const sgrEl = document.getElementById('galaxy-sgr');
          if (sgrEl && sgrEl.onclick) sgrEl.onclick();
        }, 1200);
      } else if (params.get('panel') === 'sun') {
        setTimeout(() => {
          const sunEl = document.getElementById('galaxy-sun');
          if (sunEl && sunEl.onclick) sunEl.onclick();
        }, 1200);
      }
      // back=1: 自动返回地球（验证返回逻辑）
      if (params.get('back') === '1') {
        setTimeout(() => {
          console.log('[galaxy] auto-back');
          setViewMode('earth');
        }, 2500);
      }
    }, 800);
  }
}, 2000);
