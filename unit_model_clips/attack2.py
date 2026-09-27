"""attack2: the hanging right hand. A twist to load it, then an uppercut swung across the body while the wings
buffet forward and the head snaps down to bite. Starts and ends in the sculpt's pose."""
import math

SECONDS = 2.5


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def clip(u, rig):
    load = smooth(u / 0.30) * (1.0 - smooth((u - 0.30) / 0.12))
    hit = smooth((u - 0.32) / 0.12) * (1.0 - smooth((u - 0.52) / 0.42))
    buffet = math.sin(math.pi * smooth((u - 0.28) / 0.5)) if 0.28 < u < 0.78 else 0.0
    pose = {"pelvis.t": (0.0, 0.10 * load - 0.30 * hit, -0.12 * load - 0.16 * hit),
            "pelvis": (-2.0 * load + 5.0 * hit, 0.0, -9.0 * load + 12.0 * hit),
            "spine": (-3.0 * load + 6.0 * hit, 0.0, -10.0 * load + 14.0 * hit),
            "chest": (-2.0 * load + 6.0 * hit, 0.0, -8.0 * load + 12.0 * hit),
            "neck": (-3.0 * load + 6.0 * hit, 0.0, 6.0 * load - 8.0 * hit),
            "head": (-4.0 * load + 7.0 * hit, 0.0, 6.0 * load - 8.0 * hit)}
    for side in "lr":
        rear = rig.joint(f"foot_{side}")
        slide = 0.30 * hit if side == "r" else 0.0
        step = math.sin(math.pi * hit) if side == "r" else 0.0          # the sliding foot lifts while it travels
        rig.ik(pose, f"thigh_{side}", f"shin_{side}", f"foot_{side}", (rear[0], rear[1] - slide, rear[2] + 0.12 * step),
               (12.0 * step, 0, 0))
    pose["upperarm_r"] = (26.0 * load - 58.0 * hit, -8.0 * hit, -10.0 * load + 24.0 * hit)
    pose["forearm_r"] = (-12.0 * load - 38.0 * hit, 0.0, 0.0)
    pose["hand_r"] = (10.0 * load - 22.0 * hit, 0.0, 0.0)
    pose["upperarm_l"] = (10.0 * load + 8.0 * hit, 0.0, 8.0 * load)
    pose["forearm_l"] = (6.0 * load, 0.0, 0.0)
    for side, sign in (("l", 1.0), ("r", -1.0)):
        pose[f"wing_{side}_1"] = (14.0 * buffet, sign * (10.0 * load - 8.0 * buffet), -sign * 6.0 * buffet)
        pose[f"wing_{side}_2"] = (8.0 * buffet, -sign * 12.0 * buffet, 0.0)
        pose[f"wing_{side}_3"] = (6.0 * buffet, -sign * 14.0 * buffet, 0.0)
    for name, spread in (("c", 0.0), ("l", 1.0), ("r", -1.0)):
        # the beard flares FORWARD on the bite (-rx): swung back it sinks into the chest and vanishes
        pose[f"tentacle_{name}_1"] = (-6.0 * load - 10.0 * hit, 0.0, 8.0 * spread * hit)
        pose[f"tentacle_{name}_2"] = (-8.0 * load - 14.0 * hit, 0.0, 8.0 * spread * hit)
    return pose
