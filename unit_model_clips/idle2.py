"""idle2: the restless variant. It looks slowly to one side, then rears its head, spreads its wings and bellows -
beard flaring - before settling back into the sculpt's pose. Starts and ends at rest, so idles chain seamlessly."""
import math

SECONDS = 5.0


def bump(u, start, end):
    """0 outside [start, end], a smooth hill to 1 inside."""
    if not start < u < end:
        return 0.0
    return math.sin(math.pi * (u - start) / (end - start)) ** 2


def clip(u, rig):
    look = bump(u, 0.03, 0.45)                     # a slow look to its right
    roar = bump(u, 0.42, 0.97)                     # then the bellow
    shake = math.sin(2 * math.pi * 9 * u) * bump(u, 0.55, 0.85)
    pose = {"pelvis.t": (0.0, 0.10 * roar, -0.10 * roar),
            "pelvis": (-2.0 * roar, 0.0, -4.0 * look),
            "spine": (-6.0 * roar, 0.0, -6.0 * look),
            "chest": (-8.0 * roar, 0.0, -7.0 * look),
            "neck": (-9.0 * roar, 0.0, -10.0 * look + 1.5 * shake),
            "head": (-12.0 * roar + 3.0 * look, 0.0, -14.0 * look + 2.0 * shake)}
    for side in "lr":
        rig.ik(pose, f"thigh_{side}", f"shin_{side}", f"foot_{side}", rig.joint(f"foot_{side}"))
    pose["upperarm_l"] = (-10.0 * roar, 6.0 * roar, 8.0 * roar)
    pose["forearm_l"] = (-8.0 * roar, 0.0, 0.0)
    pose["hand_l"] = (-10.0 * roar + 4.0 * shake, 0.0, 0.0)
    pose["upperarm_r"] = (-8.0 * roar, -12.0 * roar, 0.0)
    pose["forearm_r"] = (-14.0 * roar, 0.0, 0.0)
    pose["hand_r"] = (-10.0 * roar, 0.0, 0.0)
    for side, sign in (("l", 1.0), ("r", -1.0)):
        pose[f"wing_{side}_1"] = (-6.0 * roar, sign * 16.0 * roar - sign * 3.0 * look, sign * 5.0 * roar)
        pose[f"wing_{side}_2"] = (0.0, sign * 12.0 * roar + sign * 2.0 * shake, 0.0)
        pose[f"wing_{side}_3"] = (0.0, sign * 10.0 * roar + sign * 3.0 * shake, 0.0)
    for name, spread in (("c", 0.0), ("l", 1.0), ("r", -1.0)):
        pose[f"tentacle_{name}_1"] = (-9.0 * roar + 3.0 * shake, 0.0, 8.0 * spread * roar + 2.0 * look)
        pose[f"tentacle_{name}_2"] = (-11.0 * roar - 4.0 * shake, 0.0, 7.0 * spread * roar)
    return pose
