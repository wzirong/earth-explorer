#!/usr/bin/env python3
"""拉尼亚凯亚超星系团 - 真实数据版
数据: 2MRS (全天) z<0.025 共 18856 颗星系
中心: 巨引源 Great Attractor (l=311°, b=+30°) -> 赤道 (210°, -20°)
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os, json

W = H = 2048
CX, CY = W // 2, H // 2
PROJECTION_RADIUS_PX = CY - 80
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')
OUT_FILE = os.path.join(OUT_DIR, 'laniakea.png')

# 巨引源方向 (银道坐标 l=311°, b=+30°)
# 转换到赤道: 用 z=210°, -20° (近似)
LANIAKEA_RA = 210.0
LANIAKEA_DEC = -20.0


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


def load_data():
    """从 JSON 加载 2MRS 数据"""
    with open('/tmp/cosmos_real/laniakea_data.json') as f:
        return json.load(f)


def sphere_project(ra, dec, z, max_z=0.025):
    """球面投影: 中心 = 巨引源方向, 距离 = 红移 z"""
    # log scale 距离
    z_min = 0.001
    if z < z_min: z = z_min
    if z > max_z: return None
    log_ratio = math.log10(1 + z/z_min) / math.log10(1 + max_z/z_min)
    r_pix = PROJECTION_RADIUS_PX * log_ratio
    x = CX + r_pix * math.cos(math.radians(dec)) * math.sin(math.radians(ra))
    y = CY - r_pix * math.sin(math.radians(dec))
    return x, y


def in_disk(x, y):
    return (x - CX) ** 2 + (y - CY) ** 2 <= PROJECTION_RADIUS_PX ** 2


def draw_galaxies_and_filament(draw, galaxies):
    """绘制真实星系 + Delaunay filament"""
    from scipy.spatial import Delaunay
    # 投影
    pts_2d = []
    pt_data = []  # (x, y, z)
    for ra, dec, z, cz in galaxies:
        pt = sphere_project(ra, dec, z)
        if pt and in_disk(*pt):
            pts_2d.append(pt)
            pt_data.append((ra, dec, z))
    print(f'  投影: {len(pts_2d)}')

    # Delaunay filament (z<0.018 ~ 本星系群周围)
    close_pts = [p for i, p in enumerate(pts_2d) if pt_data[i][2] < 0.018]
    print(f'  近场 (z<0.018): {len(close_pts)}')
    if len(close_pts) >= 3:
        tri = Delaunay(close_pts)
        edges = set()
        for simplex in tri.simplices:
            for i in range(3):
                a, b = simplex[i], simplex[(i+1)%3]
                edges.add((min(a,b), max(a,b)))
        edge_list = []
        for a, b in edges:
            if a >= len(close_pts) or b >= len(close_pts): continue
            p1, p2 = close_pts[a], close_pts[b]
            l = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
            edge_list.append((a, b, l))
        edge_list.sort(key=lambda x: x[2])
        MAX_LEN = 70
        filament_count = 0
        for a, b, l in edge_list:
            if l > MAX_LEN: continue
            p1, p2 = close_pts[a], close_pts[b]
            mx = (p1[0]+p2[0])/2 + (hash((a,b)) % 10 - 5)
            my = (p1[1]+p2[1])/2 + (hash((b,a)) % 10 - 5)
            steps = 6
            prev_x, prev_y = p1
            for s in range(1, steps+1):
                t = s/steps
                bx = (1-t)**2*p1[0] + 2*(1-t)*t*mx + t**2*p2[0]
                by = (1-t)**2*p1[1] + 2*(1-t)*t*my + t**2*p2[1]
                draw.line([(prev_x, prev_y), (bx, by)],
                          fill=(140, 200, 240, 100), width=2)
                prev_x, prev_y = bx, by
            filament_count += 1
        print(f'  filament 边: {filament_count}')

    # 星系点 (按 z 分层着色)
    for x, y in pts_2d:
        # 找最近的 z
        # 简化: 用距离原点的像素距离粗估 z
        d = math.sqrt((x-CX)**2 + (y-CY)**2) / PROJECTION_RADIUS_PX
        z_est = 0.001 * (1/0.001 * 0.025) ** d  # 逆向 log
        z_est = min(max(z_est, 0.001), 0.025)
        if z_est < 0.003:
            col = (255, 230, 200, 200); size = 2
        elif z_est < 0.008:
            col = (255, 220, 180, 180); size = 1
        elif z_est < 0.015:
            col = (220, 210, 200, 160); size = 1
        else:
            col = (200, 200, 220, 140); size = 1
        draw.ellipse([x-size, y-size, x+size, y+size], fill=col)


def draw_famous_structures(draw):
    """标注拉尼亚凯亚相关结构 (已知超星系团)"""
    # 巨引源, 拉尼亚凯亚中心, 长蛇-半人马超团, 英仙-双鱼, 孔雀-印第安
    # 真实位置 (近似银道 -> 赤道):
    STRUCTURES = [
        ('巨引源 (Great Attractor)', 210.0, -20.0, (255, 100, 100), 18),
        ('拉尼亚凯亚中心',         210.0, -20.0, (255, 220, 120), 0),  # 同上
        ('室女团',                  187.7, 12.4,  (255, 200, 100), 15),
        ('长蛇-半人马超团',         200.0, -40.0, (255, 180, 100), 15),
        ('英仙-双鱼超团',            55.0,  20.0, (255, 200, 100), 15),
        ('孔雀-印第安超团',         330.0, -45.0, (255, 200, 100), 15),
        ('后发-狮子超团',           180.0,  20.0, (255, 200, 100), 12),
        ('天炉座超团',              50.0, -35.0, (255, 200, 100), 12),
        ('望远镜超团',              290.0, -50.0, (255, 200, 100), 12),
        ('武仙超团',                 240.0,  15.0, (255, 200, 100), 12),
        ('印第安超团',              330.0, -50.0, (255, 200, 100), 12),
        # 沙普利超团 - 在 z>0.025 范围外, 但作为外部引力源需要标注
        ('沙普利超团 (外部引力源)', 200.0, -30.0, (200, 80, 255), 14),
    ]
    for name, ra, dec, col, size in STRUCTURES:
        pt = sphere_project(ra, dec, 0.005)
        if not pt or not in_disk(*pt): continue
        x, y = pt
        if size > 0:
            # 菱形
            diamond = [(x, y-size), (x+size, y), (x, y+size), (x-size, y)]
            draw.polygon(diamond, outline=col, width=3)
            draw.polygon(diamond, fill=(0, 0, 0, 100))
            draw.ellipse([x-5, y-5, x+5, y+5], fill=(255, 255, 255, 240))
        else:
            # 中心大十字
            for s in [(60, 25), (90, 18), (140, 12)]:
                draw.ellipse([x-s[0], y-s[0], x+s[0], y+s[0]],
                             outline=col + (s[1],), width=4)
            draw.line([(x-25, y), (x+25, y)], fill=col, width=6)
            draw.line([(x, y-25), (x, y+25)], fill=col, width=6)
            draw.ellipse([x-8, y-8, x+8, y+8], fill=(255, 255, 255, 255))
            draw.ellipse([x-4, y-4, x+4, y+4], fill=col)
        # 标签
        offset = size + 14 if size > 0 else 30
        if ra > 180:
            tx, ty = x - offset - 200, y - 14
        else:
            tx, ty = x + offset, y - 14
        tw = draw.textlength(name, font=F_SMALL)
        draw.line([(x + (1 if ra < 180 else -1) * size, y),
                   (tx + (8 if ra < 180 else -8), ty + 14)],
                  fill=col, width=1)
        draw.rectangle([tx-6, ty-8, tx+tw+12, ty+30],
                      fill=(0, 0, 0, 230))
        draw.text((tx, ty), name, fill=col, font=F_SMALL)


def draw_scale_rings(draw):
    """半径刻度环"""
    rings = [
        (0.001, '1 Mpc (本星系群)',         (140, 180, 200, 60)),
        (0.005, '5 Mpc (室女团)',           (140, 180, 200, 80)),
        (0.01,  '10 Mpc (拉尼亚凯亚核心)',  (140, 180, 200, 100)),
        (0.015, '15 Mpc',                   (140, 180, 200, 120)),
        (0.02,  '20 Mpc',                   (140, 180, 200, 130)),
        (0.025, '25 Mpc (~80 Mly 边界)',    (255, 180, 100, 200)),
    ]
    for z_v, label, col in rings:
        z_min = 0.001
        log_ratio = math.log10(1 + z_v/z_min) / math.log10(1 + 0.025/z_min)
        r_pix = PROJECTION_RADIUS_PX * log_ratio
        if r_pix < 8: continue
        # 圆环
        for ang in range(0, 360, 3):
            a1 = math.radians(ang); a2 = math.radians(ang + 2)
            x1 = CX + r_pix * math.cos(a1); y1 = CY + r_pix * math.sin(a1)
            x2 = CX + r_pix * math.cos(a2); y2 = CY + r_pix * math.sin(a2)
            draw.line([(x1, y1), (x2, y2)], fill=col, width=1)
        # 标签 (45° 角位置)
        label_x = CX + (r_pix + 8) * math.cos(math.radians(-45))
        label_y = CY + (r_pix + 8) * math.sin(math.radians(-45))
        tw = draw.textlength(label, font=F_TINY)
        draw.rectangle([label_x-tw/2-4, label_y-8, label_x+tw/2+4, label_y+18], fill=(0, 0, 0, 200))
        draw.text((label_x-tw/2, label_y), label, fill=col, font=F_TINY)


def draw_info_panel(img, draw):
    """底部信息面板"""
    panel_h = 160
    overlay = Image.new('RGBA', (W, panel_h), (0, 0, 0, 200))
    img.paste(overlay, (0, H - panel_h), overlay)
    draw2 = ImageDraw.Draw(img, 'RGBA')
    facts = [
        ('包含', '室女团 + 长蛇-半人马 + 英仙-双鱼 等'),
        ('成员数', '~10 万个星系'),
        ('直径', '~520 Mly (160 Mpc)'),
        ('质量', '~10¹⁷ M☉'),
        ('发现', '2014 (Tully+ 银河系流场)'),
        ('中心', '巨引源 (l=311°, b=+30°)'),
        ('我们的', '本星系群 + 室女团 → 拉尼亚凯亚'),
        ('未来', '被沙普利超团拉向 (200 Mpc 外)'),
    ]
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
                line = w
                ly += 32
            else:
                line = test
        if line:
            draw2.text((x, ly), line, fill=(220, 230, 255, 230), font=F_SMALL)
    # 标题
    draw2.text((40, 36), '拉尼亚凯亚超星系团 (Laniakea)', fill=(255, 230, 180, 255), font=F_TITLE)
    sub = 'LANIAKEA SUPERCLUSTER · 2MRS z<0.025 18856 galaxies · 含 8 个超星系团 · 我们在内部'
    tw = draw2.textlength(sub, font=F_MED)
    draw2.rectangle([40-4, 130, 40+tw+8, 168], fill=(0, 0, 0, 180))
    draw2.text((40, 132), sub, fill=(180, 200, 230, 230), font=F_MED)


def draw_zoA(draw):
    """ZoA 银河带遮挡"""
    gal_north_ra_deg = 192.86
    incl = math.radians(62.87)
    gal_north_ra = math.radians(192.86)
    pts_pos = []
    pts_neg = []
    for l_deg in range(0, 721, 2):
        l = math.radians(l_deg / 2)
        for b_deg in [20, -20]:
            sin_dec = math.sin(math.radians(b_deg)) * math.cos(incl) + \
                      math.cos(math.radians(b_deg)) * math.sin(incl) * math.sin(l - gal_north_ra)
            dec = math.degrees(math.asin(sin_dec))
            ra_offset = math.degrees(math.atan2(math.cos(incl) * math.sin(l - gal_north_ra),
                                                math.cos(l - gal_north_ra)))
            ra = (gal_north_ra_deg - 90 + ra_offset) % 360
            pt = sphere_project(ra, dec, 0.005)
            if pt and in_disk(*pt):
                if b_deg > 0: pts_pos.append(pt)
                else: pts_neg.append(pt)
            break
    if len(pts_pos) > 1 and len(pts_neg) > 1:
        poly = pts_pos + list(reversed(pts_neg))
        for _ in range(3):
            draw.polygon(poly, fill=(0, 0, 0, 110))
    # 中线
    mid_line = []
    for i in range(min(len(pts_pos), len(pts_neg))):
        mx = (pts_pos[i][0] + pts_neg[i][0]) / 2
        my = (pts_pos[i][1] + pts_neg[i][1]) / 2
        mid_line.append((mx, my))
    if len(mid_line) > 1:
        for i in range(len(mid_line) - 1):
            draw.line([mid_line[i], mid_line[i + 1]],
                      fill=(220, 100, 60, 200), width=4)


def main():
    galaxies = load_data()
    print(f'[laniakea] 真实星系 2MRS z<0.025: {len(galaxies)}')

    img = Image.new('RGB', (W, H), (2, 3, 8))
    draw = ImageDraw.Draw(img, 'RGBA')

    print('[laniakea] 1. ZoA')
    draw_zoA(draw)

    print('[laniakea] 2. 真实星系 + Delaunay')
    draw_galaxies_and_filament(draw, galaxies)

    print('[laniakea] 3. 半径刻度环')
    draw_scale_rings(draw)

    print('[laniakea] 4. 大尺度结构标注')
    draw_famous_structures(draw)

    print('[laniakea] 5. 信息面板')
    draw_info_panel(img, draw)

    # 球面边界
    draw.ellipse([CX - PROJECTION_RADIUS_PX, CY - PROJECTION_RADIUS_PX,
                  CX + PROJECTION_RADIUS_PX, CY + PROJECTION_RADIUS_PX],
                 outline=(80, 110, 150, 180), width=3)

    img.save(OUT_FILE)
    print(f'[laniakea] saved: {OUT_FILE} ({os.path.getsize(OUT_FILE) // 1024} KB)')


if __name__ == '__main__':
    main()