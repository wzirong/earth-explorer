#!/usr/bin/env python3
"""生成高清程序化漩涡星系纹理 (RGBA, 透明背景)
- 中心核球 (暖黄, 老恒星)
- 对数螺旋臂 (蓝白, 年轻恒星/恒星形成区)
- 尘埃带 (暗, 吸收)
- 高分辨率 1024x1024, 透明背景
"""
import numpy as np
from PIL import Image
import math, os

OUT = os.path.join(os.path.dirname(__file__), 'data', 'galaxy_tex')
os.makedirs(OUT, exist_ok=True)

def make_galaxy(size=1024, arms=2, arm_tightness=0.55, arm_spread=0.25,
                bulge_radius=0.18, seed=42, tilt_deg=0, dust=True,
                bar=False, bar_len=0.3):
    """生成一张螺旋星系 RGBA 纹理
    size: 像素尺寸
    arms: 旋臂数
    arm_tightness: 螺旋紧密度 (越大越紧)
    arm_spread: 旋臂宽度
    bulge_radius: 核球半径比例
    seed: 随机种子
    """
    rng = np.random.default_rng(seed)
    half = size // 2
    y, x = np.mgrid[-half:half, -half:half].astype(np.float64)
    r = np.sqrt(x**2 + y**2) / half  # 0..1 归一化半径
    theta = np.arctan2(y, x)         # -pi..pi

    # 1. 核球 (bulge): 高斯分布, 暖黄
    bulge = np.exp(-(r / bulge_radius)**2 * 3.0)
    # 核球颜色: 暖黄白 (老恒星) -> RGB
    bulge_rgb = np.stack([
        np.ones_like(r) * 1.0,      # R
        np.ones_like(r) * 0.85,     # G
        np.ones_like(r) * 0.65,     # B
    ], axis=-1)

    # 2. 螺旋臂: 对数螺旋
    # 对数螺旋: r = a * exp(b * theta)
    # 反解: theta_arm = log(r/a) / b
    # 用对数螺旋相位
    arm_intensity = np.zeros_like(r)
    for arm_idx in range(arms):
        phase_offset = arm_idx * (2 * math.pi / arms)
        # 螺旋相位: theta - phase_offset - log(r)/b
        # 让臂从核球延伸到边缘
        b = arm_tightness  # 紧密度
        spiral_phase = theta - phase_offset - np.log(r + 0.05) / b
        # 臂密度: 相位接近 0 mod 2pi 的地方密度高
        # 用 cos 的周期性质
        wrapped = np.mod(spiral_phase, 2 * math.pi)
        # 距离臂中心线的角距离
        ang_dist = np.minimum(wrapped, 2 * math.pi - wrapped)
        arm_density = np.exp(-(ang_dist / arm_spread)**2)
        # 半径加权: 臂在中间半径最强, 核球区和边缘都弱
        radial_weight = np.exp(-((r - 0.5) / 0.5)**2 * 2.0) * (1 - bulge)
        arm_intensity += arm_density * radial_weight

    arm_intensity = np.clip(arm_intensity, 0, 1.2)

    # 3. 合成颜色: 核球(暖黄) + 臂(蓝白)
    # 臂颜色: 蓝白 (年轻恒星)
    arm_rgb = np.stack([
        np.ones_like(r) * 0.65,     # R
        np.ones_like(r) * 0.75,     # G
        np.ones_like(r) * 1.0,      # B (偏蓝)
    ], axis=-1)

    # 混合: 核球主导中心, 臂主导外围
    color = bulge_rgb * bulge[..., None] + arm_rgb * arm_intensity[..., None]
    # 让核球和臂都有的区域更亮
    color = np.clip(color, 0, 1.0)

    # 4. 亮度 (alpha): 核球 + 臂
    alpha = bulge * 1.0 + arm_intensity * 0.85
    alpha = np.clip(alpha, 0, 1.0)

    # 5. 尘埃带 (dust lanes): 沿臂的暗纹
    if dust:
        # 在臂的密度峰值附近加暗纹
        dust_noise = rng.normal(0, 1, r.shape)
        # 尘埃与臂密度相关
        dust_factor = 1 - arm_intensity * 0.5 * (dust_noise > 0.3).astype(float)
        dust_factor = np.clip(dust_factor, 0.4, 1.0)
        color *= dust_factor[..., None]
        alpha *= np.clip(1 - arm_intensity * 0.3 * (dust_noise > 0.6).astype(float), 0.4, 1.0)

    # 6. 棒旋结构 (bar) - 可选
    if bar:
        bar_mask = (np.abs(x) / half < bar_len) & (np.abs(y) / half < bar_len * 0.25)
        bar_center = np.exp(-((r / (bar_len * 0.6))**2) * 2.0)
        color[bar_mask] = np.clip(color[bar_mask] * 1.3 + 0.1, 0, 1)
        alpha[bar_mask] = np.clip(alpha[bar_mask] * 1.2 + 0.1, 0, 1)

    # 7. 添加噪声 (真实感)
    noise = rng.normal(0, 0.08, r.shape)
    color = np.clip(color + noise[..., None], 0, 1)

    # 8. 转 RGBA uint8
    rgba = np.zeros((size, size, 4), dtype=np.uint8)
    rgba[..., 0] = (color[..., 0] * 255).astype(np.uint8)
    rgba[..., 1] = (color[..., 1] * 255).astype(np.uint8)
    rgba[..., 2] = (color[..., 2] * 255).astype(np.uint8)
    rgba[..., 3] = (alpha * 255).astype(np.uint8)

    # 9. 可选: 倾角投影 (倾斜盘)
    # 简化: 在 X 方向压缩 (cos tilt)
    if tilt_deg > 0:
        img = Image.fromarray(rgba)
        w, h = img.size
        new_w = max(1, int(w * math.cos(math.radians(tilt_deg))))
        # 缩放到新宽度
        img = img.resize((new_w, h), Image.LANCZOS)
        # 居中放回原尺寸画布
        canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        canvas.paste(img, ((size - new_w)//2, 0))
        rgba = np.array(canvas)

    return Image.fromarray(rgba)

def make_elliptical(size=512, seed=42, flatten=1.0):
    """椭圆星系: 平滑的椭圆光斑, 无旋臂"""
    rng = np.random.default_rng(seed)
    half = size // 2
    y, x = np.mgrid[-half:half, -half:half].astype(np.float64)
    # 椭圆: 在 y 方向拉伸
    r = np.sqrt((x / half)**2 + (y / half * flatten)**2)
    # 高斯光斑 (椭圆星系没有尖锐核心)
    alpha = np.exp(-(r / 0.5)**2 * 2.5)
    # 颜色: 暖黄 (老恒星)
    color = np.stack([
        np.ones_like(r) * 1.0,
        np.ones_like(r) * 0.82,
        np.ones_like(r) * 0.62,
    ], axis=-1)
    color *= (0.6 + 0.4 * alpha[..., None])
    # 噪声
    noise = rng.normal(0, 0.04, r.shape)
    color = np.clip(color + noise[..., None], 0, 1)
    alpha = np.clip(alpha * 0.9, 0, 1)

    rgba = np.zeros((size, size, 4), dtype=np.uint8)
    rgba[..., 0] = (color[..., 0] * 255).astype(np.uint8)
    rgba[..., 1] = (color[..., 1] * 255).astype(np.uint8)
    rgba[..., 2] = (color[..., 2] * 255).astype(np.uint8)
    rgba[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(rgba)

def main():
    galaxies = {
        # 名称, 参数
        'milkyway':    dict(arms=4, arm_tightness=0.55, arm_spread=0.28, bulge_radius=0.16, seed=42,  bar=True,  bar_len=0.35),
        'andromeda':   dict(arms=2, arm_tightness=0.50, arm_spread=0.30, bulge_radius=0.20, seed=77,  bar=False),
        'm33':         dict(arms=2, arm_tightness=0.45, arm_spread=0.35, bulge_radius=0.10, seed=33,  bar=False),
        'lmc':         dict(arms=1, arm_tightness=0.60, arm_spread=0.50, bulge_radius=0.08, seed=111, bar=True,  bar_len=0.40),
        'smc':         dict(arms=1, arm_tightness=0.70, arm_spread=0.60, bulge_radius=0.06, seed=222, bar=False),
        'ngc300':      dict(arms=2, arm_tightness=0.50, arm_spread=0.32, bulge_radius=0.12, seed=300, bar=False),
    }
    for name, params in galaxies.items():
        img = make_galaxy(size=1024, **params)
        path = os.path.join(OUT, f'{name}.png')
        img.save(path)
        # 统计非透明像素
        arr = np.array(img)
        opaque = (arr[..., 3] > 10).sum()
        total = arr.shape[0] * arr.shape[1]
        print(f'{name}.png: {opaque/total:.1%} 不透明, {img.size}')

    # 椭圆/矮星系
    ellipticals = {
        'm32':    dict(seed=32,  flatten=1.0),
        'ngc205': dict(seed=205, flatten=0.7),
        'ngc185': dict(seed=185, flatten=0.6),
        'ngc147': dict(seed=147, flatten=0.8),
    }
    for name, params in ellipticals.items():
        img = make_elliptical(size=512, **params)
        path = os.path.join(OUT, f'{name}.png')
        img.save(path)
        arr = np.array(img)
        opaque = (arr[..., 3] > 10).sum()
        total = arr.shape[0] * arr.shape[1]
        print(f'{name}.png (椭圆): {opaque/total:.1%} 不透明')

if __name__ == '__main__':
    main()
