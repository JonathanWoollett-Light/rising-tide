"""Rebuild the equipment icons of MLT's two summoned monsters - the Deep Ones (mltd_deep_ones_equipment) and the Star
Spawn (mltd_star_spawn_equipment) - as renders of the mod's own 3D unit model, the figure both sub-units wear on the
map (CLAUDE.md > The Star Spawn model).

How the game uses them: an equipment's icon is the sprite GFX_<equipment_id>_medium (interface/mltd.gfx declares it
for the two _1 variants, the only ones there are). It is drawn in the production view (countryproductionlineview.gui,
production_military_line_entry: centred on (80, 74) at scale 0.9), the division designer, logistics and the
stockpile, from its top-left corner in some of them, which is why every OWB equipment icon is 130x60. Until this
script both sprites borrowed OWB's mirelurk king and bloodrage pictures, which are OWB's own creatures, not ours.

Output (shipped; mod_folder/gfx/interface/equipment/mltd/):
  mltd_star_spawn_equipment.dds    the Star Spawn: the rearing frame of `attack` - coiled, the left claw raised, the
                                   wings spreading, the tentacled face to the viewer - at full height in the frame
  mltd_deep_ones_equipment.dds     the Deep Ones: the lesser spawn, mid-stride in the crouched walk of `move`, head
                                   low and claws reaching - smaller in the frame, darker and greener
      each 130x60, uncompressed A8R8G8B8 (32-bit, straight alpha), 128-byte header byte-identical to OWB's
      gfx/interface/equipment/generic/mirelurk_king_equipment.dds (flags 0x2100f, depth 1, 1 mip; 31,328 bytes).
Sources (read, never written):
  the shipped model   mod_folder/gfx/models/mltd/star_spawn/: its painted diffuse, normal and specular maps (the top
                      level of each DXT5 file) and its .mesh, which the cache below must match vertex for vertex
  the model's cache   build_unit_model.py's work folder (system temp, rising_tide_unit_model): the low-poly
                      (lowpoly.blend, mesh.npz) and its skin weights. With build_unit_model's RIG table, its Rig class
                      (Rig.skin is the game's vertex shader in numpy) and the clip modules in unit_model_clips/ they
                      pose the figure exactly as the map's animations do - the same code that wrote the .anim files
  OWB's creature icons  the 27 creature equipment icons in <OWB>/gfx/interface/equipment/generic/ (mirelurks,
                      deathclaws, ghouls, geckos, yao guai, molerats, radroaches, radstag, bighorner): the glow is
                      measured off them, and the preview puts ours beside the mirelurk king and bloodrage
  vanilla's tech box and OWB's production row   preview backgrounds only
Previews (event_images/equipment_icons/, never shipped):
  equipment_icons_preview.png   each icon at 1x and 4x in the tech box (vanilla technology_available_item_bg,
                                centred on (91, 50)) and in the production row (OWB's production_item and
                                prod_land_equipment_item_large, centred on (80, 74) at 0.9), beside OWB's
                                mirelurk_king_equipment and mirelurk_bloodrage_equipment at the same scales
  <icon>_out.png                each result at 1x, lossless (what the .dds holds)
  renders.png                   the raw renders, before the grade, the fit and the glow

What it does:
  1. poses (system Python): each icon names a clip and a moment in it (u, 0-1); the clip module's own clip(u, rig)
     gives the pose and Rig.skin the low-poly's vertices. The camera is orthographic from `view` (the direction from
     the figure to the camera: a three-quarter front, near level), framed on the posed vertices' projection, so
     nothing is cut and the render spends its pixels on the figure. Two icons of one model have to read as two
     creatures at 130x60, so they differ in everything but the model: the Star Spawn upright and square to the
     viewer, seen from its left front and near level, as large as the frame allows; the Deep Ones hunched and on
     the move, seen from its right front and from above, at 78 % of the Star Spawn's scale.
  2. textures: the shipped maps are decoded back into Blender's conventions (build_unit_model.encode_normal, read
     in reverse): the diffuse as it is; the normal map's x from G and y from A (A is "up the image", the OpenGL
     way), z rebuilt; the specular map's gloss (A) turned into a roughness the way build_unit_model's preview does
     (a Blinn-Phong exponent 2^(11 g) as a GGX alpha, then its square root), its level (G) into the BSDF's F0.
  3. renders (Blender, headless, Cycles, transparent film): the posed low-poly with those three maps, under a key
     light from the upper left of the picture (the side OWB's creature icons are lit from - their shadows fall
     right and down), a cool fill and a rim from behind (PdxMeshAdvanced defines RIM_LIGHT: the engine rims its
     units too). The lights are given in camera space, so every view is lit the same way.
  4. composes (system Python, on premultiplied alpha): a grade (gamma, gain, saturation, a per-channel tint - the
     Deep Ones' darker, greener spawn), a LANCZOS fit into 130x60 and an unsharp mask. The Star Spawn takes the
     largest size at which its glow leaves nothing on the texture's border (BORDER_MAX); the Deep Ones are drawn at
     `size`, a share of the Star Spawn's pixels per model unit - the same figure, a smaller creature.
  5. glow: every OWB icon carries a black outer glow, generated here the way build_tech_icons.py generates the melee
     icons' (a distance transform of the object's alpha at SS x, a lookup, a box filter down), but with the creature
     icons' own shape, measured off OWB's 27 by the same ruler: a ring about one pixel wide and a drop shadow that
     falls right and down (RING, SHADOW). The melee icons' symmetric glow (165 / 110 / 70 / 28 / 4 at 1-5 px) is
     far heavier than the creature icons' (161 / 47 / 23 / 12 / 7 on average). `report` prints ours against theirs.
  6. writes the .dds, checks the header against OWB's and the round trip, and draws the previews.

Run from the repo root (needs Blender 5.2, the model's cache - `python build_unit_model.py` makes it - and OWB and
vanilla installed; numpy, scipy and Pillow in system Python):
  python build_equipment_icons.py                 render if the renders' key changed, then write both .dds and the previews
  python build_equipment_icons.py --no-write      previews only: mod_folder is left alone
  python build_equipment_icons.py --rerender      render even if the cached renders are current
  python build_equipment_icons.py --set deep_ones.u=0.5 --set deep_ones.clip=move --no-write   try a pose
The renders are cached in the system temp directory (rising_tide_equipment_icons), keyed on the poses, the camera,
the lights, the render settings, the shipped textures, the low-poly and the Blender half of this file, so a grade or
glow change takes seconds. Given one set of renders the .dds files are byte-identical from run to run.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import bpy  # noqa: F401 - present only when Blender runs this file
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False

ROOT = Path(__file__).resolve().parent

# --------------------------------------------------------------------------------------
# Tunables
# --------------------------------------------------------------------------------------
ICON_SIZE = (130, 60)                  # 1,220 of OWB's 1,250 equipment icons
SS = 4                                 # supersampling of the glow's distance transform and shadow
BORDER_MAX = 4.0                       # the strongest alpha a fitted icon may leave on the texture's border (0-255):
#                                        the trident's rule (build_tech_icons.py): at ~6 nothing can be seen cut
CENTRE = (65.0, 30.0)                  # where the centre of the object's box goes, before the shadow's half-offset

# The render: RENDER_PX on the long side of a frame fitted to the posed figure with RENDER_MARGIN around it, so the
# figure is drawn some ten times larger than it will be shown and the LANCZOS fit has something to reduce.
RENDER_PX = 1100
RENDER_MARGIN = 0.05                   # of the figure's larger projected extent, each side
RENDER_SAMPLES = 256
RENDER_SEED = 20260923
EXPOSURE = 0.0                         # Blender's view exposure (stops); the grade does the rest
WORLD = (0.030, 0.040, 0.045)          # ambient: the world colour behind the transparent film
# Lights, as sun lamps in CAMERA space (x right, y up, z towards the camera): the direction the light comes FROM,
# its strength, its colour (linear) and its angular size in degrees (soft shadows).
LIGHTS = (
    ("key", (-0.55, 0.75, 0.55), 4.2, (1.00, 0.95, 0.86), 8.0),
    ("fill", (0.85, -0.10, 0.50), 0.9, (0.62, 0.78, 0.90), 20.0),
    ("rim", (0.60, 0.50, -0.95), 3.2, (0.80, 0.98, 1.00), 6.0),
)

# The two icons. clip / u: the pose (build_unit_model's clips; u = 0-1 through the clip). view: the direction from the
# figure to the camera, in model space (x = the figure's LEFT, y = its BACK - it faces -y - z = up). size: "max" (the
# largest the glow allows; one icon has it) or a share of that icon's pixels per model unit - the same figure drawn
# as a smaller creature. grade: gamma (< 1 lifts), gain, tint (per channel, after the gain), saturation, sharpen
# radius and amount.
ICONS = {
    "star_spawn": dict(
        equipment="mltd_star_spawn_equipment", out="mltd_star_spawn_equipment.dds",
        clip="attack", u=0.34,                 # the rearing frame: fully coiled, left claw raised, wings spreading
        view=(0.45, -1.0, 0.10),               # its left front, near level: the face, both wings and the claw
        size="max",
        grade=dict(gamma=0.90, gain=1.12, tint=(1.0, 1.0, 1.0), saturation=1.45, sharpen_radius=0.7, sharpen_amount=0.45),
    ),
    "deep_ones": dict(
        equipment="mltd_deep_ones_equipment", out="mltd_deep_ones_equipment.dds",
        clip="move", u=0.25,                   # the crouched walk, mid-stride: head low, claws reaching forward
        view=(-0.60, -1.0, 0.30),              # its right front, from above: stalking towards the picture's right
        size=0.78,
        grade=dict(gamma=1.08, gain=0.80, tint=(0.84, 1.0, 0.76), saturation=1.10, sharpen_radius=0.7, sharpen_amount=0.45),
    ),
}

# The glow, measured off OWB's 27 creature equipment icons (see the docstring): a thin ring - alpha by distance in
# px from the object, from GLOW_OFFSET out, like build_tech_icons.GLOW - under a drop shadow of the object's own
# alpha, moved by `offset` px (right, down), blurred by `sigma` px and laid at `opacity`. Fitted to the 27 directly
# (least squares on every pixel 1-7 px from an object, object = alpha >= 250) the model reads ring 165 at 1 px falling
# by e^-(d-1)/0.34, shadow offset (1.7, 1.3), sigma 1.75, opacity 0.8. But our figures' own anti-aliased edge adds to
# the first rings, as the trident's does (build_tech_icons.GLOW_OFFSET), so the values below are fitted again on our
# two composed icons, by least squares against report's ruler (the mean alpha 1-6 px out, all round and to each side),
# to OWB's average - which they then meet within ~15 over the first 3 px; OWB's faint tail at 4-6 px (12 / 7 / 4) is
# the one thing left longer than ours.
RING = [255.0, 190.0, 7.0, 0.0]
GLOW_OFFSET = 0.7
SHADOW = dict(offset=(1.5, 0.65), sigma=1.0, opacity=0.9)

# --------------------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------------------
MOD = ROOT / "mod_folder"
OUT_DIR = MOD / "gfx/interface/equipment/mltd"
PREVIEW_DIR = ROOT / "event_images/equipment_icons"
PREVIEW = "equipment_icons_preview.png"
OWB = Path("C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/2265420196")
VANILLA = Path("C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV")
OWB_GENERIC = OWB / "gfx/interface/equipment/generic"
HEADER_REF = OWB_GENERIC / "mirelurk_king_equipment.dds"
NEIGHBOURS = ("mirelurk_king_equipment.dds", "mirelurk_bloodrage_equipment.dds")      # beside ours in the preview
CREATURE_PREFIXES = ("mirelurk", "deathclaw", "feral_ghoul", "gecko", "yao_guai", "dusky_yao_guai", "molerat",
                     "radroach", "radstag", "big_horner")
# The tech box (countrytechtreeview.gui: 183x84, the icon centred on (91, 50), unscaled) and the production row
# (countryproductionlineview.gui, production_military_line_entry: production_item at (0, 0), the equipment button
# at (1, 27), the icon centred on (80, 74) at scale 0.9). OWB overrides neither texture's look; it ships both paths.
TECH_BGS = (VANILLA / "gfx/interface/techtree/technology_available_item_bg.dds",
            VANILLA / "gfx/interface/techtree/technology_researched_item_bg.dds")
TECH_ICON_CENTRE = (91, 50)
PROD_ITEM = OWB / "gfx/interface/production_item.dds"
PROD_BUTTON = OWB / "gfx/interface/prod_land_equipment_item_large.dds"
PROD_BUTTON_AT = (1, 27)
PROD_ICON_CENTRE, PROD_ICON_SCALE = (80, 74), 0.9
PROD_CROP = (0, 0, 200, 111)           # the part of the 500x111 entry the preview shows
BLENDER_GLOB = "C:/Program Files/Blender Foundation/*/blender.exe"
LUMA = (0.2126, 0.7152, 0.0722)


# ======================================================================================
# Inside Blender: the renders
# ======================================================================================
def bl_log(msg):
    print(f"[blender] {msg}", flush=True)


def bl_stage_render(work):
    """Every job of work/manifest.json: the low-poly posed (its vertices replaced), the shipped maps on it, the
    camera and the lights placed, one transparent PNG each (straight alpha, sRGB)."""
    import json

    import numpy as np
    from mathutils import Matrix, Vector

    sys.path.insert(0, str(ROOT))
    import build_unit_model as bum                  # its Blender helpers: the GPU pick and the node-tree accessor

    manifest = json.loads((work / "manifest.json").read_text())
    bpy.ops.wm.open_mainfile(filepath=manifest["lowpoly"])       # read only: never saved
    scene = bpy.context.scene
    lp = bpy.data.objects["lowpoly"]
    scene.render.engine = "CYCLES"
    bl_log(f"rendering on {bum.bl_use_gpu(scene)}")
    scene.cycles.samples = manifest["samples"]
    scene.cycles.seed = manifest["seed"]
    scene.cycles.use_denoising = True
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = manifest["exposure"]
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"          # Pillow reads a 16-bit RGBA PNG as 8 bits anyway; the
    #                                                          ~10x reduction averages a hundred samples a pixel

    mat = bpy.data.materials.new("icon")
    nt = bum.bl_node_tree(mat)
    bsdf = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    bsdf.inputs["IOR"].default_value = manifest["ior"]
    bsdf.inputs["Metallic"].default_value = manifest["metallic"]

    def texture(name, data):
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images.load(str(work / name))
        if data:
            node.image.colorspace_settings.name = "Non-Color"
        return node

    nt.links.new(texture("tex_d.png", False).outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(texture("tex_r.png", True).outputs["Color"], bsdf.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeNormalMap")
    bump.uv_map = lp.data.uv_layers[0].name
    nt.links.new(texture("tex_n.png", True).outputs["Color"], bump.inputs["Color"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    lp.data.materials.clear()
    lp.data.materials.append(mat)

    world = bpy.data.worlds.new("icon")
    bum.bl_node_tree(world).nodes["Background"].inputs["Color"].default_value = (*manifest["world"], 1.0)
    scene.world = world

    camera = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    camera.data.type = "ORTHO"
    camera.data.sensor_fit = "AUTO"
    camera.data.clip_start, camera.data.clip_end = 0.1, 200.0
    scene.collection.objects.link(camera)
    scene.camera = camera
    lights = []
    for name, _, energy, colour, angle in manifest["lights"]:
        light = bpy.data.objects.new(name, bpy.data.lights.new(name, "SUN"))
        light.data.energy, light.data.color, light.data.angle = energy, colour, np.radians(angle)
        scene.collection.objects.link(light)
        lights.append(light)

    for job in manifest["jobs"]:
        verts = np.load(work / job["verts"]).astype(np.float32)
        lp.data.vertices.foreach_set("co", verts.reshape(-1))
        lp.data.update()
        x, y, z = (Vector(v) for v in job["basis"])
        rotation = Matrix((x, y, z)).transposed()       # columns: the camera's x (right), y (up), z (backwards)
        camera.matrix_world = Matrix.Translation(Vector(job["location"])) @ rotation.to_4x4()
        camera.data.ortho_scale = job["ortho_scale"]
        scene.render.resolution_x, scene.render.resolution_y = job["resolution"]
        scene.render.resolution_percentage = 100
        for light, world_dir in zip(lights, job["light_dirs"]):
            light.rotation_euler = Vector(world_dir).to_track_quat("Z", "Y").to_euler()
        scene.render.filepath = str(work / job["png"])
        bpy.ops.render.render(write_still=True)
        bl_log(f"rendered {job['png']} at {job['resolution'][0]}x{job['resolution'][1]}")


def blender_main():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=("render",))
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    bl_stage_render(Path(args.work))


# ======================================================================================
# System Python
# ======================================================================================
def code_hash():
    """The Blender half of this file: an edit there is a different render."""
    import hashlib
    text = Path(__file__).read_text(encoding="utf-8")
    return hashlib.sha256(text[text.index("# Inside Blender: the renders"):text.index("# System Python")].encode()).hexdigest()


def sha256(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def find_blender(explicit):
    import glob
    if explicit:
        return Path(explicit)
    found = sorted(glob.glob(BLENDER_GLOB))
    if not found:
        raise SystemExit(f"no Blender under {BLENDER_GLOB}; pass --blender")
    return Path(found[-1])


def run_blender(blender, work):
    """build_unit_model.run_blender's few lines, for this file: Blender exits 0 on a Python error unless told not to."""
    import subprocess
    log = work / "blender_render.log"
    cmd = [str(blender), "--background", "--factory-startup", "--python-exit-code", "1", "--python",
           str(Path(__file__).resolve()), "--", "--stage", "render", "--work", str(work)]
    with open(log, "w", encoding="utf-8", errors="replace") as fp:
        proc = subprocess.run(cmd, stdout=fp, stderr=subprocess.STDOUT)
    text = log.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("[blender]"):
            print("  " + line)
    if proc.returncode != 0 or "Traceback (most recent call last)" in text:
        raise SystemExit(f"Blender's render stage failed - see {log}\n" + "\n".join(text.splitlines()[-25:]))


def model_cache(bum, model_work):
    """The model's cache, checked: current skin weights, and a low-poly that welds into exactly the shipped mesh -
    otherwise the icons would show another model than the map does."""
    import json

    import numpy as np
    needed = ("mesh.npz", "weights.npz", "weights.json", "lowpoly.blend")
    missing = [name for name in needed if not (model_work / name).exists()]
    if missing:
        raise SystemExit(f"no model cache in {model_work} ({', '.join(missing)} missing): run build_unit_model.py first")
    if json.loads((model_work / "weights.json").read_text()) != bum.weights_key(model_work):
        raise SystemExit(f"the skin weights cached in {model_work} are not for this RIG and low-poly: run build_unit_model.py")
    rig = bum.load_rig(model_work)
    npz = np.load(model_work / "mesh.npz")
    welded = bum.weld(npz, rig)
    shipped = bum.first_mesh(bum.read_mesh(bum.outputs()["mesh"]))
    if (shipped["p"].shape != welded["p"].shape or np.abs(shipped["p"] - welded["p"]).max() > 1e-5
            or not np.array_equal(shipped["tri"], welded["tri"])):
        raise SystemExit(f"the low-poly cached in {model_work} is not the shipped {bum.outputs()['mesh'].name}: "
                         "run build_unit_model.py")
    return rig


def camera_basis(view):
    """The orthographic camera looking back along `view`: its x (right), y (up) and z (towards the camera) in model
    space, with the picture's up as close to the model's +z as the view allows."""
    import numpy as np
    z = np.asarray(view, dtype=np.float64)
    z /= np.linalg.norm(z)
    y = np.array([0.0, 0.0, 1.0]) - z * z[2]
    y /= np.linalg.norm(y)
    return np.cross(y, z), y, z


def decode_textures(bum, work):
    """The shipped maps, back into Blender's conventions (see the docstring). -> the BSDF's IOR and metallic."""
    import numpy as np
    from PIL import Image
    out = bum.outputs()
    d = next(bum.dds_levels(out["d"]))
    Image.fromarray(np.ascontiguousarray(d[..., :3]), "RGB").save(work / "tex_d.png")
    n = next(bum.dds_levels(out["n"])).astype(np.float64) / 255.0
    x, y = n[..., 1] * 2.0 - 1.0, n[..., 3] * 2.0 - 1.0              # G = x, A = y (encode_normal)
    z = np.sqrt(np.clip(1.0 - x * x - y * y, 0.0, 1.0))
    Image.fromarray(bum.to_bytes(np.stack([x, y, z], -1) * 0.5 + 0.5), "RGB").save(work / "tex_n.png")
    s = next(bum.dds_levels(out["s"])).astype(np.float64) / 255.0
    roughness = (2.0 / (2.0 ** (11.0 * s[..., 3]) + 2.0)) ** 0.25    # gloss (A) -> Principled roughness, as paint()
    Image.fromarray(bum.to_bytes(np.repeat(roughness[..., None], 3, -1)), "RGB").save(work / "tex_r.png")
    f0 = float(np.median(s[..., 1])) ** 2 * 0.4                    # G = the specular level: F0 = g^2 * 0.4
    return (1.0 + f0 ** 0.5) / (1.0 - f0 ** 0.5), float(np.median(s[..., 2]))


def prepare(bum, rig, work, model_work, icons):
    """Pose every icon, frame its camera and write the Blender manifest. -> (manifest, the renders' key)."""
    import hashlib
    import json

    import numpy as np
    ior, metallic = decode_textures(bum, work)
    clips = bum.load_clips()                        # the clip modules the map's .anim files were written from
    jobs = []
    for name, p in icons.items():
        if p["clip"] not in clips or not 0.0 <= float(p["u"]) <= 1.0:
            raise SystemExit(f"{name}: clip must be one of {', '.join(clips)} and u in 0-1, not {p['clip']!r} at {p['u']}")
        verts = rig.skin(clips[p["clip"]].clip(float(p["u"]), rig))
        np.save(work / f"{name}_verts.npy", verts.astype(np.float32))
        x, y, z = camera_basis(p["view"])
        sx, sy, sz = verts @ x, verts @ y, verts @ z
        pad = RENDER_MARGIN * max(np.ptp(sx), np.ptp(sy))
        width, height = np.ptp(sx) + 2 * pad, np.ptp(sy) + 2 * pad
        scale = max(width, height)
        resolution = [int(round(RENDER_PX * width / scale)), int(round(RENDER_PX * height / scale))]
        centre = x * (sx.min() + sx.max()) / 2 + y * (sy.min() + sy.max()) / 2 + z * (sz.max() + 20.0)
        light_dirs = [list(d[0] * x + d[1] * y + d[2] * z) for _, d, *_ in LIGHTS]
        jobs.append(dict(name=name, verts=f"{name}_verts.npy", png=f"{name}_render.png", basis=[list(x), list(y), list(z)],
                         location=list(centre), ortho_scale=float(scale), resolution=resolution, light_dirs=light_dirs,
                         units_per_px=float(scale / max(resolution)),
                         pose_hash=hashlib.sha256(verts.astype(np.float32).tobytes()).hexdigest()))
    manifest = dict(lowpoly=str(model_work / "lowpoly.blend"), samples=RENDER_SAMPLES, seed=RENDER_SEED,
                    exposure=EXPOSURE, world=list(WORLD), lights=[[n, list(d), e, list(c), a] for n, d, e, c, a in LIGHTS],
                    ior=ior, metallic=metallic, jobs=jobs)
    key = dict(manifest=manifest, code=code_hash(), lowpoly=sha256(manifest["lowpoly"]),
               textures={k: sha256(bum.outputs()[k]) for k in "dns"})
    (work / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return manifest, json.loads(json.dumps(key))


# --------------------------------------------------------------------------------------
# Composing: premultiplied float RGBA 0-255 throughout (build_tech_icons.py's conventions)
# --------------------------------------------------------------------------------------
def load_render(path):
    """A straight-alpha PNG -> premultiplied float RGBA 0-255."""
    import numpy as np
    from PIL import Image
    im = Image.open(path)
    if im.mode != "RGBA":
        raise SystemExit(f"{path}: expected RGBA, got {im.mode}")
    a = np.asarray(im, dtype=np.float64)
    a[..., :3] *= a[..., 3:4] / 255.0
    return a


def resample(pm, fn):
    """A PIL operation on each channel of a float array (mode F keeps the precision)."""
    import numpy as np
    from PIL import Image
    return np.stack([np.asarray(fn(Image.fromarray(np.ascontiguousarray(pm[..., k], dtype=np.float32), "F")),
                                dtype=np.float64) for k in range(pm.shape[-1])], -1)


def clamped(pm):
    import numpy as np
    pm[..., 3] = np.clip(pm[..., 3], 0.0, 255.0)
    pm[..., :3] = np.clip(pm[..., :3], 0.0, pm[..., 3:4])        # premultiplied: colour never exceeds alpha
    return pm


def placed(pm, zoom, ss=1):
    """The render scaled by `zoom` (icon px per render px) with the centre of its object's box on CENTRE, moved back
    by half the shadow's offset so that object and shadow sit centred together; on a 130x60 canvas at `ss` x.
    LANCZOS through a sub-pixel source box, so the placement is exact."""
    import numpy as np
    from PIL import Image
    ys, xs = np.where(pm[..., 3] > 127.0)
    cx, cy = (xs.min() + xs.max() + 1) / 2.0, (ys.min() + ys.max() + 1) / 2.0
    W, H = ICON_SIZE
    tx, ty = CENTRE[0] - SHADOW["offset"][0] / 2.0, CENTRE[1] - SHADOW["offset"][1] / 2.0
    x0, y0 = cx - tx / zoom, cy - ty / zoom
    m = int(np.ceil(max(0.0, -x0, -y0, x0 + W / zoom - pm.shape[1], y0 + H / zoom - pm.shape[0]))) + 4
    pad = np.pad(pm, ((m, m), (m, m), (0, 0)))
    box = (x0 + m, y0 + m, x0 + m + W / zoom, y0 + m + H / zoom)
    return clamped(resample(pad, lambda im: im.resize((W * ss, H * ss), Image.LANCZOS, box=box)))


def grade(pm, g):
    """Gamma, gain, a per-channel tint, saturation and an unsharp mask on the straight colour; premultiplied again."""
    import numpy as np
    from scipy import ndimage as ndi
    a = pm[..., 3:4] / 255.0
    rgb = np.where(a > 0, pm[..., :3] / np.maximum(a, 1e-9), 0.0) / 255.0
    rgb = np.clip(rgb, 0, 1) ** g["gamma"] * g["gain"] * np.asarray(g["tint"], dtype=np.float64)
    lum = rgb @ np.asarray(LUMA)
    rgb = np.clip(lum[..., None] + (rgb - lum[..., None]) * g["saturation"], 0, 1)
    prem = rgb * a
    blur = np.stack([ndi.gaussian_filter(prem[..., k], g["sharpen_radius"]) for k in range(3)], -1)
    prem = np.clip(prem + (prem - blur) * g["sharpen_amount"], 0.0, a)
    return np.concatenate([prem * 255.0, pm[..., 3:4]], -1)


def glow(alpha_ss):
    """The black glow (0-255) from the object's alpha at SS x: the ring from a distance transform and RING, the drop
    shadow from the alpha itself, shifted and blurred; combined as two layers of black; box-filtered down."""
    import numpy as np
    from scipy import ndimage as ndi
    d = ndi.distance_transform_edt(alpha_ss <= 127.0) / SS + GLOW_OFFSET
    ring = np.interp(d, np.arange(len(RING), dtype=np.float64), RING) / 255.0
    ring[alpha_ss > 127.0] = 1.0
    shadow = ndi.shift(alpha_ss / 255.0, (SHADOW["offset"][1] * SS, SHADOW["offset"][0] * SS), order=1, mode="constant")
    shadow = ndi.gaussian_filter(shadow, SHADOW["sigma"] * SS) * SHADOW["opacity"]
    g = 1.0 - (1.0 - ring) * (1.0 - np.clip(shadow, 0.0, 1.0))
    h, w = g.shape
    return g.reshape(h // SS, SS, w // SS, SS).mean(axis=(1, 3)) * 255.0


def compose(pm_render, zoom, g):
    """The graded object over its glow -> the icon as uint8 straight RGBA (what the .dds holds; black under alpha 0)."""
    import numpy as np
    obj = grade(placed(pm_render, zoom), g)
    oa = obj[..., 3] / 255.0
    alpha = oa + glow(placed(pm_render, zoom, SS)[..., 3]) / 255.0 * (1.0 - oa)
    rgb = np.where(alpha[..., None] > 0, obj[..., :3] / 255.0 / np.maximum(alpha[..., None], 1e-9), 0.0)
    res = np.zeros((ICON_SIZE[1], ICON_SIZE[0], 4), dtype=np.uint8)
    res[..., :3] = np.round(np.clip(rgb, 0, 1) * 255.0)
    res[..., 3] = np.round(np.clip(alpha, 0, 1) * 255.0)
    res[res[..., 3] == 0] = 0
    return res


def border_alpha(icon):
    a = icon[..., 3]
    return float(max(a[0].max(), a[-1].max(), a[:, 0].max(), a[:, -1].max()))


def fit_max(pm_render, g):
    """The largest zoom at which the icon's border alpha stays at or under BORDER_MAX (bisection)."""
    import numpy as np
    ys, xs = np.where(pm_render[..., 3] > 127.0)
    lo, hi = 0.2 * min(ICON_SIZE[0] / np.ptp(xs), ICON_SIZE[1] / np.ptp(ys)), min(ICON_SIZE[0] / np.ptp(xs), ICON_SIZE[1] / np.ptp(ys))
    for _ in range(22):
        mid = (lo + hi) / 2.0
        if border_alpha(compose(pm_render, mid, g)) <= BORDER_MAX:
            lo = mid
        else:
            hi = mid
    return lo


# --------------------------------------------------------------------------------------
# Measuring: the same ruler on ours and on OWB's creature icons
# --------------------------------------------------------------------------------------
def glow_profile(rgba):
    """Mean alpha 1-6 px from the object (alpha >= 250) - all round, and outward to the left, right, top, bottom of
    each row's / column's object - skipping pixels within 2 px of the texture's edge. -> dict of lists."""
    import numpy as np
    from scipy import ndimage as ndi
    a = np.asarray(rgba, dtype=np.float64)
    al = a[..., 3]
    obj = al >= 250.0
    h, w = al.shape
    inner = np.zeros_like(obj)
    inner[2:-2, 2:-2] = True
    d = ndi.distance_transform_edt(~obj)
    out = {"ring": [float(al[(d > k - 0.5) & (d <= k + 0.5) & inner].mean()) for k in range(1, 7)]}
    for side in ("left", "right", "top", "bottom"):
        values = [[] for _ in range(6)]
        lines = range(h) if side in ("left", "right") else range(w)
        for i in lines:
            line = obj[i] if side in ("left", "right") else obj[:, i]
            idx = np.flatnonzero(line)
            if not len(idx):
                continue
            edge, step = (idx.min(), -1) if side in ("left", "top") else (idx.max(), 1)
            for k in range(1, 7):
                j = edge + step * k
                if 2 <= j < len(line) - 2:
                    values[k - 1].append(al[i, j] if side in ("left", "right") else al[j, i])
        out[side] = [float(np.mean(v)) if v else float("nan") for v in values]
    return out


def owb_creatures():
    from PIL import Image
    files = sorted(f for f in OWB_GENERIC.glob("*.dds") if f.name.startswith(CREATURE_PREFIXES))
    return {f.name: Image.open(f).convert("RGBA") for f in files}


def report(icon, per_unit, reference):
    """Extents, border, luminance and the glow's profile against OWB's creature icons (`reference`: their mean)."""
    import numpy as np
    a = icon.astype(np.float64)
    solid = (a[..., 3] >= 250.0)
    ys, xs = np.where(solid)
    gy, gx = np.where(a[..., 3] > 8)
    lum = (a[..., :3] @ np.asarray(LUMA))[solid]
    print(f"  object x {xs.min()}-{xs.max()} y {ys.min()}-{ys.max()} ({xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1} px, "
          f"{per_unit:.2f} px per model unit); glow x {gx.min()}-{gx.max()} y {gy.min()}-{gy.max()}; "
          f"strongest alpha on the border {border_alpha(icon):.0f}")
    print(f"  object luminance p10 / median / p90: {np.percentile(lum, 10):.0f} / {np.median(lum):.0f} / "
          f"{np.percentile(lum, 90):.0f}   (OWB's creatures: {reference['luma']})")
    ours = glow_profile(icon)
    for key in ("ring", "left", "right", "top", "bottom"):
        print(f"  glow {key:<6} 1-6 px: " + " / ".join(f"{v:3.0f}" for v in ours[key])
              + "   OWB: " + " / ".join(f"{v:3.0f}" for v in reference[key]))


def reference_profile():
    """OWB's 27 creature icons, measured by glow_profile and averaged; their objects' luminance percentiles."""
    import numpy as np
    icons = owb_creatures()
    profiles = [glow_profile(im) for im in icons.values()]
    out = {k: [float(np.nanmean([p[k][i] for p in profiles])) for i in range(6)]
           for k in ("ring", "left", "right", "top", "bottom")}
    lums = np.concatenate([(np.asarray(im, dtype=np.float64)[..., :3] @ np.asarray(LUMA))[np.asarray(im)[..., 3] >= 250]
                           for im in icons.values()])
    out["luma"] = " / ".join(f"{v:.0f}" for v in np.percentile(lums, [10, 50, 90]))
    return out


# --------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------
def write_dds_like_owb(icon, out_path):
    """Pillow writes uncompressed A8R8G8B8 with flags 0x100f / depth 0 / mipmapcount 0; OWB's equipment icons carry
    flags 0x2100f / depth 1 / mipmapcount 1 with the same single level. Patch those three dwords, so the header is
    OWB's mirelurk king's byte for byte (build_tech_icons.py does the same against its Conch Knife)."""
    import hashlib
    import struct

    import numpy as np
    from PIL import Image
    out_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(icon, "RGBA").save(out_path)            # no pixel_format kwarg -> uncompressed A8R8G8B8
    d = bytearray(out_path.read_bytes())
    ref = HEADER_REF.read_bytes()
    for off in (8, 24, 28):                                  # flags, depth, mipmapcount
        d[off:off + 4] = ref[off:off + 4]
    out_path.write_bytes(bytes(d))
    if ref[:128] != bytes(d[:128]) or len(d) != len(ref):
        raise SystemExit(f"{out_path}: header or size differs from OWB's {HEADER_REF.name}")
    h, w = struct.unpack("<2I", d[12:20])
    re = Image.open(out_path)
    re.load()
    if (w, h) != ICON_SIZE or re.size != ICON_SIZE or not np.array_equal(np.asarray(re.convert("RGBA")), icon):
        raise SystemExit(f"{out_path}: the round trip through Pillow differs")
    flags, = struct.unpack("<I", d[8:12])
    print(f"  {out_path.relative_to(ROOT).as_posix()}: {w}x{h}, {len(d):,} bytes, flags 0x{flags:x}; reopened "
          f"{re.mode} {re.size}; sha256 {hashlib.sha256(bytes(d)).hexdigest()[:16]}")


def write_preview(built, renders):
    """Each icon at 1x and 4x in the tech box and in the production row, beside OWB's two mirelurks."""
    from PIL import Image, ImageDraw
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    tiles = [(f"OWB {n.removesuffix('_equipment.dds')}", Image.open(OWB_GENERIC / n).convert("RGBA")) for n in NEIGHBOURS]
    tiles += [(f"ours: {n}", Image.fromarray(icon, "RGBA")) for n, icon in built.items()]
    tech_bgs = [Image.open(p).convert("RGBA") for p in TECH_BGS]
    prod = Image.open(PROD_ITEM).convert("RGBA")
    prod.alpha_composite(Image.open(PROD_BUTTON).convert("RGBA"), PROD_BUTTON_AT)

    def tech(icon, bg):
        tile = bg.copy()
        tile.alpha_composite(icon, (TECH_ICON_CENTRE[0] - icon.width // 2, TECH_ICON_CENTRE[1] - icon.height // 2))
        return tile

    def production(icon):
        tile = prod.copy()
        small = icon.resize((round(icon.width * PROD_ICON_SCALE), round(icon.height * PROD_ICON_SCALE)), Image.LANCZOS)
        tile.alpha_composite(small, (PROD_ICON_CENTRE[0] - small.width // 2, PROD_ICON_CENTRE[1] - small.height // 2))
        return tile.crop(PROD_CROP)

    pad, label = 14, 16
    sections = [("tech box (vanilla available / researched)", [tech(icon, tech_bgs[0]) for _, icon in tiles],
                 [tech(icon, tech_bgs[1]) for _, icon in tiles]),
                ("production row (OWB's production_item and equipment button; icon at 0.9)",
                 [production(icon) for _, icon in tiles], None)]
    blocks = []
    for title, row, row2 in sections:
        tw, th = row[0].size
        # 1x: every tile in a row (and the researched background under it); 4x: two tiles a row
        ones = [row] + ([row2] if row2 else [])
        width = max(pad + len(row) * (tw + pad), pad + 2 * (tw * 4 + pad))
        height = label + len(ones) * (th + label + pad) + 2 * (th * 4 + label + pad)
        block = Image.new("RGBA", (width, height), (30, 32, 34, 255))
        draw = ImageDraw.Draw(block)
        draw.text((pad, 2), f"{title}: 1x", fill=(235, 225, 190))
        y = label
        for r in ones:
            for i, ((text, _), tile) in enumerate(zip(tiles, r)):
                x = pad + i * (tw + pad)
                draw.text((x, y), text, fill=(200, 200, 200))
                block.alpha_composite(tile, (x, y + label))
            y += th + label + pad
        for i, ((text, _), tile) in enumerate(zip(tiles, row)):
            x, yy = pad + i % 2 * (tw * 4 + pad), y + i // 2 * (th * 4 + label + pad)
            draw.text((x, yy), f"{text}, 4x", fill=(200, 200, 200))
            block.alpha_composite(tile.resize((tw * 4, th * 4), Image.NEAREST), (x, yy + label))
        blocks.append(block)
    sheet = Image.new("RGBA", (max(b.width for b in blocks), sum(b.height for b in blocks)), (30, 32, 34, 255))
    y = 0
    for block in blocks:
        sheet.alpha_composite(block, (0, y))
        y += block.height
    sheet.convert("RGB").save(PREVIEW_DIR / PREVIEW)
    for name, icon in built.items():
        Image.fromarray(icon, "RGBA").save(PREVIEW_DIR / f"{name}_out.png")
    # the raw renders, side by side on a mid grey, 400 px tall
    shots = [Image.open(r).convert("RGBA") for r in renders]
    shots = [s.resize((round(s.width * 400 / s.height), 400), Image.LANCZOS) for s in shots]
    strip = Image.new("RGBA", (sum(s.width for s in shots) + pad * (len(shots) + 1), 400 + 2 * pad), (88, 90, 86, 255))
    x = pad
    for s in shots:
        strip.alpha_composite(s, (x, pad))
        x += s.width + pad
    strip.convert("RGB").save(PREVIEW_DIR / "renders.png")
    print(f"previews -> {PREVIEW_DIR.relative_to(ROOT).as_posix()}/{PREVIEW}, renders.png, "
          + ", ".join(f"{n}_out.png" for n in built))


def parse_set(items):
    """--set icon.key=value: a float, a tuple of floats (comma-separated) or a string, into ICONS."""
    icons = {name: dict(p, grade=dict(p["grade"])) for name, p in ICONS.items()}
    for item in items or []:
        path, _, value = item.partition("=")
        name, _, key = path.partition(".")
        if name not in icons:
            raise SystemExit(f"--set {item}: no icon {name!r} (one of {', '.join(icons)})")
        target = icons[name]["grade"] if key in icons[name]["grade"] else icons[name]
        if key not in target:
            raise SystemExit(f"--set {item}: {name} has no {key!r}")
        try:
            parsed = tuple(float(v) for v in value.split(",")) if "," in value else float(value)
        except ValueError:
            parsed = value
        target[key] = parsed
    return icons


def main():
    import argparse
    import json
    import tempfile

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--no-write", action="store_true", help="previews only: do not touch mod_folder")
    ap.add_argument("--rerender", action="store_true", help="render even if the cached renders are current")
    ap.add_argument("--set", action="append", metavar="ICON.KEY=VALUE", help="override an ICONS entry or grade key")
    ap.add_argument("--blender", help=f"blender.exe (default: the newest under {BLENDER_GLOB})")
    ap.add_argument("--model-work", help="build_unit_model.py's cache (default: its own, in the system temp directory)")
    ap.add_argument("--work", default=str(Path(tempfile.gettempdir()) / "rising_tide_equipment_icons"),
                    help="this script's render cache")
    args = ap.parse_args()
    icons = parse_set(args.set)

    sys.path.insert(0, str(ROOT))
    import build_unit_model as bum
    model_work = Path(args.model_work) if args.model_work else Path(tempfile.gettempdir()) / "rising_tide_unit_model"
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    print("Posing")
    rig = model_cache(bum, model_work)
    manifest, key = prepare(bum, rig, work, model_work, icons)
    have = json.loads((work / "renders.json").read_text()) if (work / "renders.json").exists() else None
    pngs = [work / job["png"] for job in manifest["jobs"]]
    if args.rerender or have != key or not all(p.exists() for p in pngs):
        print(f"Rendering {len(pngs)} views")
        (work / "renders.json").unlink(missing_ok=True)       # a render that dies half-way must not look current
        run_blender(find_blender(args.blender), work)
        (work / "renders.json").write_text(json.dumps(key, indent=1))
    else:
        print("The cached renders are current")

    print("Composing")
    reference = reference_profile()
    renders = {job["name"]: (load_render(work / job["png"]), job["units_per_px"]) for job in manifest["jobs"]}
    built = {}
    largest = [name for name, p in icons.items() if p["size"] == "max"]
    if len(largest) != 1:
        raise SystemExit(f"exactly one icon takes size \"max\" (the others are shares of it), not {len(largest)}")
    per_unit = None                                                     # the "max" icon's pixels per model unit
    for name in largest + [n for n in icons if n not in largest]:
        p, (pm, units_per_px) = icons[name], renders[name]
        zoom = fit_max(pm, p["grade"]) if p["size"] == "max" else per_unit * float(p["size"]) * units_per_px
        per_unit = per_unit or zoom / units_per_px
        built[name] = compose(pm, zoom, p["grade"])
        print(f"{name} ({p['equipment']}): {p['clip']} at u = {float(p['u']):.3f}, seen from {tuple(p['view'])}")
        report(built[name], zoom / units_per_px, reference)
        if border_alpha(built[name]) > BORDER_MAX:
            raise SystemExit(f"{name}: its glow reaches the texture's border (alpha {border_alpha(built[name]):.0f} > "
                             f"{BORDER_MAX:.0f}): lower its share or change the pose")
    built = {name: built[name] for name in icons}
    if not args.no_write:
        for name, p in icons.items():
            write_dds_like_owb(built[name], OUT_DIR / p["out"])
    write_preview(built, [work / job["png"] for job in manifest["jobs"]])


if __name__ == "__main__":
    blender_main() if IN_BLENDER else main()
