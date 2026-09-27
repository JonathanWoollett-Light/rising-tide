"""attack: the raised left claw. It rears back and coils (wings spreading for balance), then lunges - the claw
raking forward and down - and recovers. Starts and ends in the sculpt's pose; the rear foot slides up with the lunge."""
import math

SECONDS = 2.25


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def phases(u):
    """-> (coil, strike): coil rises over the wind-up and is spent by the strike; strike snaps in and eases out."""
    coil = smooth(u / 0.34) * (1.0 - smooth((u - 0.34) / 0.12))
    strike = smooth((u - 0.36) / 0.18) * (1.0 - smooth((u - 0.60) / 0.34))
    return coil, strike


def clip(u, rig):
    coil, strike = phases(u)
    pose = {"pelvis.t": (0.0, 0.22 * coil - 0.55 * strike, -0.08 * coil - 0.28 * strike),
            "pelvis": (-4.0 * coil + 9.0 * strike, 0.0, 8.0 * coil - 10.0 * strike),
            "spine": (-6.0 * coil + 10.0 * strike, 0.0, 9.0 * coil - 12.0 * strike),
            "chest": (-5.0 * coil + 8.0 * strike, 0.0, 8.0 * coil - 10.0 * strike),
            "neck": (4.0 * coil - 6.0 * strike, 0.0, -6.0 * coil + 8.0 * strike),
            "head": (5.0 * coil - 8.0 * strike, 0.0, -6.0 * coil + 8.0 * strike)}
    rig.ik(pose, "thigh_l", "shin_l", "foot_l", rig.joint("foot_l"))
    rear = rig.joint("foot_r")
    rig.ik(pose, "thigh_r", "shin_r", "foot_r", (rear[0], rear[1] - 0.55 * strike, rear[2] + 0.10 * math.sin(math.pi * strike)),
           (14.0 * math.sin(math.pi * strike), 0, 0))
    pose["upperarm_l"] = (-38.0 * coil + 46.0 * strike, 10.0 * coil, 22.0 * coil - 26.0 * strike)
    pose["forearm_l"] = (-24.0 * coil + 30.0 * strike, 0.0, 0.0)
    pose["hand_l"] = (-16.0 * coil + 24.0 * strike, 0.0, 0.0)
    pose["upperarm_r"] = (14.0 * coil - 22.0 * strike, 0.0, 0.0)
    pose["forearm_r"] = (-10.0 * coil - 8.0 * strike, 0.0, 0.0)
    coil_late, strike_late = phases(u - 0.035)          # the wing tips and the beard trail the body by a frame or two
    for side, sign in (("l", 1.0), ("r", -1.0)):
        pose[f"wing_{side}_1"] = (-8.0 * coil + 10.0 * strike, sign * (14.0 * coil - 10.0 * strike), 0.0)
        pose[f"wing_{side}_2"] = (0.0, sign * (10.0 * coil_late - 12.0 * strike_late), 0.0)
        pose[f"wing_{side}_3"] = (0.0, sign * (8.0 * coil_late - 14.0 * strike_late), 0.0)
    for name in "clr":
        pose[f"tentacle_{name}_1"] = (-8.0 * coil_late + 18.0 * strike_late, 0.0, 0.0)
        pose[f"tentacle_{name}_2"] = (-10.0 * coil_late + 22.0 * strike_late, 0.0, 0.0)
    return pose
