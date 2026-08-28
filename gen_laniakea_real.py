#!/usr/bin/env python3
"""拉尼亚凯亚超星系团内已知亮星系图 - 基于真实 SIMBAD 数据
视角: 5.2 亿光年尺度, 包含约 5 万颗 SIMBAD 已知星系(覆盖到 z<0.08, 即 ~3 亿光年)
风格: 与之前的 laniakea 示意图统一 (拉尼亚凯亚 / 巨引源 / 长丝)
"""
from PIL import Image, ImageDraw, ImageFilter
import math, csv, random, os

# 画布: 2048x2048, 提高密度 (50000 颗/4M 像素 = 1/80, 比 1/320 好 4 倍)
W, H = 2048, 2048
CX, CY = W // 2, H // 2
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')


def draw_galaxy(draw, cx, cy, radius, rotation=0, gtype='spiral'):
    """简化版星系绘制 (小尺寸, 适合 5 万颗场景)"""
    # 核球
    bulge_r = max(1, int(radius * 0.3))
    for i in range(bulge_r, 0, -1):
        t = i / bulge_r
        a = int(255 * (1 - t) * 0.85)
        col = (255, int(220 + 30 * t), int(160 + 60 * t), a)
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=col)
    # 旋臂
    for arm in range(2):
        base_angle = rotation + arm * math.pi
        steps = 30
        for s in range(steps):
            t = s / steps
            r = radius * 0.2 + radius * 0.8 * t
            theta = base_angle + t * 3.0
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta) * 0.55
            sw = max(1, int(3 - r / radius * 2))
            if sw < 1: continue
            b = random.randint(170, 230)
            a = int(255 * (1 - (r / radius) ** 1.5) * 0.7)
            draw.ellipse([x - sw, y - sw, x + sw, y + sw],
                         fill=(b - 40, b - 20, min(255, b + 10), a))


def draw_dwarf_elliptical(draw, cx, cy, size):
    for i in range(size, 0, -1):
        a = int(255 * (1 - i / size) * 0.7)
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(220, 200, 160, a))


def vignette(img, strength=0.85):
    """径向暗角, 中心 50% 完全不暗"""
    mask = Image.new('L', (W, H), 255)
    md = ImageDraw.Draw(mask)
    radius_inner = int(max(W, H) * 0.5)
    radius_outer = int(max(W, H) * 0.55)
    for i in range(radius_inner, radius_outer, 4):
        t = (i - radius_inner) / (radius_outer - radius_inner)
        a = max(0, int(255 * (1 - t) * strength))
        md.ellipse([CX - i, CY - i, CX + i, CY + i], outline=a, width=4)
    md.ellipse([CX - radius_outer, CY - radius_outer, CX + radius_outer, CY + radius_outer], outline=0, width=4)
    mask = mask.filter(ImageFilter.GaussianBlur(40))
    black = Image.new('RGB', (W, H), (0, 0, 0))
    return Image.composite(img, black, mask)


def gen_laniakea_real():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    random.seed(7777)

    # 背景散点
    for _ in range(3000):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        b = random.randint(40, 180)
        r = random.choice([1, 1, 2])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, min(255, b + 10), 200))

    # 巨引源 (Great Attractor) - 中心偏下
    ga_x, ga_y = CX, CY + 50
    for i in range(150, 0, -1):
        a = int(220 * (1 - i / 150) ** 1.3)
        draw.ellipse([ga_x - i, ga_y - i, ga_x + i, ga_y + i], fill=(255, 220, 160, a))
    # 核心
    for i in range(50, 0, -1):
        a = int(255 * (1 - i / 50))
        draw.ellipse([ga_x - i, ga_y - i, ga_x + i, ga_y + i], fill=(255, 240, 200, a))

    # 6 条长丝状结构从巨引源向外延伸 (多且宽, 适应 2048 画布)
    filaments = [
        (math.radians(15), 900, 50, 700),
        (math.radians(-35), 850, 48, 650),
        (math.radians(-100), 800, 45, 600),
        (math.radians(140), 850, 48, 650),
        (math.radians(175), 800, 45, 600),
        (math.radians(60), 750, 42, 550),
    ]
    for ang, length, w, density in filaments:
        # 长丝上的星系
        for _ in range(density):
            s = random.uniform(w, length)
            bx = ga_x + s * math.cos(ang)
            by = ga_y + s * math.sin(ang)
            offset = random.gauss(0, w * 0.6)
            x = bx + offset * math.cos(ang + math.pi / 2)
            y = by + offset * math.sin(ang + math.pi / 2)
            if not (0 < x < W and 0 < y < H): continue
            kind = random.random()
            if kind < 0.5:
                draw_dwarf_elliptical(draw, int(x), int(y), random.randint(2, 6))
            elif kind < 0.8:
                draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(140, 170, 220, 200))
            else:
                draw_galaxy(draw, x, y, random.randint(3, 7), rotation=random.uniform(0, 2 * math.pi))
        # 长丝节点
        for node_pos in [0.35, 0.65, 0.9]:
            s = int(node_pos * length)
            bx = ga_x + s * math.cos(ang)
            by = ga_y + s * math.sin(ang)
            x = bx + random.gauss(0, w * 0.2)
            y = by + random.gauss(0, w * 0.2)
            if not (0 < x < W and 0 < y < H): continue
            for r2 in range(45, 0, -1):
                t2 = r2 / 45
                a = int(240 * (1 - t2) * 0.9)
                draw.ellipse([x - r2, y - r2, x + r2, y + r2], fill=(255, 230, 180, a))
            for _ in range(18):
                ang2 = random.uniform(0, 2 * math.pi)
                rr = random.uniform(35, 65)
                gx = x + rr * math.cos(ang2)
                gy = y + rr * math.sin(ang2)
                draw_dwarf_elliptical(draw, int(gx), int(gy), random.randint(2, 4))

    # ── 加载真实 SIMBAD 星系 ──
    csv_paths = ['/tmp/laniakea08.csv', '/tmp/galaxies_all.csv']
    csv_path = next((p for p in csv_paths if os.path.exists(p)), None)
    if not csv_path:
        print('[laniakea_real] no CSV data')
        return
    print(f'[laniakea_real] loading {csv_path}')

    count = 0
    # 星系先按"真实 3D 空间分布"映射: 用球面投影把天球坐标压到超团视图
    # 简化: 把天球当作拉尼亚凯亚 3D 空间的"内壁", 距离由 z 决定
    # 视角: 从拉尼亚凯亚中心往外看, 把天球赤道当作径向坐标
    # z 越大越远 → 映射到外圈
    # ra (0-360) 映射到角度; dec 映射到 z 轴高度
    with open(csv_path) as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                ra = float(row['ra'])
                dec = float(row['dec'])
                z = float(row['rvz_redshift'])
            except (ValueError, KeyError):
                continue
            if z < 0 or z > 0.08:
                continue

            # 映射算法:
            # 距离 d = z / 0.08 (归一化 0-1)
            # 角度 theta = ra * π / 180
            # 高度 h = dec / 90 (归一化 -1 到 1)
            # 拉尼亚凯亚视图是 2D 投影: x = d * cos(theta), y = h
            # 加上巨引源偏移
            d = z / 0.08
            theta = ra * math.pi / 180
            h = dec / 90
            # 缩放到画布 (拉尼亚凯亚范围 1000px 半径, 占满 2048x2048)
            R = 1000
            x = CX + d * R * math.cos(theta) + random.gauss(0, 2)
            y = CY + d * R * math.sin(theta) * 0.6 + h * 500
            if not (0 < x < W and 0 < y < H): continue

            # 大小和颜色按 z 决定
            if z < 0.005:
                size = 5
                col = (255, 235, 200, 240)
                draw.ellipse([x - size * 2, y - size * 2, x + size * 2, y + size * 2],
                             fill=(255, 230, 180, 60))
            elif z < 0.015:
                size = 3
                col = (255, 230, 180, 220)
            elif z < 0.04:
                size = 2
                col = (240, 220, 180, 180)
            else:
                size = 1
                col = (200, 190, 170, 130)
            draw.ellipse([x - size, y - size, x + size, y + size], fill=col)
            count += 1
    print(f'[laniakea_real] {count} 真实星系已绘制')

    # 本星系群位置标记 (右下)
    lg_x, lg_y = CX + 1500, CY + 800
    for i in range(60, 0, -1):
        a = int(120 * (1 - i / 60))
        draw.ellipse([lg_x - i, lg_y - i, lg_x + i, lg_y + i], fill=(80, 130, 220, a))
    draw_galaxy(draw, lg_x, lg_y, 18, rotation=0.3)

    # 暗角
    img = vignette(img, strength=0.6)
    img.save(os.path.join(OUT_DIR, 'laniakea_real.png'))
    print('[laniakea_real] saved')


if __name__ == '__main__':
    gen_laniakea_real()