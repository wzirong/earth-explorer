#!/usr/bin/env python3
"""本星系群 v3 - 更亮更丰富
数据: McConnachie 2012 (101 颗, 含 MW 卫星 + M31 伴星系 + 外围) + Cosmicflows-2 (73 颗) 合并去重
改进: 星系点加径向光晕 (glow), 尺寸/亮度提升, M31/M33 强化 (不加虚假背景星)
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os, json, re, random

W = H = 2048
CX, CY = W // 2, H // 2
PROJECTION_RADIUS_PX = CY - 80  # 944
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')
OUT_FILE = os.path.join(OUT_DIR, 'local_group.png')


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


F_TINY = get_font(20)
F_SMALL = get_font(28)
F_MED = get_font(36)
F_LARGE = get_font(48)
F_TITLE = get_font(80)
F_SCALE = get_font(30)


def norm_key(name):
    s = re.sub(r'[^A-Z0-9]', '', name.upper())
    s = re.sub(r'(NGC|IC|UGC|UGCA|ESO|DDO|KKR|KKH|UKS)(0+)(\d)', r'\1\3', s)
    return s


def load_galaxies():
    """McConnachie 2012 + Cosmicflows-2 合并, 返回 [(name, ra, dec, d_mpc)]"""
    mcc = json.load(open('/tmp/mcc_src/mcc_merged.json'))
    cf2 = json.load(open('/tmp/cosmos_real/local_group_real.json'))  # [name, ra, dec, d_mpc]

    galaxies = {}
    for m in mcc:
        if not m['d_kpc']:
            continue
        if m['norm'] == 'MilkyWay':
            continue
        galaxies[norm_key(m['norm'])] = [m['name'].split(' (')[0], m['ra'], m['dec'], m['d_kpc'] / 1000.0]
    # Cosmicflows-2 补充 (McConnachie 没有的)
    for name, ra, dec, d in cf2:
        k = norm_key(name)
        if k not in galaxies:
            galaxies[k] = [name, ra, dec, d]
    out = list(galaxies.values())
    # 去重: 坐标太近的 (M31 系列别名)
    return out


def sphere_project(ra_deg, dec_deg, d_mpc, max_d=3.0):
    MIN_VISIBLE_MPC = 0.03
    if d_mpc > max_d: return None
    d_use = max(d_mpc, MIN_VISIBLE_MPC)
    r_pix = PROJECTION_RADIUS_PX * math.sqrt(d_use / max_d)
    x = CX + r_pix * math.cos(math.radians(dec_deg)) * math.sin(math.radians(ra_deg))
    y = CY - r_pix * math.sin(math.radians(dec_deg))
    return x, y


def in_disk(x, y):
    return (x - CX) ** 2 + (y - CY) ** 2 <= PROJECTION_RADIUS_PX ** 2


def draw_background_grid(draw):
    gal_north_ra = math.radians(192.86)
    incl = math.radians(62.87)
    gal_north_ra_deg = 192.86
    for l_deg in [0, 90, 180, 270]:
        pts = []
        for b_deg in range(-89, 90, 5):
            sin_dec = math.sin(math.radians(b_deg)) * math.cos(incl) + \
                      math.cos(math.radians(b_deg)) * math.sin(incl) * math.sin(math.radians(l_deg) - gal_north_ra)
            dec = math.degrees(math.asin(sin_dec))
            ra_offset = math.degrees(math.atan2(math.cos(incl) * math.sin(math.radians(l_deg) - gal_north_ra),
                                                math.cos(math.radians(l_deg) - gal_north_ra)))
            ra = (gal_north_ra_deg - 90 + ra_offset) % 360
            pt = sphere_project(ra, dec, 3.0)
            if pt and in_disk(*pt):
                pts.append(pt)
        if len(pts) > 1:
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i+1]], fill=(70, 95, 130, 60), width=1)
    # 银道面带
    pts_pos = []; pts_neg = []
    for l_deg in range(0, 721, 2):
        l = math.radians(l_deg / 2)
        for b_deg in [15, -15]:
            sin_dec = math.sin(math.radians(b_deg)) * math.cos(incl) + \
                      math.cos(math.radians(b_deg)) * math.sin(incl) * math.sin(l - gal_north_ra)
            dec = math.degrees(math.asin(sin_dec))
            ra_offset = math.degrees(math.atan2(math.cos(incl) * math.sin(l - gal_north_ra),
                                                math.cos(l - gal_north_ra)))
            ra = (gal_north_ra_deg - 90 + ra_offset) % 360
            pt = sphere_project(ra, dec, 3.0)
            if pt and in_disk(*pt):
                if b_deg > 0: pts_pos.append(pt)
                else: pts_neg.append(pt)
            break
    if len(pts_pos) > 1 and len(pts_neg) > 1:
        poly = pts_pos + list(reversed(pts_neg))
        for _ in range(2):
            draw.polygon(poly, fill=(0, 0, 0, 80))
    draw.ellipse([CX - PROJECTION_RADIUS_PX, CY - PROJECTION_RADIUS_PX,
                  CX + PROJECTION_RADIUS_PX, CY + PROJECTION_RADIUS_PX],
                 outline=(90, 125, 170, 200), width=3)


def draw_background_stars(img, draw):
    """微弱背景星点 (模拟深场遥远星系, 不喧宾夺主)"""
    random.seed(670488)
    n = 1500
    for _ in range(n):
        while True:
            x = random.uniform(0, W - 1); y = random.uniform(0, H - 1)
            if (x - CX) ** 2 + (y - CY) ** 2 <= (PROJECTION_RADIUS_PX - 4) ** 2:
                break
        v = random.choice([16, 22, 30, 40, 52, 68])
        r = random.choice([0.6, 0.8, 1.0, 1.3, 1.5])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(v, v, v + 2, 255))


def draw_filaments(draw, galaxies):
    """Delaunay filament (近场) - 更亮一点"""
    from scipy.spatial import Delaunay
    pts_2d = []; pt_indices = []
    for i, (name, ra, dec, d) in enumerate(galaxies):
        if d > 1.5: continue
        pt = sphere_project(ra, dec, d, max_d=3.0)
        if pt and in_disk(*pt):
            pts_2d.append(pt); pt_indices.append(i)
    if len(pts_2d) < 3: return
    tri = Delaunay(pts_2d)
    edges = set()
    for simplex in tri.simplices:
        for i in range(3):
            a, b = simplex[i], simplex[(i+1) % 3]
            edges.add((min(a, b), max(a, b)))
    edge_list = [(a, b, math.sqrt((pts_2d[a][0]-pts_2d[b][0])**2 + (pts_2d[a][1]-pts_2d[b][1])**2))
                 for a, b in edges]
    edge_list.sort(key=lambda x: x[2])
    for a, b, l in edge_list:
        if l > 80: continue
        p1 = pts_2d[a]; p2 = pts_2d[b]
        mx = (p1[0] + p2[0])/2 + (hash((a, b)) % 10 - 5)
        my = (p1[1] + p2[1])/2 + (hash((b, a)) % 10 - 5)
        steps = 6
        prev_x, prev_y = p1
        for s in range(1, steps+1):
            t = s/steps
            bx = (1-t)**2*p1[0] + 2*(1-t)*t*mx + t**2*p2[0]
            by = (1-t)**2*p1[1] + 2*(1-t)*t*my + t**2*p2[1]
            draw.line([(prev_x, prev_y), (bx, by)], fill=(150, 210, 250, 130), width=2)
            prev_x, prev_y = bx, by


def galaxy_style(d):
    """距离 -> (核心尺寸, 核心颜色, glow 半径, glow 强度)"""
    if d < 0.1:
        return 11, (255, 240, 210, 255), 44, 180
    elif d < 0.3:
        return 9, (255, 230, 190, 250), 38, 160
    elif d < 0.8:
        return 7, (252, 230, 195, 240), 30, 140
    elif d < 1.5:
        return 6, (225, 225, 245, 225), 24, 115
    else:
        return 5, (200, 205, 230, 200), 17, 95


def draw_galaxies(img, draw, galaxies):
    """双层绘制: glow 层 (blur) + 核心层"""
    glow_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    core_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(core_layer)

    FAMOUS = {
        'M31': 'M31 仙女座', 'M33': 'M33 三角座', 'M32': 'M32', 'M110': 'M110',
        'NGC0147': 'NGC 147', 'NGC0185': 'NGC 185',
        'LMC': 'LMC 大麦', 'SMC': 'SMC 小麦',
        'IC0010': 'IC 10', 'IC1613': 'IC 1613', 'NGC6822': 'NGC 6822',
        'WLM': 'WLM', 'Phoenix': '凤凰座矮星系', 'Tucana': '杜鹃座矮星系',
        'SextansA': '六分仪A', 'SextansB': '六分仪B', 'SextansdSp': '六分仪座矮椭球',
        'Carina': '船底座矮星系', 'Fornax': '天炉座矮星系', 'LeoI': '狮子座 I',
        'LeoII': '狮子座 II', 'Sculptor': '玉夫座矮星系', 'Draco': '天龙座矮星系',
        'UrsaMinor': '小熊座矮星系', 'SagittariusdSph': '人马座矮椭球',
    }
    positions = {}
    for name, ra, dec, d in galaxies:
        pt = sphere_project(ra, dec, d, max_d=3.0)
        if not pt or not in_disk(*pt): continue
        x, y = pt
        size, col, glow_r, glow_a = galaxy_style(d)
        positions[name] = (x, y)
        # glow: 多级填充圆 (径向渐变近似)
        for i in range(3):
            rr = glow_r * (1 - i * 0.30)
            aa = int(glow_a * (0.55 - i * 0.15))
            if aa <= 0: continue
            gd.ellipse([x-rr, y-rr, x+rr, y+rr], fill=(col[0], col[1], col[2], aa))
        # 核心
        cd.ellipse([x-size, y-size, x+size, y+size], fill=col)

    # M31 强化 (旋臂 + 大 glow)
    if 'M31' in positions:
        x, y = positions['M31']
        gd.ellipse([x-70, y-42, x+70, y+42], fill=(230, 190, 230, 40))
        gd.ellipse([x-46, y-28, x+46, y+28], fill=(245, 210, 245, 55))
        for ring_r, alpha in [(46, 110), (68, 80), (90, 55), (110, 35)]:
            gd.ellipse([x-ring_r, y-ring_r*0.55, x+ring_r, y+ring_r*0.55],
                       outline=(235, 195, 235, alpha), width=3)
        cd.ellipse([x-10, y-10, x+10, y+10], fill=(255, 240, 255, 255))
        cd.ellipse([x-4, y-4, x+4, y+4], fill=(255, 255, 255, 255))
    # M33 强化
    if 'M33' in positions:
        x, y = positions['M33']
        gd.ellipse([x-40, y-24, x+40, y+24], fill=(220, 200, 250, 45))
        for ring_r, alpha in [(24, 95), (38, 60)]:
            gd.ellipse([x-ring_r, y-ring_r*0.6, x+ring_r, y+ring_r*0.6],
                       outline=(225, 205, 255, alpha), width=2)
        cd.ellipse([x-6, y-6, x+6, y+6], fill=(255, 245, 255, 255))

    # 光晕模糊合成
    glow_blur = glow_layer.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(glow_blur)
    img.alpha_composite(core_layer)
    return positions


def draw_labels(draw, galaxies, positions):
    """标签 (画在最终层上)"""
    FAMOUS_CN = {
        'M31': 'M31 仙女座', 'M33': 'M33 三角座', 'M32': 'M32', 'M110': 'M110',
        'NGC0147': 'NGC 147', 'NGC0185': 'NGC 185', 'LMC': 'LMC 大麦',
        'SMC': 'SMC 小麦', 'IC0010': 'IC 10', 'IC1613': 'IC 1613',
        'NGC6822': 'NGC 6822', 'WLM': 'WLM', 'Phoenix': '凤凰座矮星系',
        'Tucana': '杜鹃座矮星系', 'SextansA': '六分仪A', 'SextansB': '六分仪B',
        'Carina': '船底座矮星系', 'Fornax': '天炉座矮星系', 'LeoI': '狮子座 I',
        'LeoII': '狮子座 II', 'Sculptor': '玉夫座矮星系', 'Draco': '天龙座矮星系',
        'UrsaMinor': '小熊座矮星系', 'SagittariusdSph': '人马座矮椭球',
    }
    for name, (x, y) in positions.items():
        if name not in FAMOUS_CN:
            continue
        label = FAMOUS_CN[name]
        # 用 ra 判断左右 (从 galaxies 找 ra)
        ra = None
        for n, r, dec, d in galaxies:
            if n == name:
                ra = r; break
        offset_x, offset_y = 16, -16
        if ra is not None and ra > 180:
            offset_x = -210
        tx, ty = x + offset_x, y + offset_y
        tw = draw.textlength(label, font=F_SMALL)
        draw.rectangle([tx-4, ty-6, tx+tw+8, ty+24], fill=(0, 0, 0, 230))
        draw.text((tx, ty), label, fill=(255, 235, 200, 255), font=F_SMALL)


def draw_mw_center(draw):
    x, y = CX, CY
    col = (255, 220, 120, 255)
    for ring_r, ring_a in [(40, 100), (80, 80), (140, 55), (220, 35), (320, 20)]:
        draw.ellipse([x-ring_r, y-ring_r, x+ring_r, y+ring_r],
                     outline=(255, 220, 120, ring_a), width=5)
    draw.line([(x-30, y), (x+30, y)], fill=col, width=7)
    draw.line([(x, y-30), (x, y+30)], fill=col, width=7)
    draw.ellipse([x-8, y-8, x+8, y+8], fill=(255, 255, 255, 255))
    draw.ellipse([x-4, y-4, x+4, y+4], fill=col)
    label = '银河系 (你在这里)'
    tx, ty = x + 100, y - 100
    tw = draw.textlength(label, font=F_LARGE)
    draw.rectangle([tx-8, ty-10, tx+tw+16, ty+52], fill=(0, 0, 0, 240))
    draw.text((tx, ty), label, fill=col, font=F_LARGE)
    sub = '← WE ARE HERE'
    stw = draw.textlength(sub, font=F_SMALL)
    draw.rectangle([tx-8, ty+58, tx+stw+16, ty+82], fill=(255, 220, 120, 240))
    draw.text((tx, ty+60), sub, fill=(0, 0, 0), font=F_SMALL)
    draw.line([(x+30, y-30), (tx-8, ty+22)], fill=col, width=2)


def draw_scale_rings(draw):
    rings = [
        (0.05, '50 kpc (银河系盘)', (150, 190, 210, 70), -45),
        (0.2,  '200 kpc (银河晕)',  (150, 190, 210, 90), 60),
        (0.5,  '0.5 Mpc',           (150, 190, 210, 110), -65),
        (1.0,  '1 Mpc (~3.3 Mly)',  (150, 190, 210, 130), 75),
        (2.0,  '2 Mpc (~6.5 Mly)',  (150, 190, 210, 130), -25),
    ]
    for d_mpc, label, col, ang_deg in rings:
        r_pix = PROJECTION_RADIUS_PX * math.sqrt(d_mpc / 3.0)
        if r_pix < 8: continue
        for ang in range(0, 360, 4):
            a1 = math.radians(ang); a2 = math.radians(ang + 2.5)
            x1 = CX + r_pix * math.cos(a1); y1 = CY + r_pix * math.sin(a1)
            x2 = CX + r_pix * math.cos(a2); y2 = CY + r_pix * math.sin(a2)
            draw.line([(x1, y1), (x2, y2)], fill=col, width=1)
        label_x = CX + (r_pix + 8) * math.cos(math.radians(ang_deg))
        label_y = CY + (r_pix + 8) * math.sin(math.radians(ang_deg))
        tw = draw.textlength(label, font=F_TINY)
        if 90 < ang_deg < 270:
            anchor_x = label_x - tw
        else:
            anchor_x = label_x
        draw.rectangle([anchor_x-4, label_y-8, anchor_x+tw+8, label_y+18], fill=(0, 0, 0, 200))
        draw.text((anchor_x, label_y), label, fill=col, font=F_TINY)


def draw_info_panel(img, draw):
    panel_h = 140
    overlay = Image.new('RGBA', (W, panel_h), (0, 0, 0, 210))
    img.paste(overlay, (0, H - panel_h), overlay)
    draw2 = ImageDraw.Draw(img, 'RGBA')
    facts = [
        ('成员',    '100+ 个星系'),
        ('最大',    'M31 (仙女座) + 银河系'),
        ('直径',    '约 10 Mly (3.1 Mpc)'),
        ('重心',    '银河系-M31 之间'),
        ('类型',    '双主星系群 (M31 + 银河系)'),
        ('未来',    '约 45 亿年后银河系-M31 合并'),
    ]
    col_w = W // len(facts)
    for i, (k, v) in enumerate(facts):
        x = i * col_w + 30
        y = H - panel_h + 24
        draw2.text((x, y), k, fill=(255, 200, 100, 255), font=F_LARGE)
        draw2.text((x, y + 60), v, fill=(225, 235, 255, 255), font=F_MED)
    draw2.text((40, 36), '本星系群 (Local Group)', fill=(255, 230, 180, 255), font=F_TITLE)
    sub = 'LOCAL GROUP · 101 galaxies (McConnachie 2012 + Cosmicflows-2) · 含银河系 + M31 + M33'
    tw = draw2.textlength(sub, font=F_MED)
    draw2.rectangle([40-4, 130, 40+tw+8, 168], fill=(0, 0, 0, 180))
    draw2.text((40, 132), sub, fill=(185, 205, 235, 240), font=F_MED)


def main():
    galaxies = load_galaxies()
    print(f'[local_group v3] 星系总数(合并去重): {len(galaxies)}')

    img = Image.new('RGB', (W, H), (2, 3, 8))
    draw = ImageDraw.Draw(img, 'RGBA')

    print('[1/6] 背景网格 + ZoA')
    draw_background_grid(draw)

    print('[2/5] Delaunay filament')
    draw_filaments(draw, galaxies)

    print('[3/5] 星系 (glow + 核心)')
    img = img.convert('RGBA')
    positions = draw_galaxies(img, draw, galaxies)

    print('[4/5] 刻度环 + 银河系中心 + 标签')
    draw_scale_rings(draw)
    draw_mw_center(draw)
    draw_labels(draw, galaxies, positions)

    print('[5/5] 信息面板')
    draw_info_panel(img, draw)

    img = img.convert('RGB')
    img.save(OUT_FILE)
    print(f'saved: {OUT_FILE} ({os.path.getsize(OUT_FILE) // 1024} KB)')


if __name__ == '__main__':
    main()
