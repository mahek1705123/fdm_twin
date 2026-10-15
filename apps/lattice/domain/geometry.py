"""Schematic lattice geometry in unit-cell coordinates (y points down). Pure Python."""
import math


def _ring(cx, cy, r, a0):
    return [(cx + r * math.cos(a0 + k * math.pi / 8), cy + r * math.sin(a0 + k * math.pi / 8)) for k in range(17)]


def tile(topology: str, angle: float, n: int = 4) -> list[list[tuple[float, float]]]:
    """n x n tiling as a list of polylines. Used for the dashboard drawing and the ANSYS beam model."""
    out, a = [], abs(angle)
    for j in range(n):
        for i in range(n):
            if topology == "Honeycomb":
                ox, oy = i + (0.5 if j % 2 else 0), j * 0.75
                pts = [(.5, 0), (1, .25), (1, .75), (.5, 1), (0, .75), (0, .25), (.5, 0)]
                out.append([(x + ox, y + oy) for x, y in pts])
            elif topology == "Auxetic_Honeycomb":
                k = 0.10 + 0.22 * a / 20
                pts = [(0, 0), (.5, k), (1, 0), (1, 1), (.5, 1 - k), (0, 1), (0, 0)]
                out.append([(x + i, y + j) for x, y in pts])
            elif topology == "Star_Reentrant":
                k = 0.28
                pts = [(0, 0), (.5, k), (1, 0), (1 - k, .5), (1, 1), (.5, 1 - k), (0, 1), (k, .5), (0, 0)]
                out.append([(x + i, y + j) for x, y in pts])
            else:  # Chiral: rings joined by tangent ligaments (the angle skews the ligaments)
                al, r, cx, cy = math.radians(-80 + angle * 0.5), 0.13, i + .5, j + .5
                out.append(_ring(cx, cy, r, al))

                def pt(x, y, t):
                    return (x + r * math.cos(t), y + r * math.sin(t))

                if i < n - 1:
                    out.append([pt(cx, cy, al), pt(cx + 1, cy, al + math.pi)])
                if j < n - 1:
                    out.append([pt(cx, cy, al - math.pi / 2), pt(cx, cy - 1, al + math.pi / 2)])
    return out


def beams(paths):
    """Collapse polylines into unique keypoints and beam segments (indices are 1-based)."""
    ids, pts, segs = {}, [], set()

    def kid(p):
        key = (round(p[0], 4), round(p[1], 4))
        if key not in ids:
            ids[key] = len(ids) + 1
            pts.append(p)
        return ids[key]

    for path in paths:
        for p, q in zip(path, path[1:]):
            a, b = kid(p), kid(q)
            if a != b:
                segs.add((min(a, b), max(a, b)))
    return pts, sorted(segs)
