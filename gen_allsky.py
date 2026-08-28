#!/usr/bin/env python3
"""全天主要星系分布图 - Mollweide 投影
数据源: SIMBAD TAP, 带红移的星系 (TAP 默认上限 5 万颗)
视角: 全天图, 类似 Google Sky / 2MASS
"""
from PIL import Image, ImageDraw, ImageFilter
import math, csv, random, os

# 画布: Mollweide 投影宽高比 2:1
W, H = 4096, 2048
CX, CY = W // 2, H // 2
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')


def mollweide(ra_deg, dec_deg):
    """赤经/赤纬 → Mollweide 像素坐标。安全处理极地。
    公式: a = W/2, b = H/2, b/a = 1/2
          x = (a/π) * (λ - π) * cos(φ)
          y = b * sin(φ)
    """
    a = W / 2
    b = H / 2
    if dec_deg >= 89.99:
        return CX, CY - b * 0.96
    if dec_deg <= -89.99:
        return CX, CY + b * 0.96
    phi = dec_deg * math.pi / 180
    target = math.pi * math.sin(dec_deg * math.pi / 180)
    for _ in range(10):
        denom = 2 + 2 * math.cos(2 * phi)
        if abs(denom) < 1e-10:
            break
        phi -= (2 * phi + math.sin(2 * phi) - target) / denom
    # ra 转弧度
    lam = ra_deg * math.pi / 180
    x = (a / math.pi) * (lam - math.pi) * math.cos(phi) + CX
    y = -b * math.sin(phi) + CY
    return x, y


def is_inside_ellipse(x, y):
    """Mollweide 投影的有效区域是椭圆。检查点是否在内。"""
    # 椭圆边界: a=W/2, b=H/2
    a = W / 2 - 20
    b = H / 2 - 20
    return ((x - CX) / a) ** 2 + ((y - CY) / b) ** 2 <= 1


def draw_ellipse_border(draw, color=(80, 80, 80, 200), width=2):
    """画 Mollweide 投影的椭圆边界"""
    a = W // 2 - 20
    b = H // 2 - 20
    draw.ellipse([CX - a, CY - b, CX + a, CY + b], outline=color, width=width)


def draw_galactic_plane(draw):
    """银河平面横贯全天。平滑曲线, 用多采样点避免块状叠加。"""
    gal_north_ra = math.radians(192.86)
    pts = []
    # 高密度采样保证平滑
    for l_deg in range(0, 721, 1):
        l = math.radians(l_deg / 2)
        b = 0
        sin_dec = math.sin(b) * math.cos(math.radians(62.87)) + \
                  math.cos(b) * math.sin(math.radians(62.87)) * math.sin(l - gal_north_ra)
        dec = math.degrees(math.asin(sin_dec))
        ra_offset = math.degrees(math.atan2(math.cos(math.radians(62.87)) * math.sin(l - gal_north_ra),
                                            math.cos(l - gal_north_ra)))
        ra = (math.degrees(gal_north_ra) - 90 + ra_offset) % 360
        pts.append(mollweide(ra, dec))
    # 画一条平滑粗带 (line + width 形成柔和过渡)
    if len(pts) > 1:
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            if not (is_inside_ellipse(x1, y1) and is_inside_ellipse(x2, y2)):
                continue
            draw.line([(x1, y1), (x2, y2)], fill=(220, 200, 170, 25), width=8)


def draw_coord_grid(draw, step=30):
    """画赤道/银道经纬网格(浅灰色)"""
    # 赤道线 (dec = 0)
    pts = []
    for ra in range(0, 361, 2):
        x, y = mollweide(ra, 0)
        if is_inside_ellipse(x, y):
            pts.append((x, y))
    if len(pts) > 1:
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=(60, 80, 120, 80), width=1)
    # 经线 (ra 固定, dec 变化)
    for ra in range(0, 360, 30):
        pts = []
        for dec in range(-89, 90, 2):
            x, y = mollweide(ra, dec)
            if is_inside_ellipse(x, y):
                pts.append((x, y))
        if len(pts) > 1:
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i + 1]], fill=(60, 80, 120, 50), width=1)


def gen_allsky():
    img = Image.new('RGB', (W, H), (2, 3, 8))
    draw = ImageDraw.Draw(img, 'RGBA')

    # 1. 坐标网格
    draw_coord_grid(draw)

    # 2. 银河平面
    draw_galactic_plane(draw)

    # 3. 椭圆边界
    draw_ellipse_border(draw)

    # 4. 背景散点 (全天背景星系, 模拟深空)
    random.seed(123)
    for _ in range(8000):
        # 球面均匀采样 (dec 用 arcsin 校正)
        u = random.random()
        dec = math.degrees(math.asin(2 * u - 1)) * 0.85  # 略微避开极地
        ra = random.uniform(0, 360)
        x, y = mollweide(ra, dec)
        if not is_inside_ellipse(x, y):
            continue
        size = 1
        col = (180, 200, 220, random.randint(60, 110))
        draw.ellipse([x - size, y - size, x + size, y + size], fill=col)

    # 5. SIMBAD 真实星系数据
    csv_path = '/tmp/galaxies_all.csv'
    if not os.path.exists(csv_path):
        print(f'[allsky] ERROR: {csv_path} not found')
        return
    count = 0
    near_count = 0
    with open(csv_path) as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                ra = float(row['ra'])
                dec = float(row['dec'])
                z = float(row['rvz_redshift'])
            except (ValueError, KeyError):
                continue
            x, y = mollweide(ra, dec)
            if not is_inside_ellipse(x, y):
                continue
            # 红移决定大小
            if z < 0.005:
                # 最近邻, 画成亮星系
                size = 7
                col = (255, 235, 200, 250)
                # 柔晕
                draw.ellipse([x - size * 2.5, y - size * 2.5, x + size * 2.5, y + size * 2.5], fill=(255, 230, 180, 60))
                near_count += 1
            elif z < 0.01:
                size = 4
                col = (255, 230, 180, 230)
            elif z < 0.05:
                size = 3
                col = (255, 230, 180, 200)
            elif z < 0.2:
                size = 2
                col = (240, 220, 180, 170)
            elif z < 0.5:
                size = 2
                col = (220, 210, 180, 150)
            elif z < 1.5:
                size = 1
                col = (200, 190, 170, 110)
            else:
                size = 1
                col = (180, 170, 160, 80)
            draw.ellipse([x - size, y - size, x + size, y + size], fill=col)
            count += 1
    print(f'[allsky] {count} 星系已绘制, 其中近邻 z<0.005: {near_count}')

    # 6. 著名星系标记 (红色十字)
    famous = [
        ('M31 仙女座', 10.68, 41.27, 7),
        ('银河系中心方向', 266.40, -29.0, 7),
        ('M33 三角座', 23.46, 30.66, 5),
        ('M87 (室女A)', 187.71, 12.39, 6),
        ('半人马 A', 201.37, -43.02, 5),
        ('M81 (波德)', 148.89, 69.07, 4),
        ('M104 (草帽)', 189.99, -11.62, 5),
        ('M51 (涡状)', 202.47, 47.20, 5),
        ('IC 1101 (最大)', 228.21, 5.85, 4),
        ('GN-z11 (最远)', 189.05, 62.27, 5),
        ('草帽星系', 189.99, -11.62, 5),
        ('黑眼睛 M64', 194.18, 21.68, 4),
        ('玉夫座 NGC 253', 11.89, -25.29, 5),
        ('雪茄 M82', 148.97, 69.68, 4),
        ('风车 M101', 210.80, 54.35, 4),
    ]
    drawn_famous = set()
    for name, ra, dec, r_size in famous:
        key = (round(ra, 1), round(dec, 1))
        if key in drawn_famous: continue
        drawn_famous.add(key)
        x, y = mollweide(ra, dec)
        if not is_inside_ellipse(x, y):
            continue
        # 红色十字标记 - 更亮更大
        # 外圈十字 (粗)
        draw.line([(x - r_size * 1.5, y), (x + r_size * 1.5, y)], fill=(255, 60, 60, 255), width=3)
        draw.line([(x, y - r_size * 1.5), (x, y + r_size * 1.5)], fill=(255, 60, 60, 255), width=3)
        # 圆点中心
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255, 255))
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 60, 60, 255))
        # 背景环 (让标记在深色背景上更显眼)
        for ring in [(r_size * 2.5, (255, 60, 60, 30)), (r_size * 3, (255, 60, 60, 15))]:
            rs, col = ring
            draw.ellipse([x - rs, y - rs, x + rs, y + rs], outline=col, width=1)

    # 7. 银河平面遮挡 (Zone of Avoidance): 在银道±15° 范围内让星系点变暗
    # 简化: 在银河带上叠加深色遮罩
    pts = []
    for l_deg in range(0, 361, 3):
        l = math.radians(l_deg)
        b = 0
        sin_dec = math.sin(b) * math.cos(math.radians(62.87)) + \
                  math.cos(b) * math.sin(math.radians(62.87)) * math.sin(l - math.radians(192.86))
        dec = math.degrees(math.asin(sin_dec))
        ra_offset = math.degrees(math.atan2(math.cos(math.radians(62.87)) * math.sin(l - math.radians(192.86)),
                                            math.cos(l - math.radians(192.86))))
        ra = (192.86 - 90 + ra_offset) % 360
        pts.append(mollweide(ra, dec))
    if len(pts) > 1:
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            if not (is_inside_ellipse(x1, y1) and is_inside_ellipse(x2, y2)):
                continue
            draw.line([(x1, y1), (x2, y2)], fill=(0, 0, 0, 80), width=12)  # 半透明黑遮罩

    # 8. 暗角 (Mollweide 椭圆已自带边界, 暗角可以不加)

    img.save(os.path.join(OUT_DIR, 'allsky_galaxies.png'))
    print('[allsky] saved')


if __name__ == '__main__':
    gen_allsky()