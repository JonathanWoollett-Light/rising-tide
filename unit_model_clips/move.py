"""move: a heavy, crouched walk. One cycle = two steps. The feet are driven by IK along paths whose speed is
continuous where a foot lands and lifts, so a planted foot stays planted and nothing snaps."""
import math

SECONDS = 1.75
STRIDE = 1.0          # how far a foot travels over the ground, front to back
LIFT = 0.5            # how high the ankle rises in the swing
STANCE = 0.6          # share of the cycle a foot spends on the ground
CROUCH = 0.2          # the pelvis rides this much lower than in the sculpt: legs that start 90 % straight need room
BEHIND = 0.8          # the stride is centred this far behind the hips (the sculpt's own rear foot is out in a lunge)
WIDTH = 1.15          # each foot's track, this far from the mid-line (the sculpt's feet: +1.5 and -0.56)


def wave(u, phase=0.0):
    return math.sin(2 * math.pi * (u + phase))


def foot_path(phase):
    """-> (dy, dz, pitch) of an ankle for a phase in [0, 1): stance (front to back at a constant speed), then a
    swing that leaves and arrives at that same speed (a cubic Hermite), so the path has no corner."""
    phase %= 1.0
    speed = STRIDE / STANCE                       # per unit of phase, backwards (+y)
    if phase < STANCE:
        return -STRIDE / 2 + speed * phase, 0.0, 0.0
    s = (phase - STANCE) / (1.0 - STANCE)
    m = speed * (1.0 - STANCE)                    # the end tangents, in swing units
    h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
    dy = h00 * (STRIDE / 2) + h10 * m + h01 * (-STRIDE / 2) + h11 * m
    lift = math.sin(math.pi * s) ** 2
    # the toes trail (point down) as the foot leaves the ground and lift before it lands on its heel
    return dy, LIFT * lift, 22.0 * math.sin(math.pi * s) ** 2 * (1 - s) - 9.0 * math.sin(math.pi * s) ** 2 * s


def clip(u, rig):
    pose = {}
    centre_y = rig.joint("pelvis")[1] + BEHIND
    step = math.cos(4 * math.pi * u)               # twice per cycle: +1 at each foot strike
    # the body first: IK needs to know where the hips are
    pose["pelvis.t"] = (0.12 * wave(u, 0.25), 0.0, -CROUCH - 0.06 * step)
    pose["pelvis"] = (3.0 + 1.5 * step, 2.5 * wave(u, 0.25), 6.0 * wave(u))
    pose["spine"] = (1.5 * math.cos(4 * math.pi * u + 0.6), -1.5 * wave(u, 0.25), -3.5 * wave(u))
    pose["chest"] = (0.0, -1.0 * wave(u, 0.25), -4.0 * wave(u))
    pose["neck"] = (2.5 * math.cos(4 * math.pi * u + 1.0), 0.0, 1.5 * wave(u))
    pose["head"] = (2.0 * math.cos(4 * math.pi * u + 1.6), 0.0, 1.0 * wave(u))
    for side, phase in (("l", u), ("r", u + 0.5)):
        dy, dz, pitch = foot_path(phase)
        rest = rig.joint(f"foot_{side}")
        x = rig.joint("pelvis")[0] + (WIDTH if side == "l" else -WIDTH)
        # the knees point forward and a little out: without a pole the far-folded right leg throws its knee sideways
        rig.ik(pose, f"thigh_{side}", f"shin_{side}", f"foot_{side}", (x, centre_y + dy, rest[2] + dz), (pitch, 0, 0),
               pole=(0.35 if side == "l" else -0.35, -1.0, 0.0))
    # arms swing against the legs; the raised left claw only a little
    pose["upperarm_r"] = (11.0 * wave(u), 0.0, 0.0)
    pose["forearm_r"] = (-6.0 + 8.0 * wave(u, -0.12), 0.0, 0.0)
    pose["upperarm_l"] = (-5.0 * wave(u), 0.0, 3.0 * wave(u, 0.2))
    pose["forearm_l"] = (-4.0 * wave(u, -0.12), 0.0, 0.0)
    # wings: a slow beat on every step, the outer parts trailing
    for side, sign in (("l", 1.0), ("r", -1.0)):
        pose[f"wing_{side}_1"] = (3.0 * step, -sign * 5.0 * math.cos(4 * math.pi * u + 0.3), 0.0)
        pose[f"wing_{side}_2"] = (0.0, -sign * 6.0 * math.cos(4 * math.pi * u - 0.5), 0.0)
        pose[f"wing_{side}_3"] = (0.0, -sign * 7.0 * math.cos(4 * math.pi * u - 1.2), 0.0)
    # the beard swings like pendulums, each bundle a little out of step
    for k, name in enumerate(("c", "l", "r")):
        lag = 0.08 * k
        pose[f"tentacle_{name}_1"] = (6.0 * math.cos(4 * math.pi * (u - 0.10 - lag)), 0.0, 3.0 * wave(u, -0.1 - lag))
        pose[f"tentacle_{name}_2"] = (9.0 * math.cos(4 * math.pi * (u - 0.22 - lag)), 0.0, 5.0 * wave(u, -0.22 - lag))
    return pose
