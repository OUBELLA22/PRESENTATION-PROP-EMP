#!/usr/bin/env python3
"""Draw the presentation illustrations as PNG files (standard library only).

Outputs (in ./images):
  car_harness.png      - stylised car with its wiring harness + detachable pigtail
  pigtail_diagram.png  - dashboard harness -> detachable pigtail -> instrumentation
"""
import math
import os
import struct
import zlib

S = 2  # supersampling factor (anti-aliasing)


def rgb(h):
    return bytes(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.W, self.H = w * S, h * S
        self.rows = [bytearray(rgb(bg) * self.W) for _ in range(self.H)]

    def poly(self, pts, color):
        c = rgb(color)
        pts = [(x * S, y * S) for x, y in pts]
        n = len(pts)
        ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys))), min(self.H, int(max(ys)) + 1)):
            yc = y + 0.5
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= yc < y2) or (y2 <= yc < y1):
                    xs.append(x1 + (yc - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            row = self.rows[y]
            for k in range(0, len(xs) - 1, 2):
                a = max(0, int(math.ceil(xs[k] - 0.5)))
                b = min(self.W, int(math.ceil(xs[k + 1] - 0.5)))
                if b > a:
                    row[3 * a:3 * b] = c * (b - a)

    def circle(self, cx, cy, r, color):
        self.poly([(cx + r * math.cos(t * math.pi / 40), cy + r * math.sin(t * math.pi / 40))
                   for t in range(80)], color)

    def rrect(self, x, y, w, h, r, color):
        pts = []
        for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0),
                           (x + r, y + h - r, 90), (x + r, y + r, 180)):
            for k in range(11):
                a = math.radians(a0 + 9 * k)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.poly(pts, color)

    def line(self, p, q, width, color):
        (x1, y1), (x2, y2) = p, q
        d = math.hypot(x2 - x1, y2 - y1) or 1
        nx, ny = -(y2 - y1) / d * width / 2, (x2 - x1) / d * width / 2
        self.poly([(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)], color)

    def path(self, pts, width, color, closed=False, caps=True):
        seq = pts + ([pts[0]] if closed else [])
        for a, b in zip(seq, seq[1:]):
            self.line(a, b, width, color)
        if caps:
            for p in seq:
                self.circle(p[0], p[1], width / 2, color)

    def png(self, filename):
        out = bytearray()
        for y in range(self.h):
            r0, r1 = self.rows[2 * y], self.rows[2 * y + 1]
            line = bytearray(3 * self.w)
            for c in range(3):
                a, b = r0[c::3], r1[c::3]
                line[c::3] = bytes((p + q + r + s + 2) >> 2
                                   for p, q, r, s in zip(a[0::2], a[1::2], b[0::2], b[1::2]))
            out += b"\x00" + line

        def chunk(t, d):
            c = struct.pack(">I", len(d)) + t + d
            return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

        data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(bytes(out), 9)) + chunk(b"IEND", b""))
        with open(filename, "wb") as f:
            f.write(data)


def smooth(pts, n=3, closed=True):
    """Chaikin corner cutting."""
    for _ in range(n):
        new = []
        m = len(pts)
        rng = range(m) if closed else range(m - 1)
        for i in rng:
            p, q = pts[i], pts[(i + 1) % m]
            new += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]),
                    (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
        pts = new if closed else [pts[0]] + new + [pts[-1]]
    return pts


NAVY, BLUE, CYAN, LIGHT = "0B2A4A", "0070AD", "12ABDB", "EEF5FB"
ORANGE, GREEN, WHITE = "E07B00", "2E9E5B", "FFFFFF"


def car_image(path):
    W, H = 1020, 810
    c = Canvas(W, H, NAVY)
    # soft concentric glow behind the car
    for r, col in ((380, "0C2E52"), (300, "0D3358"), (220, "0F3A63"), (140, "114270")):
        c.circle(500, 440, r, col)
    # ground
    c.rrect(60, 612, 900, 8, 4, "1B5C8C")
    # body
    body = smooth([(100, 530), (95, 450), (140, 415), (280, 410), (340, 310), (430, 272), (640, 272),
                   (740, 340), (880, 380), (925, 430), (930, 530)], 3)
    c.poly(body, "123F6B")
    c.path(body, 6, CYAN, closed=True)
    # windows
    c.poly(smooth([(355, 400), (398, 318), (470, 292), (522, 292), (522, 400)], 2), "1B5C8C")
    c.poly(smooth([(548, 292), (630, 292), (702, 346), (728, 400), (548, 400)], 2), "1B5C8C")
    # headlight
    c.circle(902, 432, 15, "FFF3B0")
    # wheels
    for cx in (260, 770):
        c.circle(cx, 535, 94, "0A2036")
        c.circle(cx, 535, 80, "050F1A")
        c.circle(cx, 535, 50, CYAN)
        c.circle(cx, 535, 42, "0B2A4A")
        c.circle(cx, 535, 12, CYAN)
    # harness inside the body
    route = [(150, 490), (420, 490), (560, 490), (690, 440), (790, 424)]
    c.path(route, 18, "0E4A78")
    c.path(route, 8, CYAN)
    for x, y in ((420, 490), (690, 440)):
        c.rrect(x - 20, y - 20, 40, 40, 8, WHITE)
        c.rrect(x - 12, y - 12, 24, 24, 5, BLUE)
    # branch wires to the dashboard
    c.path([(560, 490), (600, 455), (640, 455)], 5, "7FD6F2")
    # detachable pigtail leaving the car at the front
    pig = smooth([(790, 424), (860, 424), (945, 424), (985, 470), (985, 560)], 3, closed=False)
    c.path(pig, 14, "7A4300")
    c.path(pig, 8, ORANGE)
    c.rrect(962, 556, 46, 56, 8, WHITE)
    c.rrect(970, 564, 30, 40, 5, ORANGE)
    c.png(path)


def diagram_image(path):
    W, H = 2340, 200
    c = Canvas(W, H, WHITE)
    c.rrect(0, 0, W, H, 30, LIGHT)
    # dashboard harness
    c.rrect(40, 36, 660, 128, 22, BLUE)
    for k, col in enumerate((CYAN, WHITE, ORANGE, "7FD6F2", GREEN)):
        y = 60 + k * 22
        c.path([(70, y), (560, y)], 8, col)
        c.path([(560, y), (610, 100 + (k - 2) * 5)], 8, col)
    c.rrect(640, 80, 90, 40, 8, "07243F")      # socket-less harness end (no instrumentation connector)
    # pigtail cable
    cable = smooth([(730, 100), (900, 100), (1010, 148), (1210, 148), (1330, 52), (1450, 100), (1600, 100)],
                   3, closed=False)
    c.path(cable, 18, "7A4300")
    c.path(cable, 11, ORANGE)
    # plug at each end
    for x in (700, 1600):
        c.rrect(x, 70, 70, 60, 10, WHITE)
        c.rrect(x + 12, 82, 46, 36, 6, ORANGE)
        for k in range(3):
            c.circle(x + 26 + k * 16 - 8, 100, 4, WHITE)
    # instrumentation box with waveform
    c.rrect(1690, 36, 610, 128, 22, CYAN)
    wave = [(1730 + i * 6, 100 - 34 * math.sin(i / 5.5) * (0.65 + 0.35 * math.sin(i / 14))) for i in range(0, 92)]
    c.path(wave, 7, NAVY)
    c.png(path)


if __name__ == "__main__":
    os.makedirs("images", exist_ok=True)
    car_image("images/car_harness.png")
    diagram_image("images/pigtail_diagram.png")
    print("Wrote images/car_harness.png and images/pigtail_diagram.png")
