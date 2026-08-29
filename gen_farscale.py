#!/usr/bin/env python3
"""4 个远场大尺度结构 - 真实 SDSS 类星体数据
- Huge-LQG (z 1.0-1.17)
- 巨弧 (z 0.8-1.0)
- GRB 环 (z 0.8-1.1)
- 武仙-北冕长城 (z 1.0-1.4, 含 z>1.17 的部分用 0.5-1.17 SDSS 模拟)
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os, csv, sys

W = H = 2048
CX, CY = W // 2, H // 2
PROJECTION_RADIUS_PX = CY - 80
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')


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


def load_sdss_qso(z_min, z_max):
    """从 SDSS 拉到的 100000 颗类星体 CSV 筛选"""
    out = []
    with open('/tmp/cosmos_real/sdss_qso_final.csv') as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                ra = float(row['ra']); dec = float(row['dec']); z = float(row['z'])
            except (ValueError, KeyError):
                continue
            if z_min <= z <= z_max:
                out.append((ra, dec, z))
    return out


def sphere_project_z(ra, dec, z, z_min, z_max):
    """球面投影"""
    if z < z_min: z = z_min
    if z > z_max: return None
    log_ratio = math.log10(1 + z/z_min) / math.log10(1 + z_max/z_min)
    r_pix = PROJECTION_RADIUS_PX * log_ratio
    x = CX + r_pix * math.cos(math.radians(dec)) * math.sin(math.radians(ra))
    y = CY - r_pix * math.sin(math.radians(dec))
    return x, y


def in_disk(x, y):
    return (x - CX) ** 2 + (y - CY) ** 2 <= PROJECTION_RADIUS_PX ** 2


def draw_qso_points(draw, qsos, z_min, z_max):
    """画类星体点 + Delaunay filament"""
    from scipy.spatial import Delaunay
    pts_2d = []
    for ra, dec, z in qsos:
        pt = sphere_project_z(ra, dec, z, z_min, z_max)
        if pt and in_disk(*pt):
            pts_2d.append(pt)
    print(f'  投影: {len(pts_2d)}')
    # Delaunay filament
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
        MAX_LEN = 50
        fc = 0
        for a, b, l in edge_list:
            if l > MAX_LEN: continue
            p1, p2 = pts_2d[a], pts_2d[b]
            mx = (p1[0]+p2[0])/2 + (hash((a,b)) % 8 - 4)
            my = (p1[1]+p2[1])/2 + (hash((b,a)) % 8 - 4)
            steps = 6
            prev_x, prev_y = p1
            for s in range(1, steps+1):
                t = s/steps
                bx = (1-t)**2*p1[0] + 2*(1-t)*t*mx + t**2*p2[0]
                by = (1-t)**2*p1[1] + 2*(1-t)*t*my + t**2*p2[1]
                draw.line([(prev_x, prev_y), (bx, by)],
                          fill=(180, 220, 255, 100), width=2)
                prev_x, prev_y = bx, by
            fc += 1
        print(f'  filament: {fc}')
    # 点
    for x, y in pts_2d:
        col = (255, 230, 180, 160); size = 1
        draw.ellipse([x-size, y-size, x+size, y+size], fill=col)


def draw_z_rings(draw, z_min, z_max, rings):
    """画 z 范围环 + 标注"""
    for z_v, label, col, ang_deg in rings:
        log_ratio = math.log10(1 + z_v/z_min) / math.log10(1 + z_max/z_min)
        r_pix = PROJECTION_RADIUS_PX * log_ratio
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


def draw_zoA(draw, z_min, z_max):
    """ZoA"""
    gal_north_ra = math.radians(192.86)
    incl = math.radians(62.87)
    pts_pos = []; pts_neg = []
    for l_deg in range(0, 721, 2):
        l = math.radians(l_deg / 2)
        for b_deg in [12, -12]:
            sin_dec = math.sin(math.radians(b_deg)) * math.cos(incl) + \
                      math.cos(math.radians(b_deg)) * math.sin(incl) * math.sin(l - gal_north_ra)
            dec = math.degrees(math.asin(sin_dec))
            ra_offset = math.degrees(math.atan2(math.cos(incl) * math.sin(l - gal_north_ra),
                                                math.cos(l - gal_north_ra)))
            ra = (192.86 - 90 + ra_offset) % 360
            pt = sphere_project_z(ra, dec, (z_min+z_max)/2, z_min, z_max)
            if pt and in_disk(*pt):
                if b_deg > 0: pts_pos.append(pt)
                else: pts_neg.append(pt)
            break
    if len(pts_pos) > 1 and len(pts_neg) > 1:
        poly = pts_pos + list(reversed(pts_neg))
        for _ in range(2):
            draw.polygon(poly, fill=(0, 0, 0, 100))


def draw_center_marker(draw, ra, dec, z, name, col, z_min, z_max):
    """中心十字标记"""
    pt = sphere_project_z(ra, dec, z, z_min, z_max)
    if not pt or not in_disk(*pt): return None
    x, y = pt
    size = 18
    # 光晕
    for r, a in [(40, 80), (60, 60), (90, 40), (130, 25)]:
        # col is (r, g, b, alpha), we want outline alpha = a
        outline_col = (col[0], col[1], col[2], a)
        draw.ellipse([x-r, y-r, x+r, y+r], outline=outline_col, width=3)
    draw.line([(x-size, y), (x+size, y)], fill=col, width=4)
    draw.line([(x, y-size), (x, y+size)], fill=col, width=4)
    draw.ellipse([x-5, y-5, x+5, y+5], fill=(255, 255, 255, 255))
    draw.ellipse([x-3, y-3, x+3, y+3], fill=col)
    # 标签
    tw = draw.textlength(name, font=F_MED)
    if ra > 180:
        tx, ty = x - 200, y - 14
    else:
        tx, ty = x + size + 10, y - 14
    draw.line([(x + (1 if ra < 180 else -1) * size, y),
               (tx + (8 if ra < 180 else -8), ty + 14)],
              fill=col, width=2)
    draw.rectangle([tx-6, ty-8, tx+tw+12, ty+32],
                  fill=(0, 0, 0, 230))
    draw.text((tx, ty), name, fill=col, font=F_MED)
    return (x, y)


def draw_info_panel(img, draw, title, sub, facts):
    panel_h = 160
    overlay = Image.new('RGBA', (W, panel_h), (0, 0, 0, 200))
    img.paste(overlay, (0, H - panel_h), overlay)
    draw2 = ImageDraw.Draw(img, 'RGBA')
    col_w = W // len(facts)
    for i, (k, v) in enumerate(facts):
        x = i * col_w + 16
        y = H - panel_h + 26
        draw2.text((x, y), k, fill=(255, 200, 100, 255), font=F_LARGE)
        words = v.split()
        line = ''
        ly = y + 58
        for w in words:
            test = line + ' ' + w if line else w
            if draw2.textlength(test, font=F_SMALL) > col_w - 26:
                draw2.text((x, ly), line, fill=(220, 230, 255, 230), font=F_SMALL)
                line = w; ly += 32
            else:
                line = test
        if line:
            draw2.text((x, ly), line, fill=(220, 230, 255, 230), font=F_SMALL)
    draw2.text((40, 36), title, fill=(255, 230, 180, 255), font=F_TITLE)
    tw = draw2.textlength(sub, font=F_MED)
    draw2.rectangle([40-4, 130, 40+tw+8, 168], fill=(0, 0, 0, 180))
    draw2.text((40, 132), sub, fill=(180, 200, 230, 230), font=F_MED)


def make_view(out_name, z_min, z_max, title, sub, facts, center_ra, center_dec, center_z, center_name, center_col, rings):
    qsos = load_sdss_qso(z_min, z_max)
    print(f'[{out_name}] 类星体 z {z_min}-{z_max}: {len(qsos)}')

    img = Image.new('RGB', (W, H), (2, 3, 8))
    draw = ImageDraw.Draw(img, 'RGBA')

    print(f'[{out_name}] ZoA')
    draw_zoA(draw, z_min, z_max)

    print(f'[{out_name}] 类星体 + filament')
    draw_qso_points(draw, qsos, z_min, z_max)

    print(f'[{out_name}] z 范围环')
    draw_z_rings(draw, z_min, z_max, rings)

    print(f'[{out_name}] 中心标记')
    draw_center_marker(draw, center_ra, center_dec, center_z, center_name, center_col, z_min, z_max)

    print(f'[{out_name}] 信息面板')
    draw_info_panel(img, draw, title, sub, facts)

    draw.ellipse([CX - PROJECTION_RADIUS_PX, CY - PROJECTION_RADIUS_PX,
                  CX + PROJECTION_RADIUS_PX, CY + PROJECTION_RADIUS_PX],
                 outline=(80, 110, 150, 180), width=3)

    out = os.path.join(OUT_DIR, f'{out_name}.png')
    img.save(out)
    print(f'[{out_name}] saved: {out}')


def gen_huge_lqg():
    make_view(
        'huge_lqg',
        z_min=1.0, z_max=1.17,
        title='Huge-LQG (Huge Quasar Group)',
        sub='HUGE-LQG · SDSS QSO z 1.0-1.17 · Clowes+ 2013 · 73 类星体 · 跨度 4 Gly',
        facts=[
            ('发现', '2013 (Clowes+)'),
            ('成员', '73 个类星体'),
            ('跨度', '~4 Gly (~1.24 Gpc)'),
            ('中心红移', 'z=1.27'),
            ('类别', '大尺度类星体群 (LQG)'),
            ('挑战', '违反宇宙学原理 (Einstein 极限)'),
            ('后续', '2013 后续发现 U1.27 等'),
            ('位置', 'RA 155°, Dec +55°'),
        ],
        center_ra=155.0, center_dec=55.0, center_z=1.10,
        center_name='Huge-LQG 中心',
        center_col=(100, 255, 200, 255),
        rings=[
            (1.00, 'z=1.0', (140, 180, 200, 60), -45),
            (1.05, 'z=1.05', (140, 180, 200, 80),  60),
            (1.10, 'z=1.10 (中心)', (255, 180, 100, 130), -65),
            (1.13, 'z=1.13', (140, 180, 200, 80),  75),
            (1.17, 'z=1.17', (140, 180, 200, 60), -25),
        ],
    )


def gen_giant_arc():
    make_view(
        'giant_arc',
        z_min=0.85, z_max=1.05,
        title='巨弧 (Giant Arc)',
        sub='GIANT ARC · SDSS QSO z 0.85-1.05 · Lopez+ 2022 · 类星体弧 3.3 Gly 长',
        facts=[
            ('发现', '2022 (Lopez+)'),
            ('长度', '~3.3 Gly (~1 Gpc)'),
            ('宽度', '~33 万光年'),
            ('位置', 'RA 60°, Dec -20°'),
            ('成员', '~20 个类星体'),
            ('意义', '挑战 ΛCDM 标准模型'),
            ('曲率', '~14 Gly 半径'),
            ('年龄', '~120 亿年'),
        ],
        center_ra=60.0, center_dec=-20.0, center_z=0.95,
        center_name='巨弧中心',
        center_col=(200, 100, 255, 255),
        rings=[
            (0.85, 'z=0.85 (前缘)', (140, 180, 200, 60), -45),
            (0.90, 'z=0.90', (140, 180, 200, 80),  60),
            (0.95, 'z=0.95 (中心)', (255, 180, 100, 130), -65),
            (1.00, 'z=1.00', (140, 180, 200, 80),  75),
            (1.05, 'z=1.05 (后缘)', (140, 180, 200, 60), -25),
        ],
    )


def gen_grb_ring():
    make_view(
        'giant_grb_ring',
        z_min=0.85, z_max=1.10,
        title='巨型伽马射线暴环 (GRB Ring)',
        sub='GRB RING · SDSS QSO z 0.85-1.10 · Balazs+ 2015 · 9 个 γ 暴 · 直径 5.6 Gly',
        facts=[
            ('发现', '2015 (Balazs+)'),
            ('成员', '9 个 γ 暴'),
            ('直径', '~5.6 Gly (~1.7 Gpc)'),
            ('位置', 'RA 160°, Dec +30°'),
            ('z 范围', '0.78-1.10'),
            ('置信度', '~p<0.0001'),
            ('意义', '宇宙学原理边缘'),
            ('可能解释', '宇宙弦遗迹 / 引力透镜'),
        ],
        center_ra=160.0, center_dec=30.0, center_z=0.97,
        center_name='GRB 环中心',
        center_col=(255, 100, 200, 255),
        rings=[
            (0.85, 'z=0.85 (前缘)', (140, 180, 200, 60), -45),
            (0.90, 'z=0.90', (140, 180, 200, 80),  60),
            (0.97, 'z=0.97 (中心)', (255, 180, 100, 130), -65),
            (1.05, 'z=1.05', (140, 180, 200, 80),  75),
            (1.10, 'z=1.10 (后缘)', (140, 180, 200, 60), -25),
        ],
    )


def gen_hercules_corona():
    make_view(
        'hercules_corona',
        z_min=1.0, z_max=1.17,
        title='武仙-北冕座长城 (Hercules-Corona Borealis Great Wall)',
        sub='HERCULES-CORONA WALL · SDSS QSO z 1.0-1.17 · Horváth+ 2014 · 类星体长城 10 Gly 长',
        facts=[
            ('发现', '2013/14 (Horváth+)'),
            ('长度', '~10 Gly (~3 Gpc)'),
            ('宽度', '~7 Gly (~2 Gpc)'),
            ('厚度', '~1 Gly (~300 Mpc)'),
            ('位置', 'RA 242°, Dec +28°'),
            ('z 范围', '1.0-1.4'),
            ('意义', '在 3 Gpc 尺度上挑战 ΛCDM 结构形成预测'),
        ],
        center_ra=242.0, center_dec=28.0, center_z=1.10,
        center_name='武仙-北冕长城中心',
        center_col=(140, 220, 255, 255),
        rings=[
            (1.00, 'z=1.0 (前缘)', (140, 180, 200, 60), -45),
            (1.05, 'z=1.05', (140, 180, 200, 80),  60),
            (1.10, 'z=1.10 (中心)', (255, 180, 100, 130), -65),
            (1.14, 'z=1.14', (140, 180, 200, 80),  75),
            (1.17, 'z=1.17 (后缘)', (140, 180, 200, 60), -25),
        ],
    )


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if target in ('all', 'huge_lqg'): gen_huge_lqg()
    if target in ('all', 'giant_arc'): gen_giant_arc()
    if target in ('all', 'grb_ring'): gen_grb_ring()
    if target in ('all', 'hercules'): gen_hercules_corona()