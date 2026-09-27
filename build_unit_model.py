"""Rebuild the Star Spawn's 3D unit model - mesh, textures, skeleton, skin and animations - from a high-poly
sculpt (an STL) with Blender and numpy.

The sculpt is a 3D-print miniature: ~2 million triangles, no UVs, no colour, one fixed pose. A map unit is a few
thousand triangles with three textures, a skeleton and a handful of animation clips, so this script

  1. (inside Blender, headless) imports the STL, stands it upright facing Blender -Y, drops loose debris,
     normalises it to MESH_HEIGHT, decimates a copy to TARGET_TRIS, unwraps it (Smart UV Project on a smoothed
     stand-in, see bl_unwrap) and bakes from the sculpt onto the copy with Cycles: the tangent-space normal
     map, an object-space one for check(), ambient occlusion and two emission "mask" passes (noise,
     pointiness, height, up-facing) that the texture painter below reads;
  2. (inside Blender) builds an armature from the RIG table and solves automatic (bone heat) skin weights;
  3. (system Python) paints the diffuse / normal / specular textures from the bakes and writes them as DXT5 DDS
     with a full mip chain (the flags and caps of OWB's mirelurk_d.dds and of vanilla's unit textures); poses
     the rig with the clip modules in CLIP_DIR; writes the Clausewitz .mesh with its skin and skeleton and one
     .anim per clip (formats: io_pdx_mesh's pdx_data.py; checked against OWB's mirelurk files), and generates
     the pdxmesh .gfx, the animation .asset and the entity .asset - all into a staging folder;
  4. checks what it wrote - see check() - and only then copies it into mod_folder;
  5. (--preview) renders the finished model and every clip in Blender into event_images/unit_model/.

Engine conventions this file relies on (each measured, not assumed - see CLAUDE.md > The Star Spawn model):
  space      Y up, -Z forward, left-handed. Blender (x, y, z) -> (x, z, y): a reflection, so triangle winding is
             reversed and V is flipped (v' = 1 - v), exactly as io_pdx_mesh does.
  winding    in OWB's and vanilla's meshes cross(p1 - p0, p2 - p0) agrees with the vertex normals on ~100 % of
             triangles; check() holds ours above 98 % (decimation folds a few slivers over) and to the same
             signed volume.
  normal map OWB's copy of gfx/FX/standardfuncsgfx.fxh, UnpackRRxGNormal: x = G, y = -(A), z rebuilt; B is the
             EMISSIVE mask (PdxMeshAdvanced defines EMISSIVE), so B stays 0. Because the space swap is a
             reflection the engine's bitangent is the mirror of Blender's, which cancels the shader's flip: A
             takes Blender's green channel as it is (A = up the image, the OpenGL way, as vanilla's own maps).
             check() proves it: decoded the shader's way through the mesh's own tangent frame, the shipped map
             must reproduce an object-space bake through the same rays.
  spec map   pdxmesh.shader PixelPdxMeshStandard under PDX_IMPROVED_BLINN_PHONG: G = specular level
             (g * g * 0.4), B = metalness, A = glossiness, R unused.
  shader     PdxMeshAdvanced, as OWB's mirelurk and every other OWB unit meshsettings that names a shader
             (OWB's static buildings and map objects use PdxMeshAdvancedSnow): plain PdxMeshStandard carries
             no defines and would read these textures in the legacy RGB layout. With a skin in the mesh the
             engine takes the effect's Skinned variant by itself (the mirelurk names plain PdxMeshAdvanced too).
  skeleton   a bone is  ix, pa (its parent's index; none on the root), tx = the INVERSE of its bind matrix as
             four columns of three; the skin is four (bone index, weight) pairs per vertex, -1 / 0 where unused,
             the weights summing to 1 (the shader rebuilds the fourth as 1 - the other three); at most 50 bones
             (pdxmesh.shader's matBones[50]).
  animation  per bone a local translation t and rotation q (x, y, z, w) relative to its parent; per file the
             first sample of every bone, a string naming which of t / q / s it animates, and the samples packed
             frame by frame and, within a frame, bone by bone. world = parent's world . T(t) R(q); a vertex moves
             by sum of weight . world . tx. emulate() does exactly that, and was proven on OWB's mirelurk with
             its own clips before it was trusted with ours.
  entity     a sub-unit's `sprite = X` resolves to the entity `X_entity` (`TAG_X_entity` overrides it). An
             animation is declared in an .asset whose folder its `file` is relative to - beside the .anim, as
             vanilla does (OWB declares its creatures' one folder up: `file = "mirelurk/mirelurk_idle.anim"`) -
             given an id in the pdxmesh, and played by an entity state.

Run from anywhere:
    python build_unit_model.py                 bake / weigh if the caches are stale, then write, check and publish
    python build_unit_model.py --preview       ... and render the preview sheet, a sheet per clip and a video
    python build_unit_model.py --rebake        ignore the bake cache
    python build_unit_model.py --check         only re-check the shipped files (no Blender, no sculpt)
    python build_unit_model.py --clip move     measure and draw one clip from the caches, in seconds (clip authoring)
    python build_unit_model.py --src X.stl --blender "C:/.../blender.exe" --work D:/durable/cache
Needs Blender (built and only ever run with 5.2.2 LTS; the newest install under BLENDER_GLOB is used, pin one
with --blender) and, in system Python, numpy and Pillow; ffmpeg on the PATH adds the preview video. The sculpt
is NOT in the repo (100 MB, licence unknown): --src defaults to SRC_DEFAULT. The caches live in the system temp
directory: the bake's key is the sculpt's hash, BAKE_KEYS and a hash of this file's baking half; the weights'
key is the RIG tables, the low-poly and a hash of the weighing code. Given one bake the written files are
byte-identical from run to run; across re-bakes on one device the mesh and the occlusion are bit-identical and
the other bakes differ by one float16 step in a few hundred texels, which rarely reaches a shipped byte.
"""
import sys
import time
from pathlib import Path

try:
    import bpy  # noqa: F401 - present only when Blender runs this file
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False

# --------------------------------------------------------------------------------------
# Tunables. (The painter's blend strengths and thresholds are in paint(), beside the palette they mix.)
# --------------------------------------------------------------------------------------
SUBJECT = "mltd_star_spawn"                 # names the mesh, the textures, the pdxmesh and the entity
MODEL_DIR = "gfx/models/mltd/star_spawn"    # under mod_folder; the mesh, the textures and the pdxmesh .gfx
ENTITY_FILE = "gfx/entities/mltd_entities.asset"
SUB_UNIT_FILE = "common/units/mltd_units.txt"
SUB_UNITS = ("mltd_star_spawn", "mltd_deep_ones")      # the sub-units whose `sprite` names this model's entity

SRC_DEFAULT = Path.home() / "Downloads" / "cthuluMINI.V1.1.stl"
SRC_UP_AXIS = "Y"            # the sculpt's up axis: X, -X, Y, -Y, Z or -Z (this STL: Y, standing on y = 0)
SRC_YAW_DEG = 0.0            # then a turn about the up axis, so that the figure faces Blender -Y (PDX -Z, forward)
SRC_ROLL_DEG = -4.2          # then a lean about the forward axis. This miniature stood on a scenic base that is
#                              not in the STL, so one sole hung 3 % of its height in the air: the lean seats both
DEBRIS_SHARE = 0.005         # loose parts holding less than this share of the sculpt's vertices are dropped

TARGET_TRIS = 6000           # OWB: mirelurk 2,751, deathclaw 3,824, super mutant behemoth 6,344
MESH_HEIGHT = 8.0            # PDX units. An OWB human is 7.37 tall at entity scale 0.8
ENTITY_SCALE = 1.0           # -> 8.0 on the map: 1.35x an OWB human (5.9), a little over a deathclaw (7.6). At 1.2
#                              (9.6, twice the mirelurks beside it) it read as too large in game

UV_ANGLE_DEG = 66.0
UV_PROXY_SMOOTH = 3          # Laplacian iterations (volume-preserving) on the stand-in the unwrap sees: bl_unwrap
UV_ISLAND_MARGIN = 0.004     # every island is padded by this fraction of the texture, so neighbours sit 8 texels
#                              apart at TEX_D and 4 (one DXT block) at TEX_N / TEX_S, and 4 / 2 from the edge
BAKE_RES = 2048              # baked at this size, painted at TEX_D (a 2x2 supersample)
BAKE_MARGIN_PX = 16
CAGE_EXTRUSION = 0.10        # an absolute distance in mesh units, like the next three (the sculpt lies within
MAX_RAY_DISTANCE = 0.35      # 0.05 of the low-poly at MESH_HEIGHT = 8): re-tune them with MESH_HEIGHT
AO_DISTANCE = 1.6
NOISE_LARGE = (0.85, 5.0, 0.55)     # scale, detail, roughness of the three object-space noises the painter reads
NOISE_FINE = (5.5, 3.0, 0.6)
NOISE_PATCH = (0.32, 2.0, 0.5)
SAMPLES = {"NORMAL": 4, "EMIT": 4, "AO": 96}
SEED = 20260921

TEX_D = 1024                 # OWB's mirelurk_d.dds is 1024
TEX_N = 512                  # vanilla's commonest unit normal-map size
TEX_S = 512

# Diffuse palette, sRGB 0-255: the mod's abyssal teal. Its brightness is set against OWB's mirelurk_d.dds, whose
# model the Deep Ones wear beside this one (luma p5 / median / p95 = 40 / 58 / 110 when this was written; paint()
# measures it again and prints both).
DEEP = (26, 66, 62)          # the body, in the troughs of the large noise
MID = (70, 142, 118)         # ... and on its crests
PATCH = (98, 124, 70)        # murky olive, in broad patches
SPECKLE = (176, 190, 116)    # sickly mottling
RIDGE = (150, 204, 178)      # raised detail (pointiness above the median)
CREVICE = (30, 20, 42)       # violet-black in the cuts (pointiness below it)
AO_FLOOR = 0.44              # diffuse = paint * (AO_FLOOR + (1 - AO_FLOOR) * ao ** AO_GAMMA)
AO_GAMMA = 1.2
TOP_LIGHT = (0.80, 0.36)     # paint *= a + b * up-facing
WET_FEET = (0.70, 0.22)      # paint darkens to `a` at the ground and is full by height `b` (share of MESH_HEIGHT)

SPEC_LEVEL = 150             # spec map G: (150/255)^2 * 0.4 = 0.14. Vanilla's railway gun: 128
GLOSS_RANGE = (46, 118)      # spec map A, from deep cuts to open skin (wet). Vanilla's railway gun: ~65

PREVIEW_RES = 640
PREVIEW_SAMPLES = 64
PREVIEW_CARDS = ((96, 92, 70), (30, 52, 12))    # stand-ins for OWB's wasteland and for the Oregon coast's dark olive

# The skeleton: joint -> (parent, where it is). A joint is the pivot its bone turns about, in MODEL SPACE - the
# bake's: x = the figure's LEFT, y = its BACK (it faces -y), z = up, feet on z = 0. This is the export order, and it
# is DEPTH-FIRST (a bone, then its whole subtree), as all 487 skeletons in vanilla and OWB are. Every bone exports with an IDENTITY rest orientation, so a pose's rotation about the
# model's axes is the bone's local rotation as it stands (see Rig). The sculpt is a posed miniature, not a T-pose,
# so the joints were placed by measurement: each part sliced along its own axis for its centre line, the bends
# read off that, every joint walked to the middle of its limb and checked for lying inside the body, left and
# right segment lengths held to each other (CLAUDE.md > The Star Spawn model > The rig).
RIG = {
    "root": (None, (0.05, 0.55, 0)),
    "pelvis": ("root", (0.05, 0.55, 3)),
    "spine": ("pelvis", (0, 0.3, 3.9)),
    "chest": ("spine", (0, 0.2, 4.9)),
    "neck": ("chest", (0, -0.7, 5.6)),
    "head": ("neck", (0.05, -1.4, 5.95)),
    "tentacle_c_1": ("head", (-0.11, -2.22, 5)),
    "tentacle_c_2": ("tentacle_c_1", (-0.08, -2.06, 3.99)),
    "tentacle_l_1": ("head", (0.55, -1.98, 4.97)),
    "tentacle_l_2": ("tentacle_l_1", (0.69, -1.74, 4.13)),
    "tentacle_r_1": ("head", (-0.3, -1.93, 4.93)),
    "tentacle_r_2": ("tentacle_r_1", (-0.66, -1.92, 3.98)),
    "upperarm_l": ("chest", (1.13, -0.46, 5.04)),
    "forearm_l": ("upperarm_l", (2.02, -1.03, 4.48)),
    "hand_l": ("forearm_l", (2.65, -1.53, 4.97)),
    "upperarm_r": ("chest", (-1.24, -0.21, 4.85)),
    "forearm_r": ("upperarm_r", (-1.83, 0.17, 3.95)),
    "hand_r": ("forearm_r", (-2.36, -0.09, 3.17)),
    "wing_l_1": ("chest", (1.07, 0.43, 5.55)),
    "wing_l_2": ("wing_l_1", (1.72, 0.41, 6.58)),
    "wing_l_3": ("wing_l_2", (2.3, 0.2, 7.4)),
    "wing_r_1": ("chest", (-1.11, 0.52, 5.34)),
    "wing_r_2": ("wing_r_1", (-1.9, 0.65, 6.2)),
    "wing_r_3": ("wing_r_2", (-2.7, 0.5, 6.95)),
    "thigh_l": ("pelvis", (0.83, 0.61, 2.71)),
    "shin_l": ("thigh_l", (1.4, 0.45, 1.89)),
    "foot_l": ("shin_l", (1.5, 1.15, 1)),
    "toe_l": ("foot_l", (1.91, 0.72, 0.31)),
    "thigh_r": ("pelvis", (-0.8, 0.62, 2.71)),
    "shin_r": ("thigh_r", (-0.77, 1.16, 2.02)),
    "foot_r": ("shin_r", (-0.56, 2.18, 1.1)),
    "toe_r": ("foot_r", (-0.72, 1.78, 0.35)),
}
# Where a leaf bone ends, and which child a branching joint's segment runs to. Only the weights solver sees
# these - it needs segments to measure "near this bone" along; the engine gets joints alone.
RIG_TAILS = {
    "head": (0.1, -2.3, 5.8),
    "tentacle_c_2": (0.05, -2.45, 3),
    "tentacle_l_2": (0.78, -1.98, 3.2),
    "tentacle_r_2": (-0.73, -2.5, 3.3),
    "hand_l": (3.31, -2.6, 5.1),
    "hand_r": (-2.05, -0.8, 2.25),
    "toe_l": (2.14, 0.18, 0.06),
    "toe_r": (-0.8, 1.35, 0.12),
    "wing_l_3": (2.95, 0.45, 7.7),
    "wing_r_3": (-3.3, 0.85, 7.15),
}
RIG_PRIMARY = {"pelvis": "spine", "spine": "chest", "chest": "neck", "neck": "head"}
MAX_BONES = 50               # pdxmesh.shader: float4x4 matBones[50]

FPS = 24                     # OWB's creature clips are 24 fps
CLIP_DIR = "unit_model_clips"           # beside this script: one module per animation id (see load_clips)
# (state, animation id, the rest of the state's line): the pattern of OWB's mirelurk_entity and vanilla's
# infantry_rifle_entity - idles and attacks are `looping = no` variants drawn by `chance`, each attack handing
# back to the attack state; a retreat is the walk played faster, and drill the restless idle. No `death`: the
# mirelurk has none either.
STATES = (
    ("idle", "idle", "animation_blend_time = 0.4 animation_speed = 1.0 chance = 4 looping = no"),
    ("idle", "idle2", "animation_blend_time = 0.4 animation_speed = 1.0 chance = 1 looping = no"),
    ("move", "move", "animation_blend_time = 0.4 animation_speed = 1.0"),
    ("retreat", "move", "animation_blend_time = 0.4 animation_speed = 1.25"),
    ("attack", "attack", 'animation_blend_time = 0.3 animation_speed = 1.0 chance = 3 looping = no next_state = "attack"'),
    ("attack", "attack2", 'animation_blend_time = 0.3 animation_speed = 1.0 chance = 2 looping = no next_state = "attack"'),
    ("defend", "defend", "animation_blend_time = 0.3 animation_speed = 1.0"),
    ("support_attack", "attack2", "animation_blend_time = 0.3 animation_speed = 1.0"),
    ("training", "idle2", "animation_blend_time = 0.3 animation_speed = 1.0"),
)
ANIMATIONS = tuple(dict.fromkeys(animation for _, animation, _ in STATES))

OWB = Path("C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/2265420196")
OWB_REF_MESH = OWB / "gfx/models/owbentity/mirelurk/mirelurk.mesh"
OWB_REF_DDS = OWB / "gfx/models/owbentity/mirelurk/mirelurk_d.dds"
OWB_REF_ANIM = OWB / "gfx/models/owbentity/mirelurk/mirelurk_attack.anim"
BLENDER_GLOB = "C:/Program Files/Blender Foundation/*/blender.exe"
BLENDER_TESTED = (5, 2)

# The bake cache is stale when the sculpt, one of these, or the baking half of this file changes.
BAKE_KEYS = ("SRC_UP_AXIS", "SRC_YAW_DEG", "SRC_ROLL_DEG", "DEBRIS_SHARE", "TARGET_TRIS", "MESH_HEIGHT",
             "UV_ANGLE_DEG", "UV_PROXY_SMOOTH", "UV_ISLAND_MARGIN", "BAKE_RES", "BAKE_MARGIN_PX", "CAGE_EXTRUSION",
             "MAX_RAY_DISTANCE", "AO_DISTANCE", "NOISE_LARGE", "NOISE_FINE", "NOISE_PATCH", "SAMPLES", "SEED")
BAKE_FILES = ("mesh.npz", "normal.npy", "normal_object.npy", "ao.npy", "masks_a.npy", "masks_b.npy",
              "lowpoly.blend", "bake.json")
PREVIEW_VIEWS = {"side": (1, 0, 0.12), "quarter": (0.75, -1, 0.45), "front": (0, -1, 0.12), "map": (0.45, -1, 1.35)}

# The turn that takes the sculpt's up axis to Blender's +Z (each a proper rotation, so the winding is untouched).
UP_AXIS_TURN = {"Z": None, "-Z": ("X", 180.0), "Y": ("X", 90.0), "-Y": ("X", -90.0), "X": ("Y", -90.0),
                "-X": ("Y", 90.0)}
if SRC_UP_AXIS not in UP_AXIS_TURN:
    raise ValueError(f"SRC_UP_AXIS must be one of {sorted(UP_AXIS_TURN)}, not {SRC_UP_AXIS!r}")


# ======================================================================================
# Inside Blender
# ======================================================================================
def bl_log(msg):
    print(f"[blender] {msg}", flush=True)


def bl_use_gpu(scene):
    """Cycles on the first GPU backend that has a device of its own; CPU otherwise. `prefs.devices` lists every
    backend's devices at once, so the test must be on the device's own type."""
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for backend in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
        try:
            prefs.compute_device_type = backend
        except TypeError:
            continue
        prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == backend]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == backend
            scene.cycles.device = "GPU"
            return f"{backend}: {gpus[0].name}"
    scene.cycles.device = "CPU"
    return "CPU"


def bl_node_tree(datablock):
    """A material's or world's node tree. Blender 5 always has one and means to drop `use_nodes` in 6.0; 4.x
    needs it set."""
    if not datablock.node_tree:
        datablock.use_nodes = True
    return datablock.node_tree


def bl_socket(node, *names, output=False):
    sockets = node.outputs if output else node.inputs
    for name in names:
        if name in sockets:
            return sockets[name]
    raise KeyError(f"{node.bl_idname}: none of {names}")


def bl_mask_material(name, channels):
    """An emission material whose R, G, B are three scalar fields, for an EMIT bake. `channels` builds them."""
    mat = bpy.data.materials.new(name)
    nt = bl_node_tree(mat)
    nt.nodes.clear()
    combine = nt.nodes.new("ShaderNodeCombineColor")
    emit = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    for socket, field in zip(("Red", "Green", "Blue"), channels(nt)):
        nt.links.new(field, combine.inputs[socket])
    nt.links.new(combine.outputs[0], emit.inputs["Color"])
    nt.links.new(emit.outputs[0], out.inputs["Surface"])
    return mat


def bl_noise(nt, coords, scale, detail, roughness):
    node = nt.nodes.new("ShaderNodeTexNoise")
    node.noise_dimensions = "3D"
    bl_socket(node, "Scale").default_value = scale
    bl_socket(node, "Detail").default_value = detail
    bl_socket(node, "Roughness").default_value = roughness
    nt.links.new(coords, bl_socket(node, "Vector"))
    return bl_socket(node, "Fac", "Factor", output=True)


def bl_channels_a(nt):
    """R large noise, G fine noise, B raw pointiness (Cycles' curvature; the painter normalises it)."""
    coords = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
    geometry = nt.nodes.new("ShaderNodeNewGeometry")
    return bl_noise(nt, coords, *NOISE_LARGE), bl_noise(nt, coords, *NOISE_FINE), geometry.outputs["Pointiness"]


def bl_channels_b(nt):
    """R height (0 at the ground, 1 at the crown), G up-facing (normal.z mapped to 0-1), B very large noise."""
    coords = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
    geometry = nt.nodes.new("ShaderNodeNewGeometry")

    def z_of(vector, mul, add):
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(vector, sep.inputs[0])
        math = nt.nodes.new("ShaderNodeMath")
        math.operation = "MULTIPLY_ADD"
        nt.links.new(sep.outputs["Z"], math.inputs[0])
        math.inputs[1].default_value = mul
        math.inputs[2].default_value = add
        return math.outputs[0]

    return (z_of(coords, 1.0 / MESH_HEIGHT, 0.0), z_of(geometry.outputs["Normal"], 0.5, 0.5),
            bl_noise(nt, coords, *NOISE_PATCH))


def bl_pixels(image):
    """An image's RGB as a top-down float array (Blender stores rows bottom-up)."""
    import numpy as np
    w, h = image.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    image.pixels.foreach_get(buf)
    return buf.reshape(h, w, 4)[::-1, :, :3]


def bl_unwrap(lp):
    """Smart UV Project, but on a smoothed stand-in. A decimated sculpt is so bumpy that the projection's
    angle test shatters it (measured: 1,252 islands on 6,000 triangles); a volume-preserving Laplacian pass
    halves that. The topology is untouched, so the UVs are the real mesh's too: its coordinates go back, the
    islands are rescaled against its true areas (average_islands_scale - otherwise the smoothing starves thin
    parts of texels) and repacked with an exact margin. (Smart UV Project's own island_margin is added per
    island and left 15 % of the texture in use.)"""
    import math

    import numpy as np
    me = lp.data
    me.uv_layers.new(name="UVMap")
    true_co = np.empty(len(me.vertices) * 3, dtype=np.float32)
    me.vertices.foreach_get("co", true_co)
    if UV_PROXY_SMOOTH:
        mod = lp.modifiers.new("uv_proxy", "LAPLACIANSMOOTH")
        mod.lambda_factor = 1.0
        mod.iterations = UV_PROXY_SMOOTH
        mod.use_volume_preserve = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(UV_ANGLE_DEG), island_margin=0.0, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    me.vertices.foreach_set("co", true_co)
    me.update()
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, margin_method="FRACTION", margin=UV_ISLAND_MARGIN, shape_method="CONCAVE")
    bpy.ops.object.mode_set(mode="OBJECT")
    me.shade_smooth()


def bl_stage_bake(src, work):
    import json
    import math

    import bmesh
    import numpy as np
    from mathutils import Matrix, Vector

    started = time.time()
    if tuple(bpy.app.version[:2]) != BLENDER_TESTED:
        bl_log(f"untested Blender {bpy.app.version_string}: this was built with {BLENDER_TESTED[0]}.{BLENDER_TESTED[1]}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bpy.ops.wm.stl_import(filepath=str(src))
    hp = bpy.context.selected_objects[0]
    hp.name = "highpoly"
    me = hp.data
    stats = {"sculpt_verts": len(me.vertices), "sculpt_tris": len(me.polygons)}
    bl_log(f"imported {stats['sculpt_tris']:,} triangles in {time.time() - started:.1f}s")

    # Stand it up (Blender is Z up), turn it to face -Y, lean it onto both feet.
    turn = Matrix.Rotation(math.radians(SRC_ROLL_DEG), 4, "Y") @ Matrix.Rotation(math.radians(SRC_YAW_DEG), 4, "Z")
    if UP_AXIS_TURN[SRC_UP_AXIS]:
        axis, degrees = UP_AXIS_TURN[SRC_UP_AXIS]
        turn = turn @ Matrix.Rotation(math.radians(degrees), 4, axis)
    me.transform(turn)

    # Drop loose debris (this sculpt carries one 544-vertex shell inside the torso). The test is size alone, so
    # every dropped part is logged: a small part that belongs (an eye, a separate claw) would go too.
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    seen = bytearray(len(bm.verts))
    parts = []
    for v in bm.verts:
        if seen[v.index]:
            continue
        seen[v.index] = 1
        stack, part = [v], []
        while stack:
            cur = stack.pop()
            part.append(cur)
            for e in cur.link_edges:
                other = e.other_vert(cur)
                if not seen[other.index]:
                    seen[other.index] = 1
                    stack.append(other)
        parts.append(part)
    debris = [p for p in parts if len(p) < DEBRIS_SHARE * len(bm.verts)]
    stats["loose_parts"] = len(parts)
    stats["debris_verts"] = sum(len(p) for p in debris)
    for p in debris:
        centre = sum((v.co for v in p), Vector()) / len(p)
        bl_log(f"dropped a loose part of {len(p):,} vertices around ({centre.x:.2f}, {centre.y:.2f}, {centre.z:.2f})"
               " in the sculpt's own units")
    if debris:
        bmesh.ops.delete(bm, geom=[v for p in debris for v in p], context="VERTS")
        bm.to_mesh(me)
    bm.free()
    bl_log(f"{len(parts)} loose parts, dropped {len(debris)}")

    # Feet on z = 0, bounding box centred on the origin in x/y, MESH_HEIGHT tall.
    co = np.empty(len(me.vertices) * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    lo, hi = co.min(0), co.max(0)
    scale = MESH_HEIGHT / float(hi[2] - lo[2])
    me.transform(Matrix.Scale(scale, 4) @ Matrix.Translation(Vector((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2,
                                                                     -lo[2]))))
    me.update()
    stats["source_scale"] = scale
    stats["size"] = [float(x) for x in (hi - lo) * scale]
    me.shade_smooth()

    # The low-poly copy.
    lp = hp.copy()
    lp.data = me.copy()
    lp.name = "lowpoly"
    lp.data.name = "lowpoly"
    scene.collection.objects.link(lp)
    for o in scene.objects:
        o.select_set(False)
    lp.select_set(True)
    bpy.context.view_layer.objects.active = lp
    tick = time.time()
    mod = lp.modifiers.new("decimate", "DECIMATE")
    mod.ratio = TARGET_TRIS / len(lp.data.polygons)
    mod.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    lp.data.shade_smooth()
    stats["lowpoly_verts"] = len(lp.data.vertices)
    stats["lowpoly_tris"] = len(lp.data.polygons)
    bl_log(f"decimated to {stats['lowpoly_tris']:,} triangles in {time.time() - tick:.1f}s")

    bl_unwrap(lp)

    # Cycles, baking from the sculpt (selected) onto the copy (active).
    scene.render.engine = "CYCLES"
    stats["device"] = bl_use_gpu(scene)
    scene.cycles.seed = SEED
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False
    world = bpy.data.worlds.new("world")
    world.light_settings.distance = AO_DISTANCE
    scene.world = world
    bl_log(f"baking on {stats['device']}")

    target = bpy.data.materials.new("bake_target")
    nodes = bl_node_tree(target).nodes
    tex = nodes.new("ShaderNodeTexImage")
    nodes.active = tex
    tex.select = True
    lp.data.materials.append(target)
    hp.data.materials.append(bl_mask_material("masks_a", bl_channels_a))
    hp.data.materials.append(bl_mask_material("masks_b", bl_channels_b))
    hp.select_set(True)
    lp.select_set(True)
    bpy.context.view_layer.objects.active = lp

    def bake(kind, name, slot=None, space="TANGENT"):
        tick = time.time()
        if slot is not None:                      # which of the sculpt's two mask materials emits
            hp.data.polygons.foreach_set("material_index", np.full(len(hp.data.polygons), slot, dtype=np.int32))
            hp.data.update()
        image = bpy.data.images.new(name, BAKE_RES, BAKE_RES, alpha=False, float_buffer=True, is_data=True)
        tex.image = image
        scene.cycles.samples = SAMPLES[kind]
        extra = dict(normal_space=space, normal_r="POS_X", normal_g="POS_Y", normal_b="POS_Z") \
            if kind == "NORMAL" else {}
        bpy.ops.object.bake(type=kind, use_selected_to_active=True, cage_extrusion=CAGE_EXTRUSION,
                            max_ray_distance=MAX_RAY_DISTANCE, margin=BAKE_MARGIN_PX, margin_type="EXTEND",
                            use_clear=True, target="IMAGE_TEXTURES", **extra)
        np.save(work / f"{name}.npy", bl_pixels(image).astype(np.float16))
        bpy.data.images.remove(image)
        bl_log(f"baked {name} in {time.time() - tick:.1f}s")

    bake("NORMAL", "normal")
    bake("NORMAL", "normal_object", space="OBJECT")    # never shipped: what check() holds the tangent map to
    bake("AO", "ao")
    bake("EMIT", "masks_a", slot=0)
    bake("EMIT", "masks_b", slot=1)

    # The copy's geometry as the engine needs it: per-corner normals, tangents (MikkTSpace, the bake's own
    # frame), UVs. The host welds the corners and converts them to PDX space.
    lme = lp.data
    lme.calc_tangents(uvmap=lme.uv_layers.active.name)
    n_loops = len(lme.loops)

    def loops(attr, width, dtype=np.float32):
        buf = np.empty(n_loops * width, dtype=dtype)
        lme.loops.foreach_get(attr, buf)
        return buf.reshape(-1, width) if width > 1 else buf

    uv = np.empty(n_loops * 2, dtype=np.float32)
    lme.uv_layers.active.uv.foreach_get("vector", uv)
    loop_total = np.empty(len(lme.polygons), dtype=np.int32)
    lme.polygons.foreach_get("loop_total", loop_total)
    if not (loop_total == 3).all():
        raise RuntimeError("the decimated mesh is not all triangles")
    loop_start = np.empty(len(lme.polygons), dtype=np.int32)
    lme.polygons.foreach_get("loop_start", loop_start)
    lco = np.empty(len(lme.vertices) * 3, dtype=np.float32)
    lme.vertices.foreach_get("co", lco)
    lco = lco.reshape(-1, 3)

    np.savez(work / "mesh.npz", co=lco, loop_vert=loops("vertex_index", 1, np.int32), loop_normal=loops("normal", 3),
             loop_tangent=loops("tangent", 3), loop_bitangent_sign=loops("bitangent_sign", 1), loop_uv=uv.reshape(-1, 2),
             tri_loops=loop_start[:, None] + np.arange(3, dtype=np.int32)[None, :])

    bpy.data.objects.remove(hp)
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(work / "lowpoly.blend"), compress=True)
    stats["blender"] = bpy.app.version_string
    stats["seconds"] = round(time.time() - started, 1)
    (work / "bake_stats.json").write_text(json.dumps(stats, indent=2))
    bl_log(f"done in {stats['seconds']}s")


# ======================================================================================
# Inside Blender: the rig (an edit below this line does not make the bake stale)
# ======================================================================================
def bl_stage_weights(work):
    """An armature from RIG, Blender's automatic (bone heat) weights on the low-poly, saved dense: the host keeps
    the four strongest per vertex. A Blender bone is a segment and a skeleton joint a point: bone N runs from
    joint N to its primary child, or to its RIG_TAILS entry. The root deforms nothing - it carries the figure."""
    import numpy as np
    from mathutils import Vector

    bpy.ops.wm.open_mainfile(filepath=str(work / "lowpoly.blend"))
    lp = bpy.data.objects["lowpoly"]
    for modifier in list(lp.modifiers):
        lp.modifiers.remove(modifier)
    armature = bpy.data.armatures.new("rig")
    rig = bpy.data.objects.new("rig", armature)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (parent, head) in RIG.items():
        bone = armature.edit_bones.new(name)
        bone.head = Vector(head)
        children = [c for c, (q, _) in RIG.items() if q == name]
        if parent is None:
            bone.tail = bone.head + Vector((0.0, 0.4, 0.0))
        elif name in RIG_TAILS:
            bone.tail = Vector(RIG_TAILS[name])
        elif name in RIG_PRIMARY or children:
            bone.tail = Vector(RIG[RIG_PRIMARY.get(name, children[0] if children else name)][1])
        else:
            raise RuntimeError(f"{name} is a leaf without a RIG_TAILS entry")
    for name, (parent, _) in RIG.items():
        if parent:
            armature.edit_bones[name].parent = armature.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    for name, (parent, _) in RIG.items():
        armature.bones[name].use_deform = parent is not None
    for o in bpy.context.scene.objects:
        o.select_set(False)
    lp.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")

    names = list(RIG)
    groups = {g.index: g.name for g in lp.vertex_groups}
    weights = np.zeros((len(lp.data.vertices), len(names)), dtype=np.float32)
    for v in lp.data.vertices:
        for g in v.groups:
            weights[v.index, names.index(groups[g.group])] = g.weight
    orphans = int((weights.sum(1) < 1e-6).sum())
    if orphans:
        raise RuntimeError(f"bone heat left {orphans} vertices without a weight (a non-manifold patch?)")
    np.savez(work / "weights.npz", weights=weights, names=np.array(names))
    bl_log(f"weighed {len(weights):,} vertices to {len(names)} bones; up to {int((weights > 0).sum(1).max())} "
           "influences a vertex before the host keeps four")


# ======================================================================================
# Inside Blender: previews
# ======================================================================================
def bl_preview_material(work, lp):
    mat = bpy.data.materials.new("preview")
    nt = bl_node_tree(mat)
    bsdf = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    # The engine's specular level as the BSDF's F0. The BSDF conserves energy and the engine adds its specular on
    # top of the diffuse, so the preview stays ~10 % darker than the game: an approximation, not the game.
    f0 = (SPEC_LEVEL / 255.0) ** 2 * 0.4
    bsdf.inputs["IOR"].default_value = (1.0 + f0 ** 0.5) / (1.0 - f0 ** 0.5)

    def texture(name, data):
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images.load(str(work / name))
        if data:
            node.image.colorspace_settings.name = "Non-Color"
        return node

    diffuse = texture("preview_d.png", False)
    nt.links.new(diffuse.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(texture("preview_r.png", True).outputs["Color"], bsdf.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(texture("preview_n.png", True).outputs["Color"], bump.inputs["Color"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.nodes.active = diffuse                      # what Workbench's texture colour shows
    lp.data.materials.clear()
    lp.data.materials.append(mat)


def bl_stage_frames(work):
    """Posed copies of the low-poly, drawn fast (Workbench) on a ground plane: work/frames/<clip>.npy is
    (frames, vertices, 3) in the low-poly's own vertex order; manifest.json says which views and what size."""
    import json

    import numpy as np
    from mathutils import Vector

    manifest = json.loads((work / "frames" / "manifest.json").read_text())
    bpy.ops.wm.open_mainfile(filepath=str(work / "lowpoly.blend"))
    scene = bpy.context.scene
    lp = bpy.data.objects["lowpoly"]
    bl_preview_material(work, lp)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.002))
    ground = bpy.data.materials.new("ground")
    ground.diffuse_color = (0.42, 0.40, 0.34, 1)
    bpy.context.active_object.data.materials.append(ground)

    scene.render.engine = "BLENDER_WORKBENCH"
    shading = scene.display.shading
    shading.light, shading.color_type = "STUDIO", "TEXTURE"
    shading.show_shadows, shading.shadow_intensity, shading.show_cavity = True, 0.6, True
    shading.studiolight_intensity = 2.4
    scene.display.light_direction = (0.4, 0.5, 0.75)
    scene.display.render_aa = "5"
    scene.render.resolution_x = scene.render.resolution_y = manifest["size"]
    scene.world = bpy.data.worlds.new("frames")
    scene.world.color = (0.16, 0.19, 0.22)
    camera = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    camera.data.type, camera.data.ortho_scale = "ORTHO", MESH_HEIGHT * 1.55
    scene.collection.objects.link(camera)
    scene.camera = camera
    centre = Vector((0.0, 0.3, MESH_HEIGHT * 0.43))
    count = 0
    for job in manifest["jobs"]:
        frames = np.load(work / "frames" / f"{job['name']}.npy")
        for view in job["views"]:
            d = Vector(PREVIEW_VIEWS[view]).normalized()
            camera.location = centre + d * MESH_HEIGHT * 5
            camera.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
            for f in range(len(frames)):
                lp.data.vertices.foreach_set("co", frames[f].reshape(-1))
                lp.data.update()
                scene.render.filepath = str(work / "frames" / f"{job['name']}_{view}_{f:03d}.png")
                bpy.ops.render.render(write_still=True)
                count += 1
    bl_log(f"drew {count} frames")


def bl_stage_preview(work):
    from mathutils import Vector

    bpy.ops.wm.open_mainfile(filepath=str(work / "lowpoly.blend"))
    scene = bpy.context.scene
    lp = bpy.data.objects["lowpoly"]
    scene.render.engine = "CYCLES"
    bl_log(f"rendering on {bl_use_gpu(scene)}")
    scene.cycles.samples = PREVIEW_SAMPLES
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = PREVIEW_RES
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"

    bl_preview_material(work, lp)

    world = bpy.data.worlds.new("preview")
    bl_node_tree(world).nodes["Background"].inputs["Color"].default_value = (0.10, 0.13, 0.14, 1.0)
    scene.world = world
    for name, energy, direction in (("sun", 4.0, (0.5, -0.6, 0.9)), ("fill", 1.2, (-0.8, -0.3, 0.3))):
        light = bpy.data.objects.new(name, bpy.data.lights.new(name, "SUN"))
        light.data.energy = energy
        light.rotation_euler = Vector(direction).to_track_quat("Z", "Y").to_euler()
        scene.collection.objects.link(light)

    camera = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = MESH_HEIGHT * 1.25
    scene.collection.objects.link(camera)
    scene.camera = camera
    centre = Vector((0.0, 0.0, MESH_HEIGHT * 0.5))
    # "map" is roughly the game's view: from the front quarter, looking down at ~50 degrees.
    views = {"front": (0, -1, 0), "quarter": (0.8, -1, 0.35), "side": (1, 0, 0), "back": (0, 1, 0.15),
             "map": (0.45, -1, 1.35)}
    for name, direction in views.items():
        d = Vector(direction).normalized()
        camera.location = centre + d * MESH_HEIGHT * 4
        camera.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(work / f"view_{name}.png")
        bpy.ops.render.render(write_still=True)
    bl_log("rendered " + ", ".join(views))


def blender_main():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=("bake", "weights", "frames", "preview"))
    ap.add_argument("--src")
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    if args.stage == "bake":
        bl_stage_bake(Path(args.src), Path(args.work))
    else:
        {"weights": bl_stage_weights, "frames": bl_stage_frames, "preview": bl_stage_preview}[args.stage](Path(args.work))


# ======================================================================================
# System Python
# ======================================================================================
ROOT = Path(__file__).resolve().parent
MOD = ROOT / "mod_folder"
PREVIEW_DIR = ROOT / "event_images" / "unit_model"


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for block in iter(lambda: fp.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def code_hash(start, end):
    """A stretch of this file, between two of its banner comments: an edit there (the unwrap, a bake setting that
    is not a tunable) is a different result. A comment counts too - one re-run is cheaper than a stale cache."""
    import hashlib
    text = Path(__file__).read_text(encoding="utf-8")
    return hashlib.sha256(text[text.index(start):text.index(end)].encode()).hexdigest()


def bake_code_hash():
    return code_hash("# Inside Blender\n", "# Inside Blender: the rig")


def weights_key(work):
    """What the skin weights depend on: the skeleton - in its order, which is the weights' column order - the
    low-poly they were solved on and the solving code."""
    import json
    return json.loads(json.dumps({"rig": [list(RIG.items()), RIG_TAILS, RIG_PRIMARY], "mesh": sha256(work / "mesh.npz"),
                                  "code": code_hash("# Inside Blender: the rig", "# Inside Blender: previews")}))


def find_blender(explicit):
    import glob
    if explicit:
        return Path(explicit)
    found = sorted(glob.glob(BLENDER_GLOB))
    if not found:
        raise SystemExit(f"no Blender under {BLENDER_GLOB}; pass --blender")
    return Path(found[-1])


def run_blender(blender, work, stage, *extra):
    import subprocess
    log = work / f"blender_{stage}.log"
    # Blender exits 0 on a Python error unless --python-exit-code is given.
    cmd = [str(blender), "--background", "--factory-startup", "--python-exit-code", "1", "--python",
           str(Path(__file__).resolve()), "--", "--stage", stage, "--work", str(work), *extra]
    with open(log, "w", encoding="utf-8", errors="replace") as fp:
        proc = subprocess.run(cmd, stdout=fp, stderr=subprocess.STDOUT)
    text = log.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("[blender]"):
            print("  " + line)
    if proc.returncode != 0 or "Traceback (most recent call last)" in text:
        raise SystemExit(f"Blender's {stage} stage failed - see {log}\n" + "\n".join(text.splitlines()[-25:]))


# --------------------------------------------------------------------------------------
# Clausewitz .mesh (binary): '@@b@', then objects ('[' x depth, name, NUL) and properties
# ('!', name length, name, type 'i'/'f'/'s', count, data). See io_pdx_mesh/pdx_data.py, whose writer
# reproduces our file byte for byte.
# --------------------------------------------------------------------------------------
MESH_LAYOUT = ("object", f"{SUBJECT}Shape", "mesh", "aabb", "material", "skin", "skeleton", *RIG, "locator")
MESH_PROPERTIES = {"mesh": ["p", "n", "ta", "u0", "tri"], "aabb": ["min", "max"],
                   "material": ["shader", "diff", "n", "spec"], "skin": ["bones", "ix", "w"]}
SWAP = [0, 2, 1]                                   # Blender (x, y, z) <-> PDX (x, z, y): a reflection, its own inverse


def mesh_property(name, value):
    import struct

    import numpy as np
    head = b"!" + struct.pack("b", len(name)) + name.encode("latin-1")
    if isinstance(value, str):
        raw = value.encode("latin-1") + b"\x00"          # an empty string is still one NUL, as in OWB's files
        return head + b"s" + struct.pack("<ii", 1, len(raw)) + raw
    value = np.asarray(value)
    if value.dtype.kind == "i":
        return head + b"i" + struct.pack("<i", value.size) + value.astype("<i4").tobytes()
    return head + b"f" + struct.pack("<i", value.size) + value.astype("<f4").tobytes()


def mesh_object(name, depth):
    return b"[" * depth + name.encode("latin-1") + b"\x00"


def write_mesh(path, shape, arrays, textures):
    """The layout of OWB's mirelurk.mesh: mesh (p n ta u0 tri) > aabb, material, skin; then the skeleton, a bone an
    object; then an empty locator. `arrays` carries the skin ("ix", "w") and the bones' PDX-space joints."""
    import numpy as np
    data = b"@@b@" + mesh_property("pdxasset", np.array([1, 0], dtype=np.int32))
    data += mesh_object("object", 1) + mesh_object(shape, 2) + mesh_object("mesh", 3)
    for key in MESH_PROPERTIES["mesh"]:
        data += mesh_property(key, arrays[key].reshape(-1))
    data += mesh_object("aabb", 4)
    data += mesh_property("min", arrays["p"].min(0)) + mesh_property("max", arrays["p"].max(0))
    data += mesh_object("material", 4) + mesh_property("shader", "PdxMeshAdvanced")
    for key, name in zip(("diff", "n", "spec"), textures):
        data += mesh_property(key, name)
    data += mesh_object("skin", 4) + mesh_property("bones", np.array([4], dtype=np.int32))
    data += mesh_property("ix", arrays["ix"].reshape(-1)) + mesh_property("w", arrays["w"].reshape(-1))
    data += mesh_object("skeleton", 3)
    for i, (name, (parent, _)) in enumerate(RIG.items()):
        data += mesh_object(name, 4) + mesh_property("ix", np.array([i], dtype=np.int32))
        if parent is not None:
            data += mesh_property("pa", np.array([list(RIG).index(parent)], dtype=np.int32))
        # the inverse bind matrix, four columns of three: every bone rests unrotated, so it is I | -joint
        data += mesh_property("tx", np.concatenate([np.eye(3).reshape(-1), -arrays["joints"][i]]).astype(np.float32))
    data += mesh_object("locator", 1)
    path.write_bytes(data)


def write_anim(path, rig, poses, joints):
    """info (fps, sa = samples, j = bones) > a bone an object (sa = which curves it animates; t, q, s = its first
    sample); then samples (t, q), packed frame by frame and, within a frame, bone by bone. `joints` are PDX-space.
    q and -q are one rotation, but the engine interpolates between samples, so each bone's quaternions are kept
    on one side from frame to frame."""
    import numpy as np
    t = np.zeros((len(poses), len(rig.names), 3))
    q = np.zeros((len(poses), len(rig.names), 4))
    for f, pose in enumerate(poses):
        for i, name in enumerate(rig.names):
            origin = joints[rig.parent[i]] if rig.parent[i] >= 0 else np.zeros(3)
            t[f, i] = joints[i] - origin + np.asarray(pose.get(name + ".t", (0.0, 0.0, 0.0)), dtype=np.float64)[SWAP]
            q[f, i] = matrix_quaternion(rotvec_matrix(pose.get(name, (0.0, 0.0, 0.0)))[np.ix_(SWAP, SWAP)])
            if f and q[f, i] @ q[f - 1, i] < 0:
                q[f, i] = -q[f, i]
    moves_t = np.abs(t - t[:1]).max((0, 2)) > 1e-6
    moves_q = np.abs(q - q[:1]).max((0, 2)) > 1e-7
    data = b"@@b@" + mesh_property("pdxasset", np.array([1, 0], dtype=np.int32))
    data += mesh_object("info", 1) + mesh_property("fps", np.array([FPS], dtype=np.float32))
    data += mesh_property("sa", np.array([len(poses)], dtype=np.int32))
    data += mesh_property("j", np.array([len(rig.names)], dtype=np.int32))
    for i, name in enumerate(rig.names):
        data += mesh_object(name, 2) + mesh_property("sa", ("t" if moves_t[i] else "") + ("q" if moves_q[i] else ""))
        data += mesh_property("t", t[0, i].astype(np.float32)) + mesh_property("q", q[0, i].astype(np.float32))
        data += mesh_property("s", np.array([1.0], dtype=np.float32))
    data += mesh_object("samples", 1)
    if moves_t.any():
        data += mesh_property("t", t[:, moves_t].astype(np.float32).reshape(-1))
    if moves_q.any():
        data += mesh_property("q", q[:, moves_q].astype(np.float32).reshape(-1))
    path.write_bytes(data)


def read_mesh(path):
    """-> {object path (tuple of names): {property: ndarray | str}}, both in file order. Raises on a byte it
    cannot place, so a file that reads has no trailing bytes."""
    import struct

    import numpy as np
    raw = path.read_bytes()
    if raw[:4] != b"@@b@":
        raise ValueError(f"{path}: not a binary Clausewitz mesh")
    pos, stack, out = 4, [], {(): {}}
    while pos < len(raw):
        if raw[pos:pos + 1] == b"[":
            depth = 0
            while raw[pos:pos + 1] == b"[":
                depth, pos = depth + 1, pos + 1
            end = raw.index(b"\x00", pos)
            stack = stack[:depth - 1] + [raw[pos:end].decode("latin-1")]
            out.setdefault(tuple(stack), {})
            pos = end + 1
        elif raw[pos:pos + 1] == b"!":
            length = raw[pos + 1]
            name = raw[pos + 2:pos + 2 + length].decode("latin-1")
            pos += 2 + length
            kind, count = raw[pos:pos + 1], struct.unpack_from("<i", raw, pos + 1)[0]
            pos += 5
            if kind == b"s":
                size = struct.unpack_from("<i", raw, pos)[0]
                value = raw[pos + 4:pos + 4 + size].rstrip(b"\x00").decode("latin-1")
                pos += 4 + size
            else:
                value = np.frombuffer(raw, dtype="<i4" if kind == b"i" else "<f4", count=count, offset=pos).copy()
                pos += 4 * count
            out[tuple(stack)][name] = value
        else:
            raise ValueError(f"{path}: unexpected byte {raw[pos:pos + 1]!r} at {pos}")
    return out


def ancestors(parent, i):
    """The indices above bone i, itself excluded."""
    out = []
    while parent[i] >= 0:
        i = parent[i]
        out.append(i)
    return out


def first_mesh(tree):
    """The first renderable mesh of a read_mesh() tree (p, n, ta, u0 and tri present)."""
    for props in tree.values():
        if all(k in props for k in ("p", "n", "ta", "u0", "tri")):
            return {k: props[k].reshape(-1, w) for k, w in (("p", 3), ("n", 3), ("ta", 4), ("u0", 2), ("tri", 3))}
    raise ValueError("no mesh with p, n, ta, u0 and tri")


def winding_agreement(mesh):
    """Share of triangles whose cross(p1 - p0, p2 - p0) points the way their vertex normals do."""
    import numpy as np
    p, n, tri = mesh["p"], mesh["n"], mesh["tri"]
    geometric = np.cross(p[tri[:, 1]] - p[tri[:, 0]], p[tri[:, 2]] - p[tri[:, 0]])
    return float(((geometric * n[tri].mean(1)).sum(1) > 0).mean())


def signed_volume(mesh):
    """Positive when the stored winding faces outwards in the engine's sense (OWB's and vanilla's do): an
    inside-out sculpt - STL winding is not repaired on import - turns it negative."""
    import numpy as np
    p, tri = mesh["p"].astype(np.float64), mesh["tri"]
    return float((p[tri[:, 0]] * np.cross(p[tri[:, 1]], p[tri[:, 2]])).sum() / 6.0)


# --------------------------------------------------------------------------------------
# DDS: DXT5 with a full mip chain under one header with OWB's field values (flags 0xa1007, caps 0x401008,
# linear size of the top level). Pillow writes no mip chain, so each level is compressed alone and spliced.
# Pillow compresses the colour half of a block. The alpha half is ours: Pillow's is a 6-value quantiser that
# never emits the block's own endpoints, which cost the normal map's y 40 % of its range inside every block.
# The normal map's colour half is ours too - the shader reads only its G.
# --------------------------------------------------------------------------------------
def dds_header(path):
    import struct
    raw = path.read_bytes()[:128]
    size, flags, height, width, pitch, depth, mips = struct.unpack_from("<7I", raw, 4)
    pf_size, pf_flags, fourcc, bpp = struct.unpack_from("<2I4sI", raw, 76)
    caps = struct.unpack_from("<I", raw, 108)[0]
    return dict(magic=raw[:4], size=size, flags=flags, w=width, h=height, pitch=pitch, mips=mips, pf_size=pf_size,
                pf_flags=pf_flags, fourcc=fourcc, bpp=bpp, caps=caps)


def dds_levels(path):
    """Every mip level of a DXT5 DDS as uint8 RGBA, top first: each level's blocks decoded by Pillow under a
    one-level header of its own."""
    import io
    import struct

    import numpy as np
    from PIL import Image
    raw, head = path.read_bytes(), dds_header(path)
    pos, size = 128, head["w"]
    for _ in range(head["mips"]):
        length = max(1, size // 4) ** 2 * 16
        one = bytearray(raw[:128])
        struct.pack_into("<7I", one, 4, 124, 0x81007, size, size, length, 0, 1)
        struct.pack_into("<I", one, 108, 0x1000)
        yield np.asarray(Image.open(io.BytesIO(bytes(one) + raw[pos:pos + length])).convert("RGBA"))
        pos, size = pos + length, max(1, size // 2)


def dxt_blocks(channel):
    """(H, W) uint8 -> (blocks, 16) int64: the 4x4 blocks in file order, the edges replicated up to a multiple of 4."""
    import numpy as np
    h, w = channel.shape
    channel = np.pad(channel, ((0, -h % 4), (0, -w % 4)), mode="edge")
    bh, bw = channel.shape[0] // 4, channel.shape[1] // 4
    return channel.reshape(bh, 4, bw, 4).transpose(0, 2, 1, 3).reshape(-1, 16).astype(np.int64)


def dxt5_alpha(channel):
    """The alpha half of DXT5 blocks in 8-value mode: a0 = the block's maximum, a1 = its minimum."""
    import numpy as np
    v = dxt_blocks(channel)
    a0, a1 = v.max(1), v.min(1)
    step = np.rint((a0[:, None] - v) * 7.0 / np.maximum(a0 - a1, 1)[:, None]).astype(np.int64)   # 0 = a0 .. 7 = a1
    index = np.where(step == 0, 0, np.where(step == 7, 1, step + 1))
    index[a0 == a1] = 0
    bits = (index << (3 * np.arange(16))).sum(1)
    out = np.zeros((len(v), 8), dtype=np.uint8)
    out[:, 0], out[:, 1] = a0, a1
    for i in range(6):
        out[:, 2 + i] = (bits >> (8 * i)) & 255
    return out


def dxt5_green(channel):
    """The colour half of DXT5 blocks for a map whose only colour channel the shader reads is G (the normal
    map): the two 6-bit green endpoints are searched around the block's extremes, R repeats G as vanilla's maps
    do, and B - PdxMeshAdvanced's emissive mask - is 0 in every endpoint, so in every texel of every level."""
    import numpy as np
    v = dxt_blocks(channel).astype(np.float64)
    top, bottom = np.rint(v.max(1) * 63.0 / 255.0).astype(np.int64), np.rint(v.min(1) * 63.0 / 255.0).astype(np.int64)
    best_error = np.full(len(v), np.inf)
    best = np.zeros((len(v), 2), dtype=np.int64)
    best_index = np.zeros((len(v), 16), dtype=np.int64)
    for d0 in range(-2, 3):
        for d1 in range(-2, 3):
            q0, q1 = np.clip(top + d0, 0, 63), np.clip(bottom + d1, 0, 63)
            q0, q1 = np.maximum(q0, q1), np.minimum(q0, q1)
            e0, e1 = ((q0 << 2) | (q0 >> 4)).astype(np.float64), ((q1 << 2) | (q1 >> 4)).astype(np.float64)
            palette = np.stack([e0, e1, (2 * e0 + e1) / 3.0, (e0 + 2 * e1) / 3.0], axis=1)
            distance = np.abs(v[:, :, None] - palette[:, None, :])
            index = distance.argmin(2)
            error = (distance.min(2) ** 2).sum(1)
            better = error < best_error
            best_error[better], best[better, 0], best[better, 1] = error[better], q0[better], q1[better]
            best_index[better] = index[better]
    q0, q1 = best[:, 0], best[:, 1]
    best_index[q0 == q1] = 0
    out = np.zeros((len(v), 8), dtype=np.uint8)
    for column, q in ((0, q0), (2, q1)):
        word = ((q >> 1) << 11) | (q << 5)
        out[:, column], out[:, column + 1] = word & 255, word >> 8
    bits = (best_index << (2 * np.arange(16))).sum(1)
    for i in range(4):
        out[:, 4 + i] = (bits >> (8 * i)) & 255
    return out


def write_dds(path, levels, green_only=False):
    """levels: uint8 RGBA arrays, each half the one before, down to 1x1. `green_only`: see dxt5_green."""
    import io
    import struct

    import numpy as np
    from PIL import Image
    payload = []
    for level in levels:
        buf = io.BytesIO()
        Image.fromarray(level, "RGBA").save(buf, format="DDS", pixel_format="DXT5")
        blocks = np.frombuffer(buf.getvalue()[128:], dtype=np.uint8).reshape(-1, 16).copy()
        blocks[:, :8] = dxt5_alpha(level[..., 3])
        if green_only:
            blocks[:, 8:] = dxt5_green(level[..., 1])
        payload.append(blocks.tobytes())
    h, w = levels[0].shape[:2]
    header = bytearray(128)
    header[:4] = b"DDS "
    struct.pack_into("<7I", header, 4, 124, 0xA1007, h, w, len(payload[0]), 0, len(levels))
    struct.pack_into("<2I4sI", header, 76, 32, 0x4, b"DXT5", 0)
    struct.pack_into("<I", header, 108, 0x401008)
    path.write_bytes(bytes(header) + b"".join(payload))


def halve(image, weights=None):
    """2x2 box filter; with `weights` (H x W) a weighted one, returning (image, weights)."""
    import numpy as np
    h, w = image.shape[:2]
    blocks = image.reshape(h // 2, 2, w // 2, 2, -1)
    if weights is None:
        return blocks.mean((1, 3))
    wb = weights.reshape(h // 2, 2, w // 2, 2, 1)
    total = wb.sum((1, 3))
    return (blocks * wb).sum((1, 3)) / np.maximum(total, 1e-9), total[..., 0] / 4.0


def push_pull(image, weights):
    """Fill texels of zero weight from their surroundings (a pull-push pyramid), so that no mip level
    bleeds the background into an island."""
    import numpy as np
    pyramid = [(image * weights[..., None], weights)]
    while pyramid[-1][1].shape[0] > 1:
        c, w = pyramid[-1]
        h2, w2 = c.shape[0] // 2, c.shape[1] // 2
        pyramid.append((c.reshape(h2, 2, w2, 2, -1).sum((1, 3)), w.reshape(h2, 2, w2, 2).sum((1, 3))))
    c, w = pyramid[-1]
    fill = c / np.maximum(w, 1e-9)[..., None]
    for c, w in reversed(pyramid[:-1]):
        fill = np.where(w[..., None] > 0, c / np.maximum(w, 1e-9)[..., None], fill.repeat(2, 0).repeat(2, 1))
    return fill


def to_size(image, size, weights=None):
    while image.shape[0] > size:
        if weights is None:
            image = halve(image)
        else:
            image, weights = halve(image, weights)
    return image if weights is None else (image, weights)


def unit(v):
    import numpy as np
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


def smoothstep(lo, hi, x):
    import numpy as np
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def to_bytes(image):
    import numpy as np
    return np.clip(np.rint(image * 255.0), 0, 255).astype(np.uint8)


def mip_chain(image, renormalise=False):
    """float 0-1 (or, with `renormalise`, unit vectors), top level first, down to 1x1."""
    levels = [image]
    while levels[-1].shape[0] > 1:
        levels.append(unit(halve(levels[-1])) if renormalise else halve(levels[-1]))
    return levels


def encode_normal(n):
    """Tangent-space normals (Blender's frame, x right, y up, z out) -> the engine's RRxG layout.
    G (and R, as vanilla's maps do) = x, A = y, B = 0 (the EMISSIVE mask)."""
    import numpy as np
    n = unit(n)
    x, y = n[..., 0] * 0.5 + 0.5, n[..., 1] * 0.5 + 0.5
    return np.stack([x, x, np.zeros_like(x), y], axis=-1)


def decode_normal_like_the_engine(rgba, flip_y=True):
    """standardfuncsgfx.fxh UnpackRRxGNormal on RGBA 0-1."""
    import numpy as np
    x = rgba[..., 1] * 2.0 - 1.0
    y = rgba[..., 3] * 2.0 - 1.0
    if flip_y:
        y = -y
    z = np.sqrt(np.clip(1.0 - x * x - y * y, 0.0, 1.0))
    return np.stack([x, y, z], axis=-1)


def luma_percentiles(rgb255):
    import numpy as np
    return np.percentile(rgb255 @ np.array([0.2126, 0.7152, 0.0722]), [5, 50, 95])


def uv_coverage(npz, size):
    """The texels (top-down) whose centre lies inside a UV triangle, grown by one texel. Blender clears a bake
    to black - a tangent-space normal bake to flat blue - so the bakes themselves cannot say where they are
    valid."""
    import numpy as np
    uv = npz["loop_uv"][npz["tri_loops"]]
    points = np.stack([uv[..., 0] * size, (1.0 - uv[..., 1]) * size], axis=-1)
    mask = np.zeros((size, size), dtype=bool)
    for a, b, c in points:
        lo = np.maximum(np.floor(np.minimum(np.minimum(a, b), c)).astype(int), 0)
        hi = np.minimum(np.ceil(np.maximum(np.maximum(a, b), c)).astype(int), size - 1)
        det = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if abs(det) < 1e-12 or (hi < lo).any():
            continue
        x, y = np.meshgrid(np.arange(lo[0], hi[0] + 1) + 0.5, np.arange(lo[1], hi[1] + 1) + 0.5)
        w1 = ((x - a[0]) * (c[1] - a[1]) - (y - a[1]) * (c[0] - a[0])) / det
        w2 = ((b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0])) / det
        mask[lo[1]:hi[1] + 1, lo[0]:hi[0] + 1] |= (w1 >= 0) & (w2 >= 0) & (w1 + w2 <= 1)
    grown = mask.copy()
    grown[1:] |= mask[:-1]
    grown[:-1] |= mask[1:]
    grown[:, 1:] |= mask[:, :-1]
    grown[:, :-1] |= mask[:, 1:]
    return grown


def paint(work, npz):
    """The three textures as float RGBA 0-1 (top-down), previews in Blender's conventions, and the
    object-space normal map that check() holds the tangent-space one to."""
    import numpy as np
    from PIL import Image

    def load(name):
        return np.load(work / f"{name}.npy").astype(np.float32)

    hit = uv_coverage(npz, BAKE_RES).astype(np.float32)
    coverage = float(hit.mean())
    covered = to_size(hit[..., None], TEX_D)[..., 0] > 0.5

    def field(image, size):
        image, weights = to_size(image, size, hit)
        return push_pull(image, weights)

    ao = field(load("ao"), TEX_D)[..., 0]
    a = field(load("masks_a"), TEX_D)
    b = field(load("masks_b"), TEX_D)
    noise_large, noise_fine, pointiness = a[..., 0], a[..., 1], a[..., 2]
    height, up, noise_patch = b[..., 0], b[..., 1], b[..., 2]

    # Pointiness is ~0.5 +- a hair; spread it robustly around its median - over the islands, not their padding.
    centre = np.median(pointiness[covered])
    spread = max(np.percentile(np.abs(pointiness[covered] - centre), 96), 1e-6)
    curvature = np.clip((pointiness - centre) / spread, -1.0, 1.0)
    ridge, crevice = np.clip(curvature, 0, 1), np.clip(-curvature, 0, 1)

    def rgb(c):
        return np.array(c, dtype=np.float32) / 255.0

    def mix(base, colour, t):
        return base + (rgb(colour) - base) * t[..., None]

    colour = rgb(DEEP) + (rgb(MID) - rgb(DEEP)) * smoothstep(0.38, 0.72, noise_large)[..., None]
    colour = mix(colour, PATCH, 0.45 * smoothstep(0.52, 0.74, noise_patch))
    colour = mix(colour, SPECKLE, 0.55 * smoothstep(0.60, 0.76, noise_fine))
    colour = mix(colour, RIDGE, 0.60 * ridge)
    colour = mix(colour, CREVICE, 0.75 * crevice)
    colour = colour * (TOP_LIGHT[0] + TOP_LIGHT[1] * up)[..., None]
    colour = colour * (WET_FEET[0] + (1.0 - WET_FEET[0]) * smoothstep(0.0, WET_FEET[1], height))[..., None]
    occlusion = AO_FLOOR + (1.0 - AO_FLOOR) * np.clip(ao, 0, 1) ** AO_GAMMA
    colour = np.clip(colour * occlusion[..., None], 0.0, 1.0)
    diffuse = np.concatenate([colour, np.ones_like(colour[..., :1])], axis=-1)

    # The map holds x and y only and the shader rebuilds z as +sqrt(...): a normal that leans past the surface
    # (0.5 % of texels, in the deepest folds) is seen mirrored. Mirror it here, so that every mip level averages
    # the vectors the engine actually reconstructs at level 0.
    normal = load("normal") * 2.0 - 1.0
    normal[..., 2] = np.abs(normal[..., 2])
    normal_n, weights = to_size(normal, TEX_N, hit)
    normal_n = push_pull(normal_n, weights)             # filled everywhere, so island borders blend into like
    flat = np.zeros_like(normal_n)
    flat[..., 2] = 1.0
    normal_n = unit(np.where(np.linalg.norm(normal_n, axis=-1, keepdims=True) > 1e-3, normal_n, flat))

    open_skin = to_size((np.clip(ao, 0, 1) ** 2 * (1.0 - 0.6 * crevice))[..., None], TEX_S)[..., 0]
    gloss = (GLOSS_RANGE[0] + (GLOSS_RANGE[1] - GLOSS_RANGE[0]) * open_skin) / 255.0
    spec = np.stack([np.zeros_like(gloss), np.full_like(gloss, SPEC_LEVEL / 255.0), np.zeros_like(gloss), gloss], -1)

    truth, weights = to_size(load("normal_object") * 2.0 - 1.0, TEX_N, hit)
    truth = unit(push_pull(truth, weights))

    ours = " / ".join(f"{x:.0f}" for x in luma_percentiles(colour[covered].astype(np.float64) * 255.0))
    if OWB_REF_DDS.exists():
        reference = np.asarray(Image.open(OWB_REF_DDS).convert("RGB"), dtype=np.float64).reshape(-1, 3)
        theirs = "OWB's mirelurk: " + " / ".join(f"{x:.0f}" for x in luma_percentiles(reference))
    else:
        theirs = "OWB's mirelurk_d.dds not found: no comparison"
    print(f"  diffuse luma p5 / median / p95: {ours}   ({theirs})")

    # The preview's roughness from the engine's own gloss: a Blinn-Phong exponent n = 2^(11 g)
    # (standardfuncsgfx.fxh) is a GGX alpha of sqrt(2 / (n + 2)), and a Principled roughness of sqrt(alpha).
    roughness = (2.0 / (2.0 ** (11.0 * gloss[..., None]) + 2.0)) ** 0.25
    previews = {"preview_d.png": colour, "preview_n.png": normal_n * 0.5 + 0.5,
                "preview_r.png": np.repeat(roughness, 3, axis=-1),
                "preview_uv.png": np.repeat(to_size(hit[..., None], TEX_D), 3, axis=-1)}
    return diffuse, normal_n, spec, previews, coverage, truth


def weld(npz, rig):
    """Corners -> engine vertices, each with its low-poly vertex's skin, and the skeleton moved along with them.
    A vertex splits where its UVs differ (a seam); where several corners weld
    the first one's normal and tangent stand, as in io_pdx_mesh (the normals are identical; the tangents differ
    on under 1 % of vertices, measured harmless)."""
    import numpy as np
    key = np.column_stack([npz["loop_vert"].astype(np.int64), np.rint(npz["loop_uv"] * 65536.0).astype(np.int64)])
    _, first, inverse = np.unique(key, axis=0, return_index=True, return_inverse=True)
    tri = inverse.reshape(-1)[npz["tri_loops"]]
    swap = [0, 2, 1]                                   # Blender (x, y, z) -> PDX (x, z, y)
    uv = npz["loop_uv"][first]
    normal = unit(npz["loop_normal"][first])
    tangent, sign = npz["loop_tangent"][first].copy(), npz["loop_bitangent_sign"][first].copy()

    # MikkTSpace can return a zero tangent at a folded corner (the vertex normal lying in its triangle's plane).
    # Rebuild it from that triangle's own dP/du, laid into the normal's plane.
    lost = np.flatnonzero(np.linalg.norm(tangent, axis=1) < 0.5)
    corner_triangle = np.empty(len(npz["loop_vert"]), dtype=np.int64)
    corner_triangle[npz["tri_loops"].reshape(-1)] = np.repeat(np.arange(len(npz["tri_loops"])), 3)
    for i in lost:
        corners = npz["tri_loops"][corner_triangle[first[i]]]
        p, t = npz["co"][npz["loop_vert"][corners]].astype(np.float64), npz["loop_uv"][corners].astype(np.float64)
        (du1, dv1), (du2, dv2) = t[1] - t[0], t[2] - t[0]
        det = du1 * dv2 - dv1 * du2
        along_u = ((p[1] - p[0]) * dv2 - (p[2] - p[0]) * dv1) / det if abs(det) > 1e-12 else np.zeros(3)
        along_u = along_u - normal[i] * (along_u @ normal[i])
        if np.linalg.norm(along_u) < 1e-6:                 # no gradient either: any direction in the plane
            along_u = np.cross(normal[i], [1.0, 0.0, 0.0] if abs(normal[i][0]) < 0.9 else [0.0, 1.0, 0.0])
        tangent[i] = along_u
    sign[np.abs(sign) < 0.5] = 1.0

    # Decimation shaves the extremes: seat the welded mesh on y = 0 again, centred (a translation only, so the
    # bakes still fit).
    vertex = npz["loop_vert"][first]
    p = npz["co"][vertex][:, swap].astype(np.float64)
    offset = np.array([(p[:, 0].min() + p[:, 0].max()) / 2, p[:, 1].min(), (p[:, 2].min() + p[:, 2].max()) / 2])
    p -= offset
    index, weight = rig.index[vertex].astype(np.int32), rig.weight[vertex].astype(np.float32)
    index[weight <= 0] = -1                           # an unused influence is -1 / 0, as in OWB's meshes
    return {
        "ix": index, "w": weight, "joints": rig.joints[:, swap] - offset, "vertex": vertex, "offset": offset,
        "p": p.astype(np.float32),
        "n": normal[:, swap].astype(np.float32),
        "ta": np.column_stack([unit(tangent)[:, swap], np.sign(sign)]).astype(np.float32),
        "u0": np.column_stack([uv[:, 0], 1.0 - uv[:, 1]]).astype(np.float32),
        "tri": tri[:, [0, 2, 1]].astype(np.int32),      # a reflection reverses the winding
    }


# --------------------------------------------------------------------------------------
# The rig. A POSE is a dict {"bone": (rx, ry, rz), "bone.t": (dx, dy, dz)}: a ROTATION VECTOR IN DEGREES about the
# model's axes, applied at the bone's joint, relative to its parent (children follow), and an optional translation
# of that joint. Right-hand rule, for a figure facing -y with x to its left:
#   +rx pitches FORWARD / down: an upright part (torso, wing) tips forward - a bow; a forward-pointing part (head,
#       the raised arm, a foot) dips; a hanging limb (the right arm, a leg, the beard) swings BACKWARD
#   -rx pitches BACK / up;   +rz yaws to the figure's LEFT;   +ry rolls the top of a part towards its LEFT.
# A CLIP MODULE (CLIP_DIR/<animation id>.py) defines SECONDS and clip(u, rig) -> pose for u in [0, 1]; every clip
# returns the same pose at 0 and 1, so idles and attacks chain and loops close. It imports nothing but `math`.
# --------------------------------------------------------------------------------------
def rotvec_matrix(rv_deg):
    import numpy as np
    rv = np.radians(np.asarray(rv_deg, dtype=np.float64))
    angle = np.linalg.norm(rv)
    if angle < 1e-12:
        return np.eye(3)
    x, y, z = rv / angle
    k = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    return np.eye(3) + np.sin(angle) * k + (1 - np.cos(angle)) * (k @ k)


def matrix_rotvec(m):
    """The rotation vector (degrees) of a rotation matrix: the inverse of rotvec_matrix."""
    import numpy as np
    angle = np.arccos(np.clip((np.trace(m) - 1.0) / 2.0, -1.0, 1.0))
    if angle < 1e-9:
        return np.zeros(3)
    if np.pi - angle < 1e-6:                                   # 180 degrees: the axis from the symmetric part,
        axis = np.sqrt(np.clip((np.diag(m) + 1.0) / 2.0, 0.0, 1.0))      # signed against its largest component
        i = int(np.argmax(axis))
        for j in range(3):
            if j != i and m[i, j] < 0:
                axis[j] = -axis[j]
    else:
        axis = np.array([m[2, 1] - m[1, 2], m[0, 2] - m[2, 0], m[1, 0] - m[0, 1]]) / (2.0 * np.sin(angle))
    return np.degrees(axis / np.linalg.norm(axis) * angle)


def matrix_quaternion(m):
    """-> (x, y, z, w), unit length (Shepperd's method)."""
    import numpy as np
    trace = np.trace(m)
    if trace > 0:
        s = np.sqrt(trace + 1.0) * 2
        q = np.array([(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, 0.25 * s])
    else:
        i = int(np.argmax(np.diag(m)))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = np.sqrt(m[i, i] - m[j, j] - m[k, k] + 1.0) * 2
        q = np.zeros(4)
        q[i], q[j], q[k], q[3] = 0.25 * s, (m[j, i] + m[i, j]) / s, (m[k, i] + m[i, k]) / s, (m[k, j] - m[j, k]) / s
    return q / np.linalg.norm(q)


def rotation_between(a, b):
    """The smallest rotation taking direction a to direction b."""
    import numpy as np
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    axis = np.cross(a, b)
    sine, cosine = np.linalg.norm(axis), float(a @ b)
    if sine < 1e-9:
        if cosine > 0:
            return np.eye(3)
        side = np.cross(a, [1.0, 0.0, 0.0] if abs(a[0]) < 0.9 else [0.0, 1.0, 0.0])
        return rotvec_matrix(180.0 * side / np.linalg.norm(side))
    return rotvec_matrix(np.degrees(np.arctan2(sine, cosine)) * axis / sine)


class Rig:
    """RIG, the four strongest skin weights of every low-poly vertex, and skinning in numpy that is, step for
    step, what the game's vertex shader does - so a preview of a pose is what the game will draw. Every bone
    rests unrotated: its world matrix is its parent's . T(joint - parent's joint + pose's .t) . R(pose)."""

    def __init__(self, co, dense_weights):
        import numpy as np
        self.names = list(RIG)
        self.parent = [self.names.index(RIG[n][0]) if RIG[n][0] else -1 for n in self.names]
        self.joints = np.array([RIG[n][1] for n in self.names], dtype=np.float64)
        self.co = np.asarray(co, dtype=np.float64)
        w = np.asarray(dense_weights, dtype=np.float64)
        order = np.argsort(-w, axis=1, kind="stable")[:, :4]
        top = np.take_along_axis(w, order, axis=1)
        top[top < 0.02] = 0.0                                  # crumbs only make a vertex wobble
        self.index, self.weight = order, top / top.sum(1, keepdims=True)

    def joint(self, name):
        """The rest position of a joint (model space)."""
        return self.joints[self.names.index(name)].copy()

    def matrices(self, pose):
        """-> (world, skin) 4x4 per bone."""
        import numpy as np
        world = []
        for i, name in enumerate(self.names):
            m = np.eye(4)
            m[:3, :3] = rotvec_matrix(pose.get(name, (0.0, 0.0, 0.0)))
            origin = self.joints[self.parent[i]] if self.parent[i] >= 0 else np.zeros(3)
            m[:3, 3] = self.joints[i] - origin + np.asarray(pose.get(name + ".t", (0.0, 0.0, 0.0)), dtype=np.float64)
            world.append(m if self.parent[i] < 0 else world[self.parent[i]] @ m)
        world = np.stack(world)
        unbind = np.tile(np.eye(4), (len(world), 1, 1))
        unbind[:, :3, 3] = -self.joints
        return world, world @ unbind

    def joint_positions(self, pose):
        return self.matrices(pose)[0][:, :3, 3]

    def skin(self, pose):
        import numpy as np
        mats = self.matrices(pose)[1]
        ph = np.concatenate([self.co, np.ones((len(self.co), 1))], axis=1)
        out = np.zeros((len(ph), 3))
        for k in range(4):
            out += np.einsum("nij,nj->ni", mats[self.index[:, k]], ph)[:, :3] * self.weight[:, k:k + 1]
        return out

    def ik(self, pose, upper, lower, end, target, end_rotation=(0.0, 0.0, 0.0), pole=None):
        """Two-bone inverse kinematics, written into `pose`: turn `upper` (a hip or shoulder) and bend `lower`
        (the knee or elbow, about the axis it is already bent about in the sculpt) so that the joint `end` (the
        ankle or wrist) lands on `target` (model space). `end` is then turned so that, in the world, it keeps
        the sculpt's own orientation plus `end_rotation` - a planted foot stays flat whatever the leg does. Set
        everything ABOVE the limb (root, pelvis, spine, chest) in the pose first: the solution depends on where
        the hip or shoulder is. An out-of-reach target gets the straightest limb that points at it. `pole` (a
        model-space direction) is where the knee or elbow should point: the limb is spun about the hip-to-ankle
        line until it does - the ankle stays on its target. Without one the knee goes wherever the smallest
        rotation leaves it, which on a leg folded far from the sculpt's pose is out sideways. Returns how far
        the end landed from the target."""
        import numpy as np
        iu, il, ie = (self.names.index(n) for n in (upper, lower, end))
        for n in (upper, lower, end):
            pose.pop(n, None)
        world = self.matrices(pose)[0]
        parent_rotation, hip = world[self.parent[iu]][:3, :3], world[iu][:3, 3]
        a0, b0 = self.joints[il] - self.joints[iu], self.joints[ie] - self.joints[il]
        l1, l2 = np.linalg.norm(a0), np.linalg.norm(b0)
        want = parent_rotation.T @ (np.asarray(target, dtype=np.float64) - hip)
        d = np.clip(np.linalg.norm(want), abs(l1 - l2) + 1e-4, l1 + l2 - 1e-4)
        axis = np.cross(a0, b0)
        if np.linalg.norm(axis) < 0.05 * l1 * l2:
            raise ValueError(f"{upper} - {lower} - {end} is straight in RIG: the hinge a knee or elbow bends about is "
                             "read off the sculpt's own bend, and there is none")
        axis = axis / np.linalg.norm(axis)
        rest_interior = np.arccos(np.clip((-a0 @ b0) / (l1 * l2), -1, 1))
        interior = np.arccos(np.clip((l1 * l1 + l2 * l2 - d * d) / (2 * l1 * l2), -1, 1))
        bend = rotvec_matrix(np.degrees(rest_interior - interior) * axis)
        swing = rotation_between(a0 + bend @ b0, want)
        if pole is not None:
            line = want / np.linalg.norm(want)
            knee = swing @ a0
            knee = knee - line * (knee @ line)
            aim = parent_rotation.T @ np.asarray(pole, dtype=np.float64)
            aim = aim - line * (aim @ line)
            if np.linalg.norm(knee) > 1e-6 and np.linalg.norm(aim) > 1e-6:
                spin = np.degrees(np.arctan2(np.cross(knee, aim) @ line, knee @ aim))
                swing = rotvec_matrix(spin * line) @ swing
        pose[upper], pose[lower] = tuple(matrix_rotvec(swing)), tuple(matrix_rotvec(bend))
        pose[end] = tuple(matrix_rotvec((parent_rotation @ swing @ bend).T @ rotvec_matrix(end_rotation)))
        return float(np.linalg.norm(self.joint_positions(pose)[ie] - np.asarray(target)))


def load_clips():
    """{animation id: module} from CLIP_DIR, in ANIMATIONS' order."""
    import importlib.util
    clips = {}
    for name in ANIMATIONS:
        path = ROOT / CLIP_DIR / f"{name}.py"
        if not path.exists():
            raise SystemExit(f"STATES names the animation {name!r} but {path} is missing")
        spec = importlib.util.spec_from_file_location(f"{CLIP_DIR}_{name}", path)
        clips[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(clips[name])
    return clips


def sample_clip(module, rig):
    """SECONDS x FPS steps and one more: the last sample repeats the first, as OWB's clips do (61 = 60 steps)."""
    steps = int(round(module.SECONDS * FPS))
    if abs(steps - module.SECONDS * FPS) > 1e-6:
        raise SystemExit(f"{module.__name__}: SECONDS = {module.SECONDS} is not a whole number of frames at {FPS} fps")
    return [module.clip(i / steps, rig) for i in range(steps + 1)]


def load_rig(work):
    import numpy as np
    weights = np.load(work / "weights.npz")
    if list(weights["names"]) != list(RIG):
        raise SystemExit(f"the skin weights cached in {work} were solved for another skeleton: run a full build")
    return Rig(np.load(work / "mesh.npz")["co"], weights["weights"])


# --------------------------------------------------------------------------------------
# The emulator: a .mesh and an .anim READ BACK and played as the engine plays them. It was proven on OWB's
# mirelurk (idle, run and attack keep the crab's feet on the ground and thrust its claws forward) before it was trusted.
# --------------------------------------------------------------------------------------
def file_rig(tree):
    import numpy as np
    bones = [(path[-1], props) for path, props in tree.items() if len(path) == 4 and path[2] == "skeleton"]
    unbind = []
    for _, props in bones:
        m = np.eye(4)
        m[:3, :4] = props["tx"].astype(np.float64).reshape(4, 3).T           # four columns of three
        unbind.append(m)
    mesh_path = next(path for path, props in tree.items() if path and path[-1] == "mesh" and "p" in props)
    skin = tree[mesh_path + ("skin",)]
    width = int(skin["bones"][0])
    return dict(names=[n for n, _ in bones], parent=[int(d["pa"][0]) if "pa" in d else -1 for _, d in bones],
                unbind=np.stack(unbind), p=tree[mesh_path]["p"].reshape(-1, 3).astype(np.float64),
                tri=tree[mesh_path]["tri"].reshape(-1, 3), ix=skin["ix"].reshape(-1, width),
                w=skin["w"].reshape(-1, width).astype(np.float64))


def file_anim(tree):
    """-> dict(fps, names, frames): frames[f][bone] = (t, q, s), the unanimated curves held at their first sample."""
    import numpy as np
    info = tree[("info",)]
    bones = [(path[-1], props) for path, props in tree.items() if len(path) == 2 and path[0] == "info"]
    samples, cursor, width = tree.get(("samples",), {}), {"t": 0, "q": 0, "s": 0}, {"t": 3, "q": 4, "s": 1}
    frames = []
    for _ in range(int(info["sa"][0])):
        pose = {}
        for name, props in bones:
            cur = {k: props[k] for k in "tqs"}
            for k in "tqs":
                if k in props["sa"]:
                    cur[k] = samples[k][cursor[k]:cursor[k] + width[k]]
                    cursor[k] += width[k]
            pose[name] = (np.asarray(cur["t"], dtype=np.float64), np.asarray(cur["q"], dtype=np.float64), float(cur["s"][0]))
        frames.append(pose)
    leftover = {k: len(samples.get(k, ())) - cursor[k] for k in "tqs"}
    return dict(fps=float(info["fps"][0]), bones=int(info["j"][0]), names=[n for n, _ in bones], frames=frames,
                leftover=leftover)


def emulate(rig, pose):
    """world = parent's world . T(t) R(q) s;  a vertex = sum of weight . world . tx . vertex."""
    import numpy as np
    world = []
    for i, name in enumerate(rig["names"]):
        t, (x, y, z, w), scale = pose[name]
        m = np.eye(4)
        m[:3, :3] = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                              [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                              [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]) * scale
        m[:3, 3] = t
        world.append(m if rig["parent"][i] < 0 else world[rig["parent"][i]] @ m)
    mats = np.stack(world) @ rig["unbind"]
    ph = np.concatenate([rig["p"], np.ones((len(rig["p"]), 1))], axis=1)
    out = np.zeros((len(ph), 3))
    for k in range(rig["ix"].shape[1]):
        used = rig["ix"][:, k] >= 0
        out[used] += np.einsum("nij,nj->ni", mats[rig["ix"][used, k]], ph[used])[:, :3] * rig["w"][used, k:k + 1]
    return out


GFX_TEMPLATE = """# Rising Tide - the {title} unit model. GENERATED by build_unit_model.py: edit its template, not this file.
# The shape of OWB's gfx/models/owbentity/mirelurk/mirelurk_mesh.gfx: the mesh, the animation ids that the
# entity's states play (each declared in {subject}_animations.asset beside this file), then the textures.
objectTypes = {{
	pdxmesh = {{
		name = "{subject}_mesh"
		file = "{model_dir}/{subject}.mesh"

{animation_ids}

		meshsettings = {{
			texture_diffuse = "{subject}_d.dds"
			texture_normal = "{subject}_n.dds"
			texture_specular = "{subject}_s.dds"
			shader = PdxMeshAdvanced
		}}
	}}
}}
"""

ANIMATIONS_TEMPLATE = """# Rising Tide - the {title}'s animations. GENERATED by build_unit_model.py: edit its template, not this file.
# As in vanilla an animation is declared beside its .anim file: `file` is relative to the declaring .asset's folder.
{animations}"""

ASSET_TEMPLATE = """# Rising Tide - unit entities. GENERATED by build_unit_model.py: edit its template, not this file.
# A sub-unit's `sprite = X` (common/units/mltd_units.txt) resolves to the entity X_entity, as OWB's
# `sprite = mirelurk_infantry` does to mirelurk_infantry_entity (gfx/models/owbentity/jango_owb_base_entity.asset).
# The states are those of OWB's mirelurk_entity (less attack_fire, which it reaches only through next_state), in
# its and vanilla's idiom: idles and attacks are `looping = no` variants drawn by `chance`, an attack handing
# back to the attack state. Every clip ends where it starts, and the variants of one state (idle / idle2,
# attack / attack2) start in the sculpt's own pose, so they chain without a jump; the rest blend in and out.
# No `death` state: the mirelurk has none either.
# scale: the mesh is {height:g} units tall; an OWB human stands 7.37 x 0.8, a deathclaw 6.3 x 1.2.
entity = {{
	name = "{subject}_entity"
	pdxmesh = "{subject}_mesh"
	scale = {scale:g}
	default_state = "idle"

{states}
}}
"""


def outputs(root=None):
    root = MOD if root is None else root
    d = root / MODEL_DIR
    out = {"mesh": d / f"{SUBJECT}.mesh", "d": d / f"{SUBJECT}_d.dds", "n": d / f"{SUBJECT}_n.dds",
           "s": d / f"{SUBJECT}_s.dds", "gfx": d / f"{SUBJECT}_mesh.gfx", "animations": d / f"{SUBJECT}_animations.asset",
           "asset": root / ENTITY_FILE}
    out.update({f"anim_{name}": d / f"{SUBJECT}_{name}.anim" for name in ANIMATIONS})
    return out


def build(work, root):
    """Write every output under `root` (the staging folder: nothing reaches mod_folder before check() passes)."""
    import numpy as np
    from PIL import Image
    out = outputs(root)
    out["mesh"].parent.mkdir(parents=True, exist_ok=True)
    out["asset"].parent.mkdir(parents=True, exist_ok=True)

    npz = np.load(work / "mesh.npz")
    rig = load_rig(work)
    arrays = weld(npz, rig)
    write_mesh(out["mesh"], MESH_LAYOUT[1], arrays, [out[k].name for k in ("d", "n", "s")])
    clips = load_clips()
    poses = {name: sample_clip(module, rig) for name, module in clips.items()}
    for name in ANIMATIONS:
        write_anim(out[f"anim_{name}"], rig, poses[name], arrays["joints"])

    diffuse, normal, spec, previews, coverage, truth = paint(work, npz)
    write_dds(out["d"], [to_bytes(level) for level in mip_chain(diffuse)])
    write_dds(out["n"], [to_bytes(encode_normal(level)) for level in mip_chain(normal, renormalise=True)],
              green_only=True)
    write_dds(out["s"], [to_bytes(level) for level in mip_chain(spec)])
    for name, image in previews.items():
        Image.fromarray(to_bytes(image), "RGB").save(work / name)

    fields = dict(subject=SUBJECT, model_dir=MODEL_DIR, title=SUBJECT.removeprefix("mltd_").replace("_", " ").title(),
                  height=MESH_HEIGHT, scale=ENTITY_SCALE,
                  animation_ids="\n".join(f'\t\tanimation = {{ id = "{name}"\ttype = "{SUBJECT}_{name}_animation" }}'
                                          for name in ANIMATIONS),
                  animations="".join(f'animation = {{\n\tname = "{SUBJECT}_{name}_animation"\n\tfile = '
                                     f'"{out[f"anim_{name}"].name}"\n}}\n' for name in ANIMATIONS),
                  states="\n".join(f'\tstate = {{ name = "{state}"\tanimation = "{animation}"\t{rest} }}'
                                   for state, animation, rest in STATES))
    out["gfx"].write_bytes(GFX_TEMPLATE.format(**fields).encode("utf-8"))        # LF, no BOM
    out["animations"].write_bytes(ANIMATIONS_TEMPLATE.format(**fields).encode("utf-8"))
    out["asset"].write_bytes(ASSET_TEMPLATE.format(**fields).encode("utf-8"))
    seconds = sum(module.SECONDS for module in clips.values())
    print(f"  wrote {len(arrays['tri']):,} triangles, {len(arrays['p']):,} vertices, {len(RIG)} bones, {len(clips)} clips "
          f"({seconds:g} s); the UV islands cover {coverage:.0%} of the texture")
    return arrays, truth, rig, poses


def check(arrays=None, truth=None, root=None, rig=None, poses=None):
    """Everything that can be checked without the game. Raises SystemExit on a failure. With `rig` and `poses`
    (a build) the clips read back from disk are also held to the poses they were written from."""
    import numpy as np
    out, failures, notes = outputs(root), [], []

    def expect(ok, message):
        (notes if ok else failures).append(("ok   " if ok else "FAIL ") + message)

    tree = read_mesh(out["mesh"])
    mesh = first_mesh(tree)
    if arrays is not None:
        same = all(np.array_equal(mesh[k], arrays[k].reshape(mesh[k].shape)) for k in ("p", "n", "ta", "u0", "tri"))
        expect(same, "the mesh reads back as it was written")
    expect(tuple(path[-1] for path in tree if path) == MESH_LAYOUT
           and all(list(tree[path]) == props for path in tree if path for name, props in MESH_PROPERTIES.items()
                   if path[-1] == name)
           and all(list(props) == (["ix", "pa", "tx"] if RIG[path[-1]][0] else ["ix", "tx"])
                   for path, props in tree.items() if len(path) == 4 and path[2] == "skeleton"),
           "objects and properties in io_pdx_mesh's order (mesh, aabb, material, skin; the skeleton; the locator)")
    reference = read_mesh(OWB_REF_MESH) if OWB_REF_MESH.exists() else None
    if reference:
        theirs = {path[-1]: list(props) for path, props in reference.items() if path}
        expect(tree[()]["pdxasset"].tolist() == reference[()]["pdxasset"].tolist()
               and theirs["mesh"] == MESH_PROPERTIES["mesh"] and theirs["aabb"] == MESH_PROPERTIES["aabb"]
               and theirs["skin"] == MESH_PROPERTIES["skin"] and theirs["root"] == ["ix", "tx"]
               and theirs["head"] == ["ix", "pa", "tx"] and "locator" in theirs,
               "pdxasset and the mesh's, aabb's, skin's and bones' properties as OWB's mirelurk.mesh")
        ref_mesh = first_mesh(reference)
        ref_note = f" (OWB's mirelurk: {winding_agreement(ref_mesh):.1%})"
        expect(signed_volume(mesh) * signed_volume(ref_mesh) > 0, "faces outwards, as OWB's mirelurk does")
    else:
        notes.append("note OWB's mirelurk.mesh not found: structure and facing not compared")
        ref_note = ""
        expect(signed_volume(mesh) > 0, "faces outwards (a positive signed volume)")
    winding = winding_agreement(mesh)
    expect(winding > 0.98, f"winding agrees with the normals on {winding:.1%} of triangles{ref_note}")
    expect(np.array_equal(np.unique(mesh["tri"]), np.arange(len(mesh["p"]))), "every vertex is indexed")
    expect(np.isfinite(mesh["p"]).all() and 0.0 <= mesh["u0"].min() and mesh["u0"].max() <= 1.0,
           "positions finite, UVs inside 0-1")
    n, t = mesh["n"], mesh["ta"][:, :3]
    expect(abs(np.linalg.norm(n, axis=1) - 1).max() < 1e-3 and abs(np.linalg.norm(t, axis=1) - 1).max() < 1e-3,
           "normals and tangents are unit length")
    expect(np.abs((n * t).sum(1)).mean() < 0.02, f"tangents are perpendicular to normals "
                                                 f"(mean |t.n| {np.abs((n * t).sum(1)).mean():.4f})")
    expect(set(np.unique(mesh["ta"][:, 3])) <= {-1.0, 1.0}, "bitangent signs are +-1")
    lo, hi = mesh["p"].min(0), mesh["p"].max(0)
    expect(abs(lo[1]) < 1e-4 and abs(hi[1] - MESH_HEIGHT) < 0.02 * MESH_HEIGHT and abs(lo[0] + hi[0]) < 1e-3
           and abs(lo[2] + hi[2]) < 1e-3, f"stands on y = 0, {hi[1]:.2f} tall, centred (x {lo[0]:.2f}..{hi[0]:.2f}, "
                                          f"z {lo[2]:.2f}..{hi[2]:.2f})")
    soles = [mesh["p"][side, 1].min() for side in (mesh["p"][:, 0] < 0, mesh["p"][:, 0] > 0)]
    expect(max(soles) < 0.01 * MESH_HEIGHT, f"both sides reach the ground (lowest points {soles[0]:.3f} and "
                                            f"{soles[1]:.3f}): SRC_ROLL_DEG is the dial")
    # The skeleton and the skin, as the vertex shader will use them.
    skeleton = file_rig(tree)
    bones = len(skeleton["names"])
    expect(skeleton["names"] == list(RIG) and bones <= MAX_BONES and skeleton["parent"][0] == -1
           and all(0 <= parent < i for i, parent in enumerate(skeleton["parent"]) if i)
           and all(skeleton["parent"][i] == i - 1 or skeleton["parent"][i] in ancestors(skeleton["parent"], i - 1)
                   for i in range(1, bones)),
           f"{bones} bones (the shader holds {MAX_BONES}), in RIG's order, depth-first as vanilla's and OWB's are")
    ix, w = skeleton["ix"], skeleton["w"]
    expect(ix.shape == (len(mesh["p"]), 4) and abs(w.sum(1) - 1).max() < 1e-5 and ix.max() < bones
           and ((ix >= 0) == (w > 0)).all() and w[:, :3].sum(1).max() <= 1 + 1e-6,
           "every vertex has four influences whose weights sum to 1; an unused one is -1 / 0")
    joints = -skeleton["unbind"][:, :3, 3]
    rest_pose = {name: (joints[i] - (joints[skeleton["parent"][i]] if i else 0), np.array([0.0, 0.0, 0.0, 1.0]), 1.0)
                 for i, name in enumerate(skeleton["names"])}
    expect(np.abs(emulate(skeleton, rest_pose) - skeleton["p"]).max() < 1e-4,
           "the bones' tx undo their own rest pose: unposed, the skin leaves every vertex where it is")
    material = next(props for path, props in tree.items() if path and path[-1] == "material")
    expect(material.get("shader") == "PdxMeshAdvanced" and all((out["mesh"].parent / material.get(k, "?")).exists()
                                                               for k in ("diff", "n", "spec")),
           "the material names PdxMeshAdvanced and three textures that exist")

    reference_dds = dds_header(OWB_REF_DDS) if OWB_REF_DDS.exists() else None
    if not reference_dds:
        notes.append("note OWB's mirelurk_d.dds not found: header class not compared")
    for key, size in (("d", TEX_D), ("n", TEX_N), ("s", TEX_S)):
        head = dds_header(out[key])
        levels = size.bit_length()
        body = sum(max(1, (size >> i) // 4) ** 2 * 16 for i in range(levels))
        ok = (head["w"], head["h"], head["mips"], head["fourcc"]) == (size, size, levels, b"DXT5") \
            and out[key].stat().st_size == 128 + body and head["pitch"] == size * size
        if reference_dds:
            ok = ok and all(head[k] == reference_dds[k] for k in ("magic", "size", "flags", "pf_size", "pf_flags",
                                                                  "fourcc", "bpp", "caps"))
        decoded = list(dds_levels(out[key]))                     # every level decodes, not only the top one
        expect(ok and len(decoded) == levels, f"{out[key].name}: {size}x{size} DXT5, {levels} mip levels that all "
               "decode, " + ("OWB's header class" if reference_dds else "header class not compared"))
        if key == "n":
            blue = max(int(level[..., 2].max()) for level in decoded)
            expect(blue == 0, f"{out[key].name}: B - PdxMeshAdvanced's emissive mask - is 0 at every mip level "
                              f"(max {blue})")

    # The shipped normal map, decoded as the shader decodes it (UnpackRRxGNormal, then the vertex shader's own
    # tangent frame), must give the normals that an object-space bake through the same rays gives - and the
    # other reading of the A channel must not. Sampled at every vertex, where the frame is known exactly. The
    # two ratios are the test of the convention; the absolute bound only guards the texture's quality.
    if truth is not None:
        shipped = next(dds_levels(out["n"])).astype(np.float32) / 255.0
        size = shipped.shape[0]
        xy = mesh["u0"] * size - 0.5
        x0, y0 = np.floor(xy[:, 0]).astype(int), np.floor(xy[:, 1]).astype(int)
        fx, fy = (xy[:, 0] - x0)[:, None], (xy[:, 1] - y0)[:, None]

        def bilinear(texture):
            def texel(x, y):
                return texture[np.clip(y, 0, size - 1), np.clip(x, 0, size - 1)]
            return (texel(x0, y0) * (1 - fx) + texel(x0 + 1, y0) * fx) * (1 - fy) \
                + (texel(x0, y0 + 1) * (1 - fx) + texel(x0 + 1, y0 + 1) * fx) * fy

        sample = bilinear(shipped)
        want = unit(bilinear(truth))[:, [0, 2, 1]]                  # Blender's object space -> PDX
        bitangent = unit(np.cross(n, t) * mesh["ta"][:, 3:4])       # pdxmesh.shader VertexPdxMeshStandard

        def error(world):
            return float(np.median(np.degrees(np.arccos(np.clip((unit(world) * want).sum(1), -1, 1)))))

        def shaded(flip_y):
            ts = decode_normal_like_the_engine(sample, flip_y)
            return ts[:, 0:1] * t + ts[:, 1:2] * bitangent + ts[:, 2:3] * n

        as_shipped, other, unmapped = error(shaded(True)), error(shaded(False)), error(n)
        expect(other > 2.0 * as_shipped and unmapped > 2.0 * as_shipped and as_shipped < 8.0,
               f"normal map, median error over {len(n):,} vertices against an object-space bake: {as_shipped:.1f} deg "
               f"as the shader reads it; {other:.1f} with the A channel the other way up; {unmapped:.1f} with no map")
    else:
        notes.append("note no bake in hand: the normal map's orientation was not re-checked (run without --check)")

    # The clips, read back and played as the engine plays them.
    reference_anim = read_mesh(OWB_REF_ANIM) if OWB_REF_ANIM.exists() else None
    if not reference_anim:
        notes.append("note OWB's mirelurk_attack.anim not found: the clips' layout not compared")
    tri = skeleton["tri"]
    edges = np.unique(np.sort(np.concatenate([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]]), axis=1), axis=0)
    rest_length = np.maximum(np.linalg.norm(skeleton["p"][edges[:, 0]] - skeleton["p"][edges[:, 1]], axis=1), 1e-6)
    feet = [np.flatnonzero(sum(np.where(ix == skeleton["names"].index(f"{part}_{side}"), w, 0.0)
                               for part in ("foot", "toe")).sum(1) > 0.6) for side in "lr"]
    for name in ANIMATIONS:
        atree = read_mesh(out[f"anim_{name}"])
        anim = file_anim(atree)
        ok = list(atree) == [(), ("info",), *(("info", bone) for bone in RIG), ("samples",)] \
            and list(atree[("info",)]) == ["fps", "sa", "j"] \
            and all(list(atree[("info", bone)]) == ["sa", "t", "q", "s"] for bone in RIG) \
            and anim["bones"] == bones and anim["fps"] == FPS and not any(anim["leftover"].values())
        if reference_anim:
            ok = ok and list(reference_anim[("info",)]) == list(atree[("info",)]) \
                and list(reference_anim[("info", "root")]) == list(atree[("info", "root")]) \
                and set(atree[("samples",)]) <= set(reference_anim[("samples",)])
        q = np.array([[pose[bone][1] for bone in RIG] for pose in anim["frames"]])
        ok = ok and abs(np.linalg.norm(q, axis=2) - 1).max() < 1e-4 and (q[1:] * q[:-1]).sum(2).min() > 0
        frames = [emulate(skeleton, pose) for pose in anim["frames"]]
        closure = float(np.abs(frames[0] - frames[-1]).max())
        lowest = min(float(f[:, 1].min()) for f in frames)
        stretch = max(float((np.linalg.norm(f[edges[:, 0]] - f[edges[:, 1]], axis=1) / rest_length).max())
                      for f in frames[::3])
        text = (f"{out[f'anim_{name}'].name}: {len(frames)} samples at {anim['fps']:g} fps in OWB's layout, unit "
                f"quaternions that never flip sign; ends where it starts ({closure:.0e}); lowest point "
                f"{lowest:+.2f}; worst edge stretch {stretch:.1f}x")
        ok = ok and closure < 1e-3 and lowest > -0.15 and stretch < 3.0
        if any(len({an for st, an, _ in STATES if st == state}) > 1 for state, animation, _ in STATES if animation == name):
            from_rest = float(np.abs(frames[0] - skeleton["p"]).max())
            text += f"; a variant of its state, so it starts in the sculpt's pose ({from_rest:.0e})"
            ok = ok and from_rest < 1e-3
        reach = np.maximum(np.stack(frames).max((0, 1)) - skeleton["p"].max(0), skeleton["p"].min(0) - np.stack(frames).min((0, 1)))
        text += f"; reaches {max(0.0, float(reach.max())):.1f} beyond the mesh's bounding box"
        if name == "move":
            floating = max(min(float(f[side, 1].min()) for side in feet) for f in frames)
            text += f"; a foot within {floating:.2f} of the ground in every frame"
            ok = ok and floating < 0.12
        if rig is not None:
            worst = max(float(np.abs(frames[f] - (rig.skin(poses[name][f])[arrays["vertex"]][:, SWAP] - arrays["offset"])).max())
                        for f in range(0, len(frames), 4))
            text += f"; read back, it is the pose it was written from to {worst:.0e}"
            ok = ok and worst < 1e-3
        expect(ok, text)

    gfx, animations, asset = (out[k].read_text(encoding="utf-8") for k in ("gfx", "animations", "asset"))
    expect(all(f'id = "{name}"\ttype = "{SUBJECT}_{name}_animation"' in gfx
               and f'name = "{SUBJECT}_{name}_animation"\n\tfile = "{out[f"anim_{name}"].name}"' in animations
               for name in ANIMATIONS)
           and all(f'name = "{state}"\tanimation = "{animation}"' in asset for state, animation, _ in STATES),
           "every state plays an animation id the pdxmesh lists, declared beside its .anim file")
    for path, text in ((out["gfx"], gfx), (out["animations"], animations), (out["asset"], asset)):
        raw = path.read_bytes()
        expect(text.count("{") == text.count("}") and b"\r" not in raw and raw[:3] != b"\xef\xbb\xbf",
               f"{path.name}: braces balance, LF, no BOM")
    expect(f'name = "{SUBJECT}_mesh"' in gfx and f'pdxmesh = "{SUBJECT}_mesh"' in asset
           and f'file = "{MODEL_DIR}/{SUBJECT}.mesh"' in gfx, "the entity names the pdxmesh, and the pdxmesh the mesh")
    units = (MOD / SUB_UNIT_FILE).read_text(encoding="utf-8")
    for sub_unit in SUB_UNITS:
        block = units[units.index(f"\t{sub_unit} = {{"):]
        expect(f"sprite = {SUBJECT}\n" in block[:block.index("\n\t}")],
               f"{SUB_UNIT_FILE}: the {sub_unit} sub-unit has `sprite = {SUBJECT}` (-> {SUBJECT}_entity)")
    if (OWB / "gfx").exists():
        clashes = [p for p in (OWB / "gfx").rglob("*") if p.suffix in (".asset", ".gfx")
                   and f'"{SUBJECT}_' in p.read_text(encoding="utf-8", errors="replace")]
        expect(not clashes, "no OWB entity or pdxmesh shares our names")
    else:
        notes.append("note OWB not found: name clashes not checked")

    for line in notes + failures:
        print("  " + line)
    if failures:
        raise SystemExit(f"{len(failures)} check(s) failed" + ("" if root is None else ": mod_folder was left alone"))


def preview_sheet(work):
    from PIL import Image, ImageDraw
    names = ("front", "quarter", "side", "back", "map")
    tiles = [Image.open(work / f"view_{name}.png").convert("RGBA") for name in names]
    size = tiles[0].width
    sheet = Image.new("RGBA", (size * 3, size * 2), (22, 30, 33, 255))
    draw = ImageDraw.Draw(sheet)
    for i, (name, tile) in enumerate(zip(names, tiles)):
        at = (i % 3 * size, i // 3 * size)
        sheet.alpha_composite(tile, at)
        draw.text((at[0] + 10, at[1] + 8), name, fill=(190, 210, 205, 255))
    # The sixth cell: the "map" view at roughly the sizes the game draws a unit, on two terrain-coloured cards.
    # Downsampled renders of the top mip level, under Blender's light: a guide to the silhouette, not the game.
    for row, card in enumerate(PREVIEW_CARDS):
        top = size + row * size // 2
        draw.rectangle((size * 2, top, size * 3, top + size // 2), fill=card + (255,))
        x = size * 2 + 30
        for px in (160, 96, 56):
            small = tiles[-1].resize((px, px), Image.LANCZOS)
            sheet.alpha_composite(small, (x, top + (size // 2 - px) // 2))
            x += px + 40
    draw.text((size * 2 + 10, size + 8), "map view at 160 / 96 / 56 px (terrain stand-ins)", fill=(230, 230, 215, 255))
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(PREVIEW_DIR / "preview.png")
    for name in ("preview_d.png", "preview_n.png", "preview_uv.png"):
        Image.open(work / name).save(PREVIEW_DIR / name.replace("preview_", "texture_"))
    print(f"  wrote {PREVIEW_DIR / 'preview.png'}")


def clip_report(rig, name, clip):
    """What makes a clip read as natural or as broken, measured: for the author of a clip (`--clip NAME`)."""
    import numpy as np
    frames = np.stack([rig.skin(pose) for pose in clip])
    joints = np.stack([rig.joint_positions(pose) for pose in clip])
    print(f"{name}: {(len(clip) - 1) / FPS:g} s, {len(clip)} samples")
    gap = float(np.abs(frames[0] - frames[-1]).max())
    print(f"  ends where it starts: {gap:.1e}" + ("" if gap < 1e-3 else "   <-- it must: idles and attacks chain, loops loop"))
    low = float(frames[..., 2].min())
    print(f"  lowest point of the mesh: z = {low:+.3f} (the sculpt: {rig.co[:, 2].min():+.3f})"
          + ("" if low > -0.12 else "   <-- sinks into the ground"))
    for side in "lr":
        bones = [rig.names.index(f"{part}_{side}") for part in ("foot", "toe")]
        verts = np.flatnonzero(sum(np.where(rig.index == bone, rig.weight, 0.0) for bone in bones).sum(1) > 0.6)
        height = frames[:, verts, 2].min(1)
        planted = height < 0.08
        speed = np.diff(frames[:, verts, 1].mean(1)) * FPS          # +y is backwards: a walker's planted foot goes back
        stance = planted[1:] & planted[:-1]
        text = f"  foot_{side}: on the ground in {planted.mean():.0%} of the samples, highest {height.max():.2f}"
        if stance.sum() > 2:
            text += f"; while planted it travels back at {speed[stance].mean():.2f} +- {speed[stance].std():.2f} units/s"
        print(text)
        hip, knee, ankle = (rig.names.index(f"{part}_{side}") for part in ("thigh", "shin", "foot"))
        reach = np.linalg.norm(rig.joints[knee] - rig.joints[hip]) + np.linalg.norm(rig.joints[ankle] - rig.joints[knee])
        stretch = np.linalg.norm(joints[:, ankle] - joints[:, hip], axis=1) / reach
        rest = np.linalg.norm(rig.joints[ankle] - rig.joints[hip]) / reach
        print(f"  leg_{side}: {stretch.min():.0%}..{stretch.max():.0%} of its full length (the sculpt: {rest:.0%})"
              + ("   <-- locks out: lower the pelvis or shorten the stride" if stretch.max() > max(0.975, rest + 0.005) else ""))
    turn = np.degrees(np.arccos(np.clip([(np.trace(rotvec_matrix(a.get(n, (0, 0, 0))).T @ rotvec_matrix(b.get(n, (0, 0, 0)))) - 1) / 2
                                        for a, b in zip(clip[:-1], clip[1:]) for n in rig.names], -1, 1))).reshape(len(clip) - 1, -1)
    at = np.unravel_index(turn.argmax(), turn.shape)
    print(f"  fastest joint: {rig.names[at[1]]}, {turn.max():.1f} degrees between samples {at[0]} and {at[0] + 1}"
          + ("   <-- over 14 a sample reads as a snap, unless it is a blow" if turn.max() > 14 else ""))


def animation_previews(work, blender, rig, poses, video=True):
    """A contact sheet per clip (eight moments, from the side and the front quarter) and, with ffmpeg on the
    PATH, one video of every clip in turn - what a still cannot show."""
    import json
    import shutil
    import subprocess

    import numpy as np
    from PIL import Image, ImageDraw
    frames_dir = work / "frames"
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir()
    size, columns, jobs, picks = 400, 8, [], {}
    for name, clip in poses.items():
        picks[name] = [int(round(i * (len(clip) - 1) / (columns - 1))) for i in range(columns)]
        np.save(frames_dir / f"sheet_{name}.npy", np.stack([rig.skin(clip[i]) for i in picks[name]]).astype(np.float32))
        jobs.append(dict(name=f"sheet_{name}", views=["side", "quarter"]))
        if video:
            np.save(frames_dir / f"video_{name}.npy", np.stack([rig.skin(pose) for pose in clip[:-1]]).astype(np.float32))
            jobs.append(dict(name=f"video_{name}", views=["map"]))
    (frames_dir / "manifest.json").write_text(json.dumps(dict(size=size, jobs=jobs)))
    run_blender(blender, work, "frames")
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for name, clip in poses.items():
        sheet = Image.new("RGB", (size * columns, size * 2))
        draw = ImageDraw.Draw(sheet)
        for r, view in enumerate(("side", "quarter")):
            for c, i in enumerate(picks[name]):
                sheet.paste(Image.open(frames_dir / f"sheet_{name}_{view}_{c:03d}.png").convert("RGB"), (c * size, r * size))
                draw.text((c * size + 6, r * size + 5), f"{name}  {i / FPS:.2f} s", fill=(255, 255, 140))
        sheet.save(PREVIEW_DIR / f"anim_{name}.png")
    print(f"  wrote {', '.join(f'anim_{name}.png' for name in poses)} to {PREVIEW_DIR}")
    ffmpeg = shutil.which("ffmpeg")
    if not video:
        return
    if not ffmpeg:
        print("  ffmpeg is not on the PATH: no animations.mp4")
        return
    count = 0
    for name, clip in poses.items():
        for repeat in range(2 if len(clip) < 3 * FPS else 1):         # a short loop plays twice
            for f in range(len(clip) - 1):
                frame = Image.open(frames_dir / f"video_{name}_map_{f:03d}.png").convert("RGB")
                ImageDraw.Draw(frame).text((8, 6), f"{name}   {f / FPS:4.2f} s", fill=(255, 255, 140))
                frame.save(frames_dir / f"reel_{count:05d}.png")
                count += 1
    video = PREVIEW_DIR / "animations.mp4"
    subprocess.run([ffmpeg, "-y", "-v", "error", "-framerate", str(FPS), "-i", str(frames_dir / "reel_%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(video)], check=True)
    print(f"  wrote {video} ({count / FPS:.0f} s)")


def main():
    import argparse
    import json
    import shutil
    import tempfile
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default=str(SRC_DEFAULT), help="the high-poly STL (not in the repo)")
    ap.add_argument("--blender", help=f"blender.exe (default: the newest under {BLENDER_GLOB})")
    ap.add_argument("--work", default=str(Path(tempfile.gettempdir()) / "rising_tide_unit_model"),
                    help="the bake cache (the system temp directory may be cleaned: name a durable one)")
    ap.add_argument("--rebake", action="store_true", help="bake even if the cache is current")
    ap.add_argument("--preview", action="store_true", help="also render event_images/unit_model/preview.png")
    ap.add_argument("--check", action="store_true", help="only check the shipped files")
    ap.add_argument("--clip", metavar="NAME", help=f"measure and draw one clip of {CLIP_DIR}/ from the caches; "
                                                   "write nothing to mod_folder")
    args = ap.parse_args()
    if args.check:
        check()
        return

    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    if args.clip:
        if args.clip not in ANIMATIONS:
            raise SystemExit(f"{args.clip!r} is not an animation STATES names: {', '.join(ANIMATIONS)}")
        if not all((work / name).exists() for name in ("mesh.npz", "weights.npz", "lowpoly.blend", "preview_d.png")):
            raise SystemExit(f"no bake and weights cached in {work}: run a full build first")
        stale = not (work / "weights.json").exists() or json.loads((work / "weights.json").read_text()) != weights_key(work)
        if stale:
            raise SystemExit(f"the skin weights cached in {work} are not for this RIG and low-poly: run a full build first")
        rig = load_rig(work)
        clip = sample_clip(load_clips()[args.clip], rig)
        clip_report(rig, args.clip, clip)
        animation_previews(work, find_blender(args.blender), rig, {args.clip: clip}, video=False)
        return
    src = Path(args.src)
    cached = json.loads((work / "bake.json").read_text()) if (work / "bake.json").exists() else {}
    have_files = all((work / name).exists() for name in BAKE_FILES)
    current = json.loads(json.dumps({"bake_code": bake_code_hash(), **{k: globals()[k] for k in BAKE_KEYS}}))
    if src.exists():
        key = {"sha256": sha256(src), **current}
    elif args.rebake or not have_files:
        raise SystemExit(f"{src} not found" + (": --rebake needs the sculpt" if have_files else
                                               f" and no bake cached in {work}: pass --src"))
    else:
        stale = [k for k, v in current.items() if cached.get(k) != v]
        if stale:
            raise SystemExit(f"{src} not found, and the cached bake was made with a different {', '.join(stale)}: "
                             "those need the sculpt")
        key = cached
        print(f"  {src} is missing: painting from the cached bake")
    if args.rebake or not have_files or cached != key:
        print(f"Baking {src.name} ({src.stat().st_size / 1e6:.0f} MB, sha256 {key['sha256'][:16]}...)")
        (work / "bake.json").unlink(missing_ok=True)        # a bake that dies half-way must not look current
        run_blender(find_blender(args.blender), work, "bake", "--src", str(src))
        (work / "bake.json").write_text(json.dumps(key, indent=2))
    else:
        print("The cached bake is current")

    wanted = weights_key(work)
    have = json.loads((work / "weights.json").read_text()) if (work / "weights.json").exists() else None
    if have != wanted or not (work / "weights.npz").exists():
        print("Weighing the skin to the skeleton")
        (work / "weights.json").unlink(missing_ok=True)
        run_blender(find_blender(args.blender), work, "weights")
        (work / "weights.json").write_text(json.dumps(wanted, indent=2))
    else:
        print("The cached skin weights are current")

    print("Writing the model")
    stage = work / "stage"
    shutil.rmtree(stage, ignore_errors=True)
    arrays, truth, rig, poses = build(work, stage)
    print("Checking")
    check(arrays, truth, stage, rig, poses)
    for staged, shipped in zip(outputs(stage).values(), outputs().values()):
        shipped.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(staged, shipped)
    for stale in set((MOD / MODEL_DIR).glob("*.anim")) - set(outputs().values()):
        stale.unlink()                                  # a clip that STATES no longer names
    if args.preview:
        print("Rendering the preview")
        run_blender(find_blender(args.blender), work, "preview")
        preview_sheet(work)
        animation_previews(work, find_blender(args.blender), rig, poses)
    for path in outputs().values():
        print(f"  {path.relative_to(ROOT).as_posix():<62} {path.stat().st_size:>9,} B  {sha256(path)[:12]}")


if __name__ == "__main__":
    blender_main() if IN_BLENDER else main()
