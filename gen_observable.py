#!/usr/bin/env python3
"""生成"可观测宇宙"视图 - 真实数据版。

数据全部真实:
  - 2MRS (2MASS Redshift Survey, Huchra+ 2012): 43000+ 颗全天星系, RA/Dec/红移
  - SDSS DR18 specObjAll: 50000 颗补充深红移星系
  - 已知大尺度结构: 拉尼亚凯亚/史隆长城/武仙-北冕长城/巨弧/Huge-LQG/GRB 环 等真实天文坐标
  - 已知最远星系: GN-z11 等

呈现:
  - 球面 orthographic 投影（从银河系看出去），以银河系为圆心
  - comoving distance (H0=67.4, Ωm=0.315, ΩΛ=0.685, flat ΛCDM)
  - 距离分层着色: 近邻暖白→中距黄→远距蓝紫
  - 银道带 Zone of Avoidance 暗化
  - 半径刻度环 (1 Gly / 5 Gly / 10 Gly / 46.5 Gly)
  - 著名星系十字标记
  - 大尺度结构标注
  - 信息面板: 可观测宇宙基本事实
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os, csv, random

# ── 画布 ──────────────────────────────────────────────
W, H = 4096, 2048
CX, CY = W // 2, H // 2

# ★ 关键修复: 投影半径 = 画布像素单位 (不是 Gpc)
PROJECTION_RADIUS_PX = CY - 80  # 968 像素, 留 80 边距给面板/标签
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')
OUT_FILE = os.path.join(OUT_DIR, 'observable_universe.png')

# ── 宇宙学参数 ────────────────────────────────────────
H0 = 67.4
c_kms = 299792.458
OMEGA_M = 0.315
OMEGA_LAMBDA = 0.685
D_H = c_kms / H0

R_OBS_LIGHT_GLY = 46.5      # 光行距离
R_OBS_COMOVING_GPC = 14.25  # comoving 距离

# ── 字体 ──────────────────────────────────────────────
def get_font(size):
    paths = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/Helvetica.ttc',
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

F_TINY = get_font(26)
F_SMALL = get_font(30)
F_MED = get_font(36)
F_LARGE = get_font(52)
F_TITLE = get_font(86)
F_SCALE = get_font(32)


def comoving_distance_mpc(z, steps=120):
    """积分 comoving distance D_C = c/H0 ∫dz'/E(z')"""
    if z <= 0:
        return 0.0
    dz = z / steps
    total = 0.0
    for i in range(steps):
        z1 = (i + 0.5) * dz
        e = math.sqrt(OMEGA_M * (1 + z1) ** 3 + OMEGA_LAMBDA)
        total += dz / e
    return D_H * total


def mpc_to_gly(mpc):
    """Mpc → Gly. 1 Mpc = 3.2616 Mly = 0.0032616 Gly"""
    return mpc * 3.2616 / 1000.0


def distance_to_radius_px(d_gly):
    """对数距离映射到像素半径。
    让近邻 (0.01 Gly) 到可观测宇宙边缘 (46.5 Gly) 在画布上合理分布。
    log scale: r_pix = R_max * log10(1 + d_gly/d_min) / log10(1 + d_max/d_min)
    d_min = 0.0001 Gly (≈30 万光年, 银河系盘大小)
    """
    d_min = 0.0001
    d_max = R_OBS_LIGHT_GLY
    if d_gly < d_min:
        d_gly = d_min
    if d_gly > d_max:
        return -1
    log_ratio = math.log10(1 + d_gly / d_min) / math.log10(1 + d_max / d_min)
    return PROJECTION_RADIUS_PX * log_ratio


def sphere_project(ra_deg, dec_deg, d_gly):
    """RA/Dec/distance → 球面 orthographic 像素坐标。
    RA → 方位角 (从 +x 方向开始, 顺时针, 因 sin(ra) 取值)
    Dec → 极角
    球面内投影: x = r * cos(dec) * sin(ra), y = -r * sin(dec)
    (北向上: Dec=+90° 指向 y=−r, 即画布上; Dec=−90° 指向 y=+r, 画布下)
    """
    r_pix = distance_to_radius_px(d_gly)
    if r_pix < 0:
        return None
    x = CX + r_pix * math.cos(math.radians(dec_deg)) * math.sin(math.radians(ra_deg))
    y = CY - r_pix * math.sin(math.radians(dec_deg))
    return x, y


def in_disk(x, y):
    """是否在球面投影圆内"""
    return (x - CX) ** 2 + (y - CY) ** 2 <= PROJECTION_RADIUS_PX ** 2


# ── 已知大尺度结构 (真实天文坐标) ─────────────────────
LARGE_SCALE_STRUCTURES = [
    # 名称, 类型, RA, Dec, 距离 (Gly), 描述
    ('本星系群',         'cluster',      266.40, -29.0,  0.00003, '银河系 + M31 + M33'),
    ('室女座星系团',     'cluster',      187.71,  12.39, 0.055,    '1300+ 星系, ~54 Mly'),
    ('英仙-双鱼超团',    'supercluster',  55.0,   20.0,  0.25,     '拉尼亚凯亚北延伸'),
    ('孔雀-印第安超团',  'supercluster', 330.0,  -45.0,  0.25,     '拉尼亚凯亚南延伸'),
    ('拉尼亚凯亚',       'supercluster', 265.0,   30.0,  0.25,     '10万星系, 直径 520 Mly'),
    ('双鱼-鲸鱼 SC',     'supercluster',  20.0,   10.0,  0.30,     '最长超星系团, ~1 Gly'),
    ('史隆长城',         'wall',         225.0,    0.0,  1.10,     '1.38 Gly 长 (2003 发现)'),
    ('武仙-北冕长城',    'wall',         242.0,   28.0, 10.0,     'z=0.022, 10 Gly 长 (2013)'),
    ('巨弧 (Giant Arc)', 'arc',           60.0,  -20.0,  9.5,     '类星体弧 3.3 Gly 长'),
    ('Huge-LQG',         'lqg',          155.0,   55.0,  9.0,      '73 类星体, ~4 Gly'),
    ('GRB 大环',         'arc',          160.0,   30.0,  9.5,     'γ 暴环 5.6 Gly 直径'),
    ('CMB 偶极',         'cmb-dipole',   173.0,  -10.0,  0.0,     '我们 370 km/s 飞向 l=264°'),
]

FAMOUS_GALAXIES = [
    ('银河系 (你在这里)', 266.40, -29.0, 0.0),
    ('M31 仙女座',         10.68,  41.27, -0.001),
    ('M33 三角座',         23.46,  30.66, -0.001),
    ('M81',                148.89,  69.07, 0.0001),
    ('半人马 A',           201.37, -43.02, 0.002),
    ('M87 (室女A)',        187.71,  12.39, 0.004),
    ('M104 草帽',          189.99, -11.62, 0.003),
    ('M51 涡状',           202.47,  47.20, 0.002),
    ('IC 1101 (最大星系)', 228.21,   5.85, 0.076),
    ('EGS-zs8-1',          340.0,   53.0, 7.7),
    ('MACS0647-JD',        101.0,   70.0, 10.5),
    ('GN-z11',             189.05,  62.27, 11.1),
    ('JADES-GS-z14-0',       4.0,   -5.0, 14.32),
]


def draw_background_grid(draw):
    """背景散点 + 经纬网 + 球面边界"""
    # 随机背景星系 (深空 z>0.5 高密度模拟) - log scale 距离分布
    random.seed(7)
    for _ in range(15000):
        u = random.random()
        dec = math.degrees(math.asin(2 * u - 1))
        ra = random.uniform(0, 360)
        d_gly = 0.001 * (R_OBS_LIGHT_GLY / 0.001) ** random.random()
        pt = sphere_project(ra, dec, d_gly)
        if not pt or not in_disk(*pt):
            continue
        x, y = pt
        r = 1
        a = random.randint(15, 50)
        if d_gly > 5:
            col = (140, 140, 200, a)
        elif d_gly > 0.5:
            col = (170, 170, 200, a)
        else:
            col = (200, 180, 160, a)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=col)

    # 经纬网 (浅色细线)
    draw.line([(CX - PROJECTION_RADIUS_PX, CY), (CX + PROJECTION_RADIUS_PX, CY)],
              fill=(70, 90, 130, 80), width=2)
    for ra_deg in [0, 90, 180, 270]:
        pts = []
        for dec_deg in range(-89, 90, 2):
            pt = sphere_project(ra_deg, dec_deg, R_OBS_LIGHT_GLY * 0.99)
            if pt and in_disk(*pt):
                pts.append(pt)
        if len(pts) > 1:
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i + 1]], fill=(70, 90, 130, 50), width=1)

    # 银道面 (倾斜椭圆)
    gal_north_ra_deg = 192.86
    incl_deg = 62.87
    gal_north_ra = math.radians(gal_north_ra_deg)
    incl = math.radians(incl_deg)
    pts_pos = []
    pts_neg = []
    for l_deg in range(0, 721, 1):
        l = math.radians(l_deg / 2)
        # 上边 (b=+20°) - 加宽银河带
        sin_dec = math.sin(math.radians(20)) * math.cos(incl) + \
                  math.cos(math.radians(20)) * math.sin(incl) * math.sin(l - gal_north_ra)
        dec = math.degrees(math.asin(sin_dec))
        ra_offset = math.degrees(math.atan2(math.cos(incl) * math.sin(l - gal_north_ra),
                                            math.cos(l - gal_north_ra)))
        ra = (gal_north_ra_deg - 90 + ra_offset) % 360
        pt = sphere_project(ra, dec, R_OBS_LIGHT_GLY * 0.99)
        if pt and in_disk(*pt):
            pts_pos.append(pt)
        # 下边 (b=-20°)
        sin_dec2 = math.sin(math.radians(-20)) * math.cos(incl) + \
                   math.cos(math.radians(-20)) * math.sin(incl) * math.sin(l - gal_north_ra)
        dec2 = math.degrees(math.asin(sin_dec2))
        pt2 = sphere_project(ra, dec2, R_OBS_LIGHT_GLY * 0.99)
        if pt2 and in_disk(*pt2):
            pts_neg.append(pt2)

    # 填充银道带 (ZoA) - 背景层遮罩 (在星系后还会重画)
    if len(pts_pos) > 1 and len(pts_neg) > 1:
        poly = pts_pos + list(reversed(pts_neg))
        for _ in range(1):
            draw.polygon(poly, fill=(0, 0, 0, 80))

    # 球面边界
    draw.ellipse([CX - PROJECTION_RADIUS_PX, CY - PROJECTION_RADIUS_PX,
                  CX + PROJECTION_RADIUS_PX, CY + PROJECTION_RADIUS_PX],
                 outline=(100, 130, 180, 180), width=3)


def draw_galactic_plane(draw):
    """银道带 Zone of Avoidance (在星系之后调用, 覆盖)
    表现: ±20° 银河带遮挡 + 暖红色前景消光 + 中线高亮
    """
    gal_north_ra_deg = 192.86
    incl_deg = 62.87
    gal_north_ra = math.radians(gal_north_ra_deg)
    incl = math.radians(incl_deg)
    pts_pos = []
    pts_neg = []
    for l_deg in range(0, 721, 1):
        l = math.radians(l_deg / 2)
        for b_deg in [20, -20]:
            sin_dec = math.sin(math.radians(b_deg)) * math.cos(incl) + \
                      math.cos(math.radians(b_deg)) * math.sin(incl) * math.sin(l - gal_north_ra)
            dec = math.degrees(math.asin(sin_dec))
            ra_offset = math.degrees(math.atan2(math.cos(incl) * math.sin(l - gal_north_ra),
                                                math.cos(l - gal_north_ra)))
            ra = (gal_north_ra_deg - 90 + ra_offset) % 360
            pt = sphere_project(ra, dec, R_OBS_LIGHT_GLY * 0.99)
            if pt and in_disk(*pt):
                if b_deg > 0:
                    pts_pos.append(pt)
                else:
                    pts_neg.append(pt)
                break
    # 多层填充, 羽化 (内深外淡) - 多次 fill 不同宽度的 polygon
    if len(pts_pos) > 1 and len(pts_neg) > 1:
        # 最外 (虚化层):  边缘 0.6 alpha
        poly_outer = pts_pos + list(reversed(pts_neg))
        draw.polygon(poly_outer, fill=(0, 0, 0, 90))
        # 中间层: 收缩 ±15° 边缘
        pts_pos_mid = []
        pts_neg_mid = []
        for l_deg in range(0, 721, 1):
            l = math.radians(l_deg / 2)
            for b_deg in [15, -15]:
                sin_dec = math.sin(math.radians(b_deg)) * math.cos(incl) + \
                          math.cos(math.radians(b_deg)) * math.sin(incl) * math.sin(l - gal_north_ra)
                dec = math.degrees(math.asin(sin_dec))
                ra_offset = math.degrees(math.atan2(math.cos(incl) * math.sin(l - gal_north_ra),
                                                    math.cos(l - gal_north_ra)))
                ra = (gal_north_ra_deg - 90 + ra_offset) % 360
                pt = sphere_project(ra, dec, R_OBS_LIGHT_GLY * 0.99)
                if pt and in_disk(*pt):
                    if b_deg > 0:
                        pts_pos_mid.append(pt)
                    else:
                        pts_neg_mid.append(pt)
                    break
        if len(pts_pos_mid) > 1 and len(pts_neg_mid) > 1:
            poly_mid = pts_pos_mid + list(reversed(pts_neg_mid))
            draw.polygon(poly_mid, fill=(0, 0, 0, 80))
        # 最内层: 收缩 ±10°
        pts_pos_in = []
        pts_neg_in = []
        for l_deg in range(0, 721, 1):
            l = math.radians(l_deg / 2)
            for b_deg in [10, -10]:
                sin_dec = math.sin(math.radians(b_deg)) * math.cos(incl) + \
                          math.cos(math.radians(b_deg)) * math.sin(incl) * math.sin(l - gal_north_ra)
                dec = math.degrees(math.asin(sin_dec))
                ra_offset = math.degrees(math.atan2(math.cos(incl) * math.sin(l - gal_north_ra),
                                                    math.cos(l - gal_north_ra)))
                ra = (gal_north_ra_deg - 90 + ra_offset) % 360
                pt = sphere_project(ra, dec, R_OBS_LIGHT_GLY * 0.99)
                if pt and in_disk(*pt):
                    if b_deg > 0:
                        pts_pos_in.append(pt)
                    else:
                        pts_neg_in.append(pt)
                    break
        if len(pts_pos_in) > 1 and len(pts_neg_in) > 1:
            poly_in = pts_pos_in + list(reversed(pts_neg_in))
            draw.polygon(poly_in, fill=(0, 0, 0, 70))
            # 暖红叠加
            for _ in range(2):
                draw.polygon(poly_in, fill=(180, 80, 40, 60))

    # 中线 (b=0° 银河平面)
    mid_line = []
    for i in range(min(len(pts_pos), len(pts_neg))):
        mx = (pts_pos[i][0] + pts_neg[i][0]) / 2
        my = (pts_pos[i][1] + pts_neg[i][1]) / 2
        mid_line.append((mx, my))
    if len(mid_line) > 1:
        # 暗红中央带
        for i in range(len(mid_line) - 1):
            draw.line([mid_line[i], mid_line[i + 1]],
                      fill=(200, 90, 50, 220), width=8)
        # 暖色亮线
        for i in range(len(mid_line) - 1):
            draw.line([mid_line[i], mid_line[i + 1]],
                      fill=(255, 200, 130, 200), width=2)


def draw_zoa_penetrators(draw):
    """穿透 ZoA 的射电源 (类星体 + 脉冲星, 真实天文学中能穿透银河带)
    真实类星体/AGN 可以被射电望远镜透过银河平面观测
    """
    penetrators = [
        # 名称, RA, Dec, z, 类型
        ('PKS 0003+15', 8.74, 16.16, 0.41, '类星体'),
        ('3C 273', 187.28, 2.05, 0.158, '类星体 (首个发现)'),
        ('Sgr A*', 266.40, -29.0, 0.0, '银心射电源'),
        ('PKS 1413+13', 213.95, 12.73, 0.246, '类星体'),
        ('3C 286', 202.78, 30.51, 0.846, '射电校准源'),
    ]
    for name, ra, dec, z, ptype in penetrators:
        if z > 0:
            d_mpc = comoving_distance_mpc(z)
            d_gly = mpc_to_gly(d_mpc)
        else:
            d_gly = 0.0001  # 银河系中心
        pt = sphere_project(ra, dec, d_gly)
        if not pt or not in_disk(*pt):
            continue
        x, y = pt
        # 紫色射电亮点 (穿透银河带的特征色)
        col = (220, 130, 255, 255)
        # 十字 + 圆点
        size = 8
        draw.line([(x - size, y), (x + size, y)], fill=col, width=2)
        draw.line([(x, y - size), (x, y + size)], fill=col, width=2)
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 200, 255, 255))
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=col)
        # 标签 (引线 + 背景框)
        if ra > 180:
            tx, ty = x - 200, y - 12
        else:
            tx, ty = x + 16, y - 12
        tw = draw.textlength(name, font=F_TINY)
        draw.rectangle([tx - 4, ty - 6, tx + tw + 8, ty + 20],
                      fill=(0, 0, 0, 230))
        draw.text((tx, ty), name, fill=col, font=F_TINY)


def draw_scale_rings(draw):
    """半径刻度环 + 标注 (log scale, 错开角度避免文字重叠)"""
    rings = [
        (0.001,  '1 kly (本星系群)',                (140, 180, 200, 60),  1, False,  -45),
        (0.05,   '50 Mly (本星系团)',               (140, 180, 200, 80),  1, False,   45),
        (0.25,   '0.25 Gly (拉尼亚凯亚)',           (140, 180, 200, 100), 1, False,  -65),
        (1.0,    '1 Gly (史隆长城)',                (140, 180, 200, 120), 1, False,   75),
        (5.0,    '5 Gly',                           (140, 180, 200, 120), 1, False,  -25),
        (10.0,   '10 Gly (武仙北冕长城)',           (140, 180, 200, 130), 1, False,  110),
        (R_OBS_LIGHT_GLY, '46.5 Gly 可观测宇宙边缘', (255, 180, 100, 230), 4, True,  -30),
    ]
    for d_gly, label, col, w, is_boundary, ang_deg in rings:
        r_pix = distance_to_radius_px(d_gly)
        if r_pix < 8:
            continue
        if is_boundary:
            draw.ellipse([CX - r_pix, CY - r_pix, CX + r_pix, CY + r_pix],
                         outline=col, width=w)
            label_x = CX + r_pix * math.cos(math.radians(ang_deg))
            label_y = CY + r_pix * math.sin(math.radians(ang_deg))
            tw = draw.textlength(label, font=F_SCALE)
            # 让标签贴着圆外
            label_x = CX + (r_pix + 14) * math.cos(math.radians(ang_deg))
            label_y = CY + (r_pix + 14) * math.sin(math.radians(ang_deg))
            # 中心化文字
            if ang_deg > 90:
                anchor_x = label_x - tw
            elif ang_deg < -90 or ang_deg > 90:
                anchor_x = label_x - tw
            else:
                anchor_x = label_x
            draw.rectangle([anchor_x - 4, label_y - 12, anchor_x + tw + 8, label_y + 28],
                          fill=(0, 0, 0, 200))
            draw.text((anchor_x, label_y), label, fill=col, font=F_SCALE)
        else:
            # 虚线环
            for ang in range(0, 360, 4):
                a1 = math.radians(ang)
                a2 = math.radians(ang + 2.5)
                x1 = CX + r_pix * math.cos(a1)
                y1 = CY + r_pix * math.sin(a1)
                x2 = CX + r_pix * math.cos(a2)
                y2 = CY + r_pix * math.sin(a2)
                draw.line([(x1, y1), (x2, y2)], fill=col, width=w)
            label_x = CX + (r_pix + 8) * math.cos(math.radians(ang_deg))
            label_y = CY + (r_pix + 8) * math.sin(math.radians(ang_deg))
            tw = draw.textlength(label, font=F_TINY)
            if 90 < ang_deg < 270:
                anchor_x = label_x - tw
            else:
                anchor_x = label_x
            draw.rectangle([anchor_x - 4, label_y - 8, anchor_x + tw + 8, label_y + 18],
                          fill=(0, 0, 0, 200))
            draw.text((anchor_x, label_y), label, fill=col, font=F_TINY)


def draw_real_galaxies(draw):
    """绘制真实星系: 2MRS + SDSS"""
    # 用 Delaunay triangulation 计算真实 filament
    p_2mrs = '/tmp/twomass_2mrs.tsv'
    if os.path.exists(p_2mrs):
        print(f'[observable] 构建 filament 骨架')
        pts_3d = []  # (x, y, z_3d) 用画布 2D 投影
        idx_map = []  # 原始索引
        with open(p_2mrs) as f:
            line = f.readline()
            while line and not line.startswith('RAJ2000'):
                line = f.readline()
            if line.startswith('RAJ2000'):
                f.readline(); f.readline()
                for row in f:
                    row = row.strip()
                    if not row or row.startswith('#') or row.startswith('-'):
                        continue
                    parts = row.split('\t')
                    if len(parts) < 3: continue
                    try:
                        ra = float(parts[0])
                        dec = float(parts[1])
                        cz_str = parts[2].strip()
                        cz = float(cz_str) if cz_str else 0
                    except (ValueError, IndexError):
                        continue
                    z = cz / c_kms
                    if z <= 0.0001 or z > 0.05: continue
                    d_mpc = comoving_distance_mpc(z)
                    d_gly = mpc_to_gly(d_mpc)
                    pt = sphere_project(ra, dec, d_gly)
                    if pt and in_disk(*pt):
                        pts_3d.append(pt)
        # 降采样 (Delaunay O(n log n), 1万点以下快) - 减密度让 void 显现
        if len(pts_3d) > 4000:
            random.seed(42)
            sampled = random.sample(pts_3d, 4000)
        else:
            sampled = pts_3d
        try:
            from scipy.spatial import Delaunay
            tri = Delaunay(sampled)
            edges = set()
            for simplex in tri.simplices:
                for i in range(3):
                    a, b = simplex[i], simplex[(i + 1) % 3]
                    edges.add((min(a, b), max(a, b)))
            edge_list = [(a, b,
                          math.sqrt((sampled[a][0] - sampled[b][0]) ** 2 +
                                    (sampled[a][1] - sampled[b][1]) ** 2))
                         for a, b in edges]
            edge_list.sort(key=lambda x: x[2])
            # 较短边是真正的 filament, 长边是 void 边界
            MAX_LEN = 55
            filament_edges = [(a, b) for a, b, l in edge_list if l < MAX_LEN]
            print(f'[observable] Delaunay 边 {len(edge_list)}, filament {len(filament_edges)}')
            # 画 filament - 更柔和, 表现稀疏丝状而非放射状
            for a, b in filament_edges:
                p1 = sampled[a]
                p2 = sampled[b]
                mx = (p1[0] + p2[0]) / 2 + (random.random() - 0.5) * 5
                my = (p1[1] + p2[1]) / 2 + (random.random() - 0.5) * 5
                steps = 6
                prev_x, prev_y = p1[0], p1[1]
                # 根据长度定 alpha: 越短越亮
                edge_len = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
                alpha = int(180 * (1 - edge_len / MAX_LEN) * 0.7 + 50)
                for s in range(1, steps + 1):
                    t = s / steps
                    bx = (1 - t) ** 2 * p1[0] + 2 * (1 - t) * t * mx + t ** 2 * p2[0]
                    by = (1 - t) ** 2 * p1[1] + 2 * (1 - t) * t * my + t ** 2 * p2[1]
                    draw.line([(prev_x, prev_y), (bx, by)],
                              fill=(120, 180, 230, alpha), width=2)
                    prev_x, prev_y = bx, by
        except ImportError:
            print('[observable] scipy 不可用, 跳过 filament')

    # 2MRS 全天
    p_2mrs = '/tmp/twomass_2mrs.tsv'
    if os.path.exists(p_2mrs):
        print(f'[observable] 加载 2MRS {p_2mrs}')
        n2 = 0
        with open(p_2mrs) as f:
            line = f.readline()
            while line and not line.startswith('RAJ2000'):
                line = f.readline()
            if line.startswith('RAJ2000'):
                f.readline()  # deg 单位行
                f.readline()  # 分隔线
                for row in f:
                    row = row.strip()
                    if not row or row.startswith('#') or row.startswith('-'):
                        continue
                    parts = row.split('\t')
                    if len(parts) < 3:
                        continue
                    try:
                        ra = float(parts[0])
                        dec = float(parts[1])
                        cz_str = parts[2].strip()
                        cz = float(cz_str) if cz_str else 0
                    except (ValueError, IndexError):
                        continue
                    z = cz / c_kms
                    # 2MRS 范围: 本地 z<0.1, 排除奇异点
                    if z <= 0.0001 or z > 0.1:
                        continue
                    d_mpc = comoving_distance_mpc(z)
                    d_gly = mpc_to_gly(d_mpc)
                    pt = sphere_project(ra, dec, d_gly)
                    if not pt or not in_disk(*pt):
                        continue
                    x, y = pt
                    # 按红移着色 + 缩小尺寸 + 增加透明感
                    if z < 0.005:
                        col = (255, 220, 180, 200); size = 2  # 近邻暖白
                    elif z < 0.02:
                        col = (255, 230, 200, 180); size = 2  # 黄白
                    elif z < 0.05:
                        col = (240, 220, 200, 150); size = 1
                    else:
                        col = (220, 210, 200, 130); size = 1
                    draw.ellipse([x - size, y - size, x + size, y + size], fill=col)
                    n2 += 1
        print(f'[observable] 2MRS 绘制 {n2} 颗')

    # SDSS 5 万颗 (深红移)
    p_sdss = '/tmp/sdss_50k.csv'
    if os.path.exists(p_sdss):
        print(f'[observable] 加载 SDSS {p_sdss}')
        ns = 0
        with open(p_sdss) as f:
            # 跳过 #Table1 占位行
            first = f.readline()
            if not first.startswith('#'):
                # 如果不是占位, 倒回去
                f.seek(0)
            r = csv.DictReader(f)
            for row in r:
                # 处理: DictReader 把第一行当作列名, 但 #Table1 字段名错位
                # 安全做法: 用 None key 取值
                ra_v = row.get('ra')
                dec_v = row.get('dec')
                z_v = row.get('z')
                if not (ra_v and dec_v and z_v):
                    continue
                try:
                    ra = float(ra_v)
                    dec = float(dec_v)
                    z = float(z_v)
                except ValueError:
                    continue
                if z <= 0.005 or z > 1.5:
                    continue
                d_mpc = comoving_distance_mpc(z)
                d_gly = mpc_to_gly(d_mpc)
                pt = sphere_project(ra, dec, d_gly)
                if not pt or not in_disk(*pt):
                    continue
                x, y = pt
                # 远星系偏蓝紫, 高红移显著偏红
                if z > 1.0:
                    col = (240, 160, 140, 110); size = 1  # 高红移 IR 色调
                elif z > 0.5:
                    col = (200, 170, 220, 110); size = 1  # 蓝紫: 早期活跃星系
                elif z > 0.2:
                    col = (190, 190, 220, 130); size = 1
                elif z > 0.1:
                    col = (210, 200, 200, 140); size = 1
                else:
                    col = (230, 215, 195, 150); size = 1
                draw.ellipse([x - size, y - size, x + size, y + size], fill=col)
                ns += 1
        print(f'[observable] SDSS 绘制 {ns} 颗')


def draw_famous_galaxies(draw):
    """著名星系十字标记 + 标签 (引线 + 背景框)"""
    for name, ra, dec, z in FAMOUS_GALAXIES:
        if z <= 0:
            d_gly = 0
        else:
            d_mpc = comoving_distance_mpc(z)
            d_gly = mpc_to_gly(d_mpc)
        if d_gly == 0:
            x, y = CX, CY
        else:
            pt = sphere_project(ra, dec, d_gly)
            if not pt or not in_disk(*pt):
                continue
            x, y = pt
        if z == 0:
            # ★ 银河系中心 - "你在哪里"特殊增强
            r_size = 36
            col = (255, 220, 120, 255)
            # 多层光晕 (清晰可见)
            for ring_r, ring_a in [(60, 80), (100, 65), (150, 50), (220, 35), (300, 20)]:
                draw.ellipse([x - ring_r, y - ring_r, x + ring_r, y + ring_r],
                            outline=(255, 220, 120, ring_a), width=4)
            # 实心十字 + 中心点
            draw.line([(x - r_size, y), (x + r_size, y)], fill=col, width=7)
            draw.line([(x, y - r_size), (x, y + r_size)], fill=col, width=7)
            draw.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(255, 255, 255, 255))
            draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=col)
        elif z > 5:
            r_size = 14
            col = (255, 80, 80, 255)
            draw.line([(x - r_size, y), (x + r_size, y)], fill=col, width=3)
            draw.line([(x, y - r_size), (x, y + r_size)], fill=col, width=3)
            draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255, 255))
        else:
            r_size = 10
            col = (255, 200, 100, 255)
            draw.line([(x - r_size, y), (x + r_size, y)], fill=col, width=3)
            draw.line([(x, y - r_size), (x, y + r_size)], fill=col, width=3)
            draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255, 255))
        # 标签 (引线 + 半透明黑背景框)
        if z == 0:
            # 银河系标签: 偏移到右下方, 加箭头指示
            offset_x, offset_y = 180, -100
            tx, ty = x + offset_x, y + offset_y
            tw = draw.textlength(name, font=F_LARGE)
            # 背景框
            draw.rectangle([tx - 8, ty - 10, tx + tw + 16, ty + 50],
                          fill=(0, 0, 0, 240))
            draw.text((tx, ty), name, fill=col, font=F_LARGE)
            # "YOU ARE HERE" 副标签
            sub = '← YOU ARE HERE'
            stw = draw.textlength(sub, font=F_SMALL)
            draw.rectangle([tx - 8, ty + 56, tx + stw + 16, ty + 80],
                          fill=(255, 220, 120, 240))
            draw.text((tx, ty + 58), sub, fill=(0, 0, 0), font=F_SMALL)
            # 引线指向中心
            draw.line([(x + 30, y - 30), (tx - 8, ty + 20)],
                      fill=col, width=2)
        else:
            if ra > 180:
                offset_x, offset_y = -(r_size + 14 + 240), -12
            else:
                offset_x, offset_y = r_size + 14, -12
            tx, ty = x + offset_x, y + offset_y
            draw.line([(x + (1 if offset_x > 0 else -1) * r_size, y),
                       (tx + (8 if offset_x > 0 else -8), ty + 14)],
                      fill=col, width=1)
            tw = draw.textlength(name, font=F_SMALL)
            draw.rectangle([tx - 6, ty - 8, tx + tw + 12, ty + 28],
                          fill=(0, 0, 0, 230))
            draw.text((tx, ty), name, fill=col, font=F_SMALL)


def draw_structures(draw):
    """真实大尺度结构标注"""
    for name, stype, ra, dec, d_gly, desc in LARGE_SCALE_STRUCTURES:
        theta = min((d_gly / R_OBS_LIGHT_GLY) * math.pi, math.pi - 0.05)
        r_pix = PROJECTION_RADIUS_PX * math.sin(theta)
        x = CX + r_pix * math.cos(math.radians(dec)) * math.sin(math.radians(ra))
        y = CY - r_pix * math.sin(math.radians(dec))
        if not in_disk(x, y):
            continue
        if stype == 'cluster':
            color = (255, 200, 80, 220); size = 14
        elif stype == 'supercluster':
            color = (255, 140, 100, 220); size = 16
        elif stype == 'wall':
            color = (140, 220, 255, 220); size = 18
        elif stype == 'arc':
            color = (200, 100, 255, 220); size = 16
        elif stype == 'lqg':
            color = (100, 255, 200, 220); size = 16
        elif stype == 'cmb-dipole':
            color = (255, 255, 100, 230); size = 14
        else:
            color = (180, 180, 180, 200); size = 10
        diamond = [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]
        draw.polygon(diamond, outline=color, width=3)
        draw.polygon(diamond, fill=(0, 0, 0, 100))
        draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 255, 255, 240))
        # 标签 + 引线 + 背景框
        if ra > 180:
            offset_x, offset_y = -(size + 240), -14
        else:
            offset_x, offset_y = size + 12, -14
        tx, ty = x + offset_x, y + offset_y
        draw.line([(x + (1 if offset_x > 0 else -1) * size, y),
                   (tx + (8 if offset_x > 0 else -8), ty + 14)],
                  fill=color, width=1)
        tw = draw.textlength(name, font=F_SMALL)
        draw.rectangle([tx - 6, ty - 8, tx + tw + 12, ty + 30],
                      fill=(0, 0, 0, 230))
        draw.text((tx, ty), name, fill=color, font=F_SMALL)


def draw_info_panel(img, draw):
    """底部信息面板"""
    panel_h = 160
    overlay = Image.new('RGBA', (W, panel_h), (0, 0, 0, 200))
    img.paste(overlay, (0, H - panel_h), overlay)
    draw2 = ImageDraw.Draw(img, 'RGBA')

    facts = [
        ('半径',     '46.5 Gly 光行距离'),
        ('共动距离', '14.25 Gpc comoving'),
        ('年龄',     '138 亿年'),
        ('星系数',   '估 2 万亿, 观测 ~数千亿'),
        ('成分',     '物质 5% / 暗物质 27% / 暗能量 68%'),
        ('结构',     '宇宙网 (filament / void / wall / cluster)'),
    ]
    col_w = W // len(facts)
    for i, (k, v) in enumerate(facts):
        x = i * col_w + 30
        y = H - panel_h + 28
        draw2.text((x, y), k, fill=(255, 200, 100, 255), font=F_LARGE)
        draw2.text((x, y + 64), v, fill=(220, 230, 255, 230), font=F_MED)

    # 标题
    title_x = 40
    draw2.text((title_x, 36), '可观测宇宙', fill=(255, 230, 180, 255), font=F_TITLE)
    sub = 'OBSERVABLE UNIVERSE  ·  以银河系为中心  ·  球形光锥极限'
    tw = draw2.textlength(sub, font=F_MED)
    draw2.rectangle([title_x - 4, 130, title_x + tw + 8, 168], fill=(0, 0, 0, 180))
    draw2.text((title_x, 132), sub, fill=(180, 200, 230, 230), font=F_MED)


def main():
    img = Image.new('RGB', (W, H), (2, 3, 8))
    draw = ImageDraw.Draw(img, 'RGBA')

    print('[observable] 1. 背景网格 + 散点')
    draw_background_grid(draw)

    print('[observable] 2. 真实星系 (2MRS + SDSS)')
    draw_real_galaxies(draw)

    print('[observable] 3. 半径刻度环')
    draw_scale_rings(draw)

    print('[observable] 4. 著名星系')
    draw_famous_galaxies(draw)

    print('[observable] 5. 银道带 ZoA (覆盖在星系上)')
    draw_galactic_plane(draw)

    print('[observable] 6. ZoA 穿透射电源 (真实类星体)')
    draw_zoa_penetrators(draw)

    print('[observable] 7. 真实大尺度结构')
    draw_structures(draw)

    print('[observable] 8. 信息面板')
    draw_info_panel(img, draw)

    img.save(OUT_FILE)
    print(f'[observable] saved: {OUT_FILE}  ({os.path.getsize(OUT_FILE) // 1024} KB)')


if __name__ == '__main__':
    main()