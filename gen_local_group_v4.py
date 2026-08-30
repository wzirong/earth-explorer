#!/usr/bin/env python3
"""本星系群 v4 - 纯粹真实
数据: McConnachie 2012 (101 颗) + Cosmicflows-2 (73 颗) 合并去重 = 150 颗真实星系
渲染: 朴素小圆点 (2-6px), 颜色按距离温和变化, 无 glow/光晕/装饰/虚假连线
"""
from PIL import Image, ImageDraw, ImageFont
import math, os, json, re

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


def norm_key(name):
    s = re.sub(r'[^A-Z0-9]', '', name.upper())
    s = re.sub(r'(NGC|IC|UGC|UGCA|ESO|DDO|KKR|KKH|UKS)(0+)(\d)', r'\1\3', s)
    return s


def load_galaxies():
    """McConnachie 2012 + Cosmicflows-2 合并去重 -> [(name, ra, dec, d_mpc)]"""
    mcc = json.load(open('/tmp/mcc_src/mcc_merged.json'))
    cf2 = json.load(open('/tmp/cosmos_real/local_group_real.json'))

    galaxies = {}
    for m in mcc:
        if not m['d_kpc']:
            continue
        if m['norm'] == 'MilkyWay':
            continue
        galaxies[norm_key(m['norm'])] = [m['name'].split(' (')[0], m['ra'], m['dec'], m['d_kpc'] / 1000.0]
    for name, ra, dec, d in cf2:
        k = norm_key(name)
        if k not in galaxies:
            galaxies[k] = [name, ra, dec, d]
    return list(galaxies.values())


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
                draw.line([pts[i], pts[i+1]], fill=(60, 80, 110, 50), width=1)
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
                 outline=(80, 110, 150, 180), width=3)


def draw_galaxies(draw, galaxies):
    """朴素圆点: 距离越近越大/亮, 无 glow/装饰"""
    FAMOUS = {
        'NGC0224': 'M31 仙女座', 'NGC0598': 'M33 三角座', 'NGC0221': 'M32',
        'NGC0205': 'M110', 'NGC0147': 'NGC 147', 'NGC0185': 'NGC 185',
        'LMC': 'LMC 大麦', 'SMC': 'SMC 小麦', 'IC0010': 'IC 10',
        'IC1613': 'IC 1613', 'NGC6822': 'NGC 6822', 'WLM': 'WLM',
        'Phoenix': '凤凰座矮星系', 'Tucana': '杜鹃座矮星系',
        'SextansA': '六分仪A', 'SextansdSp': '六分仪座矮椭球',
        'Carina': '船底座矮星系', 'Fornax': '天炉座矮星系',
    }
    for name, ra, dec, d in galaxies:
        pt = sphere_project(ra, dec, d, max_d=3.0)
        if not pt or not in_disk(*pt):
            continue
        x, y = pt
        if d < 0.1:
            col = (255, 230, 200, 230); size = 6
        elif d < 0.3:
            col = (255, 220, 180, 210); size = 4
        elif d < 0.8:
            col = (240, 220, 180, 190); size = 3
        elif d < 1.5:
            col = (200, 200, 220, 170); size = 3
        else:
            col = (180, 180, 200, 140); size = 2
        draw.ellipse([x-size, y-size, x+size, y+size], fill=col)
        if name in FAMOUS:
            label = FAMOUS[name]
            offset_x, offset_y = 18, -14
            if ra > 180:
                offset_x, offset_y = -200, -14
            tx, ty = x + offset_x, y + offset_y
            tw = draw.textlength(label, font=F_SMALL)
            draw.rectangle([tx-4, ty-6, tx+tw+8, ty+24], fill=(0, 0, 0, 230))
            draw.text((tx, ty), label, fill=col, font=F_SMALL)


def draw_mw_center(draw):
    """银河系中心标记 (真实)"""
    x, y = CX, CY
    col = (255, 220, 120, 255)
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
        (0.05, '50 kpc (银河系盘)', (140, 180, 200, 60), -45),
        (0.2,  '200 kpc (银河晕)',  (140, 180, 200, 80), 60),
        (0.5,  '0.5 Mpc',           (140, 180, 200, 100), -65),
        (1.0,  '1 Mpc (~3.3 Mly)',  (140, 180, 200, 120), 75),
        (2.0,  '2 Mpc (~6.5 Mly)',  (140, 180, 200, 120), -25),
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
    overlay = Image.new('RGBA', (W, panel_h), (0, 0, 0, 200))
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
        draw2.text((x, y + 60), v, fill=(220, 230, 255, 230), font=F_MED)
    draw2.text((40, 36), '本星系群 (Local Group)', fill=(255, 230, 180, 255), font=F_TITLE)
    sub = 'LOCAL GROUP · 150 galaxies · 真实数据 (McConnachie 2012 + Cosmicflows-2)'
    tw = draw2.textlength(sub, font=F_MED)
    draw2.rectangle([40-4, 130, 40+tw+8, 168], fill=(0, 0, 0, 180))
    draw2.text((40, 132), sub, fill=(180, 200, 230, 230), font=F_MED)


def main():
    galaxies = load_galaxies()
    print(f'[local_group v4] 真实星系 (合并去重): {len(galaxies)} 颗')

    img = Image.new('RGB', (W, H), (2, 3, 8))
    draw = ImageDraw.Draw(img, 'RGBA')

    print('[1/4] 背景网格 + ZoA')
    draw_background_grid(draw)

    print('[2/4] 真实星系 (朴素圆点)')
    draw_galaxies(draw, galaxies)

    print('[3/4] 刻度环 + 银河系中心')
    draw_scale_rings(draw)
    draw_mw_center(draw)

    print('[4/4] 信息面板')
    draw_info_panel(img, draw)

    img.save(OUT_FILE)
    print(f'saved: {OUT_FILE} ({os.path.getsize(OUT_FILE) // 1024} KB)')


if __name__ == '__main__':
    main()