
// Earth Explorer - Three.js Renderer
// THREE and OrbitControls loaded as global vars from CDN (r128 UMD)

const FALLBACK_CITIES = [
  // 亚洲 (37 cities)
  {name:"东京",name_en:"Tokyo",country:"日本",continent:"亚洲",lat:35.68,lon:139.69,salary:22000,rent:8000,meal:50,restaurant:150,price_per_sqm:80000,wiki:"https://en.wikipedia.org/wiki/Tokyo"},
  {name:"新加坡",name_en:"Singapore",country:"新加坡",continent:"亚洲",lat:1.35,lon:103.82,salary:30000,rent:12000,meal:40,restaurant:120,price_per_sqm:12000,wiki:"https://en.wikipedia.org/wiki/Singapore"},
  {name:"香港",name_en:"Hong Kong",country:"香港",continent:"亚洲",lat:22.32,lon:114.17,salary:25000,rent:15000,meal:45,restaurant:130,price_per_sqm:20000,wiki:"https://en.wikipedia.org/wiki/Hong_Kong"},
  {name:"首尔",name_en:"Seoul",country:"韩国",continent:"亚洲",lat:37.57,lon:126.98,salary:20000,rent:7000,meal:40,restaurant:100,price_per_sqm:70000,wiki:"https://en.wikipedia.org/wiki/Seoul"},
  {name:"上海",name_en:"Shanghai",country:"中国",continent:"亚洲",lat:31.23,lon:121.47,salary:16000,rent:7000,meal:35,restaurant:100,price_per_sqm:70000,wiki:"https://en.wikipedia.org/wiki/Shanghai"},
  {name:"北京",name_en:"Beijing",country:"中国",continent:"亚洲",lat:39.91,lon:116.39,salary:15000,rent:6000,meal:30,restaurant:80,price_per_sqm:60000,wiki:"https://en.wikipedia.org/wiki/Beijing"},
  {name:"曼谷",name_en:"Bangkok",country:"泰国",continent:"亚洲",lat:13.76,lon:100.50,salary:8000,rent:3500,meal:20,restaurant:50,price_per_sqm:25000,wiki:"https://en.wikipedia.org/wiki/Bangkok"},
  {name:"台北",name_en:"Taipei",country:"台湾",continent:"亚洲",lat:25.03,lon:121.57,salary:15000,rent:5000,meal:30,restaurant:80,price_per_sqm:45000,wiki:"https://en.wikipedia.org/wiki/Taipei"},
  {name:"大阪",name_en:"Osaka",country:"日本",continent:"亚洲",lat:34.69,lon:135.50,salary:19000,rent:6000,meal:40,restaurant:100,price_per_sqm:50000,wiki:"https://en.wikipedia.org/wiki/Osaka"},
  {name:"吉隆坡",name_en:"Kuala Lumpur",country:"马来西亚",continent:"亚洲",lat:3.14,lon:101.69,salary:9000,rent:3000,meal:18,restaurant:40,price_per_sqm:15000,wiki:"https://en.wikipedia.org/wiki/Kuala_Lumpur"},
  {name:"胡志明市",name_en:"Ho Chi Minh City",country:"越南",continent:"亚洲",lat:10.82,lon:106.63,salary:6000,rent:2500,meal:15,restaurant:35,price_per_sqm:25000,wiki:"https://en.wikipedia.org/wiki/Ho_Chi_Minh_City"},
  {name:"雅加达",name_en:"Jakarta",country:"印尼",continent:"亚洲",lat:-6.21,lon:106.85,salary:7000,rent:3000,meal:15,restaurant:40,price_per_sqm:20000,wiki:"https://en.wikipedia.org/wiki/Jakarta"},
  {name:"马尼拉",name_en:"Manila",country:"菲律宾",continent:"亚洲",lat:14.60,lon:120.98,salary:5000,rent:2500,meal:12,restaurant:30,price_per_sqm:20000,wiki:"https://en.wikipedia.org/wiki/Manila"},
  {name:"德里",name_en:"Delhi",country:"印度",continent:"亚洲",lat:28.61,lon:77.21,salary:7000,rent:2500,meal:10,restaurant:25,price_per_sqm:8000,wiki:"https://en.wikipedia.org/wiki/Delhi"},
  {name:"孟买",name_en:"Mumbai",country:"印度",continent:"亚洲",lat:19.08,lon:72.88,salary:8000,rent:4000,meal:12,restaurant:30,price_per_sqm:15000,wiki:"https://en.wikipedia.org/wiki/Mumbai"},
  {name:"迪拜",name_en:"Dubai",country:"阿联酋",continent:"亚洲",lat:25.20,lon:55.27,salary:35000,rent:12000,meal:50,restaurant:150,price_per_sqm:15000,wiki:"https://en.wikipedia.org/wiki/Dubai"},
  {name:"伊斯坦布尔",name_en:"Istanbul",country:"土耳其",continent:"亚洲",lat:41.01,lon:28.95,salary:10000,rent:4000,meal:20,restaurant:60,price_per_sqm:15000,wiki:"https://en.wikipedia.org/wiki/Istanbul"},
  {name:"多哈",name_en:"Doha",country:"卡塔尔",continent:"亚洲",lat:25.29,lon:51.53,salary:40000,rent:15000,meal:60,restaurant:180,price_per_sqm:13000,wiki:"https://en.wikipedia.org/wiki/Doha"},
  {name:"利雅得",name_en:"Riyadh",country:"沙特阿拉伯",continent:"亚洲",lat:24.71,lon:46.68,salary:30000,rent:8000,meal:40,restaurant:100,price_per_sqm:8000,wiki:"https://en.wikipedia.org/wiki/Riyadh"},
  {name:"安曼",name_en:"Amman",country:"约旦",continent:"亚洲",lat:31.95,lon:35.91,salary:8000,rent:3000,meal:20,restaurant:50,price_per_sqm:8000,wiki:"https://en.wikipedia.org/wiki/Amman"},
  {name:"科威特城",name_en:"Kuwait City",country:"科威特",continent:"亚洲",lat:29.38,lon:47.99,salary:30000,rent:10000,meal:40,restaurant:100,price_per_sqm:10000,wiki:"https://en.wikipedia.org/wiki/Kuwait_City"},
  {name:"贝鲁特",name_en:"Beirut",country:"黎巴嫩",continent:"亚洲",lat:33.89,lon:35.51,salary:8000,rent:4000,meal:25,restaurant:60,price_per_sqm:15000,wiki:"https://en.wikipedia.org/wiki/Beirut"},
  {name:"马斯喀特",name_en:"Muscat",country:"阿曼",continent:"亚洲",lat:23.59,lon:58.55,salary:25000,rent:8000,meal:35,restaurant:90,price_per_sqm:10000,wiki:"https://en.wikipedia.org/wiki/Muscat"},
  {name:"麦纳麦",name_en:"Manama",country:"巴林",continent:"亚洲",lat:26.22,lon:50.58,salary:25000,rent:8000,meal:35,restaurant:90,price_per_sqm:10000,wiki:"https://en.wikipedia.org/wiki/Manama"},
  {name:"特拉维夫",name_en:"Tel Aviv",country:"以色列",continent:"亚洲",lat:32.09,lon:34.78,salary:25000,rent:10000,meal:45,restaurant:120,price_per_sqm:20000,wiki:"https://en.wikipedia.org/wiki/Tel_Aviv"},
  {name:"科伦坡",name_en:"Colombo",country:"斯里兰卡",continent:"亚洲",lat:6.93,lon:79.85,salary:5000,rand:2000,meal:10,restaurant:25,price_per_sqm:10000,wiki:"https://en.wikipedia.org/wiki/Colombo"},
  {name:"加德满都",name_en:"Kathmandu",country:"尼泊尔",continent:"亚洲",lat:27.72,lon:85.31,salary:4000,rent:1500,meal:8,restaurant:20,price_per_sqm:8000,wiki:"https://en.wikipedia.org/wiki/Kathmandu"},
  {name:"仰光",name_en:"Yangon",country:"缅甸",continent:"亚洲",lat:16.87,lon:96.19,salary:4000,rent:1500,meal:8,restaurant:20,price_per_sqm:8000,wiki:"https://en.wikipedia.org/wiki/Yangon"},
  {name:"万象",name_en:"Vientiane",country:"老挝",continent:"亚洲",lat:17.96,lon:102.63,salary:4000,rent:1200,meal:8,restaurant:18,price_per_sqm:6000,wiki:"https://en.wikipedia.org/wiki/Vientiane"},
  {name:"金边",name_en:"Phnom Penh",country:"柬埔寨",continent:"亚洲",lat:11.56,lon:104.92,salary:4000,rent:1500,meal:8,restaurant:20,price_per_sqm:8000,wiki:"https://en.wikipedia.org/wiki/Phnom_Penh"},
  {name:"台北",name_en:"Taipei",country:"台湾",continent:"亚洲",lat:25.03,lon:121.57,salary:15000,rent:5000,meal:30,restaurant:80,price_per_sqm:45000,wiki:"https://en.wikipedia.org/wiki/Taipei"},
  {name:"深圳",name_en:"Shenzhen",country:"中国",continent:"亚洲",lat:22.54,lon:114.06,salary:15000,rent:5000,meal:30,restaurant:80,price_per_sqm:60000,wiki:"https://en.wikipedia.org/wiki/Shenzhen"},
  {name:"广州",name_en:"Guangzhou",country:"中国",continent:"亚洲",lat:23.13,lon:113.26,salary:13000,rent:4500,meal:25,restaurant:70,price_per_sqm:40000,wiki:"https://en.wikipedia.org/wiki/Guangzhou"},
  {name:"成都",name_en:"Chengdu",country:"中国",continent:"亚洲",lat:30.66,lon:104.07,salary:11000,rent:3000,meal:20,restaurant:60,price_per_sqm:15000,wiki:"https://en.wikipedia.org/wiki/Chengdu"},
  {name:"杭州",name_en:"Hangzhou",country:"中国",continent:"亚洲",lat:30.27,lon:120.15,salary:14000,rent:5000,meal:25,restaurant:70,price_per_sqm:35000,wiki:"https://en.wikipedia.org/wiki/Hangzhou"},
  {name:"重庆",name_en:"Chongqing",country:"中国",continent:"亚洲",lat:29.55,lon:106.55,salary:10000,rent:2500,meal:18,restaurant:50,price_per_sqm:12000,wiki:"https://en.wikipedia.org/wiki/Chongqing"},
  {name:"天津",name_en:"Tianjin",country:"中国",continent:"亚洲",lat:39.34,lon:117.20,salary:11000,rent:3000,meal:20,restaurant:55,price_per_sqm:25000,wiki:"https://en.wikipedia.org/wiki/Tianjin"},
  {name:"武汉",name_en:"Wuhan",country:"中国",continent:"亚洲",lat:30.59,lon:114.29,salary:10000,rent:2500,meal:18,restaurant:50,price_per_sqm:15000,wiki:"https://en.wikipedia.org/wiki/Wuhan"},

  // 欧洲 (54 cities)
  {name:"伦敦",name_en:"London",country:"英国",continent:"欧洲",lat:51.51,lon:-0.13,salary:35000,rent:18000,meal:45,restaurant:130,price_per_sqm:10000,wiki:"https://en.wikipedia.org/wiki/London"},
  {name:"巴黎",name_en:"Paris",country:"法国",continent:"欧洲",lat:48.86,lon:2.35,salary:25000,rent:12000,meal:40,restaurant:120,price_per_sqm:12000,wiki:"https://en.wikipedia.org/wiki/Paris"},
  {name:"柏林",name_en:"Berlin",country:"德国",continent:"欧洲",lat:52.52,lon:13.40,salary:28000,rent:10000,meal:30,restaurant:80,price_per_sqm:5000,wiki:"https://en.wikipedia.org/wiki/Berlin"},
  {name:"巴塞罗那",name_en:"Barcelona",country:"西班牙",continent:"欧洲",lat:41.39,lon:2.17,salary:20000,rent:9000,meal:30,restaurant:80,price_per_sqm:4000,wiki:"https://en.wikipedia.org/wiki/Barcelona"},
  {name:"马德里",name_en:"Madrid",country:"西班牙",continent:"欧洲",lat:40.42,lon:-3.70,salary:20000,rent:9000,meal:28,restaurant:75,price_per_sqm:3500,wiki:"https://en.wikipedia.org/wiki/Madrid"},
  {name:"罗马",name_en:"Rome",country:"意大利",continent:"欧洲",lat:41.90,lon:12.50,salary:20000,rent:10000,meal:30,restaurant:85,price_per_sqm:3500,wiki:"https://en.wikipedia.org/wiki/Rome"},
  {name:"米兰",name_en:"Milan",country:"意大利",continent:"欧洲",lat:45.46,lon:9.19,salary:22000,rent:11000,meal:35,restaurant:90,price_per_sqm:5000,wiki:"https://en.wikipedia.org/wiki/Milan"},
  {name:"阿姆斯特丹",name_en:"Amsterdam",country:"荷兰",continent:"欧洲",lat:52.37,lon:4.90,salary:30000,rent:14000,meal:40,restaurant:100,price_per_sqm:6000,wiki:"https://en.wikipedia.org/wiki/Amsterdam"},
  {name:"维也纳",name_en:"Vienna",country:"奥地利",continent:"欧洲",lat:48.21,lon:16.37,salary:25000,rent:9000,meal:30,restaurant:80,price_per_sqm:4500,wiki:"https://en.wikipedia.org/wiki/Vienna"},
  {name:"苏黎世",name_en:"Zurich",country:"瑞士",continent:"欧洲",lat:47.38,lon:8.54,salary:50000,rent:18000,meal:60,restaurant:180,price_per_sqm:12000,wiki:"https://en.wikipedia.org/wiki/Zurich"},
  {name:"日内瓦",name_en:"Geneva",country:"瑞士",continent:"欧洲",lat:46.20,lon:6.15,salary:48000,rent:18000,meal:60,restaurant:180,price_per_sqm:12000,wiki:"https://en.wikipedia.org/wiki/Geneva"},
  {name:"里斯本",name_en:"Lisbon",country:"葡萄牙",continent:"欧洲",lat:38.72,lon:-9.14,salary:12000,rent:6000,meal:20,restaurant:60,price_per_sqm:3000,wiki:"https://en.wikipedia.org/wiki/Lisbon"},
  {name:"波尔图",name_en:"Porto",country:"葡萄牙",continent:"欧洲",lat:41.16,lon:-8.63,salary:10000,rent:5000,meal:18,restaurant:50,price_per_sqm:2500,wiki:"https://en.wikipedia.org/wiki/Porto"},
  {name:"都柏林",name_en:"Dublin",country:"爱尔兰",continent:"欧洲",lat:53.35,lon:-6.26,salary:32000,rent:14000,meal:40,restaurant:110,price_per_sqm:5000,wiki:"https://en.wikipedia.org/wiki/Dublin"},
  {name:"哥本哈根",name_en:"Copenhagen",country:"丹麦",continent:"欧洲",lat:55.68,lon:12.57,salary:40000,rent:14000,meal:50,restaurant:150,price_per_sqm:6000,wiki:"https://en.wikipedia.org/wiki/Copenhagen"},
  {name:"斯德哥尔摩",name_en:"Stockholm",country:"瑞典",continent:"欧洲",lat:59.33,lon:18.07,salary:35000,rent:12000,meal:45,restaurant:130,price_per_sqm:5500,wiki:"https://en.wikipedia.org/wiki/Stockholm"},
  {name:"奥斯陆",name_en:"Oslo",country:"挪威",continent:"欧洲",lat:59.91,lon:10.75,salary:45000,rent:15000,meal:55,restaurant:160,price_per_sqm:7000,wiki:"https://en.wikipedia.org/wiki/Oslo"},
  {name:"赫尔辛基",name_en:"Helsinki",country:"芬兰",continent:"欧洲",lat:60.17,lon:24.94,salary:33000,rent:11000,meal:40,restaurant:120,price_per_sqm:5000,wiki:"https://en.wikipedia.org/wiki/Helsinki"},
  {name:"布鲁塞尔",name_en:"Brussels",country:"比利时",continent:"欧洲",lat:50.85,lon:4.35,salary:27000,rent:10000,meal:35,restaurant:95,price_per_sqm:3500,wiki:"https://en.wikipedia.org/wiki/Brussels"},
  {name:"雅典",name_en:"Athens",country:"希腊",continent:"欧洲",lat:37.98,lon:23.73,salary:12000,rent:5000,meal:22,restaurant:65,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Athens"},
  {name:"华沙",name_en:"Warsaw",country:"波兰",continent:"欧洲",lat:52.23,lon:21.01,salary:12000,rent:5000,meal:18,restaurant:50,price_per_sqm:2500,wiki:"https://en.wikipedia.org/wiki/Warsaw"},
  {name:"布拉格",name_en:"Prague",country:"捷克",continent:"欧洲",lat:50.08,lon:14.44,salary:15000,rent:6000,meal:20,restaurant:55,price_per_sqm:3000,wiki:"https://en.wikipedia.org/wiki/Prague"},
  {name:"布达佩斯",name_en:"Budapest",country:"匈牙利",continent:"欧洲",lat:47.50,lon:19.04,salary:11000,rent:5000,meal:15,restaurant:45,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Budapest"},
  {name:"克拉科夫",name_en:"Krakow",country:"波兰",continent:"欧洲",lat:50.06,lon:19.94,salary:9000,rent:4000,meal:14,restaurant:40,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Krakow"},
  {name:"维尔纽斯",name_en:"Vilnius",country:"立陶宛",continent:"欧洲",lat:54.69,lon:25.28,salary:10000,rent:4000,meal:14,restaurant:40,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Vilnius"},
  {name:"里加",name_en:"Riga",country:"拉脱维亚",continent:"欧洲",lat:56.95,lon:24.11,salary:9000,rent:4000,meal:14,restaurant:40,price_per_sqm:1800,wiki:"https://en.wikipedia.org/wiki/Riga"},
  {name:"塔林",name_en:"Tallinn",country:"爱沙尼亚",continent:"欧洲",lat:59.43,lon:24.74,salary:12000,rent:5000,meal:18,restaurant:50,price_per_sqm:2500,wiki:"https://en.wikipedia.org/wiki/Tallinn"},
  {name:"萨格勒布",name_en:"Zagreb",country:"克罗地亚",continent:"欧洲",lat:45.82,lon:15.98,salary:11000,rent:4500,meal:16,restaurant:45,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Zagreb"},
  {name:"卢布尔雅那",name_en:"Ljubljana",country:"斯洛文尼亚",continent:"欧洲",lat:46.05,lon:14.51,salary:15000,rent:6000,meal:20,restaurant:55,price_per_sqm:3000,wiki:"https://en.wikipedia.org/wiki/Ljubljana"},
  {name:"贝尔格莱德",name_en:"Belgrade",country:"塞尔维亚",continent:"欧洲",lat:44.82,lon:20.47,salary:9000,rand:3500,meal:12,restaurant:35,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Belgrade"},
  {name:"萨拉热窝",name_en:"Sarajevo",country:"波黑",continent:"欧洲",lat:43.86,lon:18.41,salary:7000,rent:2500,meal:10,restaurant:30,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Sarajevo"},
  {name:"地拉那",name_en:"Tirana",country:"阿尔巴尼亚",continent:"欧洲",lat:41.33,lon:19.82,salary:6000,rent:2500,meal:10,restaurant:28,price_per_sqm:1000,wiki:"https://en.wikipedia.org/wiki/Tirana"},
  {name:"斯科普里",name_en:"Skopje",country:"北马其顿",continent:"欧洲",lat:42.00,lon:21.44,salary:6000,rent:2200,meal:10,restaurant:25,price_per_sqm:1000,wiki:"https://en.wikipedia.org/wiki/Skopje"},
  {name:"波德戈里察",name_en:"Podgorica",country:"黑山",continent:"欧洲",lat:42.43,lon:19.26,salary:7000,rent:2500,meal:12,restaurant:30,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Podgorica"},
  {name:"索非亚",name_en:"Sofia",country:"保加利亚",continent:"欧洲",lat:42.70,lon:23.32,salary:8000,rent:3000,meal:12,restaurant:35,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Sofia"},
  {name:"布加勒斯特",name_en:"Bucharest",country:"罗马尼亚",continent:"欧洲",lat:44.44,lon:26.10,salary:9000,rent:3500,meal:14,restaurant:40,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Bucharest"},
  {name:"基辅",name_en:"Kyiv",country:"乌克兰",continent:"欧洲",lat:50.45,lon:30.52,salary:8000,rent:3000,meal:12,restaurant:35,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Kyiv"},
  {name:"基希讷乌",name_en:"Chisinau",country:"摩尔多瓦",continent:"欧洲",lat:47.01,lon:28.90,salary:5000,rent:2000,meal:8,restaurant:22,price_per_sqm:800,wiki:"https://en.wikipedia.org/wiki/Chisinau"},
  {name:"明斯克",name_en:"Minsk",country:"白俄罗斯",continent:"欧洲",lat:53.90,lon:27.57,salary:7000,rent:2500,meal:10,restaurant:28,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Minsk"},
  {name:"雷克雅未克",name_en:"Reykjavik",country:"冰岛",continent:"欧洲",lat:64.15,lon:-21.95,salary:45000,rent:15000,meal:55,restaurant:160,price_per_sqm:5000,wiki:"https://en.wikipedia.org/wiki/Reykjavik"},
  {name:"卢森堡",name_en:"Luxembourg",country:"卢森堡",continent:"欧洲",lat:49.61,lon:6.13,salary:50000,rent:18000,meal:60,restaurant:160,price_per_sqm:8000,wiki:"https://en.wikipedia.org/wiki/Luxembourg"},
  {name:"瓦莱塔",name_en:"Valletta",country:"马耳他",continent:"欧洲",lat:35.90,lon:14.51,salary:20000,rent:8000,meal:30,restaurant:80,price_per_sqm:4000,wiki:"https://en.wikipedia.org/wiki/Valletta"},
  {name:"尼科西亚",name_en:"Nicosia",country:"塞浦路斯",continent:"欧洲",lat:35.19,lon:33.38,salary:15000,rent:5000,meal:25,restaurant:65,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Nicosia"},
  {name:"第比利斯",name_en:"Tbilisi",country:"格鲁吉亚",continent:"欧洲",lat:41.72,lon:44.79,salary:6000,rand:2000,meal:8,restaurant:22,price_per_sqm:800,wiki:"https://en.wikipedia.org/wiki/Tbilisi"},
  {name:"埃里温",name_en:"Yerevan",country:"亚美尼亚",continent:"欧洲",lat:40.18,lon:44.51,salary:5000,rent:2000,meal:8,restaurant:20,price_per_sqm:800,wiki:"https://en.wikipedia.org/wiki/Yerevan"},
  {name:"布拉迪斯拉发",name_en:"Bratislava",country:"斯洛伐克",continent:"欧洲",lat:48.15,lon:17.11,salary:13000,rent:5500,meal:18,restaurant:50,price_per_sqm:2500,wiki:"https://en.wikipedia.org/wiki/Bratislava"},
  {name:"法兰克福",name_en:"Frankfurt",country:"德国",continent:"欧洲",lat:50.11,lon:8.68,salary:32000,rent:12000,meal:35,restaurant:95,price_per_sqm:5000,wiki:"https://en.wikipedia.org/wiki/Frankfurt"},
  {name:"慕尼黑",name_en:"Munich",country:"德国",continent:"欧洲",lat:48.14,lon:11.58,salary:35000,rent:14000,meal:35,restaurant:100,price_per_sqm:7000,wiki:"https://en.wikipedia.org/wiki/Munich"},
  {name:"汉堡",name_en:"Hamburg",country:"德国",continent:"欧洲",lat:53.55,lon:10.00,salary:30000,rent:11000,meal:32,restaurant:90,price_per_sqm:4500,wiki:"https://en.wikipedia.org/wiki/Hamburg"},
  {name:"佛罗伦萨",name_en:"Florence",country:"意大利",continent:"欧洲",lat:43.77,lon:11.25,salary:19000,rent:9000,meal:30,restaurant:85,price_per_sqm:4000,wiki:"https://en.wikipedia.org/wiki/Florence"},
  {name:"阿利坎特",name_en:"Alicante",country:"西班牙",continent:"欧洲",lat:38.35,lon:-0.48,salary:15000,rent:5500,meal:20,restaurant:55,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Alicante"},
  {name:"马尔默",name_en:"Malmo",country:"瑞典",continent:"欧洲",lat:55.61,lon:13.00,salary:30000,rent:10000,meal:35,restaurant:100,price_per_sqm:3500,wiki:"https://en.wikipedia.org/wiki/Malmo"},
  {name:"卑尔根",name_en:"Bergen",country:"挪威",continent:"欧洲",lat:60.39,lon:5.33,salary:40000,rent:13000,meal:50,restaurant:145,price_per_sqm:5000,wiki:"https://en.wikipedia.org/wiki/Bergen"},
  {name:"日内瓦",name_en:"Geneva",country:"瑞士",continent:"欧洲",lat:46.20,lon:6.15,salary:48000,rent:18000,meal:60,restaurant:180,price_per_sqm:12000,wiki:"https://en.wikipedia.org/wiki/Geneva"},

  // 北美洲 (25 cities)
  {name:"纽约",name_en:"New York",country:"美国",continent:"北美洲",lat:40.71,lon:-74.01,salary:50000,rent:25000,meal:50,restaurant:180,price_per_sqm:15000,wiki:"https://en.wikipedia.org/wiki/New_York_City"},
  {name:"洛杉矶",name_en:"Los Angeles",country:"美国",continent:"北美洲",lat:34.05,lon:-118.24,salary:45000,rent:20000,meal:45,restaurant:150,price_per_sqm:8000,wiki:"https://en.wikipedia.org/wiki/Los_Angeles"},
  {name:"旧金山",name_en:"San Francisco",country:"美国",continent:"北美洲",lat:37.77,lon:-122.42,salary:60000,rent:28000,meal:55,restaurant:180,price_per_sqm:12000,wiki:"https://en.wikipedia.org/wiki/San_Francisco"},
  {name:"迈阿密",name_en:"Miami",country:"美国",continent:"北美洲",lat:25.76,lon:-80.19,salary:40000,rent:18000,meal:40,restaurant:130,price_per_sqm:6000,wiki:"https://en.wikipedia.org/wiki/Miami"},
  {name:"西雅图",name_en:"Seattle",country:"美国",continent:"北美洲",lat:47.61,lon:-122.33,salary:50000,rent:20000,meal:45,restaurant:140,price_per_sqm:7000,wiki:"https://en.wikipedia.org/wiki/Seattle"},
  {name:"芝加哥",name_en:"Chicago",country:"美国",continent:"北美洲",lat:41.88,lon:-87.63,salary:40000,rent:16000,meal:40,restaurant:120,price_per_sqm:4000,wiki:"https://en.wikipedia.org/wiki/Chicago"},
  {name:"波士顿",name_en:"Boston",country:"美国",continent:"北美洲",lat:42.36,lon:-71.06,salary:50000,rent:22000,meal:48,restaurant:150,price_per_sqm:8000,wiki:"https://en.wikipedia.org/wiki/Boston"},
  {name:"华盛顿",name_en:"Washington D.C.",country:"美国",continent:"北美洲",lat:38.91,lon:-77.04,salary:50000,rent:20000,meal:45,restaurant:140,price_per_sqm:7000,wiki:"https://en.wikipedia.org/wiki/Washington,_D.C."},
  {name:"奥斯汀",name_en:"Austin",country:"美国",continent:"北美洲",lat:30.27,lon:-97.74,salary:45000,rent:15000,meal:35,restaurant:110,price_per_sqm:4500,wiki:"https://en.wikipedia.org/wiki/Austin,_Texas"},
  {name:"丹佛",name_en:"Denver",country:"美国",continent:"北美洲",lat:39.74,lon:-104.98,salary:42000,rent:15000,meal:38,restaurant:115,price_per_sqm:4500,wiki:"https://en.wikipedia.org/wiki/Denver"},
  {name:"拉斯维加斯",name_en:"Las Vegas",country:"美国",continent:"北美洲",lat:36.17,lon:-115.14,salary:38000,rent:12000,meal:35,restaurant:100,price_per_sqm:3000,wiki:"https://en.wikipedia.org/wiki/Las_Vegas"},
  {name:"菲尼克斯",name_en:"Phoenix",country:"美国",continent:"北美洲",lat:33.45,lon:-112.07,salary:38000,rent:11000,meal:30,restaurant:90,price_per_sqm:3000,wiki:"https://en.wikipedia.org/wiki/Phoenix,_Arizona"},
  {name:"波特兰",name_en:"Portland",country:"美国",continent:"北美洲",lat:45.52,lon:-122.68,salary:42000,rent:15000,meal:38,restaurant:110,price_per_sqm:4500,wiki:"https://en.wikipedia.org/wiki/Portland,_Oregon"},
  {name:"亚特兰大",name_en:"Atlanta",country:"美国",continent:"北美洲",lat:33.75,lon:-84.39,salary:40000,rent:14000,meal:35,restaurant:100,price_per_sqm:3500,wiki:"https://en.wikipedia.org/wiki/Atlanta"},
  {name:"多伦多",name_en:"Toronto",country:"加拿大",continent:"北美洲",lat:43.65,lon:-79.38,salary:40000,rent:16000,meal:40,restaurant:120,price_per_sqm:8000,wiki:"https://en.wikipedia.org/wiki/Toronto"},
  {name:"温哥华",name_en:"Vancouver",country:"加拿大",continent:"北美洲",lat:49.28,lon:-123.12,salary:40000,rent:16000,meal:40,restaurant:115,price_per_sqm:9000,wiki:"https://en.wikipedia.org/wiki/Vancouver"},
  {name:"蒙特利尔",name_en:"Montreal",country:"加拿大",continent:"北美洲",lat:45.50,lon:-73.57,salary:35000,rent:12000,meal:35,restaurant:100,price_per_sqm:5000,wiki:"https://en.wikipedia.org/wiki/Montreal"},
  {name:"卡尔加里",name_en:"Calgary",country:"加拿大",continent:"北美洲",lat:51.05,lon:-114.07,salary:40000,rent:13000,meal:38,restaurant:110,price_per_sqm:4000,wiki:"https://en.wikipedia.org/wiki/Calgary"},
  {name:"墨西哥城",name_en:"Mexico City",country:"墨西哥",continent:"北美洲",lat:19.43,lon:-99.13,salary:12000,rent:6000,meal:15,restaurant:45,price_per_sqm:2500,wiki:"https://en.wikipedia.org/wiki/Mexico_City"},
  {name:"坎昆",name_en:"Cancun",country:"墨西哥",continent:"北美洲",lat:21.16,lon:-86.85,salary:8000,rent:4000,meal:15,restaurant:45,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Cancun"},
  {name:"瓜达拉哈拉",name_en:"Guadalajara",country:"墨西哥",continent:"北美洲",lat:20.66,lon:-103.35,salary:9000,rent:4000,meal:12,restaurant:35,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Guadalajara"},
  {name:"圣何塞",name_en:"San Jose",country:"哥斯达黎加",continent:"北美洲",lat:9.93,lon:-84.08,salary:12000,rent:5000,meal:18,restaurant:50,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/San_Jose,_Costa_Rica"},
  {name:"巴拿马城",name_en:"Panama City",country:"巴拿马",continent:"北美洲",lat:9.00,lon:-79.50,salary:12000,rent:5000,meal:18,restaurant:50,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Panama_City"},
  {name:"圣多明各",name_en:"Santo Domingo",country:"多米尼加",continent:"北美洲",lat:18.49,lon:-69.89,salary:7000,rent:3000,meal:12,restaurant:35,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Santo_Domingo"},
  {name:"哈瓦那",name_en:"Havana",country:"古巴",continent:"北美洲",lat:23.11,lon:-82.37,salary:4000,rent:1500,meal:5,restaurant:20,price_per_sqm:800,wiki:"https://en.wikipedia.org/wiki/Havana"},

  // 南美洲 (14 cities)
  {name:"圣保罗",name_en:"Sao Paulo",country:"巴西",continent:"南美洲",lat:-23.55,lon:-46.63,salary:10000,rent:4000,meal:15,restaurant:45,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/S%C3%A3o_Paulo"},
  {name:"里约热内卢",name_en:"Rio de Janeiro",country:"巴西",continent:"南美洲",lat:-22.91,lon:-43.17,salary:9000,rent:4000,meal:14,restaurant:42,price_per_sqm:2500,wiki:"https://en.wikipedia.org/wiki/Rio_de_Janeiro"},
  {name:"布宜诺斯艾利斯",name_en:"Buenos Aires",country:"阿根廷",continent:"南美洲",lat:-34.60,lon:-58.38,salary:8000,rent:3000,meal:12,restaurant:38,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Buenos_Aires"},
  {name:"蒙得维的亚",name_en:"Montevideo",country:"乌拉圭",continent:"南美洲",lat:-34.90,lon:-56.16,salary:10000,rent:4000,meal:16,restaurant:45,price_per_sqm:1800,wiki:"https://en.wikipedia.org/wiki/Montevideo"},
  {name:"圣地亚哥",name_en:"Santiago",country:"智利",continent:"南美洲",lat:-33.45,lon:-70.67,salary:12000,rent:5000,meal:18,restaurant:50,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Santiago"},
  {name:"利马",name_en:"Lima",country:"秘鲁",continent:"南美洲",lat:-12.05,lon:-77.04,salary:7000,rent:3000,meal:10,restaurant:30,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Lima"},
  {name:"波哥大",name_en:"Bogota",country:"哥伦比亚",continent:"南美洲",lat:4.71,lon:-74.07,salary:7000,rent:3000,meal:10,restaurant:30,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Bogota"},
  {name:"麦德林",name_en:"Medellin",country:"哥伦比亚",continent:"南美洲",lat:6.25,lon:-75.57,salary:5000,rent:2000,meal:8,restaurant:25,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Medell%C3%ADn"},
  {name:"基多",name_en:"Quito",country:"厄瓜多尔",continent:"南美洲",lat:-0.18,lon:-78.50,salary:6000,rand:2500,meal:8,restaurant:25,price_per_sqm:1000,wiki:"https://en.wikipedia.org/wiki/Quito"},
  {name:"拉巴斯",name_en:"La Paz",country:"玻利维亚",continent:"南美洲",lat:-16.50,lon:-68.15,salary:5000,rent:2000,meal:7,restaurant:22,price_per_sqm:800,wiki:"https://en.wikipedia.org/wiki/La_Paz"},
  {name:"亚松森",name_en:"Asuncion",country:"巴拉圭",continent:"南美洲",lat:-25.26,lon:-57.67,salary:5000,rand:2000,meal:7,restaurant:20,price_per_sqm:800,wiki:"https://en.wikipedia.org/wiki/Asunci%C3%B3n"},
  {name:"加拉加斯",name_en:"Caracas",country:"委内瑞拉",continent:"南美洲",lat:10.48,lon:-66.90,salary:4000,rent:2000,meal:8,restaurant:25,price_per_sqm:800,wiki:"https://en.wikipedia.org/wiki/Caracas"},
  {name:"库里蒂巴",name_en:"Curitiba",country:"巴西",continent:"南美洲",lat:-25.43,lon:-49.27,salary:8000,rent:3000,meal:12,restaurant:35,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Curitiba"},
  {name:"卡塔赫纳",name_en:"Cartagena",country:"哥伦比亚",continent:"南美洲",lat:10.42,lon:-75.51,salary:5000,rent:2000,meal:8,restaurant:25,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Cartagena,_Colombia"},

  // 非洲 (10 cities)
  {name:"开罗",name_en:"Cairo",country:"埃及",continent:"非洲",lat:30.04,lon:31.24,salary:6000,rent:2500,meal:8,restaurant:25,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Cairo"},
  {name:"约翰内斯堡",name_en:"Johannesburg",country:"南非",continent:"非洲",lat:-26.20,lon:28.05,salary:10000,rent:4000,meal:14,restaurant:40,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Johannesburg"},
  {name:"开普敦",name_en:"Cape Town",country:"南非",continent:"非洲",lat:-33.93,lon:18.42,salary:10000,rent:4000,meal:14,restaurant:40,price_per_sqm:1800,wiki:"https://en.wikipedia.org/wiki/Cape_Town"},
  {name:"拉巴特",name_en:"Rabat",country:"摩洛哥",continent:"非洲",lat:34.02,lon:-6.83,salary:7000,rent:3000,meal:10,restaurant:28,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Rabat"},
  {name:"卡萨布兰卡",name_en:"Casablanca",country:"摩洛哥",continent:"非洲",lat:33.57,lon:-7.59,salary:7000,rent:3000,meal:10,restaurant:28,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Casablanca"},
  {name:"突尼斯",name_en:"Tunis",country:"突尼斯",continent:"非洲",lat:36.82,lon:10.17,salary:5000,rand:2000,meal:8,restaurant:22,price_per_sqm:800,wiki:"https://en.wikipedia.org/wiki/Tunis"},
  {name:"内罗毕",name_en:"Nairobi",country:"肯尼亚",continent:"非洲",lat:-1.29,lon:36.82,salary:6000,rent:2500,meal:8,restaurant:25,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Nairobi"},
  {name:"拉各斯",name_en:"Lagos",country:"尼日利亚",continent:"非洲",lat:6.52,lon:3.38,salary:5000,rent:2500,meal:7,restaurant:22,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Lagos"},
  {name:"达累斯萨拉姆",name_en:"Dar es Salaam",country:"坦桑尼亚",continent:"非洲",lat:-6.79,lon:39.21,salary:5000,rent:2000,meal:7,restaurant:20,price_per_sqm:1000,wiki:"https://en.wikipedia.org/wiki/Dar_es_Salaam"},
  {name:"阿克拉",name_en:"Accra",country:"加纳",continent:"非洲",lat:5.56,lon:-0.19,salary:5000,rent:2000,meal:7,restaurant:20,price_per_sqm:1000,wiki:"https://en.wikipedia.org/wiki/Accra"},
  {name:"基加利",name_en:"Kigali",country:"卢旺达",continent:"非洲",lat:-1.94,lon:30.06,salary:5000,rent:2000,meal:7,restaurant:20,price_per_sqm:1000,wiki:"https://en.wikipedia.org/wiki/Kigali"},
  {name:"达喀尔",name_en:"Dakar",country:"塞内加尔",continent:"非洲",lat:14.72,lon:-17.47,salary:5000,rent:2000,meal:7,restaurant:20,price_per_sqm:1000,wiki:"https://en.wikipedia.org/wiki/Dakar"},
  {name:"温得和克",name_en:"Windhoek",country:"纳米比亚",continent:"非洲",lat:-22.56,lon:17.09,salary:7000,rent:2500,meal:12,restaurant:35,price_per_sqm:1200,wiki:"https://en.wikipedia.org/wiki/Windhoek"},
  {name:"路易港",name_en:"Port Louis",country:"毛里求斯",continent:"非洲",lat:-20.16,lon:57.50,salary:7000,rent:3000,meal:12,restaurant:35,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Port_Louis,_Mauritius"},
  {name:"亚的斯亚贝巴",name_en:"Addis Ababa",country:"埃塞俄比亚",continent:"非洲",lat:9.03,lon:38.75,salary:4000,rent:1500,meal:5,restaurant:15,price_per_sqm:800,wiki:"https://en.wikipedia.org/wiki/Addis_Ababa"},
  {name:"维多利亚",name_en:"Victoria",country:"塞舌尔",continent:"非洲",lat:-4.62,lon:55.45,salary:8000,rent:4000,meal:20,restaurant:50,price_per_sqm:2000,wiki:"https://en.wikipedia.org/wiki/Victoria,_Seychelles"},

  // 大洋洲 (10 cities)
  {name:"悉尼",name_en:"Sydney",country:"澳大利亚",continent:"大洋洲",lat:-33.87,lon:151.21,salary:40000,rent:18000,meal:45,restaurant:130,price_per_sqm:10000,wiki:"https://en.wikipedia.org/wiki/Sydney"},
  {name:"墨尔本",name_en:"Melbourne",country:"澳大利亚",continent:"大洋洲",lat:-37.81,lon:144.96,salary:38000,rent:16000,meal:40,restaurant:120,price_per_sqm:7000,wiki:"https://en.wikipedia.org/wiki/Melbourne"},
  {name:"布里斯班",name_en:"Brisbane",country:"澳大利亚",continent:"大洋洲",lat:-27.47,lon:153.03,salary:35000,rent:14000,meal:38,restaurant:110,price_per_sqm:5500,wiki:"https://en.wikipedia.org/wiki/Brisbane"},
  {name:"珀斯",name_en:"Perth",country:"澳大利亚",continent:"大洋洲",lat:-31.95,lon:115.86,salary:38000,rent:15000,meal:40,restaurant:115,price_per_sqm:5000,wiki:"https://en.wikipedia.org/wiki/Perth,_Western_Australia"},
  {name:"奥克兰",name_en:"Auckland",country:"新西兰",continent:"大洋洲",lat:-36.85,lon:174.76,salary:35000,rent:14000,meal:38,restaurant:110,price_per_sqm:7000,wiki:"https://en.wikipedia.org/wiki/Auckland"},
  {name:"惠灵顿",name_en:"Wellington",country:"新西兰",continent:"大洋洲",lat:-41.29,lon:174.78,salary:35000,rent:13000,meal:38,restaurant:105,price_per_sqm:6000,wiki:"https://en.wikipedia.org/wiki/Wellington"},
  {name:"苏瓦",name_en:"Suva",country:"斐济",continent:"大洋洲",lat:-18.14,lon:178.44,salary:8000,rent:3500,meal:15,restaurant:40,price_per_sqm:1500,wiki:"https://en.wikipedia.org/wiki/Suva"},
  {name:"霍巴特",name_en:"Hobart",country:"澳大利亚",continent:"大洋洲",lat:-42.88,lon:147.33,salary:30000,rent:11000,meal:35,restaurant:95,price_per_sqm:4000,wiki:"https://en.wikipedia.org/wiki/Hobart"},
  {name:"阿德莱德",name_en:"Adelaide",country:"澳大利亚",continent:"大洋洲",lat:-34.93,lon:138.60,salary:32000,rent:12000,meal:35,restaurant:100,price_per_sqm:4500,wiki:"https://en.wikipedia.org/wiki/Adelaide"},
  {name:"堪培拉",name_en:"Canberra",country:"澳大利亚",continent:"大洋洲",lat:-35.28,lon:149.13,salary:40000,rent:15000,meal:40,restaurant:115,price_per_sqm:5500,wiki:"https://en.wikipedia.org/wiki/Canberra"},
  {name:"努美阿",name_en:"Noumea",country:"新喀里多尼亚",continent:"大洋洲",lat:-22.27,lon:166.45,salary:30000,rent:12000,meal:35,restaurant:100,price_per_sqm:4000,wiki:"https://en.wikipedia.org/wiki/Noum%C3%A9a"},
  {name:"帕皮提",name_en:"Papeete",country:"法属波利尼西亚",continent:"大洋洲",lat:-17.55,lon:-149.57,salary:25000,rent:10000,meal:30,restaurant:80,price_per_sqm:4000,wiki:"https://en.wikipedia.org/wiki/Papeete"},
];

// Country → continent mapping (handles Italian names from global.json)
const COUNTRY_TO_CONTINENT = {
  // 意大利语国家名映射
  "Portogallo":"欧洲","Spagna":"欧洲","Francia":"欧洲","Germania":"欧洲","Regno Unito":"欧洲",
  "Italia":"欧洲","Paesi Bassi":"欧洲","Svizzera":"欧洲","Austria":"欧洲","Belgio":"欧洲",
  "Grecia":"欧洲","Svezia":"欧洲","Norvegia":"欧洲","Danimarca":"欧洲","Finlandia":"欧洲",
  "Irlanda":"欧洲","Repubblica Ceca":"欧洲","Polonia":"欧洲","Ungheria":"欧洲","Romania":"欧洲",
  "Croazia":"欧洲","Estonia":"欧洲","Lituania":"欧洲","Lettonia":"欧洲","Slovacchia":"欧洲",
  "Slovenia":"欧洲","Bulgaria":"欧洲","Serbia":"欧洲","Bosnia ed Erzegovina":"欧洲",
  "Albania":"欧洲","Macedonia del Nord":"欧洲","Montenegro":"欧洲","Georgia":"欧洲",
  "Armenia":"欧洲","Moldavia":"欧洲","Bielorussia":"欧洲","Islanda":"欧洲","Lussemburgo":"欧洲",
  "Malta":"欧洲","Cipro":"欧洲","Finlandia":"欧洲",
  // 中文国家名
  "葡萄牙":"欧洲","西班牙":"欧洲","法国":"欧洲","德国":"欧洲","英国":"欧洲",
  "意大利":"欧洲","荷兰":"欧洲","瑞士":"欧洲","奥地利":"欧洲","比利时":"欧洲",
  "希腊":"欧洲","瑞典":"欧洲","挪威":"欧洲","丹麦":"欧洲","芬兰":"欧洲",
  "爱尔兰":"欧洲","捷克":"欧洲","波兰":"欧洲","匈牙利":"欧洲","罗马尼亚":"欧洲",
  "克罗地亚":"欧洲","爱沙尼亚":"欧洲","立陶宛":"欧洲","拉脱维亚":"欧洲","斯洛伐克":"欧洲",
  "斯洛文尼亚":"欧洲","保加利亚":"欧洲","塞尔维亚":"欧洲","波黑":"欧洲","黑山":"欧洲",
  "北马其顿":"欧洲","阿尔巴尼亚":"欧洲","格鲁吉亚":"欧洲","亚美尼亚":"欧洲","摩尔多瓦":"欧洲",
  "白俄罗斯":"欧洲","冰岛":"欧洲","卢森堡":"欧洲","马耳他":"欧洲","塞浦路斯":"欧洲",
  // 南美
  "Brasile":"南美洲","Argentina":"南美洲","Colombia":"南美洲","Perù":"南美洲","Cile":"南美洲",
  "Paraguay":"南美洲","Uruguay":"南美洲","Ecuador":"南美洲","Bolivia":"南美洲","Venezuela":"南美洲",
  "巴西":"南美洲","阿根廷":"南美洲","哥伦比亚":"南美洲","秘鲁":"南美洲","智利":"南美洲",
  "巴拉圭":"南美洲","乌拉圭":"南美洲","厄瓜多尔":"南美洲","玻利维亚":"南美洲","委内瑞拉":"南美洲",
  // 北美
  "Stati Uniti":"北美洲","Canada":"北美洲","Messico":"北美洲","Costa Rica":"北美洲",
  "Panama":"北美洲","Repubblica Dominicana":"北美洲","Cuba":"北美洲",
  "美国":"北美洲","加拿大":"北美洲","墨西哥":"北美洲","哥斯达黎加":"北美洲",
  "巴拿马":"北美洲","多米尼加":"北美洲","古巴":"北美洲",
  // 大洋洲
  "Australia":"大洋洲","Nuova Zelanda":"大洋洲","Figi":"大洋洲","Polinesia Francese":"大洋洲",
  "Nuova Caledonia":"大洋洲","澳大利亚":"大洋洲","新西兰":"大洋洲","斐济":"大洋洲",
  "法属波利尼西亚":"大洋洲","新喀里多尼亚":"大洋洲",
  // 非洲
  "Egitto":"非洲","Sudafrica":"非洲","Marocco":"非洲","Kenya":"非洲","Nigeria":"非洲",
  "Tanzania":"非洲","Ghana":"非洲","Etiopia":"非洲","Senegal":"非洲","Ruanda":"非洲",
  "Namibia":"非洲","Tunisia":"非洲","Maurizio":"非洲","Seicelle":"非洲",
  "埃及":"非洲","南非":"非洲","摩洛哥":"非洲","肯尼亚":"非洲","尼日利亚":"非洲",
  "坦桑尼亚":"非洲","加纳":"非洲","埃塞俄比亚":"非洲","塞内加尔":"非洲","卢旺达":"非洲",
  "纳米比亚":"非洲","突尼斯":"非洲","毛里求斯":"非洲","塞舌尔":"非洲",
  // 亚洲
  "Giappone":"亚洲","Corea del Sud":"亚洲","Cina":"亚洲","Singapore":"亚洲",
  "Hong Kong":"亚洲","Taiwan":"亚洲","Thailandia":"亚洲","Vietnam":"亚洲",
  "Indonesia":"亚洲","Malesia":"亚洲","Filippine":"亚洲","India":"亚洲",
  "Emirati Arabi Uniti":"亚洲","Turchia":"亚洲","Qatar":"亚洲","Israele":"亚洲",
  "Arabia Saudita":"亚洲","Kuwait":"亚洲","Bahrein":"亚洲","Oman":"亚洲",
  "Giordania":"亚洲","Libano":"亚洲","Sri Lanka":"亚洲","Nepal":"亚洲",
  "Myanmar":"亚洲","Laos":"亚洲","Cambogia":"亚洲","Bangladesh":"亚洲",
  "Pakistan":"亚洲","Iran":"亚洲","Iraq":"亚洲","Afghanistan":"亚洲",
  "日本":"亚洲","韩国":"亚洲","中国":"亚洲","新加坡":"亚洲",
  "香港":"亚洲","台湾":"亚洲","泰国":"亚洲","越南":"亚洲",
  "印尼":"亚洲","马来西亚":"亚洲","菲律宾":"亚洲","印度":"亚洲",
  "阿联酋":"亚洲","土耳其":"亚洲","卡塔尔":"亚洲","以色列":"亚洲",
  "沙特阿拉伯":"亚洲","科威特":"亚洲","巴林":"亚洲","阿曼":"亚洲",
  "约旦":"亚洲","黎巴嫩":"亚洲","斯里兰卡":"亚洲","尼泊尔":"亚洲",
  "缅甸":"亚洲","老挝":"亚洲","柬埔寨":"亚洲",
};

const CONTINENT_LABELS = {
  '全部':'🌍 全部','亚洲':'🌏 亚洲','欧洲':'🏰 欧洲',
  '北美洲':'🌎 北美','南美洲':'🌎 南美','非洲':'🌍 非洲','大洋洲':'🏝️ 大洋洲','中国':'🇨🇳 中国'
};

const CONTINENT_CAMERA = {
  '全部':    {lat:20,  lon:0,   dist:3.5},
  '亚洲':    {lat:35,  lon:105, dist:2.5},
  '欧洲':    {lat:50,  lon:10,  dist:2.2},
  '北美洲': {lat:40,  lon:-100,dist:2.5},
  '南美洲': {lat:-15, lon:-60, dist:2.5},
  '非洲':    {lat:0,   lon:20,  dist:2.8},
  '大洋洲': {lat:-25, lon:135, dist:2.5},
  '中国':    {lat:35,  lon:105, dist:2.0},
};

let allCities = [...FALLBACK_CITIES];
let filteredCities = [...allCities];
let activeContinent = '全部';
let raycaster, mouse;
let markers = [];
let globe, scene, camera, renderer, controls;

// ── Init ─────────────────────────────────────────────────────────────────────
function init() {
  setupThree();
  loadCityData();
  setupEventListeners();
  animate();
  setTimeout(() => document.getElementById('loading').classList.add('hidden'), 1500);
}

// ── Three.js ─────────────────────────────────────────────────────────────────
function setupThree() {
  const container = document.getElementById('canvas-container');
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0a1a);
  camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
  camera.position.set(0, 0, 3.5);
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);
  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.rotateSpeed = 0.5;
  controls.minDistance = 1.3;
  controls.maxDistance = 8;
  controls.enablePan = false;
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const dirLight = new THREE.DirectionalLight(0xfff5e0, 0.8);
  dirLight.position.set(5, 3, 5);
  scene.add(dirLight);
  addStars();
  addGlobe();
  // Init raycaster and mouse
  raycaster = new THREE.Raycaster();
  mouse = new THREE.Vector2();
  window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  });
}

function addStars() {
  const geo = new THREE.BufferGeometry();
  const count = 3000;
  const pos = new Float32Array(count * 3);
  for (let i = 0; i < count * 3; i++) pos[i] = (Math.random() - 0.5) * 200;
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  scene.add(new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.15 })));
}

function addGlobe() {
  globe = new THREE.Group();
  scene.add(globe);
  const textureLoader = new THREE.TextureLoader();
  textureLoader.load(
    'textures/earth_day.jpg',
    (texture) => {
      texture.colorSpace = THREE.SRGBColorSpace;
      const earth = new THREE.Mesh(
        new THREE.SphereGeometry(1, 64, 64),
        new THREE.MeshPhongMaterial({ map: texture, bumpScale: 0.02, specular: new THREE.Color(0x111111), shininess: 5 })
      );
      globe.add(earth);
    },
    undefined,
    () => {
      globe.add(new THREE.Mesh(
        new THREE.SphereGeometry(1, 64, 64),
        new THREE.MeshPhongMaterial({ color: 0x2266aa, specular: 0x222222, shininess: 10 })
      ));
    }
  );
  // Atmosphere glow
  const atmo = new THREE.Mesh(
    new THREE.SphereGeometry(1.04, 64, 64),
    new THREE.MeshPhongMaterial({ color: 0x4fc3f7, transparent: true, opacity: 0.08, side: THREE.BackSide })
  );
  globe.add(atmo);
  addCityMarkers();
}

function addCityMarkers() {
  markers.forEach(m => globe.remove(m));
  markers = [];
  filteredCities.forEach(city => {
    if (city.lat == null || city.lon == null) return;
    const { x, y, z } = latLonTo3D(city.lat, city.lon, 1.012);
    const isCN = city.country === '中国';
    const color = isCN ? 0xff6b6b : 0x64b5f6;
    const size = isCN ? 0.020 : 0.015;
    const marker = new THREE.Mesh(
      new THREE.SphereGeometry(size, 8, 8),
      new THREE.MeshBasicMaterial({ color })
    );
    marker.position.set(x, y, z);
    marker.userData = city;
    // Ring
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(size * 1.4, size * 1.8, 16),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.4, side: THREE.DoubleSide })
    );
    ring.lookAt(x * 2, y * 2, z * 2);
    marker.add(ring);
    globe.add(marker);
    markers.push(marker);
  });
}

function latLonTo3D(lat, lon, r) {
  const phi = (90 - lat) * Math.PI / 180;
  const theta = (lon + 180) * Math.PI / 180;
  return { x: -r * Math.sin(phi) * Math.cos(theta), y: r * Math.cos(phi), z: r * Math.sin(phi) * Math.sin(theta) };
}

// ── Data loading ──────────────────────────────────────────────────────────────
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
    // CN cities: { cities: { "北京": { "平均税后月薪": ..., ... } } }
    if (cnData && cnData.cities) {
      Object.entries(cnData.cities).forEach(([name, d]) => {
        const g = geoMap[name] || {};
        cities.push({
          name, name_en: g.en_name || name,
          country: '中国', continent: '亚洲',
          lat: g.lat != null ? g.lat : null, lon: g.lon != null ? g.lon : null,
          salary: d['平均税后月薪'] || d['税后月薪'],
          rent: d['市中心一居室月租'] || d['一居室月租'],
          meal: d['普通餐厅一餐'],
          restaurant: d['普通餐厅一餐'],
          price_per_sqm: d['二手房均价'] || d['新房均价'],
          description: '',
          wiki: `https://en.wikipedia.org/wiki/${encodeURIComponent(g.en_name || name)}`,
          website: null
        });
      });
    }
    // Global cities: { cities: [{ city_en, city_zh, country_zh, ... }] }
    if (globalData && globalData.cities) {
      globalData.cities.forEach(d => {
        const countryCN = d.country_zh || '';
        const continent = COUNTRY_TO_CONTINENT[countryCN] || '其他';
        const g = geoMap[d.city_en] || {};
        cities.push({
          name: d.city_zh || d.city_en || '',
          name_en: d.city_en || '',
          country: countryCN,
          continent,
          lat: g.lat != null ? g.lat : null, lon: g.lon != null ? g.lon : null,
          salary: d.rent_1br_cny ? d.rent_1br_cny * 0.8 : null,
          rent: d.rent_1br_cny,
          meal: d.meal_cny,
          restaurant: d.meal_cny ? d.meal_cny * 2 : null,
          price_per_sqm: null,
          description: '',
          wiki: `https://en.wikipedia.org/wiki/${encodeURIComponent(d.city_en || '')}`,
          website: null
        });
      });
    }
    // 补充：中国其他地级市（在 cities_geo 里但 cn_api/cnData 里没有的）
    const existingCN = new Set(cities.filter(c => c.country === '中国').map(c => c.name));
    Object.entries(geoMap).forEach(([zh, g]) => {
      if (g.country_zh !== '中国') return;  // 仅中国
      if (existingCN.has(zh)) return;       // 已加
      cities.push({
        name: zh, name_en: g.en_name || zh,
        country: '中国', continent: '亚洲',
        lat: g.lat, lon: g.lon,
        salary: null, rent: null, meal: null, restaurant: null, price_per_sqm: null,
        description: '该城市的成本数据待补充。',
        wiki: `https://en.wikipedia.org/wiki/${encodeURIComponent(g.en_name || zh)}`,
        website: null
      });
    });
    if (cities.length > 0) allCities = cities;
  } catch(e) {
    console.warn('API load failed, using fallback:', e);
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

// ── Events ────────────────────────────────────────────────────────────────────
function setupEventListeners() {
  document.querySelectorAll('.cont-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.cont-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeContinent = btn.dataset.continent;
      filteredCities = filterCities();
      updateCityCount();
      addCityMarkers();
      flyToContinent(activeContinent);
    });
  });

  const searchInput = document.getElementById('search-input');
  const suggestionsEl = document.getElementById('suggestions');

  searchInput.addEventListener('input', () => {
    const q = searchInput.value.trim().toLowerCase();
    if (q.length > 0) {
      const matches = allCities.filter(c =>
        c.name.toLowerCase().includes(q) || (c.name_en && c.name_en.toLowerCase().includes(q)) || c.country.toLowerCase().includes(q)
      ).slice(0, 8);
      suggestionsEl.innerHTML = matches.map(c => `
        <div class="sug-item" data-name="${c.name}" data-en="${c.name_en||''}">
          <span class="sug-name">${c.name}${c.name_en ? ' / ' + c.name_en : ''}</span>
          <span class="sug-country">${c.country}</span>
        </div>`).join('');
      suggestionsEl.classList.toggle('show', matches.length > 0);
    } else {
      suggestionsEl.classList.remove('show');
    }
  });

  searchInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const q = searchInput.value.trim().toLowerCase();
      const city = allCities.find(c => c.name.toLowerCase() === q || (c.name_en && c.name_en.toLowerCase() === q));
      if (city) { flyToCity(city); showCityPanel(city); }
      suggestionsEl.classList.remove('show');
    }
    if (e.key === 'Escape') { suggestionsEl.classList.remove('show'); searchInput.blur(); }
  });

  suggestionsEl.addEventListener('click', e => {
    const item = e.target.closest('.sug-item');
    if (item) {
      const city = allCities.find(c => c.name === item.dataset.name);
      if (city) { flyToCity(city); showCityPanel(city); searchInput.value = city.name; }
      suggestionsEl.classList.remove('show');
    }
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('#search-wrap')) suggestionsEl.classList.remove('show');
  });

  document.getElementById('panel-close').addEventListener('click', closeCityPanel);

  const tooltip = document.getElementById('tooltip');
  renderer.domElement.addEventListener('click', e => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(markers);
    if (hits.length > 0) {
      const city = hits[0].object.userData;
      flyToCity(city); showCityPanel(city);
    }
  });

  renderer.domElement.addEventListener('mousemove', e => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(markers);
    if (hits.length > 0) {
      const city = hits[0].object.userData;
      tooltip.textContent = city.name + ' (' + city.country + ')';
      tooltip.style.display = 'block';
      tooltip.style.left = (e.clientX - rect.left) + 'px';
      tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
      renderer.domElement.style.cursor = 'pointer';
    } else {
      tooltip.style.display = 'none';
      renderer.domElement.style.cursor = 'default';
    }
  });
}

// ── Fly to ────────────────────────────────────────────────────────────────────
function flyToContinent(c) {
  const p = CONTINENT_CAMERA[c];
  if (!p) return;
  animateCamera(p.lat, p.lon, p.dist);
}

function flyToCity(city) {
  if (city.lat != null) animateCamera(city.lat, city.lon, 1.8);
  else flyToContinent(city.continent === '其他' ? '全部' : city.continent);
}

function animateCamera(lat, lon, dist) {
  const target = latLonTo3D(lat, lon, dist);
  const start = { x: camera.position.x, y: camera.position.y, z: camera.position.z };
  const t0 = performance.now();
  const dur = 1200;
  function step() {
    const t = Math.min((performance.now() - t0) / dur, 1);
    const ease = t < 0.5 ? 2*t*t : -1+(4-2*t)*t;
    camera.position.x = start.x + (target.x - start.x) * ease;
    camera.position.y = start.y + (target.y - start.y) * ease;
    camera.position.z = start.z + (target.z - start.z) * ease;
    camera.lookAt(0, 0, 0);
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ── City panel ────────────────────────────────────────────────────────────────
function showCityPanel(city) {
  const isCN = city.country === '中国';
  const panel = document.getElementById('city-panel');
  const content = document.getElementById('panel-content');
  const fmt = n => n != null ? '¥' + Math.round(n).toLocaleString() : '—';
  const fmtSqm = n => n != null ? '¥' + Math.round(n).toLocaleString() + '/㎡' : '—';
  const hasData = city.salary != null || city.rent != null || city.meal != null || city.price_per_sqm != null;
  const costSection = hasData ? `
    <div class="panel-section">
      <div class="panel-section-title">💰 生活成本</div>
      <div class="stat-grid">
        <div class="stat-item"><div class="stat-label">平均月薪</div><div class="stat-value">${fmt(city.salary)}</div></div>
        <div class="stat-item"><div class="stat-label">平均房租</div><div class="stat-value">${fmt(city.rent)}</div></div>
        <div class="stat-item"><div class="stat-label">快餐/人均</div><div class="stat-value">${fmt(city.meal)}</div></div>
        <div class="stat-item"><div class="stat-label">餐厅/人均</div><div class="stat-value">${fmt(city.restaurant)}</div></div>
        <div class="stat-item full"><div class="stat-label">房价 (每平米)</div><div class="stat-value">${fmtSqm(city.price_per_sqm)}</div></div>
      </div>
    </div>` : `
    <div class="panel-section">
      <div class="panel-section-title">💰 生活成本</div>
      <div class="panel-desc" style="color: rgba(255,255,255,0.5);">📊 该城市的成本数据待补充。点击下方维基百科了解更多信息。</div>
    </div>`;
  content.innerHTML = `
    <div class="panel-header">
      <div class="panel-city-name">${city.name}</div>
      <div class="panel-country">${city.country}${city.name_en && city.name_en !== city.name ? ' · ' + city.name_en : ''}</div>
      <span class="panel-badge ${isCN ? 'badge-cn' : 'badge-global'}">${isCN ? '🇨🇳 中国城市' : '🌐 全球城市'}</span>
    </div>
    ${costSection}
    ${city.description && hasData ? `<div class="panel-section"><div class="panel-section-title">📖 城市介绍</div><div class="panel-desc">${city.description}</div></div>` : ''}
    <div class="panel-section">
      <div class="panel-section-title">🔗 链接</div>
      ${city.wiki ? `<a class="panel-link" href="${city.wiki}" target="_blank" rel="noopener">📚 Wikipedia</a>` : ''}
      ${city.website ? `<a class="panel-link" href="${city.website}" target="_blank" rel="noopener">🏛️ 官网</a>` : ''}
    </div>`;
  panel.classList.add('open');
}

function closeCityPanel() {
  document.getElementById('city-panel').classList.remove('open');
}

function updateCityCount() {
  document.getElementById('city-count').textContent = filteredCities.length + ' 个城市';
}

// ── Render loop ───────────────────────────────────────────────────────────────
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  if (!window.__noSpin) globe.rotation.y += 0.0002;
  renderer.render(scene, camera);
}

window.addEventListener('DOMContentLoaded', init);

// URL 参数支持：?view=china 启动后自动飞到中国并启用中国筛选
window.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('spin') === '0') window.__noSpin = true;
    const view = params.get('view');
    if (view === 'china' || view === '中国') {
      activeContinent = '中国';
      document.querySelectorAll('.cont-btn').forEach(b => b.classList.toggle('active', b.dataset.continent === '中国'));
      filteredCities = filterCities();
      updateCityCount();
      addCityMarkers();
      flyToContinent('中国');
    } else if (view) {
      flyToContinent(view);
    }
  }, 2500);
});
