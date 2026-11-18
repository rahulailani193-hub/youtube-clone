import cv2, numpy as np, subprocess, random, math, os, json
from collections import deque

W, H, FPS = 640, 360, 24
OUT = "../media"
THUMBS = OUT + "/thumbs"
os.makedirs(THUMBS, exist_ok=True)
FONT = cv2.FONT_HERSHEY_SIMPLEX
AA = cv2.LINE_AA


def txt(img, s, org, scale=0.6, col=(255, 255, 255), th=1, center=False):
    x, y = org
    if center:
        (tw, _), _ = cv2.getTextSize(s, FONT, scale, th)
        x = int(x - tw / 2)
    cv2.putText(img, s, (int(x), int(y)), FONT, scale, col, th, AA)


def render(name, seconds, draw, tone=(220, 277.18, 329.63), thumb_t=8):
    frames = int(seconds * FPS)
    a, b, c = tone
    expr = (f"(0.05*sin(2*PI*{a}*t)+0.035*sin(2*PI*{b}*t)+0.03*sin(2*PI*{c}*t))"
            f"*(0.65+0.35*sin(2*PI*0.25*t))")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=44100:d={seconds}",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "27", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "48k", "-shortest", "-movflags", "+faststart",
           f"{OUT}/{name}.mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    tf = int(thumb_t * FPS)
    for f in range(frames):
        img = draw(f)
        if f == tf:
            cv2.imwrite(f"{THUMBS}/{name}.jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 88])
        p.stdin.write(img.tobytes())
    p.stdin.close()
    p.wait()
    print("rendered", name, seconds, "s")


# ---------------------------------------------------------------- GAMING
def pong():
    rng = random.Random(1)
    s = dict(bx=320., by=180., vx=6., vy=3., p1=180., p2=180., s1=0, s2=0)

    def reset(d):
        s.update(bx=320., by=180., vx=6. * d, vy=rng.choice([-3, -2, 2, 3]) * 1.0)

    def draw(f):
        img = np.full((H, W, 3), (35, 25, 20), np.uint8)
        for y in range(0, H, 20):
            cv2.line(img, (320, y), (320, y + 10), (90, 90, 90), 2)
        s["bx"] += s["vx"]; s["by"] += s["vy"]
        if s["by"] < 8 or s["by"] > H - 8:
            s["vy"] = -s["vy"]
        for key, x, side in (("p1", 20, -1), ("p2", 620, 1)):
            toward = (s["vx"] < 0) if side == -1 else (s["vx"] > 0)
            tgt = s["by"] if toward else 180
            d = tgt - s[key]
            s[key] += max(-3.8, min(3.8, d))
            s[key] = max(32, min(H - 32, s[key]))
        if s["bx"] <= 30 and s["vx"] < 0 and abs(s["by"] - s["p1"]) < 36:
            s["vx"] = min(11, -s["vx"] * 1.05); s["vy"] += (s["by"] - s["p1"]) * 0.12
        if s["bx"] >= 610 and s["vx"] > 0 and abs(s["by"] - s["p2"]) < 36:
            s["vx"] = max(-11, -s["vx"] * 1.05); s["vy"] += (s["by"] - s["p2"]) * 0.12
        s["vy"] = max(-8, min(8, s["vy"]))
        if s["bx"] < -10: s["s2"] += 1; reset(1)
        if s["bx"] > W + 10: s["s1"] += 1; reset(-1)
        cv2.rectangle(img, (16, int(s["p1"]) - 32), (24, int(s["p1"]) + 32), (255, 200, 80), -1)
        cv2.rectangle(img, (616, int(s["p2"]) - 32), (624, int(s["p2"]) + 32), (80, 200, 255), -1)
        cv2.circle(img, (int(s["bx"]), int(s["by"])), 7, (255, 255, 255), -1, AA)
        txt(img, str(s["s1"]), (260, 55), 1.4, (255, 200, 80), 3, True)
        txt(img, str(s["s2"]), (380, 55), 1.4, (80, 200, 255), 3, True)
        txt(img, "PONG  |  AI vs AI", (320, 345), 0.5, (170, 170, 170), 1, True)
        return img
    return draw


def snake():
    C, R, S = 32, 18, 20
    rng = random.Random(7)
    st = {}

    def new_game():
        st["body"] = [(5, 9), (4, 9), (3, 9)]
        st["food"] = place_food()
        st["score"] = 0

    def place_food():
        while True:
            p = (rng.randrange(C), rng.randrange(R))
            if p not in st.get("body", []):
                return p

    def bfs(start, goal, blocked):
        q = deque([start]); prev = {start: None}
        while q:
            cur = q.popleft()
            if cur == goal:
                path = []
                while cur != start:
                    path.append(cur); cur = prev[cur]
                return path[::-1]
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (cur[0] + dx, cur[1] + dy)
                if 0 <= n[0] < C and 0 <= n[1] < R and n not in blocked and n not in prev:
                    prev[n] = cur; q.append(n)
        return None

    new_game()

    def step():
        body = st["body"]; head = body[0]
        blocked = set(body[:-1])
        path = bfs(head, st["food"], blocked)
        if not path:
            path = bfs(head, body[-1], set(body[:-1]) - {body[-1]})
        if not path:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (head[0] + dx, head[1] + dy)
                if 0 <= n[0] < C and 0 <= n[1] < R and n not in blocked:
                    path = [n]; break
        if not path:
            new_game(); return
        nxt = path[0]
        body.insert(0, nxt)
        if nxt == st["food"]:
            st["score"] += 10; st["food"] = place_food()
        else:
            body.pop()

    def draw(f):
        if f % 3 == 0:
            step()
        img = np.zeros((H, W, 3), np.uint8)
        for x in range(C):
            for y in range(R):
                col = (40, 55, 30) if (x + y) % 2 else (46, 64, 36)
                cv2.rectangle(img, (x * S, y * S), (x * S + S, y * S + S), col, -1)
        fx, fy = st["food"]
        cv2.circle(img, (fx * S + 10, fy * S + 10), 7, (60, 60, 230), -1, AA)
        for i, (x, y) in enumerate(st["body"]):
            col = (120, 230, 120) if i == 0 else (60, 190, 80)
            cv2.rectangle(img, (x * S + 1, y * S + 1), (x * S + S - 1, y * S + S - 1), col, -1)
        txt(img, f"SCORE {st['score']}   LENGTH {len(st['body'])}", (10, 22), 0.55, (255, 255, 255), 1)
        return img
    return draw


def breakout():
    rng = random.Random(3)
    s = {}
    colors = [(60, 60, 230), (60, 150, 240), (60, 220, 240), (80, 200, 100), (230, 150, 70)]

    def bricks():
        return {(c, r) for c in range(10) for r in range(5)}

    def serve():
        s.update(bx=s["px"], by=315., vx=rng.choice([-3, 3]) * 1.0, vy=-4.5)

    s.update(px=320., score=0, lives=3, br=bricks())
    serve()

    def draw(f):
        img = np.full((H, W, 3), (30, 20, 28), np.uint8)
        for _ in range(2):
            s["bx"] += s["vx"] / 2 * 1.0; s["by"] += s["vy"] / 2 * 1.0
        if s["bx"] < 6 or s["bx"] > W - 6:
            s["vx"] = -s["vx"]; s["bx"] = max(6, min(W - 6, s["bx"]))
        if s["by"] < 6:
            s["vy"] = abs(s["vy"])
        d = s["bx"] - s["px"]
        s["px"] += max(-6, min(6, d * 0.5)) if s["vy"] > 0 else max(-3, min(3, (320 - s["px"]) * 0.05))
        s["px"] = max(40, min(W - 40, s["px"]))
        if s["vy"] > 0 and 325 <= s["by"] <= 335 and abs(s["bx"] - s["px"]) < 46:
            off = (s["bx"] - s["px"]) / 46
            sp = 5.6
            s["vx"] = off * 4.2; s["vy"] = -math.sqrt(max(sp ** 2 - s["vx"] ** 2, 4))
        c, r = int((s["bx"] - 30) // 58), int((s["by"] - 50) // 16)
        if (c, r) in s["br"]:
            s["br"].discard((c, r)); s["vy"] = -s["vy"]; s["score"] += 10
            if not s["br"]:
                s["br"] = bricks(); serve()
        if s["by"] > H + 10:
            s["lives"] -= 1
            if s["lives"] < 0:
                s.update(lives=3, score=0, br=bricks())
            serve()
        for (c, r) in s["br"]:
            x, y = 30 + c * 58, 50 + r * 16
            cv2.rectangle(img, (x + 1, y + 1), (x + 56, y + 14), colors[r], -1)
        cv2.rectangle(img, (int(s["px"]) - 40, 330), (int(s["px"]) + 40, 340), (230, 230, 230), -1)
        cv2.circle(img, (int(s["bx"]), int(s["by"])), 6, (255, 255, 255), -1, AA)
        txt(img, f"SCORE {s['score']}", (12, 22), 0.55)
        txt(img, f"LIVES {max(s['lives'], 0)}", (W - 100, 22), 0.55)
        return img
    return draw


# ---------------------------------------------------------------- LEARNING
def grad_bg(top, bottom):
    ys = np.linspace(0, 1, H)[:, None, None]
    bg = (np.array(top) * (1 - ys) + np.array(bottom) * ys).astype(np.uint8)
    return np.repeat(bg, W, axis=1)


BG_BLUE = grad_bg((90, 40, 25), (50, 25, 15))


def times_tables():
    per = 7.0
    pal = [(80, 200, 255), (120, 230, 140), (255, 180, 90), (200, 140, 255)]

    def draw(f):
        t = f / FPS
        n = 2 + int(t // per) % 8
        lt = t % per
        img = BG_BLUE.copy()
        col = pal[n % 4]
        txt(img, f"Multiplication Table of {n}", (320, 45), 0.95, (255, 255, 255), 2, True)
        shown = max(0, min(10, int((lt - 0.4) / 0.55) + 1)) if lt >= 0.4 else 0
        for k in range(1, 11):
            if k <= shown:
                y = 85 + k * 25
                hi = (k == shown)
                c = col if hi else (230, 230, 230)
                txt(img, f"{n} x {k} = {n * k}", (60, y), 0.7 if hi else 0.62, c, 2 if hi else 1)
        for k in range(1, shown + 1):
            for j in range(n):
                cx = 330 + (k - 1) * 28 + 10
                cy = 100 + j * 24 if n <= 9 else 100
                cv2.circle(img, (cx, cy), 8, col, -1, AA)
        txt(img, "each column = one more group of n", (470, 345), 0.45, (190, 190, 190), 1, True)
        return img
    return draw


def pythagoras():
    triples = [(3, 4, 5, 22), (12, 5, 13, 9), (15, 8, 17, 6)]
    per = 20.0
    cols = [(230, 160, 80), (110, 200, 120), (80, 150, 250)]

    def lerp(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    def sq(img, pts, col, label, t):
        p0, p1, p2, p3 = pts  # p0-p1 is the triangle edge, p3/p2 are outward corners
        q2 = lerp(p1, p2, t); q3 = lerp(p0, p3, t)
        poly = np.array([p0, p1, q2, q3], np.int32)
        ov = img.copy(); cv2.fillPoly(ov, [poly], col)
        cv2.addWeighted(ov, 0.55, img, 0.45, 0, img)
        cv2.polylines(img, [poly], True, col, 2, AA)
        if t > 0.95:
            ctr = np.mean(poly, axis=0)
            txt(img, label, (ctr[0], ctr[1] + 6), 0.6, (255, 255, 255), 2, True)

    def draw(f):
        t = f / FPS
        i = int(t // per) % 3
        lt = t % per
        a, b, c, s = triples[i]
        img = BG_BLUE.copy()
        txt(img, "Pythagorean Theorem", (320, 38), 0.9, (255, 255, 255), 2, True)
        x0, y0 = 300 + (40 if i == 0 else 20), 210 + (10 if i == 0 else 0)
        P0 = (x0, y0); A = (x0 + a * s, y0); B = (x0, y0 - b * s)
        prog = min(1, lt / 2)
        cv2.line(img, P0, (int(lerp(P0, A, prog)[0]), int(lerp(P0, A, prog)[1])), (255, 255, 255), 2, AA)
        cv2.line(img, P0, (int(lerp(P0, B, prog)[0]), int(lerp(P0, B, prog)[1])), (255, 255, 255), 2, AA)
        if lt > 1.5:
            cv2.line(img, B, A, (255, 255, 255), 2, AA)
            cv2.rectangle(img, (x0 + 1, y0 - 12), (x0 + 12, y0 - 1), (255, 255, 255), 1)
        g = lambda a_, b_: max(0, min(1, (lt - a_) / (b_ - a_)))
        # squares: on leg a (below), leg b (left), hypotenuse (outward)
        sq(img, [P0, A, (A[0], y0 + a * s), (x0, y0 + a * s)], cols[0], f"a2={a*a}", g(2.5, 4.5))
        sq(img, [P0, B, (x0 - b * s, B[1]), (x0 - b * s, y0)], cols[1], f"b2={b*b}", g(4.5, 6.5))
        n = (b * s, -a * s)
        sq(img, [B, A, (A[0] + n[0], A[1] + n[1]), (B[0] + n[0], B[1] + n[1])], cols[2], f"c2={c*c}", g(6.5, 8.5))
        lines = [(8, f"Right triangle: a = {a}, b = {b}"), (11, "a^2 + b^2 = c^2"),
                 (14, f"{a*a} + {b*b} = {c*c}"), (17, f"so  c = {c}")]
        for k, (ts, s_) in enumerate(lines):
            if lt >= ts:
                txt(img, s_, (20, 80 + k * 28), 0.6, (255, 255, 255) if k < 3 else (120, 230, 140), 2 if k == 3 else 1)
        return img
    return draw


def binary():
    def draw(f):
        t = f / FPS
        v = int(t / 0.75) % 256
        img = BG_BLUE.copy()
        txt(img, "Counting in Binary", (320, 45), 0.95, (255, 255, 255), 2, True)
        txt(img, f"Decimal: {v}", (320, 110), 1.1, (80, 200, 255), 2, True)
        on = []
        for i in range(8):
            bit = 7 - i
            x = 40 + i * 70
            lit = (v >> bit) & 1
            col = (80, 220, 255) if lit else (70, 60, 55)
            cv2.rectangle(img, (x, 150), (x + 58, 230), col, -1)
            cv2.rectangle(img, (x, 150), (x + 58, 230), (255, 255, 255), 2)
            txt(img, str(lit), (x + 29, 203), 1.2, (30, 20, 15) if lit else (150, 150, 150), 2, True)
            txt(img, str(2 ** bit), (x + 29, 255), 0.55, (210, 210, 210), 1, True)
            if lit: on.append(str(2 ** bit))
        formula = " + ".join(on) + f" = {v}" if on else "0 = 0"
        txt(img, formula, (320, 310), 0.7, (255, 255, 255), 1, True)
        txt(img, "Each bit is worth double the one to its right", (320, 340), 0.45, (190, 190, 190), 1, True)
        return img
    return draw


# ---------------------------------------------------------------- SPORTS
def basketball():
    G = 0.35; T = 40; X0, Y0 = 115., 235.; HX, HY = 520, 150
    vy = (HY - Y0 - 0.5 * G * T * T) / T
    s = dict(x=X0, y=Y0, vx=0., vy=0., made=0, shots=0, flash=0, label="")

    def draw(f):
        k, lf = divmod(f, 96)
        made = (k * 7 + 3) % 10 < 7
        img = grad_bg((70, 40, 30), (35, 30, 30))
        cv2.rectangle(img, (0, 322), (W, H), (60, 110, 170), -1)
        cv2.line(img, (0, 322), (W, 322), (200, 220, 240), 2)
        # shooter
        if lf < 20:
            s["x"], s["y"] = X0, 258 - lf * 1.15
        elif lf < 60:
            t = lf - 20
            tx = HX if made else 497
            vx = (tx - X0) / T
            s["x"] = X0 + vx * t; s["y"] = Y0 + vy * t + 0.5 * G * t * t
            if lf == 59:
                s.update(shots=s["shots"] + 1)
                if made:
                    s.update(made=s["made"] + 1, flash=40, label="SWISH!", vx=0.6, vy=vy + G * T)
                else:
                    s.update(flash=40, label="RIM OUT", vx=-3.5, vy=-3.0)
        elif lf < 95:
            s["vy"] += G; s["x"] += s["vx"]; s["y"] += s["vy"]
            if s["y"] > 312:
                s["y"] = 312; s["vy"] = -s["vy"] * 0.55; s["vx"] *= 0.8
        # figure
        cv2.circle(img, (100, 170), 14, (200, 220, 240), -1, AA)
        cv2.line(img, (100, 184), (100, 250), (200, 220, 240), 4, AA)
        cv2.line(img, (100, 250), (88, 320), (200, 220, 240), 4, AA)
        cv2.line(img, (100, 250), (115, 320), (200, 220, 240), 4, AA)
        hand = (int(s["x"]) - 8, int(s["y"])) if lf < 20 else (126, 178)
        cv2.line(img, (100, 205), hand, (200, 220, 240), 4, AA)
        # hoop
        cv2.rectangle(img, (545, 95), (551, 178), (235, 235, 235), -1)
        for i in range(6):
            cv2.line(img, (500 + i * 8, 150), (506 + i * 5, 185), (230, 230, 230), 1, AA)
        cv2.line(img, (500, 150), (540, 150), (40, 110, 240), 4, AA)
        cv2.circle(img, (int(s["x"]), int(s["y"])), 10, (40, 130, 240), -1, AA)
        cv2.circle(img, (int(s["x"]), int(s["y"])), 10, (20, 50, 100), 1, AA)
        txt(img, f"MADE {s['made']} / {s['shots']}", (14, 28), 0.7, (255, 255, 255), 2)
        txt(img, "FREE THROW PRACTICE", (W - 14 - 230, 28), 0.55, (200, 200, 200), 1)
        if s["flash"] > 0:
            s["flash"] -= 1
            txt(img, s["label"], (320, 110), 1.3, (80, 230, 120) if s["label"] == "SWISH!" else (80, 120, 240), 3, True)
        return img
    return draw


def race():
    tau = 1.2; LEN = 16 * FPS
    heats = []
    for h in range(5):
        r = random.Random(100 + h)
        v = [r.uniform(10.6, 12.0) for _ in range(4)]
        fin = []
        for vv in v:
            rt = 0.0
            while vv * (rt - tau * (1 - math.exp(-rt / tau))) < 100:
                rt += 0.01
            fin.append(rt)
        heats.append((v, fin))
    lane_cols = [(80, 80, 240), (240, 160, 70), (80, 220, 240), (120, 220, 120)]

    def draw(f):
        h, lf = divmod(f, LEN)
        h %= 5
        v, fin = heats[h]
        t = lf / FPS
        rt = max(0.0, t - 3)
        img = np.full((H, W, 3), (45, 60, 160), np.uint8)
        for i in range(4):
            y = 90 + i * 55
            cv2.rectangle(img, (0, y - 25), (W, y + 25), (55, 75, 185), -1)
            cv2.line(img, (0, y + 27), (W, y + 27), (255, 255, 255), 2)
        cv2.line(img, (60, 62), (60, 310), (255, 255, 255), 3)
        for j in range(12):
            cv2.rectangle(img, (580, 62 + j * 21), (590, 62 + j * 21 + 10), (255, 255, 255), -1)
        order = np.argsort(fin)
        for i in range(4):
            y = 90 + i * 55
            d = min(100, v[i] * (rt - tau * (1 - math.exp(-rt / tau)))) if rt > 0 else 0
            x = 60 + d * 5.2
            sw = math.sin(rt * 14 + i) * 9 if 0 < rt < fin[i] else 0
            cv2.line(img, (int(x), y), (int(x - 10 + sw), y + 14), (255, 255, 255), 3, AA)
            cv2.line(img, (int(x), y), (int(x - 10 - sw), y + 14), (255, 255, 255), 3, AA)
            cv2.circle(img, (int(x), y), 12, lane_cols[i], -1, AA)
            cv2.circle(img, (int(x), y), 12, (255, 255, 255), 2, AA)
            txt(img, str(i + 1), (x, y + 5), 0.5, (255, 255, 255), 1, True)
            if rt >= fin[i]:
                txt(img, f"{fin[i]:.2f}s", (595, y + 5), 0.5, (255, 255, 255), 1)
        txt(img, f"100m DASH - HEAT {h + 1}", (16, 30), 0.75, (255, 255, 255), 2)
        if t < 1.5:
            txt(img, "ON YOUR MARKS", (320, 345), 0.8, (255, 255, 255), 2, True)
        elif t < 3:
            txt(img, "SET...", (320, 345), 0.8, (80, 220, 255), 2, True)
        elif rt < 1:
            txt(img, "GO!", (320, 345), 0.9, (80, 255, 120), 3, True)
        elif rt > max(fin) + 0.3:
            txt(img, f"WINNER: LANE {order[0] + 1}  ({fin[order[0]]:.2f}s)", (320, 345), 0.75, (80, 255, 255), 2, True)
        else:
            txt(img, f"{rt:5.2f} s", (320, 345), 0.8, (255, 255, 255), 2, True)
        return img
    return draw


def penalty():
    rng = random.Random(21)
    kicks = []
    for _ in range(40):
        tx = rng.uniform(-120, 120); ty = rng.uniform(85, 185)
        dive = max(-135, min(135, tx + rng.uniform(-95, 95)))
        kicks.append((tx, ty, dive, abs(dive - tx) < 50))
    st = dict(goals=0, saves=0, counted=-1)

    def draw(f):
        k, lf = divmod(f, 96)
        tx, ty, dive, saved = kicks[k % 40]
        img = grad_bg((95, 150, 70), (50, 110, 45))
        # stripes
        for i in range(0, H, 40):
            cv2.rectangle(img, (0, i), (W, i + 20), (60, 120, 52), -1)
        gx0, gx1, gy0, gy1 = 150, 490, 60, 220
        ov = img.copy(); cv2.rectangle(ov, (gx0, gy0), (gx1, gy1), (40, 40, 40), -1)
        cv2.addWeighted(ov, 0.45, img, 0.55, 0, img)
        for x in range(gx0, gx1, 17): cv2.line(img, (x, gy0), (x, gy1), (170, 170, 170), 1)
        for y in range(gy0, gy1, 16): cv2.line(img, (gx0, y), (gx1, y), (170, 170, 170), 1)
        cv2.rectangle(img, (gx0, gy0), (gx1, gy1), (255, 255, 255), 5)
        cv2.circle(img, (320, 320), 3, (255, 255, 255), -1)
        # keeper
        dv = 0.0
        if lf >= 26:
            dv = min(1, (lf - 26) / 14)
        kx = 320 + dive * dv
        ky = 178 - 18 * math.sin(math.pi * dv)
        cv2.rectangle(img, (int(kx) - 16, int(ky) - 30), (int(kx) + 16, int(ky) + 30), (40, 190, 250), -1)
        cv2.circle(img, (int(kx), int(ky) - 40), 12, (200, 220, 240), -1, AA)
        reach = 22 + 40 * dv
        cv2.line(img, (int(kx), int(ky) - 15), (int(kx - reach), int(ky - 15 - 22 * dv)), (40, 190, 250), 6, AA)
        cv2.line(img, (int(kx), int(ky) - 15), (int(kx + reach), int(ky - 15 - 22 * dv)), (40, 190, 250), 6, AA)
        # ball
        sx, sy = 320, 330; ex, ey = 320 + tx, ty
        if lf < 24:
            bx, by, r = sx, sy, 16
        elif lf < 40:
            p = (lf - 24) / 16
            bx = sx + (ex - sx) * p; by = sy + (ey - sy) * p; r = 16 - 7 * p
        else:
            bx, by, r = ex, ey, 9
            if saved:
                bx = ex + (-28 if dive < 0 else 28); by = ey + 38; r = 10
        cv2.circle(img, (int(bx), int(by)), int(r), (245, 245, 245), -1, AA)
        cv2.circle(img, (int(bx), int(by)), int(r), (30, 30, 30), 1, AA)
        if lf == 44 and st["counted"] != k:
            st["counted"] = k
            if saved: st["saves"] += 1
            else: st["goals"] += 1
        txt(img, f"GOALS {st['goals']}   SAVES {st['saves']}", (14, 28), 0.65, (255, 255, 255), 2)
        txt(img, f"PENALTY {k + 1}", (W - 150, 28), 0.6, (255, 255, 255), 1)
        if lf >= 44:
            txt(img, "SAVED!" if saved else "GOAL!", (320, 275), 1.4, (80, 120, 245) if saved else (80, 240, 120), 3, True)
        return img
    return draw


CLIPS = [
    # file,        seconds, factory,       tone,                   thumb second
    ("gaming-pong",           120, pong,         (196, 246.94, 293.66), 12),
    ("gaming-snake",          120, snake,        (220, 277.18, 329.63), 30),
    ("gaming-breakout",        90, breakout,     (174.6, 220, 261.63),  20),
    ("learning-times-tables",  56, times_tables, (261.63, 329.63, 392), 11),
    ("learning-pythagoras",    60, pythagoras,   (233.08, 293.66, 349.2), 13),
    ("learning-binary",        50, binary,       (246.94, 311.13, 370), 24),
    ("sports-basketball",     100, basketball,   (196, 261.63, 329.63), 10),
    ("sports-sprint",          80, race,         (220, 261.63, 329.63), 8),
    ("sports-penalty",         88, penalty,      (207.65, 261.63, 311.13), 13),
]

if __name__ == "__main__":
    import sys
    only = sys.argv[1:]
    for name, secs, fac, tone, th in CLIPS:
        if only and name not in only: continue
        render(name, secs, fac(), tone, th)
