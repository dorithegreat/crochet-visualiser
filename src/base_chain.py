import math
import drawsvg as draw

def circle_of_ellipses(n, radius=150, a=40, b=20, target_angle_deg=-45):
    """
    Draws n normal ellipses evenly spaced around a circle but leaves
    one slot (the slot nearest target_angle_deg) for the shaded ellipse.
    
    SVG uses +y downward, so:
      top-right = -45 degrees
      top       = -90 degrees
      right     =   0 degrees
      bottom    = +90 degrees
    
    Short axis points outward (radial). Long axis is tangent (rotate by θ + π/2).
    """
    d = draw.Drawing(400, 400, origin='center', display_inline=False)
    
    total_slots = n + 1
    angle_step = 2 * math.pi / total_slots  # radians
    
    # Convert target angle to radians (negative = upward in SVG)
    target_angle = math.radians(target_angle_deg)
    
    # Slot angles in radians
    slot_angles = [i * angle_step for i in range(total_slots)]

    # Normalize angle to [0, 2π)
    norm = lambda a: a % (2 * math.pi)
    target_norm = norm(target_angle)

    # Circular angular distance
    def circ_dist(a, b):
        diff = abs(a - b) % (2 * math.pi)
        return min(diff, 2 * math.pi - diff)

    # Pick the slot closest to the target direction
    shaded_index = min(range(total_slots),
                       key=lambda i: circ_dist(norm(slot_angles[i]), target_norm))
    shaded_angle = slot_angles[shaded_index]

    # Draw the normal ellipses
    for i, theta in enumerate(slot_angles):
        if i == shaded_index:
            continue
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)

        # Short axis radial → rotate by θ + 90°
        angle_deg = math.degrees(theta + math.pi/2)

        ell = draw.Ellipse(
            x, y, a, b,
            fill='none', stroke='white',
            transform=f'rotate({angle_deg},{x},{y})'
        )
        d.append(ell)

    # Draw shaded ellipse
    sx = radius * math.cos(shaded_angle)
    sy = radius * math.sin(shaded_angle)
    shaded_rot_deg = math.degrees(shaded_angle + math.pi/2)

    shaded = draw.Ellipse(
        sx, sy, a*0.6, b*0.6,
        fill='black', stroke='white',
        transform=f'rotate({shaded_rot_deg},{sx},{sy})'
    )
    d.append(shaded)

    return d


# Example usage: shaded ellipse will be placed at top-right
d = circle_of_ellipses(n=7, target_angle_deg=-45)
d.save_svg('ellipses_circle.svg')
