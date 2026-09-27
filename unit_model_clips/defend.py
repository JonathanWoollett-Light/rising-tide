"""defend: hunkered down behind its wings. A low crouch, the wings mantled forward and round like a shield, arms
drawn in, the head sunk between the shoulders - and breathing, so it loops without ever freezing."""
import math

SECONDS = 3.0


def wave(u, cycles=1.0, phase=0.0):
    return math.sin(2 * math.pi * (cycles * u + phase))


def clip(u, rig):
    breath = 0.5 - 0.5 * math.cos(2 * math.pi * 2 * u)
    flinch = max(0.0, wave(u, 1, 0.0)) ** 6                     # once a loop it braces against a blow
    pose = {"pelvis.t": (0.0, 0.18, -0.42 - 0.04 * breath - 0.08 * flinch),
            "pelvis": (5.0, 0.0, 0.0),
            "spine": (7.0 + 1.5 * breath + 3.0 * flinch, 0.0, 0.0),
            "chest": (6.0 + 1.5 * breath, 0.0, 0.0),
            "neck": (6.0 + 2.0 * flinch, 0.0, 2.0 * wave(u)),
            "head": (8.0, 0.0, 4.0 * wave(u, 1, 0.1))}
    for side in "lr":
        rig.ik(pose, f"thigh_{side}", f"shin_{side}", f"foot_{side}", rig.joint(f"foot_{side}"))
    pose["upperarm_l"] = (-10.0 - 4.0 * flinch, 0.0, -26.0)
    pose["forearm_l"] = (-16.0, 0.0, -12.0)
    pose["hand_l"] = (-10.0 + 4.0 * wave(u, 2), 0.0, 0.0)
    pose["upperarm_r"] = (-30.0 - 4.0 * flinch, 0.0, -22.0)
    pose["forearm_r"] = (-40.0, 0.0, -10.0)
    pose["hand_r"] = (-12.0, 0.0, 0.0)
    for side, sign in (("l", 1.0), ("r", -1.0)):
        # mantled forward, but not far inward: pulled in harder, both wing spars pass through the head
        pose[f"wing_{side}_1"] = (14.0 + 5.0 * flinch, -sign * (4.0 + 2.0 * breath), -sign * (4.0 - 4.0 * flinch))
        pose[f"wing_{side}_2"] = (10.0, -sign * 8.0, -sign * 8.0)
        pose[f"wing_{side}_3"] = (8.0, -sign * (8.0 + 3.0 * wave(u, 2, -0.2)), -sign * 8.0)
    for k, name in enumerate(("c", "l", "r")):
        pose[f"tentacle_{name}_1"] = (-6.0 + 2.0 * wave(u, 2, 0.1 * k), 0.0, 2.0 * wave(u, 1, 0.17 * k))
        pose[f"tentacle_{name}_2"] = (-8.0 + 3.0 * wave(u, 2, 0.1 * k - 0.15), 0.0, 3.0 * wave(u, 1, 0.17 * k - 0.2))
    return pose
