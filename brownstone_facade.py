"""Procedural NYC brownstone facade generator for Autodesk Maya (maya.cmds)."""

try:
    import maya.cmds as cmds
except Exception as exc:  # pragma: no cover - Maya runtime only
    raise ImportError("This script must run inside Autodesk Maya.") from exc


def create_shader(name, shader_type, color, transparency=None, reflectivity=None):
    """Create a shader + shading group and return the shading group."""
    shader = name
    sg = name + "SG"
    if not cmds.objExists(shader):
        shader = cmds.shadingNode(shader_type, asShader=True, name=shader)
        cmds.setAttr(shader + ".color", color[0], color[1], color[2], type="double3")
        if transparency is not None:
            cmds.setAttr(shader + ".transparency", transparency[0], transparency[1], transparency[2], type="double3")
        if reflectivity is not None and cmds.attributeQuery("reflectivity", node=shader, exists=True):
            cmds.setAttr(shader + ".reflectivity", reflectivity)
    if not cmds.objExists(sg):
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
        cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
    return sg


def assign_shader(node, shading_group):
    """Assign shading group to node."""
    if node and cmds.objExists(node):
        cmds.sets(node, edit=True, forceElement=shading_group)


def create_box(name, width, height, depth, x, y, z, parent=None, shader=None, rx=0.0, ry=0.0, rz=0.0):
    """Create a cube with consistent naming, transform, parenting, and material assignment."""
    transform = cmds.polyCube(name=name, w=width, h=height, d=depth)[0]
    cmds.xform(transform, ws=True, t=(x, y, z), ro=(rx, ry, rz))
    if parent:
        cmds.parent(transform, parent)
    if shader:
        assign_shader(transform, shader)
    return transform


def create_groups():
    """Create required logical groups and return them as a dict."""
    group_names = [
        "grp_facade",
        "grp_cornice",
        "grp_windows",
        "grp_stoop",
        "grp_entry_door",
        "grp_site",
    ]
    groups = {}
    for name in group_names:
        if cmds.objExists(name):
            cmds.delete(name)
        groups[name] = cmds.group(em=True, name=name)

    if cmds.objExists("grp_brownstone"):
        cmds.delete("grp_brownstone")
    root = cmds.group(em=True, name="grp_brownstone")
    cmds.parent(groups["grp_facade"], root)
    cmds.parent(groups["grp_cornice"], root)
    cmds.parent(groups["grp_windows"], root)
    cmds.parent(groups["grp_stoop"], root)
    cmds.parent(groups["grp_entry_door"], root)
    cmds.parent(groups["grp_site"], root)
    groups["root"] = root
    return groups


def create_window_assembly(
    base_name,
    center_x,
    center_y,
    wall_front_z,
    width,
    height,
    recess,
    groups,
    stone_sg,
    glass_sg,
    hood=False,
    sill=True,
    architrave=False,
):
    """Create recessed window, surround, optional hood/sill and optional raised architrave frame."""
    reveal_depth = max(recess - 0.05, 0.05)
    create_box(
        base_name + "_reveal",
        width,
        height,
        reveal_depth,
        center_x,
        center_y,
        wall_front_z - (recess * 0.5),
        parent=groups["grp_windows"],
        shader=stone_sg,
    )

    glass = cmds.polyPlane(name=base_name + "_glass", w=width * 0.92, h=height * 0.92, sx=1, sy=1)[0]
    cmds.xform(glass, ws=True, t=(center_x, center_y, wall_front_z - recess + 0.02), ro=(0, 0, 0))
    cmds.parent(glass, groups["grp_windows"])
    assign_shader(glass, glass_sg)

    surround_thickness = 0.16
    surround_width = 0.25
    side_h = height + surround_width * 2.0
    top_bot_w = width + surround_width * 2.0

    create_box(
        base_name + "_surround_left",
        surround_width,
        side_h,
        surround_thickness,
        center_x - (width * 0.5) - (surround_width * 0.5),
        center_y,
        wall_front_z + 0.08,
        parent=groups["grp_windows"],
        shader=stone_sg,
    )
    create_box(
        base_name + "_surround_right",
        surround_width,
        side_h,
        surround_thickness,
        center_x + (width * 0.5) + (surround_width * 0.5),
        center_y,
        wall_front_z + 0.08,
        parent=groups["grp_windows"],
        shader=stone_sg,
    )
    create_box(
        base_name + "_surround_top",
        top_bot_w,
        surround_width,
        surround_thickness,
        center_x,
        center_y + (height * 0.5) + (surround_width * 0.5),
        wall_front_z + 0.08,
        parent=groups["grp_windows"],
        shader=stone_sg,
    )
    create_box(
        base_name + "_surround_bottom",
        top_bot_w,
        surround_width,
        surround_thickness,
        center_x,
        center_y - (height * 0.5) - (surround_width * 0.5),
        wall_front_z + 0.08,
        parent=groups["grp_windows"],
        shader=stone_sg,
    )

    if architrave:
        arch_proud = 0.125
        arch_w = 0.25
        arch_h = height + arch_w * 2.0
        arch_total_w = width + arch_w * 2.0
        create_box(
            base_name + "_architrave_left",
            arch_w,
            arch_h,
            arch_proud,
            center_x - (width * 0.5) - (arch_w * 0.5),
            center_y,
            wall_front_z + 0.13,
            parent=groups["grp_windows"],
            shader=stone_sg,
        )
        create_box(
            base_name + "_architrave_right",
            arch_w,
            arch_h,
            arch_proud,
            center_x + (width * 0.5) + (arch_w * 0.5),
            center_y,
            wall_front_z + 0.13,
            parent=groups["grp_windows"],
            shader=stone_sg,
        )
        create_box(
            base_name + "_architrave_top",
            arch_total_w,
            arch_w,
            arch_proud,
            center_x,
            center_y + (height * 0.5) + (arch_w * 0.5),
            wall_front_z + 0.13,
            parent=groups["grp_windows"],
            shader=stone_sg,
        )
        create_box(
            base_name + "_architrave_bottom",
            arch_total_w,
            arch_w,
            arch_proud,
            center_x,
            center_y - (height * 0.5) - (arch_w * 0.5),
            wall_front_z + 0.13,
            parent=groups["grp_windows"],
            shader=stone_sg,
        )

    if hood:
        create_box(
            base_name + "_hood",
            width + 0.45,
            0.167,
            0.25,
            center_x,
            center_y + (height * 0.5) + 0.28,
            wall_front_z + 0.125,
            parent=groups["grp_windows"],
            shader=SHADERS["dark"],
        )

    if sill:
        create_box(
            base_name + "_sill",
            width + 0.3,
            0.12,
            0.208,
            center_x,
            center_y - (height * 0.5) - 0.23,
            wall_front_z + 0.104,
            parent=groups["grp_windows"],
            shader=stone_sg,
        )


def create_floor_windows(groups, stone_sg, glass_sg):
    """Create all window layouts for garden, parlor, floor 2, and floor 3."""
    # Garden / below-grade level
    create_window_assembly(
        "brownstone_window_garden_left",
        center_x=-7.0,
        center_y=-0.9,
        wall_front_z=0.0,
        width=3.5,
        height=3.0,
        recess=0.333,
        groups=groups,
        stone_sg=stone_sg,
        glass_sg=glass_sg,
        hood=False,
        sill=True,
        architrave=False,
    )
    create_window_assembly(
        "brownstone_window_garden_right",
        center_x=7.0,
        center_y=-0.9,
        wall_front_z=0.0,
        width=3.5,
        height=3.0,
        recess=0.333,
        groups=groups,
        stone_sg=stone_sg,
        glass_sg=glass_sg,
        hood=False,
        sill=True,
        architrave=False,
    )
    create_window_assembly(
        "brownstone_window_garden_bay_center",
        center_x=0.0,
        center_y=-0.2,
        wall_front_z=2.5,
        width=4.0,
        height=4.5,
        recess=0.333,
        groups=groups,
        stone_sg=stone_sg,
        glass_sg=glass_sg,
        hood=False,
        sill=True,
        architrave=False,
    )

    # Parlor + upper floors
    floor_specs = [
        ("floor1", 8.2, 6.5, 3.5, 6.5, True),
        ("floor2", 20.8, 6.0, 3.5, 6.0, True),
        ("floor3", 33.2, 6.0, 3.5, 6.0, True),
    ]
    for floor_name, y, side_h, side_w, bay_h, with_architrave in floor_specs:
        create_window_assembly(
            "brownstone_window_{0}_left".format(floor_name),
            center_x=-7.0,
            center_y=y,
            wall_front_z=0.0,
            width=side_w,
            height=side_h,
            recess=0.417,
            groups=groups,
            stone_sg=stone_sg,
            glass_sg=glass_sg,
            hood=True,
            sill=True,
            architrave=with_architrave,
        )
        create_window_assembly(
            "brownstone_window_{0}_right".format(floor_name),
            center_x=7.0,
            center_y=y,
            wall_front_z=0.0,
            width=side_w,
            height=side_h,
            recess=0.417,
            groups=groups,
            stone_sg=stone_sg,
            glass_sg=glass_sg,
            hood=True,
            sill=True,
            architrave=with_architrave,
        )

        create_box(
            "brownstone_window_{0}_bay_mullion".format(floor_name),
            0.25,
            bay_h,
            0.18,
            0.0,
            y,
            2.58,
            parent=groups["grp_windows"],
            shader=stone_sg,
        )

        for side_label, x in (("left", -1.4), ("right", 1.4)):
            create_window_assembly(
                "brownstone_window_{0}_bay_{1}".format(floor_name, side_label),
                center_x=x,
                center_y=y,
                wall_front_z=2.5,
                width=2.5,
                height=bay_h,
                recess=0.417,
                groups=groups,
                stone_sg=stone_sg,
                glass_sg=glass_sg,
                hood=True,
                sill=True,
                architrave=with_architrave,
            )


def create_rustication_and_joints(groups, stone_sg):
    """Create rusticated base and ashlar joint lines via explicit geometry."""
    course_heights = [0.5, 0.5, 0.5]
    y_cursor = 0.25
    for course_idx, course_height in enumerate(course_heights, start=1):
        x_cursor = -9.6
        block_widths = [2.2, 1.9, 2.4, 1.8, 2.3, 1.9, 2.1, 1.7]
        for block_idx, bw in enumerate(block_widths, start=1):
            if x_cursor + bw > 10.0:
                break
            create_box(
                "rusticated_base_course_{0:02d}_block_{1:02d}".format(course_idx, block_idx),
                bw,
                course_height - 0.03,
                0.35,
                x_cursor + (bw * 0.5),
                y_cursor,
                0.17,
                parent=groups["grp_facade"],
                shader=stone_sg,
            )
            x_cursor += bw + 0.15
        # Deep horizontal recessed joint strip
        create_box(
            "rusticated_base_joint_{0:02d}".format(course_idx),
            20.0,
            0.04,
            0.06,
            0.0,
            y_cursor + (course_height * 0.5),
            0.03,
            parent=groups["grp_facade"],
            shader=stone_sg,
        )
        y_cursor += course_height

    # Smooth ashlar V-groove style horizontal joints above base (every 1 ft)
    y_val = 1.5
    line_index = 1
    while y_val < 46.0:
        create_box(
            "ashlar_vgroove_joint_{0:02d}".format(line_index),
            20.0,
            0.04,
            0.03,
            0.0,
            y_val,
            0.015,
            parent=groups["grp_facade"],
            shader=stone_sg,
            rx=45.0,
        )
        line_index += 1
        y_val += 1.0


def create_belt_courses(groups, stone_sg):
    """Create the two required horizontal belt courses."""
    for idx, y in enumerate((14.8, 27.2), start=1):
        create_box(
            "brownstone_belt_course_{0:02d}".format(idx),
            20.0,
            0.833,
            0.083,
            0.0,
            y,
            0.041,
            parent=groups["grp_facade"],
            shader=stone_sg,
        )


def create_cornice(groups):
    """Create multi-layer cornice with dentils, fascia, brackets, and crown cap that follows bay plan."""
    dark_sg = SHADERS["dark"]

    def cornice_segment(prefix, width, depth, x, y, z, ry=0.0):
        return create_box(prefix, width, 0.333, depth, x, y, z, parent=groups["grp_cornice"], shader=dark_sg, ry=ry)

    # Dentil support line segments
    segment_specs = [
        ("cornice_dentil_band_left", 5.0, 0.25, -7.5, 46.8, 0.125, 0.0),
        ("cornice_dentil_band_right", 5.0, 0.25, 7.5, 46.8, 0.125, 0.0),
        ("cornice_dentil_band_bay_front", 10.0, 0.25, 0.0, 46.8, 2.625, 0.0),
        ("cornice_dentil_band_bay_return_left", 2.0, 0.25, -5.6, 46.8, 1.35, 30.0),
        ("cornice_dentil_band_bay_return_right", 2.0, 0.25, 5.6, 46.8, 1.35, -30.0),
    ]
    for spec in segment_specs:
        cornice_segment(*spec)

    # Dentil row (30 total)
    dentil_count = 0
    for start_x, count, spacing, z, ry in (
        (-9.4, 8, 0.65, 0.23, 0.0),
        (-6.2, 3, 0.6, 1.42, 30.0),
        (-4.3, 8, 1.25, 2.72, 0.0),
        (5.0, 3, 0.6, 1.42, -30.0),
        (6.0, 8, 0.65, 0.23, 0.0),
    ):
        for idx in range(count):
            dentil_count += 1
            create_box(
                "cornice_dentil_{0:02d}".format(dentil_count),
                0.25,
                0.333,
                0.25,
                start_x + idx * spacing,
                47.0,
                z,
                parent=groups["grp_cornice"],
                shader=dark_sg,
                ry=ry,
            )

    # Bed molding (ogee approximation with two stacked offsets)
    for suffix, y, depth, z in (("lower", 47.35, 0.25, 0.18), ("upper", 47.55, 0.22, 0.25)):
        for part, width, x, rz in (("left", 5.0, -7.5, 8.0), ("right", 5.0, 7.5, -8.0), ("bay", 10.0, 0.0, 0.0)):
            create_box(
                "cornice_bed_molding_{0}_{1}".format(suffix, part),
                width,
                0.2,
                depth,
                x,
                y,
                2.5 + z if part == "bay" else z,
                parent=groups["grp_cornice"],
                shader=dark_sg,
                rz=rz,
            )

    # Fascia / soffit slab (10 in tall, 14 in projection)
    fascia_depth = 1.167
    for part, width, x, z, ry in (
        ("left", 5.0, -7.5, fascia_depth * 0.5, 0.0),
        ("right", 5.0, 7.5, fascia_depth * 0.5, 0.0),
        ("bay_front", 10.0, 0.0, 2.5 + fascia_depth * 0.5, 0.0),
        ("bay_return_left", 2.0, -5.6, 1.25 + fascia_depth * 0.5, 30.0),
        ("bay_return_right", 2.0, 5.6, 1.25 + fascia_depth * 0.5, -30.0),
    ):
        create_box(
            "cornice_fascia_{0}".format(part),
            width,
            0.833,
            fascia_depth,
            x,
            48.1,
            z,
            parent=groups["grp_cornice"],
            shader=dark_sg,
            ry=ry,
        )

    # Brackets / modillions (approximate S-profile via two tapered blocks)
    bracket_index = 0
    for x_start, count, spacing, z, ry in (
        (-9.0, 7, 0.65, 0.55, 0.0),
        (-3.9, 7, 1.3, 2.95, 0.0),
        (6.0, 7, 0.65, 0.55, 0.0),
    ):
        for i in range(count):
            bracket_index += 1
            bx = x_start + i * spacing
            lower = create_box(
                "cornice_bracket_{0:02d}_lower".format(bracket_index),
                0.42,
                0.45,
                0.55,
                bx,
                47.55,
                z,
                parent=groups["grp_cornice"],
                shader=dark_sg,
                ry=ry,
            )
            upper = create_box(
                "cornice_bracket_{0:02d}_upper".format(bracket_index),
                0.35,
                0.4,
                0.3,
                bx,
                47.95,
                z + 0.15,
                parent=groups["grp_cornice"],
                shader=dark_sg,
                rx=-25.0,
                ry=ry,
            )
            bracket_group = cmds.group(em=True, name="cornice_bracket_{0:02d}".format(bracket_index))
            cmds.parent([lower, upper], bracket_group)
            cmds.parent(bracket_group, groups["grp_cornice"])

    # Crown cap + drip fillet
    crown_depth = 1.333
    for part, width, x, z, ry in (
        ("left", 5.0, -7.5, crown_depth * 0.5, 0.0),
        ("right", 5.0, 7.5, crown_depth * 0.5, 0.0),
        ("bay_front", 10.0, 0.0, 2.5 + crown_depth * 0.5, 0.0),
        ("bay_return_left", 2.0, -5.6, 1.25 + crown_depth * 0.5, 30.0),
        ("bay_return_right", 2.0, 5.6, 1.25 + crown_depth * 0.5, -30.0),
    ):
        create_box(
            "cornice_crown_cap_{0}".format(part),
            width,
            0.333,
            crown_depth,
            x,
            48.8,
            z,
            parent=groups["grp_cornice"],
            shader=dark_sg,
            ry=ry,
        )
        create_box(
            "cornice_drip_fillet_{0}".format(part),
            width,
            0.08,
            0.08,
            x,
            48.63,
            z + (crown_depth * 0.5) - 0.04,
            parent=groups["grp_cornice"],
            shader=dark_sg,
            ry=ry,
        )


def create_stoop_and_entry(groups, stone_sg, wood_sg, glass_sg):
    """Create stoop, cheek walls, rosettes, lamp, main entry, and below-grade entrance."""
    # Stoop steps (5) with slight taper in plan
    step_height = 0.583
    step_depth = 0.917
    top_width = 10.0
    x_offset = 2.0
    for i in range(5):
        step_name = "stoop_step_{0:02d}".format(i + 1)
        step_width = top_width + ((4 - i) * 0.2)
        y = (i + 0.5) * step_height
        z = 8.8 - ((i + 1) * step_depth)
        create_box(
            step_name,
            step_width,
            step_height,
            step_depth,
            x_offset,
            y,
            z,
            parent=groups["grp_stoop"],
            shader=stone_sg,
        )

    # Landing
    create_box(
        "stoop_landing",
        8.0,
        0.6,
        5.0,
        x_offset,
        3.2,
        4.1,
        parent=groups["grp_stoop"],
        shader=stone_sg,
    )

    # Cheek walls with coping
    for side, x in (("left", -3.2), ("right", 7.2)):
        create_box(
            "stoop_cheek_wall_{0}".format(side),
            1.167,
            3.2,
            10.0,
            x,
            1.6,
            4.1,
            parent=groups["grp_stoop"],
            shader=stone_sg,
        )
        create_box(
            "stoop_cheek_wall_{0}_coping".format(side),
            1.333,
            0.25,
            10.167,
            x,
            3.325,
            4.1,
            parent=groups["grp_stoop"],
            shader=stone_sg,
        )

        rosette = cmds.polyCylinder(name="stoop_rosette_panel_{0}".format(side), r=0.417, h=0.08, sx=20)[0]
        cmds.xform(rosette, ws=True, t=(x + (0.62 if side == "right" else -0.62), 0.8, 9.0), ro=(90, 0, 0))
        cmds.parent(rosette, groups["grp_stoop"])
        assign_shader(rosette, stone_sg)

        for groove_idx in range(6):
            create_box(
                "stoop_rosette_panel_{0}_groove_{1:02d}".format(side, groove_idx + 1),
                0.78,
                0.03,
                0.02,
                x + (0.63 if side == "right" else -0.63),
                0.8,
                9.0,
                parent=groups["grp_stoop"],
                shader=stone_sg,
                rz=groove_idx * 30.0,
                rx=90.0,
            )

    # Newel post lamp on left cheek wall
    post = cmds.polyCylinder(name="stoop_newel_post_lamp_post", r=0.125, h=2.5, sx=16)[0]
    cmds.xform(post, ws=True, t=(-3.2, 4.6, 8.8), ro=(0, 0, 0))
    cmds.parent(post, groups["grp_stoop"])
    assign_shader(post, SHADERS["dark"])

    lantern = cmds.polyCylinder(name="stoop_newel_post_lamp_lantern", r=0.208, h=0.583, sx=6)[0]
    cmds.xform(lantern, ws=True, t=(-3.2, 5.15, 8.8), ro=(0, 30, 0))
    cmds.parent(lantern, groups["grp_stoop"])
    assign_shader(lantern, SHADERS["dark"])

    # Main entry surround and door assembly
    door_center_x = x_offset
    door_center_y = 8.0
    door_center_z = 2.65

    create_box(
        "entry_pilaster_left",
        0.333,
        8.0,
        0.167,
        door_center_x - 1.95,
        door_center_y,
        door_center_z,
        parent=groups["grp_entry_door"],
        shader=stone_sg,
    )
    create_box(
        "entry_pilaster_right",
        0.333,
        8.0,
        0.167,
        door_center_x + 1.95,
        door_center_y,
        door_center_z,
        parent=groups["grp_entry_door"],
        shader=stone_sg,
    )
    create_box(
        "entry_entablature",
        4.4,
        0.5,
        0.25,
        door_center_x,
        12.2,
        door_center_z + 0.02,
        parent=groups["grp_entry_door"],
        shader=stone_sg,
    )

    create_box("brownstone_entry_door_main", 3.5, 8.0, 0.167, door_center_x, 8.0, 2.43, parent=groups["grp_entry_door"], shader=wood_sg)

    panel_index = 0
    for row in range(3):
        for col in range(2):
            panel_index += 1
            px = door_center_x + (-0.85 if col == 0 else 0.85)
            py = 10.3 - row * 2.45
            create_box(
                "entry_door_panel_{0:02d}".format(panel_index),
                1.2,
                2.1,
                0.08,
                px,
                py,
                2.36,
                parent=groups["grp_entry_door"],
                shader=wood_sg,
            )

    # Transom with two panes
    create_box("entry_transom_frame", 3.5, 1.167, 0.12, door_center_x, 12.75, 2.48, parent=groups["grp_entry_door"], shader=stone_sg)
    for side, x in (("left", door_center_x - 0.85), ("right", door_center_x + 0.85)):
        transom_glass = cmds.polyPlane(name="entry_transom_glass_{0}".format(side), w=1.5, h=0.9)[0]
        cmds.xform(transom_glass, ws=True, t=(x, 12.75, 2.41), ro=(0, 0, 0))
        cmds.parent(transom_glass, groups["grp_entry_door"])
        assign_shader(transom_glass, glass_sg)

    # Wall-mounted light fixture (right of main surround)
    create_box("entry_light_bracket_arm", 0.08, 0.08, 0.5, door_center_x + 2.7, 10.8, 2.72, parent=groups["grp_entry_door"], shader=SHADERS["dark"])
    fixture = cmds.polyCylinder(name="entry_light_fixture_downlight", r=0.125, h=0.417, sx=16)[0]
    cmds.xform(fixture, ws=True, t=(door_center_x + 2.95, 10.65, 2.72), ro=(90, 0, 0))
    cmds.parent(fixture, groups["grp_entry_door"])
    assign_shader(fixture, SHADERS["dark"])

    # Below-grade secondary entrance and areaway
    create_box("garden_areaway_pit", 6.0, 3.5, 4.0, door_center_x, -1.75, 6.0, parent=groups["grp_site"], shader=stone_sg)
    create_box("garden_entry_surround", 3.3, 7.0, 0.2, door_center_x, -0.25, 0.15, parent=groups["grp_entry_door"], shader=stone_sg)
    create_box("garden_entry_door", 2.8, 6.5, 0.16, door_center_x, -0.3, 0.07, parent=groups["grp_entry_door"], shader=wood_sg)

    panel_index = 0
    for row in range(2):
        for col in range(2):
            panel_index += 1
            px = door_center_x + (-0.65 if col == 0 else 0.65)
            py = 1.1 - row * 2.8
            create_box(
                "garden_entry_panel_{0:02d}".format(panel_index),
                0.95,
                2.1,
                0.07,
                px,
                py,
                0.0,
                parent=groups["grp_entry_door"],
                shader=wood_sg,
            )


def create_site_elements(groups, stone_sg):
    """Create retaining wall/fence, planting planes, and sidewalk."""
    # Front retaining wall/fence and coping
    create_box("site_retaining_wall", 20.0, 2.5, 0.833, 0.0, 1.25, 10.4, parent=groups["grp_site"], shader=stone_sg)
    create_box("site_retaining_wall_coping", 20.2, 0.25, 1.0, 0.0, 2.625, 10.4, parent=groups["grp_site"], shader=stone_sg)

    # Planting strips (2 inches thick)
    planting_sg = create_shader("brownstone_planting_green", "lambert", (0.18, 0.36, 0.18))
    for name, x in (("site_planting_plane_left", -5.5), ("site_planting_plane_right", 9.5)):
        plane = cmds.polyPlane(name=name, w=3.4, h=3.0, sx=1, sy=1)[0]
        cmds.xform(plane, ws=True, t=(x, 0.083, 6.0), ro=(0, 0, 0))
        cmds.parent(plane, groups["grp_site"])
        assign_shader(plane, planting_sg)
        create_box(name + "_thickness", 3.4, 0.167, 3.0, x, 0.0, 6.0, parent=groups["grp_site"], shader=planting_sg)

    # Sidewalk plane extending 10 ft in front of lot line
    sidewalk = cmds.polyPlane(name="site_sidewalk_plane", w=24.0, h=10.0, sx=8, sy=4)[0]
    cmds.xform(sidewalk, ws=True, t=(0.0, 0.0, 15.4), ro=(0, 0, 0))
    cmds.parent(sidewalk, groups["grp_site"])
    sidewalk_sg = create_shader("site_sidewalk_concrete", "lambert", (0.46, 0.46, 0.46))
    assign_shader(sidewalk, sidewalk_sg)


def create_facade_mass(groups, stone_sg):
    """Create 4-story massing with full-height center bay and angled faces."""
    # Main 20' wide x 52' high x 6' deep facade shell
    create_box("brownstone_main_facade_mass", 20.0, 52.0, 6.0, 0.0, 22.5, -3.0, parent=groups["grp_facade"], shader=stone_sg)

    # Full-height center bay bump-out (10' wide, +2.5' projection)
    create_box("brownstone_center_bay_core", 10.0, 52.0, 8.5, 0.0, 22.5, -1.75, parent=groups["grp_facade"], shader=stone_sg)

    # Angled side faces (~30 degrees)
    create_box("brownstone_center_bay_angled_side_left", 1.5, 52.0, 3.0, -5.65, 22.5, 1.25, parent=groups["grp_facade"], shader=stone_sg, ry=30.0)
    create_box("brownstone_center_bay_angled_side_right", 1.5, 52.0, 3.0, 5.65, 22.5, 1.25, parent=groups["grp_facade"], shader=stone_sg, ry=-30.0)

    # Quarter-round corner beads on bay corners (1 inch radius)
    bead_radius = 0.083
    for side, x in (("left", -5.0), ("right", 5.0)):
        bead = cmds.polyCylinder(name="bay_corner_bead_{0}".format(side), r=bead_radius, h=52.0, sx=14)[0]
        cmds.xform(bead, ws=True, t=(x, 22.5, 2.45), ro=(0, 0, 0))
        cmds.parent(bead, groups["grp_facade"])
        assign_shader(bead, stone_sg)


def main():
    """Build complete NYC brownstone facade in a fresh Maya scene."""
    global SHADERS

    # Required shader palette
    SHADERS = {
        "stone": create_shader("brownstone_sandstone", "lambert", (0.72, 0.55, 0.42)),
        "dark": create_shader("brownstone_dark_iron", "lambert", (0.08, 0.07, 0.07)),
        "wood": create_shader("brownstone_honey_wood", "lambert", (0.55, 0.35, 0.12)),
        "glass": create_shader("brownstone_bronze_glass", "blinn", (0.10, 0.09, 0.08), transparency=(0.35, 0.35, 0.35), reflectivity=0.25),
    }

    # Group hierarchy
    groups = create_groups()

    # Structural massing and wall articulation
    create_facade_mass(groups, SHADERS["stone"])
    create_rustication_and_joints(groups, SHADERS["stone"])
    create_belt_courses(groups, SHADERS["stone"])

    # Windows across all floors
    create_floor_windows(groups, SHADERS["stone"], SHADERS["glass"])

    # Cornice stack and ornaments
    create_cornice(groups)

    # Entry, stoop, and basement access
    create_stoop_and_entry(groups, SHADERS["stone"], SHADERS["wood"], SHADERS["glass"])

    # Site geometry
    create_site_elements(groups, SHADERS["stone"])

    print("NYC brownstone facade generated successfully.")


main()
