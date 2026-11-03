"""Create the original Field Atlas in Blender, export GLB, and render a fallback.

Run with Blender: blender --background --python scripts/build_field_atlas.py
The terrain is an artistic landscape, not a map or a GPS record.
"""

from pathlib import Path
import hashlib
import json
import math

import bpy
from mathutils import Vector, noise

noise.seed_set(95)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "blender"
OUTPUT = ROOT / "static" / "models"
SOURCE.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.render.engine = "CYCLES"
bpy.context.scene.cycles.samples = 32
bpy.context.scene.cycles.use_denoising = True


def material(name, color, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = 0.76
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Emission Color"].default_value = (*color, 1)
    shader.inputs["Emission Strength"].default_value = emission
    return mat


rock = material("Limestone", (0.19, 0.24, 0.21), 0.12)
snow = material("Summit chalk", (0.72, 0.78, 0.72), 0.04)
lowland = material("Forest stone", (0.035, 0.065, 0.047), 0.08)
contour = material("Survey contour", (0.17, 0.56, 0.43), 0.15, 0.12)
trail = material("Route vermilion", (1.0, 0.075, 0.008), 0.06, 0.65)
mint = material("Survey marker", (0.035, 0.95, 0.62), 0.1, 0.6)
base = material("Basalt cut", (0.027, 0.043, 0.037), 0.15)
grid = material("Datum grid", (0.11, 0.20, 0.16), 0.0, 0.1)


def height(x, y):
    peaks = [(-2.4, 1.9, 4.7, 2.1), (0.6, 0.6, 5.7, 2.2),
             (3.5, 2.4, 3.9, 1.9), (-4.7, -1.2, 2.6, 1.6), (3.9, -2.7, 2.5, 1.8)]
    summits = []
    for px, py, amp, spread in peaks:
        dx, dy = x - px, y - py
        radius = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        ridge = 1 + .20 * math.sin(angle * 5 + 1) + .12 * math.sin(angle * 9 + radius * 1.4)
        summits.append(amp * math.exp(-((radius * ridge / spread) ** 1.4)))
    summit = max(summits)
    edge = min(1.0, max(0.0, (8.8 - max(abs(x), abs(y))) / 2.3))
    broad = noise.fractal(Vector((x * .47, y * .47, 2.7)), 1.0, 2.0, 4)
    detail = noise.noise_vector(Vector((x * 1.55, y * 1.55, 1.2))).x
    return 0.12 + max(0.0, summit + broad * .7 + detail * .2) * edge


N = 120
SPAN = 17.6
vertices = []
faces = []
for j in range(N + 1):
    for i in range(N + 1):
        x, y = -8.8 + SPAN * i / N, -8.8 + SPAN * j / N
        vertices.append((x, y, height(x, y)))
for j in range(N):
    for i in range(N):
        a = j * (N + 1) + i
        faces.extend([(a, a + 1, a + N + 2), (a, a + N + 2, a + N + 1)])
mesh = bpy.data.meshes.new("Alpine heightfield")
mesh.from_pydata(vertices, [], faces)
mesh.update()
terrain = bpy.data.objects.new("Field Atlas terrain", mesh)
bpy.context.collection.objects.link(terrain)
for mat in (lowland, rock, snow):
    mesh.materials.append(mat)
for polygon in mesh.polygons:
    z = sum(vertices[index][2] for index in polygon.vertices) / 3
    polygon.material_index = 2 if z > 3.55 else 1 if z > 1.15 else 0
    polygon.use_smooth = True


def curves(name, paths, radius, mat):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 1
    data.bevel_depth = radius
    data.bevel_resolution = 0
    for points in paths:
        spline = data.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for point, xyz in zip(spline.points, points):
            point.co = (*xyz, 1)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    data.materials.append(mat)
    return obj


# Intersect the triangles with horizontal planes to author actual contour geometry.
segments = []
for level_index in range(1, 20):
    z = level_index * .28
    for face in faces:
        points = [vertices[index] for index in face]
        if not min(p[2] for p in points) < z < max(p[2] for p in points):
            continue
        hits = []
        for first, second in ((0, 1), (1, 2), (2, 0)):
            p, q = points[first], points[second]
            if (p[2] < z) != (q[2] < z):
                t = (z - p[2]) / (q[2] - p[2])
                hits.append((p[0] + t*(q[0]-p[0]), p[1] + t*(q[1]-p[1]), z + .04))
        if len(hits) == 2:
            segments.append(hits)
curves("Elevation contours", segments, .017, contour)

edge_path = []
for axis in range(4):
    for i in range(N + 1):
        v = -8.8 + SPAN * i / N
        x, y = ((v, -8.8), (8.8, v), (-v, 8.8), (-8.8, -v))[axis]
        edge_path.append((x, y, height(x, y)))
walls, wall_faces = [], []
for i, p in enumerate(edge_path):
    walls.extend([p, (p[0], p[1], -.65)])
    wall_faces.append((2*i, 2*i+1, (2*i+3) % (len(edge_path)*2), (2*i+2) % (len(edge_path)*2)))
wall_mesh = bpy.data.meshes.new("Cutaway edge")
wall_mesh.from_pydata(walls, [], wall_faces)
wall_mesh.materials.append(base)
wall_obj = bpy.data.objects.new("Basalt section", wall_mesh)
bpy.context.collection.objects.link(wall_obj)

grid_paths = []
for i in range(-12, 13):
    grid_paths.extend([[(-12, i, -.72), (12, i, -.72)], [(i, -12, -.72), (i, 12, -.72)]])
curves("Survey datum", grid_paths, .012, grid)

route_points = []
for i in range(241):
    t = i / 240
    x = -6.2 + t * 7.0 + math.sin(t * math.pi * 5) * .52
    y = -5.8 + t * 6.4 + math.sin(t * math.pi * 4) * .42
    route_points.append((x, y, height(x, y) + .075))
curves("Summit route", [route_points], .038, trail)

for index in (0, 80, 160, 240):
    x, y, z = route_points[index]
    curves(f"Station mast {index}", [[(x, y, z), (x, y, z + .75)]], .022, mint)
    bpy.ops.mesh.primitive_torus_add(major_radius=.15, minor_radius=.025, major_segments=20,
                                    minor_segments=4, location=(x, y, z + .74))
    bpy.context.object.name = f"Survey station {index}"
    bpy.context.object.data.materials.append(mint)
    if index in (0, 160, 240):
        label, href = {0: ("Training", "/workouts"), 160: ("Projects", "/projects"), 240: ("Systems", "/folloze-gtm")}[index]
        bpy.context.object["label"] = label
        bpy.context.object["href"] = href

# Convert authored curves once so the web export carries no procedural dependencies.
for obj in list(bpy.context.scene.objects):
    if obj.type == "CURVE":
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target="MESH")

scene = bpy.context.scene
scene.world.color = (0.16, 0.16, 0.16)
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.12, .16, .14, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .45


def area(name, location, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size, data.color = energy, "DISK", size, color
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((0, 0, 1)) - obj.location).to_track_quat("-Z", "Y").to_euler()


area("Soft daylight", (1, -4, 15), 1900, 10, (.88, .96, 1.0))
area("Warm ridge", (-8, 5, 9), 1600, 8, (1.0, .76, .53))
area("Mint bounce", (7, 8, 6), 700, 7, (.36, 1.0, .72))
camera_data = bpy.data.cameras.new("Atlas camera")
camera = bpy.data.objects.new("Atlas camera", camera_data)
scene.collection.objects.link(camera)
camera.location = (15, -18, 15)
camera.rotation_euler = (Vector((0, 0, 1)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 26
scene.camera = camera
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"

bpy.ops.object.select_all(action="DESELECT")
for obj in scene.objects:
    if obj.type == "MESH":
        obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUTPUT / "field-atlas.glb"), export_format="GLB",
                          use_selection=True, export_animations=False, export_cameras=False,
                          export_lights=False, export_extras=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE / "field-atlas.blend"))
scene.render.filepath = str(OUTPUT / "field-atlas-poster.png")
bpy.ops.render.render(write_still=True)
manifest = {
    "asset": "Field Atlas", "authoring_tool": bpy.app.version_string,
    "source": "assets/blender/field-atlas.blend", "generator": "scripts/build_field_atlas.py",
    "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "blend_sha256": hashlib.sha256((SOURCE / "field-atlas.blend").read_bytes()).hexdigest(),
    "provenance": "Original procedural artwork. No third-party models, textures, or GPS data.",
    "triangles": sum(len(poly.vertices) - 2 for obj in scene.objects if obj.type == "MESH" for poly in obj.data.polygons),
    "outputs": {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in OUTPUT.iterdir() if p.suffix in (".glb", ".png")},
}
(SOURCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
