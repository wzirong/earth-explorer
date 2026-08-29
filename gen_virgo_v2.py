#!/usr/bin/env python3
"""室女座星系团 - 真实数据版
数据: Extended Virgo Cluster Catalog (Kim+ 2014, VizieR J/ApJS/215/22) - 2096 颗星系
RA 范围: 182-193°, Dec 范围: 2-19° (跨度 ~11° x 17°, 中心 M87)
已知著名成员: M87, M86, M84, M49, M60, M58, M59, M61, M90, M91, M98, M99, M100
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os, json

W = H = 2048
CX, CY = W // 2, H // 2
PROJECTION_RADIUS_PX = CY - 80  # 944
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')
OUT_FILE = os.path.join(OUT_DIR, 'virgo_cluster.png')

# 室女团中心 M87
M87_RA = 187.706
M87_DEC = 12.391

# 室女团范围 (RA 180-195, Dec 2-20, 跨度 ~11° x 17°)
RA_MIN, RA_MAX = 180.5, 194.5
DEC_MIN, DEC_MAX = 2.0, 19.5
RA_SPAN = RA_MAX - RA_MIN
DEC_SPAN = DEC_MAX - DEC_MIN


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
F_LARGE = get_font(48)
F_TITLE = get_font(80)
F_SCALE = get_font(30)


def load_vcc_data():
    """加载 VCC 2096 颗真实星系"""
    with open('/tmp/cosmos_real/vcc_real.json') as f:
        return json.load(f)


def sphere_project(ra, dec):
    """球面投影: 中心 = M87 (187.7, 12.4), 距离 = 角距离"""
    # 简单 gnomonic (切平面) 投影, M87 在中心
    # dx = (RA - M87_RA) * cos(dec), dy = dec - M87_dec
    # 1° ≈ 130 px (覆盖画面)
    DEG_TO_PX_X = PROJECTION_RADIUS_PX / (RA_SPAN / 2 * 0.95)  # X 比例
    DEG_TO_PX_Y = PROJECTION_RADIUS_PX / (DEC_SPAN / 2 * 0.95)  # Y 比例
    dx = (ra - M87_RA) * math.cos(math.radians(dec)) * DEG_TO_PX_X
    dy = -(dec - M87_DEC) * DEG_TO_PX_Y  # 北上
    return CX + dx, CY + dy


def in_disk(x, y):
    return (x - CX) ** 2 + (y - CY) ** 2 <= PROJECTION_RADIUS_PX ** 2


def draw_virgo_galaxies(draw, vcc):
    """绘制 VCC 真实星系 + Delaunay filament"""
    # 1. Delaunay filament (近场密集区)
    from scipy.spatial import Delaunay
    pts_2d = []
    for name, ra, dec in vcc:
        pt = sphere_project(ra, dec)
        if pt and in_disk(*pt):
            pts_2d.append(pt)
    print(f'  VCC 投影成功: {len(pts_2d)}')
    if len(pts_2d) >= 3:
        tri = Delaunay(pts_2d)
        edges = set()
        for simplex in tri.simplices:
            for i in range(3):
                a, b = simplex[i], simplex[(i+1)%3]
                edges.add((min(a,b), max(a,b)))
        edge_list = []
        for a, b in edges:
            if a >= len(pts_2d) or b >= len(pts_2d): continue
            p1, p2 = pts_2d[a], pts_2d[b]
            l = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
            edge_list.append((a, b, l))
        edge_list.sort(key=lambda x: x[2])
        # 只保留短边 = filament
        MAX_LEN = 80
        filament_count = 0
        for a, b, l in edge_list:
            if l > MAX_LEN: continue
            p1, p2 = pts_2d[a], pts_2d[b]
            mx = (p1[0]+p2[0])/2 + (hash((a,b)) % 12 - 6)
            my = (p1[1]+p2[1])/2 + (hash((b,a)) % 12 - 6)
            steps = 6
            prev_x, prev_y = p1
            for s in range(1, steps+1):
                t = s/steps
                bx = (1-t)**2*p1[0] + 2*(1-t)*t*mx + t**2*p2[0]
                by = (1-t)**2*p1[1] + 2*(1-t)*t*my + t**2*p2[1]
                draw.line([(prev_x, prev_y), (bx, by)],
                          fill=(140, 200, 240, 90), width=2)
                prev_x, prev_y = bx, by
            filament_count += 1
        print(f'  filament 边: {filament_count}')

    # 2. 真实星系点 (按亮度/大小)
    FAMOUS = {
        '1316': ('M87', 12.0, (255, 100, 100)),   # 室女A, 中心
        '881':  ('M86', 9.5, (255, 200, 120)),
        '763':  ('M84', 10.0, (255, 200, 120)),
        '1226': ('M49', 9.5, (255, 200, 120)),
        '1890': ('M60', 9.5, (255, 200, 120)),
        '1727': ('M58', 10.5, (255, 200, 120)),
        '1903': ('M59', 10.5, (255, 200, 120)),
        '508':  ('M61', 10.5, (255, 200, 120)),
        '1690': ('M90', 10.0, (255, 200, 120)),
        '1615': ('M91', 11.0, (255, 200, 120)),
        '92':   ('M98', 11.0, (255, 200, 120)),
        '307':  ('M99', 10.5, (255, 200, 120)),
        '596':  ('M100', 10.5, (255, 200, 120)),
    }
    # M85, M88 等不在 EVCC 原始数据中, 这里保留 (可手动加)
    EXTRA_FAMOUS = {
        # (RA, Dec, label, color)
        'M85':  (186.350, 18.379, 'M85', (255, 200, 120)),
        'M88':  (187.997, 14.420, 'M88', (255, 200, 120)),
        'NGC4388': (186.452, 12.661, 'NGC 4388', (180, 130, 255)),
        'NGC4438': (186.729, 13.008, 'NGC 4438 (眼)', (180, 130, 255)),
    }
    for name, ra, dec in vcc:
        pt = sphere_project(ra, dec)
        if not pt or not in_disk(*pt): continue
        x, y = pt
        # 默认: 小暗星系 (旋涡/矮椭)
        col = (200, 200, 220, 150); size = 2
        # 标记著名星系
        if name in FAMOUS:
            label, mag, fcol = FAMOUS[name]
            col = fcol + (240,)
            if name == '1316':  # M87
                size = 24  # 巨大 (M87 是 cD 巨星系)
                # M87 喷流 (真实方向 PA=288°, 长度 ~80 kpc = 0.27°)
                # 1° ≈ 130 px, 所以喷流 ~35 px
                jet_angle = math.radians(-72)  # 288° (PA)
                jet_len = 50
                jet_end_x = x + jet_len * math.cos(jet_angle)
                jet_end_y = y + jet_len * math.sin(jet_angle)
                # 喷流多层 (向远端衰减)
                for jr, ja in [(50, 220), (40, 200), (30, 180), (20, 160)]:
                    dx = jr * math.cos(jet_angle); dy = jr * math.sin(jet_angle)
                    draw.line([(x + dx*0.1, y + dy*0.1), (x + dx, y + dy)],
                              fill=(140, 180, 255, ja), width=2)
                # 反向喷流 (S 形)
                opp_angle = jet_angle + math.pi
                for jr, ja in [(50, 220), (40, 200), (30, 180)]:
                    dx = jr * math.cos(opp_angle); dy = jr * math.sin(opp_angle)
                    draw.line([(x + dx*0.1, y + dy*0.1), (x + dx, y + dy)],
                              fill=(140, 180, 255, ja), width=2)
                # 中心十字 + 红点
                draw.line([(x-15, y), (x+15, y)], fill=col, width=4)
                draw.line([(x, y-15), (x, y+15)], fill=col, width=4)
                draw.ellipse([x-6, y-6, x+6, y+6], fill=(255, 255, 255, 255))
                draw.ellipse([x-3, y-3, x+3, y+3], fill=col)
            else:
                size = 12
                draw.line([(x-size, y), (x+size, y)], fill=col, width=3)
                draw.line([(x, y-size), (x, y+size)], fill=col, width=3)
                draw.ellipse([x-4, y-4, x+4, y+4], fill=(255, 255, 255, 255))
                draw.ellipse([x-2, y-2, x+2, y+2], fill=col)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=col)


def draw_famous_labels(draw, vcc):
    """标注著名星系"""
    FAMOUS = {
        '1316': ('M87 · 室女A (cD + 黑洞 6.5×10⁹ M☉)', True),
        '881':  ('M86', False),
        '763':  ('M84', False),
        '1226': ('M49', False),
        '1890': ('M60', False),
        '1727': ('M58', False),
        '1903': ('M59', False),
        '508':  ('M61', False),
        '1690': ('M90', False),
        '1615': ('M91', False),
        '92':   ('M98', False),
        '307':  ('M99', False),
        '596':  ('M100', False),
    }
    # 手动补充
    EXTRA = {
        'M85':  (186.350, 18.379, 'M85', (255, 200, 120, 220)),
        'M88':  (187.997, 14.420, 'M88', (255, 200, 120, 220)),
        'NGC4388': (186.452, 12.661, 'NGC 4388 (Seyfert)', (180, 130, 255, 220)),
    }
    for name, ra, dec in vcc:
        if name not in FAMOUS: continue
        pt = sphere_project(ra, dec)
        if not pt: continue
        x, y = pt
        label, big = FAMOUS[name]
        # 标签位置: M87 大标签在右侧; 其它就近
        if big:
            tx, ty = x + 50, y - 50
            draw.line([(x+30, y-30), (tx, ty+22)], fill=(255, 100, 100, 220), width=2)
            tw = draw.textlength(label, font=F_MED)
            draw.rectangle([tx-8, ty-10, tx+tw+16, ty+44], fill=(0, 0, 0, 240))
            draw.text((tx, ty), label, fill=(255, 100, 100, 240), font=F_MED)
            # 副标签: 黑洞 / 喷流
            sub = '超大质量黑洞 6.5 × 10⁹ M☉'
            stw = draw.textlength(sub, font=F_TINY)
            draw.rectangle([tx-8, ty+50, tx+stw+16, ty+72], fill=(0, 0, 0, 240))
            draw.text((tx, ty+52), sub, fill=(255, 200, 130, 240), font=F_TINY)
        else:
            tx, ty = x + 18, y - 14
            if ra > M87_RA + 3:
                tx, ty = x - 90, y - 14
            draw.line([(x+8, y), (tx, ty+14)], fill=(255, 200, 120, 180), width=1)
            tw = draw.textlength(label, font=F_TINY)
            draw.rectangle([tx-4, ty-6, tx+tw+8, ty+22], fill=(0, 0, 0, 230))
            draw.text((tx, ty), label, fill=(255, 200, 120, 240), font=F_TINY)

    # 手动补充星系
    for name, (ra, dec, label, col) in EXTRA.items():
        pt = sphere_project(ra, dec)
        if not pt: continue
        x, y = pt
        # 十字
        size = 8
        draw.line([(x-size, y), (x+size, y)], fill=col, width=2)
        draw.line([(x, y-size), (x, y+size)], fill=col, width=2)
        draw.ellipse([x-3, y-3, x+3, y+3], fill=(255, 255, 255, 255))
        # 标签
        tx, ty = x + 18, y - 14
        if ra > M87_RA + 2:
            tx, ty = x - 90, y - 14
        tw = draw.textlength(label, font=F_TINY)
        draw.rectangle([tx-4, ty-6, tx+tw+8, ty+22], fill=(0, 0, 0, 230))
        draw.text((tx, ty), label, fill=col, font=F_TINY)


def draw_background(draw):
    """背景 + 银河带 (室女团本身有 ZoA 但比较小)"""
    # 球面边界
    draw.ellipse([CX - PROJECTION_RADIUS_PX, CY - PROJECTION_RADIUS_PX,
                  CX + PROJECTION_RADIUS_PX, CY + PROJECTION_RADIUS_PX],
                 outline=(80, 110, 150, 180), width=3)
    # 银河带 (室女团覆盖低银纬区)
    gal_north_ra_deg = 192.86
    incl = math.radians(62.87)
    gal_north_ra = math.radians(192.86)
    pts_pos = []
    pts_neg = []
    for l_deg in range(0, 721, 2):
        l = math.radians(l_deg / 2)
        for b_deg in [15, -15]:
            sin_dec = math.sin(math.radians(b_deg)) * math.cos(incl) + \
                      math.cos(math.radians(b_deg)) * math.sin(incl) * math.sin(l - gal_north_ra)
            dec = math.degrees(math.asin(sin_dec))
            ra_offset = math.degrees(math.atan2(math.cos(incl) * math.sin(l - gal_north_ra),
                                                math.cos(l - gal_north_ra)))
            ra = (gal_north_ra_deg - 90 + ra_offset) % 360
            pt = sphere_project(ra, dec)
            if pt and in_disk(*pt):
                if b_deg > 0: pts_pos.append(pt)
                else: pts_neg.append(pt)
            break
    if len(pts_pos) > 1 and len(pts_neg) > 1:
        poly = pts_pos + list(reversed(pts_neg))
        for _ in range(2):
            draw.polygon(poly, fill=(0, 0, 0, 80))
    # 银河面中线
    mid_line = []
    for i in range(min(len(pts_pos), len(pts_neg))):
        mx = (pts_pos[i][0] + pts_neg[i][0]) / 2
        my = (pts_pos[i][1] + pts_neg[i][1]) / 2
        mid_line.append((mx, my))
    if len(mid_line) > 1:
        for i in range(len(mid_line) - 1):
            draw.line([mid_line[i], mid_line[i + 1]], fill=(180, 90, 50, 130), width=2)


def draw_scale_bars(draw):
    """半径尺 (角距离和真实距离)"""
    # 室女团距地 ~16.5 Mpc, 1° ≈ 290 kpc
    bars = [
        (1.0, '1° ≈ 290 kpc'),
        (3.0, '3° ≈ 870 kpc (1 Mly)'),
        (5.0, '5° ≈ 1.45 Mly'),
        (8.0, '8° ≈ 2.3 Mly'),
    ]
    for ang_deg, label in bars:
        r_pix = (ang_deg / (RA_SPAN/2*0.95)) * PROJECTION_RADIUS_PX
        # 圆环
        for ang in range(0, 360, 4):
            a1 = math.radians(ang); a2 = math.radians(ang + 2.5)
            x1 = CX + r_pix * math.cos(a1); y1 = CY + r_pix * math.sin(a1)
            x2 = CX + r_pix * math.cos(a2); y2 = CY + r_pix * math.sin(a2)
            draw.line([(x1, y1), (x2, y2)], fill=(140, 180, 200, 80), width=1)
        # 标签
        label_x = CX + (r_pix + 8) * math.cos(math.radians(-45))
        label_y = CY + (r_pix + 8) * math.sin(math.radians(-45))
        tw = draw.textlength(label, font=F_TINY)
        draw.rectangle([label_x-4, label_y-8, label_x+tw+8, label_y+18], fill=(0, 0, 0, 200))
        draw.text((label_x, label_y), label, fill=(140, 200, 240, 230), font=F_TINY)


def draw_info_panel(img, draw):
    """底部信息面板"""
    panel_h = 160
    overlay = Image.new('RGBA', (W, panel_h), (0, 0, 0, 200))
    img.paste(overlay, (0, H - panel_h), overlay)
    draw2 = ImageDraw.Draw(img, 'RGBA')
    facts = [
        ('成员数', '1300+ 大星系 (VCC 2096)'),
        ('直径', '约 1.5 Mpc (~5 Mly)'),
        ('距离', '~16.5 Mpc (~54 Mly)'),
        ('红移', '0.0036 (~1100 km/s)'),
        ('类型', '不规则团 + 多个亚团 (A, B)'),
        ('属', '室女超团 (本星系群归属)'),
        ('中心', 'M87 (cD 巨星系 + 黑洞)'),
        ('射流', 'M87 喷流 80 kpc'),
    ]
    col_w = W // len(facts)
    for i, (k, v) in enumerate(facts):
        x = i * col_w + 16
        y = H - panel_h + 26
        draw2.text((x, y), k, fill=(255, 200, 100, 255), font=F_LARGE)
        # 拆行
        words = v.split()
        line = ''
        ly = y + 58
        for w in words:
            test = line + ' ' + w if line else w
            if draw2.textlength(test, font=F_SMALL) > col_w - 26:
                draw2.text((x, ly), line, fill=(220, 230, 255, 230), font=F_SMALL)
                line = w
                ly += 32
            else:
                line = test
        if line:
            draw2.text((x, ly), line, fill=(220, 230, 255, 230), font=F_SMALL)
    # 标题
    draw2.text((40, 36), '室女座星系团 (Virgo Cluster)', fill=(255, 230, 180, 255), font=F_TITLE)
    sub = 'VIRGO CLUSTER · Extended VCC 2014 (Kim+ 2014) · 2096 galaxies · 含 M87 (室女A) + M86 + M84 + M49 ...'
    tw = draw2.textlength(sub, font=F_MED)
    draw2.rectangle([40-4, 130, 40+tw+8, 168], fill=(0, 0, 0, 180))
    draw2.text((40, 132), sub, fill=(180, 200, 230, 230), font=F_MED)


def main():
    vcc = load_vcc_data()
    print(f'[virgo] 真实星系 VCC: {len(vcc)}')

    img = Image.new('RGB', (W, H), (2, 3, 8))
    draw = ImageDraw.Draw(img, 'RGBA')

    print('[virgo] 1. 背景 + ZoA')
    draw_background(draw)

    print('[virgo] 2. VCC 真实星系 + Delaunay filament')
    draw_virgo_galaxies(draw, vcc)

    print('[virgo] 3. 半径尺')
    draw_scale_bars(draw)

    print('[virgo] 4. 著名星系标注')
    draw_famous_labels(draw, vcc)

    print('[virgo] 5. 信息面板')
    draw_info_panel(img, draw)

    img.save(OUT_FILE)
    print(f'[virgo] saved: {OUT_FILE} ({os.path.getsize(OUT_FILE) // 1024} KB)')


if __name__ == '__main__':
    main()