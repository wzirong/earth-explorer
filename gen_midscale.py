#!/usr/bin/env python3
"""史隆长城 + 双鱼-鲸鱼 - 真实数据版 (中场结构)
数据: 2MRS z=0.05-0.10 (史隆长城, 6510 颗) + z=0.04-0.07 (双鱼鲸鱼, 10859 颗)
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os, json, sys

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


def draw_zoA(draw, z_min, z_max):
    """ZoA 银河带"""
    gal_north_ra = math.radians(192.86)
    incl = math.radians(62.87)
    pts_pos = []; pts_neg = []
    for l_deg in range(0, 721, 2):
        l = math.radians(l_deg / 2)
        for b_deg in [15, -15]:
            sin_dec = math.sin(math.radians(b_deg)) * math.cos(incl) + \
                      math.cos(math.radians(b_deg)) * math.sin(incl) * math.sin(l - gal_north_ra)
            dec = math.degrees(math.asin(sin_dec))
            ra_offset = math.degrees(math.atan2(math.cos(incl) * math.sin(l - gal_north_ra),
                                                math.cos(l - gal_north_ra)))
            ra = (192.86 - 90 + ra_offset) % 360
            pt = sphere_project_z(ra, dec, z_min*2, z_min, z_max)
            if pt and in_disk(*pt):
                if b_deg > 0: pts_pos.append(pt)
                else: pts_neg.append(pt)
            break
    if len(pts_pos) > 1 and len(pts_neg) > 1:
        poly = pts_pos + list(reversed(pts_neg))
        for _ in range(2):
            draw.polygon(poly, fill=(0, 0, 0, 100))
    # 中线
    mid_line = []
    for i in range(min(len(pts_pos), len(pts_neg))):
        mx = (pts_pos[i][0] + pts_neg[i][0]) / 2
        my = (pts_pos[i][1] + pts_neg[i][1]) / 2
        mid_line.append((mx, my))
    if len(mid_line) > 1:
        for i in range(len(mid_line) - 1):
            draw.line([mid_line[i], mid_line[i + 1]],
                      fill=(180, 80, 40, 130), width=3)


def draw_filament(draw, pts_2d, max_len=60):
    """Delaunay filament"""
    from scipy.spatial import Delaunay
    if len(pts_2d) < 3: return
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
    count = 0
    for a, b, l in edge_list:
        if l > max_len: continue
        p1, p2 = pts_2d[a], pts_2d[b]
        mx = (p1[0]+p2[0])/2 + (hash((a,b)) % 10 - 5)
        my = (p1[1]+p2[1])/2 + (hash((b,a)) % 10 - 5)
        steps = 6
        prev_x, prev_y = p1
        for s in range(1, steps+1):
            t = s/steps
            bx = (1-t)**2*p1[0] + 2*(1-t)*t*mx + t**2*p2[0]
            by = (1-t)**2*p1[1] + 2*(1-t)*t*my + t**2*p2[1]
            draw.line([(prev_x, prev_y), (bx, by)],
                      fill=(140, 200, 240, 90), width=2)
            prev_x, prev_y = bx, by
        count += 1
    return count


def draw_galaxies(draw, galaxies, z_min, z_max):
    """画真实星系"""
    pts_2d = []
    for ra, dec, z, cz in galaxies:
        pt = sphere_project_z(ra, dec, z, z_min, z_max)
        if pt and in_disk(*pt):
            pts_2d.append(pt)
    print(f'  投影: {len(pts_2d)}')
    fc = draw_filament(draw, pts_2d)
    if fc is not None:
        print(f'  filament: {fc}')
    # 星系点
    for x, y in pts_2d:
        col = (200, 200, 220, 130); size = 1
        draw.ellipse([x-size, y-size, x+size, y+size], fill=col)
    return pts_2d


def draw_scale_rings(draw, z_min, z_max, labels):
    for z_v, label, col in labels:
        log_ratio = math.log10(1 + z_v/z_min) / math.log10(1 + z_max/z_min)
        r_pix = PROJECTION_RADIUS_PX * log_ratio
        if r_pix < 8: continue
        for ang in range(0, 360, 4):
            a1 = math.radians(ang); a2 = math.radians(ang + 2.5)
            x1 = CX + r_pix * math.cos(a1); y1 = CY + r_pix * math.sin(a1)
            x2 = CX + r_pix * math.cos(a2); y2 = CY + r_pix * math.sin(a2)
            draw.line([(x1, y1), (x2, y2)], fill=col, width=1)
        label_x = CX + (r_pix + 8) * math.cos(math.radians(-45))
        label_y = CY + (r_pix + 8) * math.sin(math.radians(-45))
        tw = draw.textlength(label, font=F_TINY)
        draw.rectangle([label_x-tw/2-4, label_y-8, label_x+tw/2+4, label_y+18], fill=(0, 0, 0, 200))
        draw.text((label_x-tw/2, label_y), label, fill=col, font=F_TINY)


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


def gen_sloan():
    """史隆长城"""
    with open('/tmp/cosmos_real/sloan_wall_data.json') as f:
        galaxies = json.load(f)
    print(f'[sloan] 2MRS z 0.05-0.10: {len(galaxies)} 颗')
    z_min, z_max = 0.05, 0.10

    img = Image.new('RGB', (W, H), (2, 3, 8))
    draw = ImageDraw.Draw(img, 'RGBA')
    draw_zoA(draw, z_min, z_max)
    pts = draw_galaxies(draw, galaxies, z_min, z_max)
    draw_scale_rings(draw, z_min, z_max, [
        (0.05, 'z=0.05 (前缘)',     (140, 180, 200, 60)),
        (0.07, 'z=0.07',            (140, 180, 200, 80)),
        (0.08, 'z=0.08 (中心)',     (255, 180, 100, 130)),
        (0.09, 'z=0.09',            (140, 180, 200, 80)),
        (0.10, 'z=0.10 (后缘)',     (140, 180, 200, 60)),
    ])
    draw_info_panel(img, draw,
        '史隆长城 (SDSS Great Wall)',
        'SDSS GREAT WALL · 2MRS z 0.05-0.10 · 2003 发现 · 1.38 Gly 长 · 曾认为最大结构 (后被武仙-北冕长城超越)',
        [
            ('发现', '2003 (Gott+ 12)'),
            ('长度', '1.38 Gly (~425 Mpc)'),
            ('厚度', '~80 Mpc'),
            ('位置', 'z=0.08 (RA 225°, Dec 0°)'),
            ('红移', '~24000 km/s'),
            ('距离', '~1 Gly (3 亿光年)'),
            ('曾第一', '2013 被武仙-北冕长城超越'),
            ('覆盖', 'SDSS DR12 主巡天'),
        ])
    draw.ellipse([CX - PROJECTION_RADIUS_PX, CY - PROJECTION_RADIUS_PX,
                  CX + PROJECTION_RADIUS_PX, CY + PROJECTION_RADIUS_PX],
                 outline=(80, 110, 150, 180), width=3)
    out = os.path.join(OUT_DIR, 'sloan_great_wall.png')
    img.save(out)
    print(f'[sloan] saved: {out}')


def gen_pisces_cetus():
    """双鱼-鲸鱼超星系团复合体"""
    with open('/tmp/cosmos_real/pisces_cetus_data.json') as f:
        galaxies = json.load(f)
    print(f'[pisces_cetus] 2MRS z 0.04-0.07: {len(galaxies)} 颗')
    z_min, z_max = 0.04, 0.07

    img = Image.new('RGB', (W, H), (2, 3, 8))
    draw = ImageDraw.Draw(img, 'RGBA')
    draw_zoA(draw, z_min, z_max)
    pts = draw_galaxies(draw, galaxies, z_min, z_max)
    draw_scale_rings(draw, z_min, z_max, [
        (0.04, 'z=0.04 (前缘)',     (140, 180, 200, 60)),
        (0.05, 'z=0.05',            (140, 180, 200, 80)),
        (0.055, 'z=0.055 (中心)',   (255, 180, 100, 130)),
        (0.06, 'z=0.06',            (140, 180, 200, 80)),
        (0.07, 'z=0.07 (后缘)',     (140, 180, 200, 60)),
    ])
    draw_info_panel(img, draw,
        '双鱼-鲸鱼超星系团复合体 (Pisces-Cetus SC)',
        'PISCES-CETUS SC · 2MRS z 0.04-0.07 · 最长超星系团 (1 Gly 长) · 1987 发现',
        [
            ('发现', '1987 (Tully+ 1992 详测)'),
            ('长度', '~1 Gly (~300 Mpc)'),
            ('成员', '~30 个星系团'),
            ('位置', 'z=0.055 (RA 20°, Dec 10°)'),
            ('距离', '~830 Mly (~255 Mpc)'),
            ('特点', '沿银道方向拉长'),
            ('红移', '~16500 km/s'),
            ('关系', '与拉尼亚凯亚邻接'),
        ])
    draw.ellipse([CX - PROJECTION_RADIUS_PX, CY - PROJECTION_RADIUS_PX,
                  CX + PROJECTION_RADIUS_PX, CY + PROJECTION_RADIUS_PX],
                 outline=(80, 110, 150, 180), width=3)
    out = os.path.join(OUT_DIR, 'pisces_cetus.png')
    img.save(out)
    print(f'[pisces_cetus] saved: {out}')


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if target in ('all', 'sloan'):
        gen_sloan()
    if target in ('all', 'pisces_cetus'):
        gen_pisces_cetus()