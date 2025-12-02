# arch_ellipses.py
import math
import drawsvg as draw



def angle_from_origin(point):
    """
    Returns the angle (in degrees) between the positive x-axis
    and the vector from (0,0) to (x,y).
    """
    x, y = point
    if x == 0 and y == 0:
        raise ValueError("Angle is undefined for point (0,0).")
    return math.degrees(math.atan2(y, x))

# ---------- Internal utility functions ----------
def bezier_point(P0, P1, P2, P3, t):
    u = 1 - t
    b0 = u**3
    b1 = 3*u**2*t
    b2 = 3*u*t**2
    b3 = t**3
    x = b0*P0[0] + b1*P1[0] + b2*P2[0] + b3*P3[0]
    y = b0*P0[1] + b1*P1[1] + b2*P2[1] + b3*P3[1]
    return x, y

def bezier_derivative(P0, P1, P2, P3, t):
    u = 1 - t
    dx = 3*((P1[0]-P0[0])*u*u + 2*(P2[0]-P1[0])*u*t + (P3[0]-P2[0])*t*t)
    dy = 3*((P1[1]-P0[1])*u*u + 2*(P2[1]-P1[1])*u*t + (P3[1]-P2[1])*t*t)
    return dx, dy

def bezier_length(P0, P1, P2, P3, n_intervals=1000):
    if n_intervals % 2 == 1: n_intervals += 1
    h = 1.0 / n_intervals
    s = 0.0
    def speed(t):
        dx, dy = bezier_derivative(P0, P1, P2, P3, t)
        return math.hypot(dx, dy)
    s += speed(0) + speed(1)
    for i in range(1, n_intervals):
        coef = 4 if i % 2 == 1 else 2
        s += coef * speed(i*h)
    return s * (h/3.0)

def find_h_for_length(P0, P3, desired_length, h_min=0.0, h_max=1000.0, tol=1e-6, max_iter=60, simpson_intervals=1000):
    x0, y0 = P0
    x3, y3 = P3
    c = math.hypot(x3 - x0, y3 - y0)
    if desired_length < c - 1e-12:
        raise ValueError("Desired length smaller than chord distance between endpoints.")
    def length_for_h(h):
        dx = x3 - x0
        dy = y3 - y0
        angle = math.atan2(dy, dx)
        cosA = math.cos(-angle)
        sinA = math.sin(-angle)
        def to_local(px, py):
            tx = px - x0
            ty = py - y0
            return tx*cosA - ty*sinA, tx*sinA + ty*cosA
        P0_local = (0.0, 0.0)
        P3_local = (c, 0.0)
        P1_local = (0.25*c, h)
        P2_local = (0.75*c, h)
        return bezier_length(P0_local, P1_local, P2_local, P3_local, n_intervals=simpson_intervals)
    lo = h_min
    hi = h_max
    for _ in range(max_iter):
        mid = 0.5*(lo+hi)
        Lmid = length_for_h(mid)
        if abs(Lmid - desired_length) <= tol:
            return mid
        if Lmid < desired_length:
            lo = mid
        else:
            hi = mid
    return 0.5*(lo+hi)

def sample_bezier_by_arclength(P0, P1, P2, P3, n_samples=100, sample_grid=5000):
    M = sample_grid
    ts = [i / M for i in range(M + 1)]
    pts = [bezier_point(P0, P1, P2, P3, t) for t in ts]
    ders = [bezier_derivative(P0, P1, P2, P3, t) for t in ts]
    speeds = [math.hypot(dx, dy) for dx, dy in ders]
    cum = [0.0]
    for i in range(1, M+1):
        seg = 0.5*(speeds[i-1]+speeds[i])*(1.0/M)
        cum.append(cum[-1]+seg)
    total = cum[-1]
    samples = []
    for k in range(n_samples):
        s_target = (k/(n_samples-1))*total if n_samples>1 else 0.0
        lo_idx = 0
        hi_idx = M
        while lo_idx<hi_idx:
            mid = (lo_idx+hi_idx)//2
            if cum[mid]<s_target:
                lo_idx=mid+1
            else:
                hi_idx=mid
        idx = max(1, lo_idx)
        s0, s1 = cum[idx-1], cum[idx]
        t0, t1 = ts[idx-1], ts[idx]
        if s1 - s0 == 0:
            t_est = t0
        else:
            t_est = t0 + (s_target - s0)*(t1 - t0)/(s1 - s0)
        x, y = bezier_point(P0, P1, P2, P3, t_est)
        dx, dy = bezier_derivative(P0, P1, P2, P3, t_est)
        samples.append((t_est, (x,y), (dx,dy)))
    return samples

# ---------- Public function ----------
def draw_chain(drawing, P0, P3, desired_length=100.0, n_ellipses=30, dependent = 0):
    """
    Places 'n_ellipses' along an arch between points P0 and P3 in the given drawsvg Drawing.
    
    Parameters:
    - drawing: drawsvg.Drawing instance
    - P0, P3: tuple (x, y) start and end points
    - desired_length: approximate curve length
    - n_ellipses: number of ellipses along the curve
    """
    h = find_h_for_length(P0, P3, desired_length)
    x0, y0 = P0
    x3, y3 = P3
    dx = x3 - x0
    dy = y3 - y0
    angle = math.atan2(dy, dx)
    c = math.hypot(dx, dy)
    cosA = math.cos(angle)
    sinA = math.sin(angle)
    def to_world(lx, ly):
        wx = lx*cosA - ly*sinA + x0
        wy = lx*sinA + ly*cosA + y0
        return wx, wy
    P0_local = (0.0, 0.0)
    P1_local = (0.25*c, h)
    P2_local = (0.75*c, h)
    P3_local = (c, 0.0)
    # sample points along arc-length
    samples = sample_bezier_by_arclength(
        P0_local, P1_local, P2_local, P3_local,
        n_samples=n_ellipses + 2   # <-- add two extra so trimmed list still has n_ellipses
    )
    samples = samples[1:-1] 
    # ellipse shape
    shape = draw.Group()
    shape.append(draw.Ellipse(0, 0, 12, 5, stroke='black', fill='none', stroke_width=1))
    for t_local, (lx,ly), (dx_local,dy_local) in samples:
        wx, wy = to_world(lx, ly)
        dxw = dx_local * cosA - dy_local * sinA
        dyw = dx_local * sinA + dy_local * cosA
        ang = math.degrees(math.atan2(dyw, dxw))
        drawing.append(draw.Use(shape, 0, 0, transform=f"translate({wx},{wy}) rotate({ang})"))

    samples = sample_bezier_by_arclength(
        P0_local, P1_local, P2_local, P3_local,
        n_samples=  dependent + 2   # <-- add two extra so trimmed list still has n_ellipses
    )
    samples = samples[1:-1] 

    res = []
    for t_local, (lx,ly), (dx_local,dy_local) in samples:
        wx, wy = to_world(lx, ly)
        dxw = dx_local * cosA - dy_local * sinA
        dyw = dx_local * sinA + dy_local * cosA
        ang = math.degrees(math.atan2(dyw, dxw))
        res.append((wx, wy, ang + 90))

    return res


def draw_base_chain(drawing, n, radius=40, a=10, b=4, target_angle_deg=-45):
    """
    Adds n normal ellipses + 1 shaded ellipse to an existing drawsvg.Drawing.

    Parameters
    ----------
    drawing : drawsvg.Drawing
        The drawing to append ellipses into.
    n : int
        Number of normal ellipses. Total ellipses = n + 1.
    radius : float
        Distance from the origin to ellipse centers.
    a : float
        Semi-major axis (long radius).
    b : float
        Semi-minor axis (short radius).
    target_angle_deg : float
        Direction (in SVG coordinate degrees) where the shaded ellipse should appear.
        (SVG: negative angles go upward, so top-right = -45°)
    """
        
    total_slots = n + 1
    angle_step = 2 * math.pi / total_slots
    target_angle = math.radians(target_angle_deg)

    # Slot angles
    slot_angles = [i * angle_step for i in range(total_slots)]

    # Normalize helper
    norm = lambda a: a % (2 * math.pi)

    # Circular distance
    def circ_dist(a, b):
        diff = abs(a - b) % (2 * math.pi)
        return min(diff, 2 * math.pi - diff)

    # Find the slot closest to the desired angle
    shaded_index = min(
        range(total_slots),
        key=lambda i: circ_dist(norm(slot_angles[i]), norm(target_angle))
    )
    shaded_angle = slot_angles[shaded_index]

    # --- Draw normal ellipses ---
    for i, theta in enumerate(slot_angles):
        if i == shaded_index:
            continue

        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        angle_deg = math.degrees(theta + math.pi/2)

        ell = draw.Ellipse(
            x, y, a, b,
            fill='none', stroke='black',
            transform=f'rotate({angle_deg},{x},{y})'
        )
        drawing.append(ell)

    # --- Draw shaded ellipse ---
    sx = radius * math.cos(shaded_angle)
    sy = radius * math.sin(shaded_angle)
    shaded_rot = math.degrees(shaded_angle + math.pi/2)

    shaded = draw.Ellipse(
        sx, sy, a * 0.6, b * 0.6,
        fill='black', stroke='black',
        transform=f'rotate({shaded_rot},{sx},{sy})'
    )
    drawing.append(shaded)

    return (sx, sy)

def draw_starting_chain(drawing, n, start, rx = 8, ry = 4, spacing = 19, 
            stroke='black', fill='none'):
    """
    Add n ellipses of radii (rx, ry) to an existing drawsvg.Drawing.
    Ellipses are placed in a line starting at start=(x,y) and oriented
    directly away from (0,0). `spacing` = distance between ellipse centers.
    """
    x, y = start

    # Unit direction vector away from the origin
    L = math.hypot(x, y)
    if L == 0:
        raise ValueError("start must not be (0,0)")
    ux, uy = x / L, y / L

    # Angle comes from the helper function
    angle_deg = angle_from_origin((x, y))

    first_cx = x + (0.5 * spacing + 5) * ux
    first_cy = y + (0.5 * spacing + 5) * uy

    centers = [
        (first_cx + i * spacing * ux, first_cy + i * spacing * uy)
        for i in range(n)
    ]

    # Draw ellipses
    for cx, cy in centers:
        e = draw.Ellipse(
            cx, cy, rx, ry,
            fill=fill, stroke=stroke,
            transform=f'rotate({angle_deg},{cx},{cy})'
        )
        drawing.append(e)


def draw_cluster_lines(d, P0, P1, n_lines=3, n_strikes=1,
                    curve_factor=0.25,
                    stroke='black', stroke_width=2):

    x0, y0 = P0
    x1, y1 = P1

    # Direction vector
    dx = x1 - x0
    dy = y1 - y0
    L = math.hypot(dx, dy)

    # Unit direction
    ux = dx / L
    uy = dy / L

    # Perpendicular (for lateral offsets)
    px = -uy
    py = ux

    # Symmetric offsets
    mid = (n_lines - 1) / 2
    offsets = [(i - mid) for i in range(n_lines)]
    if n_lines > 1:
        m = max(abs(o) for o in offsets)
        offsets = [o / m for o in offsets]
    else:
        offsets = [0]

    for off in offsets:
        lateral = off * curve_factor * L

        # Control point (midpoint + lateral offset)
        cx = (x0 + x1)/2 + px * lateral
        cy = (y0 + y1)/2 + py * lateral

        # Draw the curve
        p = draw.Path(stroke=stroke, fill='none', stroke_width=stroke_width)
        p.M(x0, y0)
        p.Q(cx, cy, x1, y1)
        d.append(p)

        # -------- FIX: strikes must follow each curved line, not the center line --------
        def bezier_point(t):
            # Quadratic Bézier interpolation
            x = (1-t)**2 * x0 + 2*(1-t)*t * cx + t**2 * x1
            y = (1-t)**2 * y0 + 2*(1-t)*t * cy + t**2 * y1
            return x, y
        # -------------------------------------------------------------------------------

        spacing = 1/(n_strikes+1)
        for k in range(n_strikes):
            t = (k+1)*spacing

            # Corrected: get the actual curve point
            bx, by = bezier_point(t)

            # Strike length
            sl = 0.15 * L

            # Strike endpoints (perpendicular)
            sx1 = bx - px * sl/2
            sy1 = by - py * sl/2
            sx2 = bx + px * sl/2
            sy2 = by + py * sl/2

            strike = draw.Path(stroke=stroke, fill='none', stroke_width=stroke_width)
            strike.M(sx1, sy1)
            strike.L(sx2, sy2)
            d.append(strike)

