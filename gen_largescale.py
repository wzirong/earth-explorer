#!/usr/bin/env python3
"""生成 4 个新宇宙大尺度结构示意图 (统一 2048x2048 / 黑底暗角 / 风格延续 gen_universe.py)

  - pisces_cetus.png        双鱼-鲸鱼座超星系团复合体 (~10 亿光年, 1987 发现)
  - giant_arc.png           巨弧 (Giant Arc, 2021 发现, ~33 亿光年)
  - huge_lqg.png            Huge-LQG (2012 发现, 73 颗类星体群, ~40 亿光年)
  - giant_grb_ring.png      巨型伽马射线暴环 (2015 发现, ~56 亿光年直径)
  - hercules_corona.png     武仙-北冕座长城 (2013 发现, ~100 亿光年, 已知最大结构)

风格: 暗色背景 + 结构高亮(暖黄/冷蓝/粉红)+ 散落背景星系 + 暗角
"""
from PIL import Image, ImageDraw, ImageFilter
import math, random, os

W = H = 2048
CX = CY = W // 2
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')


def vignette(img, strength=0.85):
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


def scatter_stars(img, count, color_range, r_range=(1, 2)):
    draw = ImageDraw.Draw(img, 'RGBA')
    for _ in range(count):
        u = random.random()
        v = random.random()
        d = (u ** 0.5) * (W // 2 - 50)
        ang = v * 2 * math.pi
        x = int(CX + d * math.cos(ang))
        y = int(CY + d * math.sin(ang))
        b = random.randint(*color_range)
        r = random.choice([r_range[0]] * 4 + [r_range[1]])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, min(255, b + 10)))


def draw_glow_node(draw, cx, cy, size, color):
    """带光晕的小点 (类星体 / GRB 源)"""
    for r in range(size, 0, -1):
        t = r / size
        a = int(255 * (1 - t) * 0.6)
        c = color + (a,)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    # 中心亮
    draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 255, 255, 240))


def draw_filament(draw, x1, y1, x2, y2, width, color, density=80, jitter=30, curve=0.0):
    """画一条丝状结构 (从 x1,y1 到 x2,y2), 沿路径散布点 + 厚度变化
    curve > 0: 向垂直方向凸出 (正弦扰动 + 中点偏移)
    """
    # 中点偏移 (弧形)
    mid_off = curve
    for i in range(density):
        t = i / density
        # 沿线的位置 (含弧形扰动)
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        # 垂直方向 (相对连线)
        dx = -(y2 - y1)
        dy = (x2 - x1)
        norm = math.hypot(dx, dy) or 1
        dx, dy = dx / norm, dy / norm
        # 弧形: 中点偏移 + 小的正弦扰动
        offset = mid_off * math.sin(math.pi * t) + curve * 30 * math.sin(3 * math.pi * t + 0.7)
        x += dx * offset
        y += dy * offset
        for _ in range(int(width)):
            jx = x + dx * random.uniform(-jitter, jitter) * 0.5
            jy = y + dy * random.uniform(-jitter, jitter) * 0.5
            r = random.choice([1, 1, 2, 2, 3])
            a = random.randint(120, 220)
            draw.ellipse([jx - r, jy - r, jx + r, jy + r], fill=color + (a,))


def draw_arc(draw, cx, cy, radius, start_deg, end_deg, width, color, density=400, jitter=20):
    """画一段圆弧 (Giant Arc 用)"""
    for i in range(density):
        t = i / density
        ang = math.radians(start_deg + (end_deg - start_deg) * t)
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        # 切线方向 (垂直径向)
        tx, ty = -math.sin(ang), math.cos(ang)
        for _ in range(int(width)):
            jx = x + tx * random.uniform(-jitter, jitter) * 0.6
            jy = y + ty * random.uniform(-jitter, jitter) * 0.6
            r = random.choice([1, 1, 2, 3])
            a = random.randint(140, 230)
            draw.ellipse([jx - r, jy - r, jx + r, jy + r], fill=color + (a,))


def draw_cluster(draw, cx, cy, radius, count, color, density_grad=2.0):
    """画一个超星系团/类星体群 (球状分布)"""
    for _ in range(count):
        u = random.random()
        v = random.random()
        d = (u ** (1 / density_grad)) * radius
        ang = v * 2 * math.pi
        x = int(cx + d * math.cos(ang))
        y = int(cy + d * math.sin(ang))
        r = random.choice([1, 1, 2, 3])
        a = random.randint(180, 240)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color + (a,))


# ── 1. 双鱼-鲸鱼座超星系团复合体 (Pisces-Cetus Supercluster Complex) ──
# 1987 Tully 发现; 长丝状, 10 亿光年长, 1.5 亿光年宽, 横跨双鱼座到鲸鱼座
def gen_pisces_cetus():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    random.seed(1987)
    scatter_stars(img, 6000, (50, 200), (1, 2))

    # 主干: 横向细长丝状结构, 从左上到右下
    # 6 个超星系团节点串成链
    nodes = [
        (CX - 850, CY - 350, 1.0, (255, 210, 150)),   # 节点 1 (暖)
        (CX - 500, CY - 200, 0.9, (200, 200, 220)),   # 节点 2
        (CX - 150, CY - 50, 1.0, (255, 200, 150)),    # 节点 3 (暖)
        (CX + 200, CY + 50, 1.1, (220, 210, 200)),    # 节点 4
        (CX + 550, CY + 200, 0.9, (255, 220, 160)),   # 节点 5
        (CX + 880, CY + 320, 0.8, (200, 200, 220)),   # 节点 6
    ]
    # 连线
    for i in range(len(nodes) - 1):
        x1, y1, s1, c1 = nodes[i]
        x2, y2, s2, c2 = nodes[i + 1]
        draw_filament(draw, x1, y1, x2, y2, width=80, color=c1, density=120, jitter=20)

    # 各节点超星系团 (球状分布)
    for x, y, s, c in nodes:
        draw_cluster(draw, x, y, int(180 * s), count=1200, color=c, density_grad=2.5)

    # 旁边小超星系团点缀
    for _ in range(8):
        x = CX + random.randint(-800, 800)
        y = CY + random.randint(-500, 500)
        if any(math.hypot(x - n[0], y - n[1]) < 220 for n in nodes): continue
        draw_cluster(draw, x, y, 100, count=400, color=(180, 190, 210), density_grad=2.5)

    img = vignette(img, strength=0.9)
    img.save(os.path.join(OUT_DIR, 'pisces_cetus.png'))
    print('[pisces_cetus] saved')


# ── 2. 巨弧 (Giant Arc) ──
# 2021 Alexia Lopez 在 MgII 吸收线巡天中发现, 横跨天空约 1/4 圈 (~18 Gly, 实际长度 ~3.3 Gly)
def gen_giant_arc():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    random.seed(2021)
    scatter_stars(img, 5500, (50, 200), (1, 2))

    # 圆心略偏画布, 半径 800, 大弧度 (跨 ~120°, 更符合"巨弧"视觉)
    ring_cx, ring_cy = CX - 200, CY + 150
    ring_r = 850
    start_deg, end_deg = 200, 330  # 130° 弧
    # 主弧 (粗)
    draw_arc(draw, ring_cx, ring_cy, ring_r, start_deg, end_deg, width=80,
             color=(255, 200, 130), density=1200, jitter=18)
    # 内侧副弧 (更亮)
    draw_arc(draw, ring_cx, ring_cy, ring_r - 25, start_deg + 2, end_deg - 2, width=40,
             color=(255, 220, 160), density=1000, jitter=10)

    # 弧上 MgII 吸收体 / 类星体亮点
    for _ in range(220):
        t = random.random()
        ang = math.radians(start_deg + (end_deg - start_deg) * t)
        x = ring_cx + ring_r * math.cos(ang)
        y = ring_cy + ring_r * math.sin(ang)
        # 切线方向位移
        tx, ty = -math.sin(ang), math.cos(ang)
        jx = x + tx * random.uniform(-25, 25)
        jy = y + ty * random.uniform(-25, 25)
        draw_glow_node(draw, jx, jy, random.randint(5, 12), (255, 220, 150))

    # 弧两端"延伸" - 模拟真实的"截断" (非闭合)
    for side in [start_deg, end_deg]:
        ang = math.radians(side)
        for r_extra in range(50, 200, 30):
            x = ring_cx + (ring_r + r_extra) * math.cos(ang)
            y = ring_cy + (ring_r + r_extra) * math.sin(ang)
            draw_cluster(draw, int(x), int(y), 40, count=80, color=(180, 180, 200), density_grad=3)

    # 背景稀疏丝状
    for _ in range(5):
        x1 = CX + random.randint(-700, 700)
        y1 = CY + random.randint(-500, 500)
        x2 = x1 + random.randint(-300, 300)
        y2 = y1 + random.randint(-150, 150)
        # 跳过与弧重合区域
        if any(math.hypot(x1 - ring_cx, y1 - ring_cy) < 1000 for _ in [0]):
            continue
        draw_filament(draw, x1, y1, x2, y2, width=15, color=(120, 130, 160),
                      density=30, jitter=12, curve=20)

    img = vignette(img, strength=0.9)
    img.save(os.path.join(OUT_DIR, 'giant_arc.png'))
    print('[giant_arc] saved')


# ── 3. Huge-LQG (超大类星体群) ──
# 2012-2013 Clowes 发现, 73 颗类星体, 长 ~4 Gly, 宽 ~2 Gly, 距 z~1.27
def gen_huge_lqg():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    random.seed(2012)
    scatter_stars(img, 5000, (50, 200), (1, 2))

    # 主结构: 椭球状分布, 长轴沿对角, 含 73 颗类星体
    # 把 73 颗类星体大致放成长椭球 (3 Gly × 1.5 Gly)
    # 椭圆: 长半轴 800, 短半轴 400, 旋转 30°
    angle = math.radians(30)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    n_quasars = 73
    for _ in range(n_quasars):
        # 在椭圆内随机分布 (拒绝采样)
        for _ in range(20):
            u = random.uniform(-1, 1)
            v = random.uniform(-1, 1)
            if u * u + v * v <= 1:
                break
        # 椭圆坐标
        lx = u * 800
        ly = v * 400
        # 旋转
        x = CX + lx * cos_a - ly * sin_a
        y = CY + lx * sin_a + ly * cos_a
        # 类星体大小: 中心大, 边缘小
        size = random.randint(6, 14)
        draw_glow_node(draw, x, y, size, (255, 220, 130))

    # 周围星点
    for _ in range(2000):
        x = CX + random.randint(-900, 900)
        y = CY + random.randint(-700, 700)
        if math.hypot(x - CX, y - CY) > 900: continue
        r = random.choice([1, 1, 2])
        a = random.randint(80, 180)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(180, 200, 230, a))

    img = vignette(img, strength=0.85)
    img.save(os.path.join(OUT_DIR, 'huge_lqg.png'))
    print('[huge_lqg] saved')


# ── 4. 巨型伽马射线暴环 (Giant GRB Ring) ──
# 2015 Balazs 发现, 9 个 GRBs 在天空上成 5.6 Gly 直径的环, 中心 5.5-7.5 Gly
def gen_giant_grb_ring():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    random.seed(2015)
    scatter_stars(img, 5000, (50, 200), (1, 2))

    # 环: 中心偏离画布中心, 半径 800 (椭圆, 模拟红移距离造成的透视)
    ring_cx, ring_cy = CX + 80, CY - 100
    ring_rx, ring_ry = 820, 700  # 椭圆, 倾斜感
    ring_rot = math.radians(20)  # 椭圆倾角

    # 环本身 (9 个 GRB 节点 + 模糊连线, 非均匀角度)
    n_grb = 9
    # 用确定性间隔 + 强抖动, 避免八边形
    base_angles = [i * 360 / n_grb for i in range(n_grb)]
    random.shuffle(base_angles)  # 随机顺序
    positions = []
    for ang_deg in sorted(base_angles):  # 排序后按角度放置
        ang = math.radians(ang_deg + random.uniform(-12, 12))
        # 椭圆参数化
        x = ring_cx + ring_rx * math.cos(ang) * math.cos(ring_rot) - ring_ry * math.sin(ang) * math.sin(ring_rot)
        y = ring_cy + ring_rx * math.cos(ang) * math.sin(ring_rot) + ring_ry * math.sin(ang) * math.cos(ring_rot)
        # 半径抖动
        r_jitter = random.uniform(0.92, 1.08)
        dx = x - ring_cx
        dy = y - ring_cy
        x = ring_cx + dx * r_jitter
        y = ring_cy + dy * r_jitter
        positions.append((x, y))
        # GRB 节点 (大 + 强光晕, 紫红色, 大小不等)
        draw_glow_node(draw, x, y, random.randint(12, 24), (255, 120, 180))

    # 环连线: 沿椭圆平滑绘制 (不再是节点间的直线段)
    n_segs = 600
    for i in range(n_segs):
        t = i / n_segs
        ang = 2 * math.pi * t
        # 椭圆参数
        ex = ring_rx * math.cos(ang) * math.cos(ring_rot) - ring_ry * math.sin(ang) * math.sin(ring_rot)
        ey = ring_rx * math.cos(ang) * math.sin(ring_rot) + ring_ry * math.sin(ang) * math.cos(ring_rot)
        # 半径抖动 (每个采样点独立, 消除折线)
        r_jit = random.uniform(0.92, 1.08)
        x = ring_cx + ex * r_jit
        y = ring_cy + ey * r_jit
        # 厚度方向: 法线方向偏移
        # 椭圆法线近似: 直接用径向
        nx_dir = ex / math.hypot(ex, ey) if math.hypot(ex, ey) > 0 else 1
        ny_dir = ey / math.hypot(ex, ey) if math.hypot(ex, ey) > 0 else 0
        for k in range(5):  # 厚度
            # 法线方向 + 切线方向混合
            tk = (k - 2) * 6
            # 切线 (椭圆切线近似)
            tx_dir = -math.sin(ang) * math.cos(ring_rot) - (ring_ry / ring_rx) * math.cos(ang) * math.sin(ring_rot)
            ty_dir = -math.sin(ang) * math.sin(ring_rot) + (ring_ry / ring_rx) * math.cos(ang) * math.cos(ring_rot)
            tnorm = math.hypot(tx_dir, ty_dir) or 1
            tx_dir, ty_dir = tx_dir / tnorm, ty_dir / tnorm
            jx = x + tx_dir * tk + random.uniform(-10, 10)
            jy = y + ty_dir * tk + random.uniform(-10, 10)
            a = random.randint(100, 200)
            draw.ellipse([jx - 1, jy - 1, jx + 1, jy + 1], fill=(220, 130, 180, a))

    # 背景星系点缀
    for _ in range(1800):
        x = CX + random.randint(-950, 950)
        y = CY + random.randint(-950, 950)
        # 不在环上
        d_ell = math.hypot((x - ring_cx) * math.cos(-ring_rot) - (y - ring_cy) * math.sin(-ring_rot),
                           (x - ring_cx) * math.sin(-ring_rot) + (y - ring_cy) * math.cos(-ring_rot))
        # 还原到椭圆参数空间
        a_ell = (x - ring_cx) * math.cos(-ring_rot) - (y - ring_cy) * math.sin(-ring_rot)
        b_ell = (x - ring_cx) * math.sin(-ring_rot) + (y - ring_cy) * math.cos(-ring_rot)
        ell_r = math.hypot(a_ell / ring_rx, b_ell / ring_ry) * min(ring_rx, ring_ry)
        if 0.85 < ell_r / min(ring_rx, ring_ry) < 1.15: continue
        r = random.choice([1, 1, 2])
        a = random.randint(70, 170)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(140, 160, 200, a))

    img = vignette(img, strength=0.85)
    img.save(os.path.join(OUT_DIR, 'giant_grb_ring.png'))
    print('[giant_grb_ring] saved')


# ── 5. 武仙-北冕座长城 (Hercules-Corona Borealis Great Wall) ──
# 2013 Horvath 发现, 已知最大结构, 10 Gly 长, 7.2 Gly 宽, 中心 9.6 Gly (z ~ 2)
# 形式: 厚长丝状, 近乎不规则"墙" (平滑曲线, 非折线)
def gen_hercules_corona():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    random.seed(2013)
    scatter_stars(img, 5500, (50, 200), (1, 2))

    # 主轴: 用 Bezier 曲线控制, 让结构"蜿蜒"而非直线
    # 5 个控制点 (不规则 Y 抖动形成蜿蜒)
    P0 = (CX - 950, CY + 200)
    P1 = (CX - 500, CY - 100)
    P2 = (CX, CY - 250)
    P3 = (CX + 500, CY + 100)
    P4 = (CX + 950, CY - 200)
    # Bezier 曲线采样
    def bezier(t, P0, P1, P2, P3, P4):
        u = 1 - t
        x = (u**4 * P0[0] + 4 * u**3 * t * P1[0] + 6 * u**2 * t**2 * P2[0]
             + 4 * u * t**3 * P3[0] + t**4 * P4[0])
        y = (u**4 * P0[1] + 4 * u**3 * t * P1[1] + 6 * u**2 * t**2 * P2[1]
             + 4 * u * t**3 * P3[1] + t**4 * P4[1])
        return x, y

    n_pts = 500
    curve_pts = [bezier(i / n_pts, P0, P1, P2, P3, P4) for i in range(n_pts + 1)]

    # 沿曲线画 6 条并行丝 (形成厚墙)
    for lane in range(-3, 4):
        lane_off = lane * 70
        for i in range(n_pts):
            x, y = curve_pts[i]
            # 切线
            if i < n_pts:
                tx = curve_pts[i + 1][0] - x
                ty = curve_pts[i + 1][1] - y
            else:
                tx, ty = x - curve_pts[i - 1][0], y - curve_pts[i - 1][1]
            norm = math.hypot(tx, ty) or 1
            tx, ty = tx / norm, ty / norm
            # 法线 (垂直)
            nx, ny = -ty, tx
            # 抖动偏移
            jx = x + nx * lane_off + nx * random.uniform(-15, 15)
            jy = y + ny * lane_off + ny * random.uniform(-15, 15)
            r = random.choice([1, 1, 2, 3])
            a = random.randint(150, 230)
            if lane == 0:
                col = (255, 200, 130, a)  # 中心丝暖色
            else:
                col = (200, 200, 220, a)
            draw.ellipse([jx - r, jy - r, jx + r, jy + r], fill=col)

    # 沿曲线在控制点附近画节点 (超星系团密集)
    for cx_pt in [P0, P1, P2, P3, P4]:
        draw_cluster(draw, int(cx_pt[0]), int(cx_pt[1]), 200, count=1500, color=(255, 200, 130), density_grad=2.0)

    # 沿线中间也撒点
    for i in range(0, n_pts, 30):
        x, y = curve_pts[i]
        for _ in range(15):
            jx = x + random.uniform(-150, 150)
            jy = y + random.uniform(-150, 150)
            r = random.choice([1, 2, 3])
            a = random.randint(120, 200)
            draw.ellipse([jx - r, jy - r, jx + r, jy + r], fill=(220, 200, 200, a))

    # 周边稀疏背景
    for _ in range(1500):
        x = CX + random.randint(-900, 900)
        y = CY + random.randint(-700, 700)
        r = random.choice([1, 1, 2])
        a = random.randint(60, 150)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(140, 150, 180, a))

    img = vignette(img, strength=0.9)
    img.save(os.path.join(OUT_DIR, 'hercules_corona.png'))
    print('[hercules_corona] saved')


if __name__ == '__main__':
    gen_pisces_cetus()
    gen_giant_arc()
    gen_huge_lqg()
    gen_giant_grb_ring()
    gen_hercules_corona()
    print('\nAll 5 large-scale structures generated.')
