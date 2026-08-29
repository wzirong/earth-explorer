#!/usr/bin/env python3
"""M31 仙女座 - 真实数据版
底图: NASA/ESA Hubble M31 拼接 (cdn.spacetelescope.org)
标注: 真实伴星系位置 (M32, M110, NGC 147, NGC 185, IC 10 等)
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os, json

W = H = 2048
CX, CY = W // 2, H // 2
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')
OUT_FILE = os.path.join(OUT_DIR, 'andromeda.png')
M31_HST = '/tmp/cosmos_real/m31_nasa3.jpg'


def get_font(size):
    paths = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/Helvetica.ttc',
    ]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()


F_TINY = get_font(22)
F_SMALL = get_font(28)
F_MED = get_font(36)
F_LARGE = get_font(52)
F_TITLE = get_font(86)
F_SCALE = get_font(32)


def hms2deg(hms):
    p = hms.strip().split()
    if len(p) != 3: return None
    try: h, m, s = [float(x) for x in p]; return (h + m/60 + s/3600) * 15
    except: return None


def dms2deg(dms):
    s = dms.strip(); sign = 1
    if s.startswith('-'): sign = -1; s = s[1:]
    elif s.startswith('+'): s = s[1:]
    p = s.split()
    if len(p) != 3: return None
    try: d, m, sc = [float(x) for x in p]; return sign * (d + m/60 + sc/3600)
    except: return None


def load_m31_satellites():
    """从 cosmicflows local group data 取 M31 附近卫星"""
    sats = []
    with open('/tmp/cosmos_real/local_group.tsv') as f:
        line = f.readline()
        while line and not line.startswith('Name\t'): line = f.readline()
        f.readline(); f.readline()
        import re
        for row in f:
            row = row.strip()
            if not row or row.startswith('#'): continue
            parts = re.split(r'\t+', row)
            if len(parts) < 4: continue
            try: dist = float(parts[3])
            except: continue
            ra = hms2deg(parts[1]); dec = dms2deg(parts[2])
            if ra is None or dec is None: continue
            name = parts[0].strip()
            # M31 附近卫星 (d < 1 Mpc, 在 M31 方向 ±15°)
            if name in ('NGC0224', 'NGC0221', 'NGC0205', 'NGC0147', 'NGC0185',
                       'IC0010', 'IC1613', 'NGC6822', 'LGS3', 'And2', 'And3',
                       'And5', 'And6', 'And7', 'And9', 'And10', 'And11', 'And12',
                       'And13', 'And14', 'And15', 'And16', 'And17', 'And18', 'And19',
                       'And20', 'And21', 'And22', 'And23', 'And24', 'And25', 'And26', 'And27',
                       'CasdSph', 'LMC', 'SMC', 'WLM', 'Phoenix', 'Tucana',
                       'Cetus', 'DDO210', 'ESO594-004'):
                sats.append((name, ra, dec, dist))
    return sats


def draw_info_panel(img, draw):
    """顶部信息面板"""
    panel_h = 180
    overlay = Image.new('RGBA', (W, panel_h), (0, 0, 0, 180))
    img.paste(overlay, (0, 0), overlay)
    draw2 = ImageDraw.Draw(img, 'RGBA')
    # 标题
    draw2.text((40, 30), '仙女座星系 (M31 · Andromeda)', fill=(255, 230, 180, 255), font=F_TITLE)
    sub = 'M31 · 银河系最近的大型旋涡星系 · 距离 2.5 Mly (770 kpc) · 即将与银河系合并'
    tw = draw2.textlength(sub, font=F_MED)
    draw2.rectangle([40-4, 130, 40+tw+8, 168], fill=(0, 0, 0, 180))
    draw2.text((40, 132), sub, fill=(180, 200, 230, 230), font=F_MED)
    # 右上角数据
    facts = [
        ('质量', '1.5 × 10¹² M☉ (含暗物质)'),
        ('恒星数', '~1 万亿 (银河系 ~3 倍)'),
        ('已知卫星', '39 个矮星系 (本图可识别)'),
        ('视星等', '3.4 (肉眼可见)'),
    ]
    fx = W - 700
    for i, (k, v) in enumerate(facts):
        y = 30 + i * 38
        draw2.text((fx, y), k, fill=(255, 200, 100, 255), font=F_SMALL)
        draw2.text((fx + 130, y), v, fill=(220, 230, 255, 230), font=F_SMALL)


def draw_hubble_bg(img, draw):
    """哈勃真实图作底图"""
    if not os.path.exists(M31_HST):
        return
    # Hubble M31 是 1280x409, 倾斜 ~77°, 显示整个盘
    hst = Image.open(M31_HST).convert('RGBA')
    # 旋转 -35° 让盘更水平 (原图是 38° 倾角)
    hst_rot = hst.rotate(-35, expand=True, resample=Image.BICUBIC)
    # 缩放到合适大小 (画布宽 1800px)
    target_w = 1800
    ratio = target_w / hst_rot.width
    target_h = int(hst_rot.height * ratio)
    hst_resized = hst_rot.resize((target_w, target_h), Image.LANCZOS)
    # 居中放置
    px = (W - target_w) // 2
    py = CY - target_h // 2 + 100  # 向下偏一点避开顶部 panel
    # 加暗化叠层
    dark = Image.new('RGBA', hst_resized.size, (0, 0, 0, 40))
    hst_resized = Image.alpha_composite(hst_resized, dark)
    img.paste(hst_resized, (px, py), hst_resized)
    # 边框
    draw2 = ImageDraw.Draw(img, 'RGBA')
    draw2.rectangle([px, py, px+target_w, py+target_h], outline=(120, 150, 200, 180), width=2)
    # 底部标签 (上移到图片顶上方, 避免与事实面板重叠)
    cap = '底图: NASA/ESA Hubble Space Telescope · Andromeda Galaxy M31'
    cw = draw2.textlength(cap, font=F_TINY)
    cap_y = py - 32
    draw2.rectangle([(W-cw)//2-4, cap_y-6, (W+cw)//2+4, cap_y+18], fill=(0, 0, 0, 200))
    draw2.text(((W-cw)//2, cap_y), cap, fill=(180, 200, 230, 230), font=F_TINY)
    return px, py, target_w, target_h


def draw_satellites(img, draw, satellites):
    """标注 M31 真实伴星系"""
    # M31 中心 (10.68°, 41.27°)
    M31_RA, M31_DEC = 10.68, 41.27
    # 简易投影: 把 RA/Dec 转换为相对 M31 的角距离
    # 用等距投影: dx = (RA - M31_RA) * cos(Dec), dy = (Dec - M31_DEC)
    # 1° ≈ 70 px (覆盖画面)
    DEG_TO_PX = 25  # 25 像素 / 度
    for name, ra, dec, dist in satellites:
        if name == 'NGC0224':  # M31 本身跳过
            continue
        dx = (ra - M31_RA) * math.cos(math.radians(dec)) * DEG_TO_PX
        dy = (dec - M31_DEC) * DEG_TO_PX
        # M31 中心在画面中心
        x = CX + dx
        y = CY + dy + 100
        # 距离标注
        d_kpc = dist * 1000  # Mpc -> kpc
        if d_kpc < 200:
            color = (255, 100, 100, 230); size = 8  # 极近卫星
        elif d_kpc < 500:
            color = (255, 200, 100, 220); size = 6
        else:
            color = (180, 200, 230, 200); size = 5
        # 画圈
        draw.ellipse([x-size-2, y-size-2, x+size+2, y+size+2], outline=color, width=2)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=(255, 255, 255, 200))
        # 著名星系命名
        NAMES = {
            'NGC0221': 'M32', 'NGC0205': 'M110', 'NGC0147': 'NGC 147',
            'NGC0185': 'NGC 185', 'IC0010': 'IC 10', 'IC1613': 'IC 1613',
            'NGC6822': 'NGC 6822', 'And2': 'And II', 'And3': 'And III',
            'And5': 'And V', 'And6': 'And VI', 'And7': 'And VII',
            'And9': 'And IX', 'And10': 'And X', 'And11': 'And XI',
            'And12': 'And XII', 'And13': 'And XIII', 'And14': 'And XIV',
            'And15': 'And XV', 'And16': 'And XVI', 'And17': 'And XVII',
            'And18': 'And XVIII', 'And19': 'And XIX', 'And20': 'And XX',
            'And21': 'And XXI', 'And22': 'And XXII', 'And23': 'And XXIII',
            'And24': 'And XXIV', 'And25': 'And XXV', 'And26': 'And XXVI',
            'And27': 'And XXVII', 'LGS3': 'LGS 3', 'CasdSph': 'Cas dSph',
            'LMC': 'LMC', 'SMC': 'SMC', 'WLM': 'WLM',
            'Phoenix': 'Phoenix', 'Tucana': 'Tucana', 'Cetus': 'Cetus',
        }
        label = NAMES.get(name, name)
        # 标签 (引线 + 框)
        if dx > 50:
            tx, ty = x + size + 8, y - 14
            anchor = 'left'
        elif dx < -50:
            tx, ty = x - size - 8 - 80, y - 14
            anchor = 'right'
        else:
            tx, ty = x + size + 8, y + 8
            anchor = 'left'
        tw = draw.textlength(label, font=F_TINY)
        if anchor == 'right':
            tx = x - size - 8 - tw
        # 引线
        draw.line([(x, y), (tx + tw//2 if anchor == 'left' else tx + tw//2, ty + 14)],
                  fill=color, width=1)
        draw.rectangle([tx-4, ty-6, tx+tw+8, ty+20], fill=(0, 0, 0, 230))
        draw.text((tx, ty), label, fill=color, font=F_TINY)


def draw_mw_position(img, draw):
    """标注银河系位置 (相对 M31)
    箭头从画面内中心向左上指出, 标签在画面内
    """
    # 终点 (银河系方向, 在画面内上区)
    ex, ey = 250, 280
    # 起点 (M31 主体内, 表示从 M31 中心出发指向银河系)
    sx, sy = CX, CY + 100
    # 箭头
    draw.line([(sx, sy), (ex, ey)], fill=(255, 220, 120, 200), width=4)
    # 箭头头
    draw.polygon([(ex, ey), (ex + 25, ey - 12), (ex + 12, ey + 18)],
                 fill=(255, 220, 120, 240))
    # 标签 (放在终点附近, 不被裁切)
    label = '银河系\n(我们, 770 kpc 外)'
    tw = draw.textlength('(我们, 770 kpc 外)', font=F_MED)
    draw.rectangle([ex - 8, ey - 16, ex + tw + 16, ey + 60], fill=(0, 0, 0, 230))
    draw.text((ex, ey - 12), '银河系', fill=(255, 220, 120, 240), font=F_MED)
    draw.text((ex, ey + 26), '(我们, 770 kpc 外)', fill=(255, 220, 120, 240), font=F_SMALL)


def draw_m32_m110(img, draw):
    """专门标注 M32 和 M110 (它们在 M31 盘内, 需要引线拉出来)"""
    # M32 实际位置: NGC0221 (10.67, 40.87), M31 中心 10.68, 41.27
    # 在画面中几乎重叠 M31 核心
    M31_CX = CX
    M31_CY = CY + 100
    DEG_TO_PX = 25
    # M32 (NGC0221)
    m32_x = M31_CX + (10.67 - 10.68) * math.cos(math.radians(40.87)) * DEG_TO_PX
    m32_y = M31_CY + (40.87 - 41.27) * DEG_TO_PX
    # M110 (NGC0205)
    m110_x = M31_CX + (10.09 - 10.68) * math.cos(math.radians(41.69)) * DEG_TO_PX
    m110_y = M31_CY + (41.69 - 41.27) * DEG_TO_PX
    # 引线 + 框
    for name, sx, sy, ex, ey, col in [
        ('M32 (NGC 221)', m32_x, m32_y, M31_CX - 650, M31_CY - 100, (255, 100, 100)),
        ('M110 (NGC 205)', m110_x, m110_y, M31_CX - 600, M31_CY + 200, (255, 180, 100)),
    ]:
        # 引线
        draw.line([(ex, ey), (sx, sy)], fill=col + (220,), width=2)
        # 终点画圈
        draw.ellipse([sx-5, sy-5, sx+5, sy+5], outline=col + (255,), width=2)
        draw.ellipse([sx-3, sy-3, sx+3, sy+3], fill=(255, 255, 255, 255))
        # 标签框
        tw = draw.textlength(name, font=F_MED)
        draw.rectangle([ex - 8, ey - 8, ex + tw + 12, ey + 36], fill=(0, 0, 0, 230))
        draw.text((ex, ey), name, fill=col + (255,), font=F_MED)


def draw_facts_panel(img, draw):
    """底部信息栏"""
    panel_h = 200
    overlay = Image.new('RGBA', (W, panel_h), (0, 0, 0, 200))
    img.paste(overlay, (0, H - panel_h), overlay)
    draw2 = ImageDraw.Draw(img, 'RGBA')
    facts = [
        ('直径', '22 万光年 (~银河系 1.5×)'),
        ('类型', 'SA(s)b 旋涡星系'),
        ('距离', '2.54 Mly (780 kpc)'),
        ('径向速度', '−300 km/s (在靠近我们)'),
        ('未来', '~45 亿年后与银河系合并 (Milkomeda)'),
        ('M32/M110', '位于 HST 视野外 (图右上区域)'),
    ]
    col_w = W // len(facts)
    for i, (k, v) in enumerate(facts):
        x = i * col_w + 20
        y = H - panel_h + 30
        draw2.text((x, y), k, fill=(255, 200, 100, 255), font=F_LARGE)
        # 自动换行
        words = v.split()
        line = ''
        ly = y + 60
        for w in words:
            test = line + ' ' + w if line else w
            if draw2.textlength(test, font=F_SMALL) > col_w - 30:
                draw2.text((x, ly), line, fill=(220, 230, 255, 230), font=F_SMALL)
                line = w
                ly += 36
            else:
                line = test
        if line:
            draw2.text((x, ly), line, fill=(220, 230, 255, 230), font=F_SMALL)


def main():
    sats = load_m31_satellites()
    print(f'[M31] 伴星系 (含本星系群 d<2.5 Mpc): {len(sats)}')

    img = Image.new('RGB', (W, H), (2, 3, 8))
    draw = ImageDraw.Draw(img, 'RGBA')

    # 顶部信息
    draw_info_panel(img, draw)

    # Hubble 真实图底图
    draw_hubble_bg(img, draw)

    # 伴星系标注
    draw_satellites(img, draw, sats)

    # 银河系箭头
    draw_mw_position(img, draw)

    # M32 / M110 特殊标注 (在 M31 盘内)
    draw_m32_m110(img, draw)

    # 底部事实面板
    draw_facts_panel(img, draw)

    img.save(OUT_FILE)
    print(f'[M31] saved: {OUT_FILE} ({os.path.getsize(OUT_FILE) // 1024} KB)')


if __name__ == '__main__':
    main()