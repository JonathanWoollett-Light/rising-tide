"""idle: the sculpt's own pose, breathing. Slow, heavy, and never still: the chest swells, the wings sway a beat
behind it, the beard drifts, the raised claw flexes. The feet are pinned where the sculpt has them."""
import math

SECONDS = 4.0


def wave(u, cycles=1.0, phase=0.0):
    return math.sin(2 * math.pi * (cycles * u + phase))


def sway(u):
    breath = 0.5 - 0.5 * math.cos(2 * math.pi * 2 * u)          # two breaths a loop, 0..1
    pose = {"pelvis.t": (0.03 * wave(u), 0.0, -0.05 * breath),
            "pelvis": (0.0, 0.8 * wave(u), 1.0 * wave(u, 1, 0.1)),
            "spine": (-1.6 * breath, 0.0, -0.8 * wave(u)),
            "chest": (-1.8 * breath, 0.6 * wave(u, 1, 0.2), 0.0),
            "neck": (1.2 * breath, 0.0, 2.5 * wave(u, 1, 0.15)),
            "head": (1.5 * breath + 1.0 * wave(u, 2, 0.3), 1.0 * wave(u, 1, 0.4), 3.5 * wave(u, 1, 0.22))}
    pose["upperarm_l"] = (1.5 * wave(u, 1, 0.3), 0.0, 2.0 * wave(u, 1, 0.05))
    pose["forearm_l"] = (2.5 * wave(u, 2, 0.1), 0.0, 0.0)
    pose["hand_l"] = (5.0 * wave(u, 2, 0.35), 0.0, 3.0 * wave(u, 1, 0.5))
    pose["upperarm_r"] = (2.0 * wave(u, 1, 0.55), 1.0 * breath, 0.0)
    pose["forearm_r"] = (2.0 * wave(u, 1, 0.7), 0.0, 0.0)
    pose["hand_r"] = (4.0 * wave(u, 2, 0.6), 0.0, 0.0)
    for side, sign in (("l", 1.0), ("r", -1.0)):
        pose[f"wing_{side}_1"] = (1.5 * wave(u, 1, 0.1), -sign * (2.0 + 3.5 * breath), sign * 1.5 * wave(u, 1, 0.3))
        pose[f"wing_{side}_2"] = (0.0, -sign * 3.0 * wave(u, 2, -0.12), 0.0)
        pose[f"wing_{side}_3"] = (0.0, -sign * 4.0 * wave(u, 2, -0.24), 0.0)
    for k, name in enumerate(("c", "l", "r")):
        pose[f"tentacle_{name}_1"] = (3.0 * wave(u, 2, 0.1 * k), 0.0, 3.0 * wave(u, 1, 0.17 * k))
        pose[f"tentacle_{name}_2"] = (5.0 * wave(u, 2, 0.1 * k - 0.15), 0.0, 5.0 * wave(u, 1, 0.17 * k - 0.2))
    return pose


def clip(u, rig):
    """The sway, less where it stands at u = 0: the clip starts and ends in the sculpt's own pose, as idle2 does,
    so the two idles chain without a step. Then the feet are pinned."""
    now, start = sway(u), sway(0.0)
    pose = {bone: tuple(a - b for a, b in zip(value, start[bone])) for bone, value in now.items()}
    for side in "lr":
        rig.ik(pose, f"thigh_{side}", f"shin_{side}", f"foot_{side}", rig.joint(f"foot_{side}"))
    return pose
