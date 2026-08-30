#!/usr/bin/env python3
"""Generate a soft-pastel cinematic .cube LUT for talking-head studio footage.

The look, in order of operations:
  1. Soft S-curve  - gentle contrast that keeps midtones open (no crunch).
  2. Highlight knee - rolls the top end off so key light and skin don't clip.
  3. Split tone    - cool teal in shadows, warm cream in highlights.
  4. Desaturation  - pulls color toward luma for the pastel feel.
  5. Filmic lift   - shadows never reach 0, giving the matte / faded base.

The lift lands last on purpose: applied before the curve, the contrast stage
pulls it back below zero and it clips away to true black.

Tweak the CONSTANTS block and re-run. Output is a 33^3 domain-0-1 cube file.
"""

import math
from pathlib import Path

# --- CONSTANTS ---------------------------------------------------------------
LUT_SIZE = 33
TITLE = "Soft Pastel Studio"

LIFT = 0.035          # how far off black the shadows sit (matte amount)
CONTRAST = 0.22       # S-curve strength; 0 = none, 1 = full smoothstep
KNEE_START = 0.72     # highlights above this begin compressing
KNEE_CEIL = 0.94      # ceiling the rolled-off highlights approach

SHADOW_TINT = (0.94, 1.01, 1.06)   # teal-leaning multiplier at the bottom
HIGHLIGHT_TINT = (1.03, 1.005, 0.97)  # warm cream multiplier at the top
TINT_STRENGTH = 0.55   # 0 = neutral, 1 = full tint

SATURATION = 0.86     # <1 desaturates toward luma
LUMA = (0.2126, 0.7152, 0.0722)  # Rec.709 weights
# -----------------------------------------------------------------------------


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def apply_lift(x):
    return LIFT + x * (1.0 - LIFT)


def soft_s_curve(x):
    """Blend toward a smoothstep. Pins 0, 0.5 and 1, so it adds contrast
    without shifting black, white or mid grey."""
    smooth = x * x * (3.0 - 2.0 * x)
    return clamp(x + CONTRAST * (smooth - x))


# Rate that makes the knee's slope exactly 1 where it meets the identity
# section, so highlights only ever compress -- never stretch.
_KNEE_K = (1.0 - KNEE_START) / (KNEE_CEIL - KNEE_START)


def highlight_knee(x):
    if x <= KNEE_START:
        return x
    t = (x - KNEE_START) / (1.0 - KNEE_START)
    # Exponential approach to KNEE_CEIL: fast at first, asymptotic at the top.
    rolled = 1.0 - math.exp(-_KNEE_K * t)
    return KNEE_START + (KNEE_CEIL - KNEE_START) * rolled


def split_tone(rgb):
    luma = sum(c * w for c, w in zip(rgb, LUMA))
    # Weight shadow vs highlight tint by luma, smoothstepped for a soft handoff.
    w = luma * luma * (3.0 - 2.0 * luma)
    out = []
    for c, s, h in zip(rgb, SHADOW_TINT, HIGHLIGHT_TINT):
        mult = s * (1.0 - w) + h * w
        mult = 1.0 + (mult - 1.0) * TINT_STRENGTH
        out.append(clamp(c * mult))
    return out


def desaturate(rgb):
    luma = sum(c * w for c, w in zip(rgb, LUMA))
    return [clamp(luma + (c - luma) * SATURATION) for c in rgb]


def transform(rgb):
    rgb = [soft_s_curve(c) for c in rgb]
    rgb = [highlight_knee(c) for c in rgb]
    rgb = split_tone(rgb)
    rgb = desaturate(rgb)
    rgb = [apply_lift(c) for c in rgb]
    return rgb


def main():
    lines = [
        f'TITLE "{TITLE}"',
        "",
        f"LUT_3D_SIZE {LUT_SIZE}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
        "",
    ]

    n = LUT_SIZE - 1
    # .cube order: red index varies fastest, then green, then blue.
    for b in range(LUT_SIZE):
        for g in range(LUT_SIZE):
            for r in range(LUT_SIZE):
                out = transform([r / n, g / n, b / n])
                lines.append(" ".join(f"{c:.6f}" for c in out))

    dest = Path(__file__).resolve().parent.parent / "Soft_Pastel_Studio.cube"
    dest.write_text("\n".join(lines) + "\n")
    print(f"Wrote {dest} ({LUT_SIZE}^3 = {LUT_SIZE**3} entries)")


if __name__ == "__main__":
    main()
