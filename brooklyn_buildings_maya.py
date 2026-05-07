"""Procedural Brooklyn-style apartment generators for Maya."""

try:
    import maya.cmds as cmds
except Exception as exc:  # pragma: no cover - Maya runtime only
    raise ImportError("This script must run inside Autodesk Maya.") from exc


def safe_poly(op_name, *args, **kwargs):
    """Run a poly command with warning-based error handling."""
    try:
        return getattr(cmds, op_name)(*args, **kwargs)
    except Exception as err:  # pragma: no cover - Maya runtime only
        print("Warning: {0} failed: {1}".format(op_name, err))
        return None


def safe_merge_vertices(*args, **kwargs):
    """Try both merge-vertex command names across Maya versions."""
    result = safe_poly("polyMergeVertices", *args, **kwargs)
    if result is not None:
        return result
    return safe_poly("polyMergeVertex", *args, **kwargs)


def ensure_layer(name):
    if not cmds.objExists(name):
        cmds.createDisplayLayer(name=name, empty=True)
    if cmds.attributeQuery("visibility", node=name, exists=True):
        cmds.setAttr(name + ".visibility", 1)
    return name


def make_lambert(name, color):
    shader = name + "_lambert"
    sg = shader + "SG"
    if not cmds.objExists(shader):
        shader = cmds.shadingNode("lambert", asShader=True, name=shader)
        cmds.setAttr(shader + ".color", color[0], color[1], color[2], type="double3")
    if not cmds.objExists(sg):
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
        cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
    return sg


def assign_material(node, shading_group):
    if node and cmds.objExists(node):
        cmds.sets(node, edit=True, forceElement=shading_group)


def add_window(parent, prefix, x, y, z, width, height, frame_sg, glass_sg, mullions=(2, 2), arch=False):
    frame = safe_poly("polyCube", n=prefix + "_frame", w=width, h=height, d=0.25)
    if frame:
        frame_t = frame[0]
        cmds.parent(frame_t, parent)
        cmds.move(x, y, z, frame_t, absolute=True)
        assign_material(frame_t, frame_sg)

        if arch:
            arch_piece = safe_poly("polyCylinder", n=prefix + "_arch", r=width * 0.5, h=0.2, sx=12, sy=1, sz=1)
            if arch_piece:
                arch_t = arch_piece[0]
                cmds.parent(arch_t, parent)
                cmds.rotate(90, 0, 0, arch_t, absolute=True)
                cmds.move(x, y + (height * 0.5), z + 0.05, arch_t, absolute=True)
                assign_material(arch_t, frame_sg)

    glass = safe_poly("polyPlane", n=prefix + "_glass", w=width * 0.75, h=height * 0.75, sx=1, sy=1)
    if glass:
        glass_t = glass[0]
        cmds.parent(glass_t, parent)
        cmds.rotate(0, 0, 0, glass_t, absolute=True)
        cmds.move(x, y, z + 0.08, glass_t, absolute=True)
        assign_material(glass_t, glass_sg)

    # style detail: double-hung mullion grids generated procedurally
    mx, my = mullions
    for i in range(1, mx):
        mull = safe_poly("polyCube", n="{0}_vmullion_{1}".format(prefix, i), w=0.06, h=height * 0.72, d=0.08)
        if mull:
            mt = mull[0]
            cmds.parent(mt, parent)
            offset = (float(i) / mx - 0.5) * (width * 0.72)
            cmds.move(x + offset, y, z + 0.1, mt, absolute=True)
            assign_material(mt, frame_sg)
    for j in range(1, my):
        mull = safe_poly("polyCube", n="{0}_hmullion_{1}".format(prefix, j), w=width * 0.72, h=0.06, d=0.08)
        if mull:
            mt = mull[0]
            cmds.parent(mt, parent)
            offset = (float(j) / my - 0.5) * (height * 0.72)
            cmds.move(x, y + offset, z + 0.1, mt, absolute=True)
            assign_material(mt, frame_sg)


def create_classic_building(x_offset):
    grp = cmds.group(em=True, n="building_01_classic")
    width, depth, height = 14.0, 11.0, 15.0

    brick_sg = make_lambert("b01_brick", (0.36, 0.18, 0.14))
    stone_sg = make_lambert("b01_stone", (0.48, 0.40, 0.34))
    trim_sg = make_lambert("b01_trim", (0.28, 0.20, 0.15))
    iron_sg = make_lambert("b01_iron", (0.08, 0.08, 0.1))
    glass_sg = make_lambert("b01_glass", (0.32, 0.42, 0.50))

    body = safe_poly("polyCube", n="b01_body", w=width, h=height, d=depth)
    if body:
        body_t = body[0]
        cmds.parent(body_t, grp)
        cmds.move(x_offset, height * 0.5, 0, body_t, absolute=True)
        assign_material(body_t, brick_sg)

        # style detail: rusticated stone base with horizontal scoring
        base = safe_poly("polyCube", n="b01_rusticated_base", w=width + 0.2, h=3.2, d=depth + 0.2)
        if base:
            bt = base[0]
            cmds.parent(bt, grp)
            cmds.move(x_offset, 1.6, 0.1, bt, absolute=True)
            assign_material(bt, stone_sg)
            for s in range(1, 4):
                score = safe_poly("polyCube", n="b01_base_score_{0}".format(s), w=width + 0.3, h=0.06, d=0.2)
                if score:
                    st = score[0]
                    cmds.parent(st, grp)
                    cmds.move(x_offset, 0.6 + s * 0.7, depth * 0.5 + 0.2, st, absolute=True)
                    assign_material(st, trim_sg)

    # style detail: central stoop with five steps
    for i in range(5):
        step = safe_poly("polyCube", n="b01_step_{0}".format(i + 1), w=2.8 - i * 0.25, h=0.25, d=0.8)
        if step:
            st = step[0]
            cmds.parent(st, grp)
            cmds.move(x_offset, 0.12 + i * 0.25, depth * 0.5 + 0.7 + i * 0.4, st, absolute=True)
            assign_material(st, stone_sg)

    # style detail: iron railings along stoop
    for side in (-1, 1):
        for i in range(6):
            rail = safe_poly("polyCylinder", n="b01_railing_{0}_{1}".format("l" if side < 0 else "r", i), r=0.04, h=1.0, sx=8)
            if rail:
                rt = rail[0]
                cmds.parent(rt, grp)
                cmds.move(x_offset + side * 1.4, 0.55 + i * 0.2, depth * 0.5 + 0.8 + i * 0.4, rt, absolute=True)
                assign_material(rt, iron_sg)

    # style detail: symmetric upper-floor windows (4 per row) with 2x2 mullions
    floor_y = [4.8, 7.8, 10.8, 13.6]
    x_positions = [-4.5, -1.5, 1.5, 4.5]
    for fi, y in enumerate(floor_y):
        for wi, wx in enumerate(x_positions):
            add_window(grp, "b01_win_{0}_{1}".format(fi + 1, wi + 1), x_offset + wx, y, depth * 0.5 + 0.12, 2.1, 2.2, trim_sg, glass_sg, mullions=(2, 2))
            # style detail: brownstone lintels and sills at each window
            lintel = safe_poly("polyCube", n="b01_lintel_{0}_{1}".format(fi + 1, wi + 1), w=2.3, h=0.2, d=0.3)
            sill = safe_poly("polyCube", n="b01_sill_{0}_{1}".format(fi + 1, wi + 1), w=2.3, h=0.15, d=0.35)
            if lintel:
                lt = lintel[0]
                cmds.parent(lt, grp)
                cmds.move(x_offset + wx, y + 1.2, depth * 0.5 + 0.18, lt, absolute=True)
                assign_material(lt, stone_sg)
            if sill:
                st = sill[0]
                cmds.parent(st, grp)
                cmds.move(x_offset + wx, y - 1.2, depth * 0.5 + 0.2, st, absolute=True)
                assign_material(st, stone_sg)

    # style detail: parapet with dentils and coping
    parapet = safe_poly("polyCube", n="b01_parapet", w=width + 0.6, h=1.0, d=1.2)
    if parapet:
        pt = parapet[0]
        cmds.parent(pt, grp)
        cmds.move(x_offset, height + 0.5, depth * 0.5 - 0.2, pt, absolute=True)
        assign_material(pt, stone_sg)

    for i in range(12):
        dentil = safe_poly("polyCube", n="b01_dentil_{0}".format(i + 1), w=0.4, h=0.25, d=0.35)
        if dentil:
            dt = dentil[0]
            cmds.parent(dt, grp)
            cmds.move(x_offset - width * 0.5 + 0.7 + i * 1.2, height + 0.05, depth * 0.5 + 0.25, dt, absolute=True)
            assign_material(dt, trim_sg)

    # style detail: cornice brackets repeated procedurally
    for i in range(10):
        bracket = safe_poly("polyCube", n="b01_cornice_bracket_{0}".format(i + 1), w=0.5, h=0.6, d=0.4)
        if bracket:
            bt = bracket[0]
            cmds.parent(bt, grp)
            cmds.move(x_offset - width * 0.5 + 1.0 + i * 1.3, height - 0.4, depth * 0.5 + 0.4, bt, absolute=True)
            assign_material(bt, trim_sg)

    return grp


def create_italianate_building(x_offset):
    grp = cmds.group(em=True, n="building_02_italianate")
    width, depth, height = 13.0, 10.5, 17.0

    brick_sg = make_lambert("b02_brick", (0.40, 0.20, 0.14))
    stone_sg = make_lambert("b02_stone", (0.56, 0.50, 0.43))
    trim_sg = make_lambert("b02_trim", (0.34, 0.28, 0.20))
    roof_sg = make_lambert("b02_roof", (0.16, 0.14, 0.12))
    glass_sg = make_lambert("b02_glass", (0.25, 0.35, 0.45))

    body = safe_poly("polyCube", n="b02_body", w=width, h=height, d=depth)
    if body:
        bt = body[0]
        cmds.parent(bt, grp)
        cmds.move(x_offset, height * 0.5, 0, bt, absolute=True)
        assign_material(bt, brick_sg)

    # style detail: scored rustication on ground floor
    rustication = safe_poly("polyCube", n="b02_rustication", w=width + 0.2, h=3.0, d=depth + 0.2)
    if rustication:
        rt = rustication[0]
        cmds.parent(rt, grp)
        cmds.move(x_offset, 1.5, 0.1, rt, absolute=True)
        assign_material(rt, stone_sg)
        for s in range(4):
            line = safe_poly("polyCube", n="b02_score_{0}".format(s + 1), w=width + 0.4, h=0.05, d=0.2)
            if line:
                lt = line[0]
                cmds.parent(lt, grp)
                cmds.move(x_offset, 0.5 + s * 0.65, depth * 0.5 + 0.2, lt, absolute=True)
                assign_material(lt, trim_sg)

    # style detail: stringcourses between floors
    for i in range(1, 5):
        course = safe_poly("polyCube", n="b02_stringcourse_{0}".format(i), w=width + 0.5, h=0.2, d=0.5)
        if course:
            ct = course[0]
            cmds.parent(ct, grp)
            cmds.move(x_offset, 3.0 + i * 2.7, depth * 0.5 + 0.2, ct, absolute=True)
            assign_material(ct, trim_sg)

    # style detail: tall narrow windows with molded/arched tops
    x_positions = [-3.8, -1.2, 1.2, 3.8]
    for floor in range(5):
        y = 3.8 + floor * 2.5
        for wi, wx in enumerate(x_positions):
            add_window(grp, "b02_win_{0}_{1}".format(floor + 1, wi + 1), x_offset + wx, y, depth * 0.5 + 0.12, 1.5, 2.4, trim_sg, glass_sg, mullions=(1, 2), arch=True)

    # style detail: segmental arches above second-floor windows
    for wi, wx in enumerate(x_positions):
        seg = safe_poly("polyCylinder", n="b02_segmental_arch_{0}".format(wi + 1), r=0.9, h=0.2, sx=12)
        if seg:
            st = seg[0]
            cmds.parent(st, grp)
            cmds.rotate(90, 0, 0, st, absolute=True)
            cmds.move(x_offset + wx, 6.8, depth * 0.5 + 0.18, st, absolute=True)
            assign_material(st, stone_sg)

    # style detail: projecting three-facet bay window at left with 30-degree side facets
    bay_center = safe_poly("polyCube", n="b02_bay_center", w=2.2, h=7.5, d=1.6)
    if bay_center:
        bct = bay_center[0]
        cmds.parent(bct, grp)
        cmds.move(x_offset - 5.0, 6.0, depth * 0.5 + 0.8, bct, absolute=True)
        assign_material(bct, stone_sg)
    for side, rot in ((-1, -30), (1, 30)):
        facet = safe_poly("polyCube", n="b02_bay_facet_{0}".format("l" if side < 0 else "r"), w=1.2, h=7.5, d=1.2)
        if facet:
            ft = facet[0]
            cmds.parent(ft, grp)
            cmds.rotate(0, rot, 0, ft, absolute=True)
            cmds.move(x_offset - 5.0 + side * 1.15, 6.0, depth * 0.5 + 0.35, ft, absolute=True)
            assign_material(ft, stone_sg)

    # style detail: heavy decorative cornice with paired brackets
    cornice = safe_poly("polyCube", n="b02_cornice", w=width + 1.0, h=0.9, d=1.5)
    if cornice:
        ct = cornice[0]
        cmds.parent(ct, grp)
        cmds.move(x_offset, height - 0.3, depth * 0.5 + 0.4, ct, absolute=True)
        assign_material(ct, trim_sg)
    for i in range(6):
        for pair in (0, 0.35):
            br = safe_poly("polyCube", n="b02_bracket_{0}_{1}".format(i + 1, int(pair * 100)), w=0.25, h=0.7, d=0.35)
            if br:
                bt = br[0]
                cmds.parent(bt, grp)
                cmds.move(x_offset - width * 0.5 + 1.2 + i * 2.0 + pair, height - 0.7, depth * 0.5 + 0.7, bt, absolute=True)
                assign_material(bt, trim_sg)

    # style detail: overhanging eaves via roofline extrusion
    roof = safe_poly("polyCube", n="b02_eaves", w=width + 1.4, h=0.4, d=depth + 1.4)
    if roof:
        rt = roof[0]
        cmds.parent(rt, grp)
        cmds.move(x_offset, height + 0.2, 0, rt, absolute=True)
        assign_material(rt, roof_sg)
        safe_poly("polyExtrude", rt + ".f[1]", ltz=0.2)

    return grp


def create_romanesque_building(x_offset):
    grp = cmds.group(em=True, n="building_03_romanesque")
    width, depth, height = 17.0, 12.0, 13.0

    stone_sg = make_lambert("b03_stone", (0.44, 0.38, 0.30))
    trim_sg = make_lambert("b03_trim", (0.34, 0.28, 0.22))
    roof_sg = make_lambert("b03_roof", (0.15, 0.13, 0.1))
    glass_sg = make_lambert("b03_glass", (0.28, 0.36, 0.46))

    body = safe_poly("polyCube", n="b03_body", w=width, h=height, d=depth)
    if body:
        bt = body[0]
        cmds.parent(bt, grp)
        cmds.move(x_offset, height * 0.5, 0, bt, absolute=True)
        assign_material(bt, stone_sg)

    # style detail: round-arched entrance
    doorway = safe_poly("polyCube", n="b03_door_block", w=3.0, h=3.6, d=0.8)
    arch = safe_poly("polyCylinder", n="b03_door_arch", r=1.5, h=0.8, sx=16)
    if doorway:
        dt = doorway[0]
        cmds.parent(dt, grp)
        cmds.move(x_offset, 1.8, depth * 0.5 + 0.3, dt, absolute=True)
        assign_material(dt, trim_sg)
    if arch:
        at = arch[0]
        cmds.parent(at, grp)
        cmds.rotate(90, 0, 0, at, absolute=True)
        cmds.move(x_offset, 3.6, depth * 0.5 + 0.3, at, absolute=True)
        assign_material(at, trim_sg)

    # style detail: rock-faced corner and portal stones
    for cx in (-width * 0.5 + 0.6, width * 0.5 - 0.6):
        for cy in range(6):
            rock = safe_poly("polyCube", n="b03_rock_{0}_{1}".format("l" if cx < 0 else "r", cy), w=0.8, h=0.8, d=0.8)
            if rock:
                rt = rock[0]
                cmds.parent(rt, grp)
                cmds.move(x_offset + cx, 0.5 + cy * 0.9, depth * 0.5 + 0.2, rt, absolute=True)
                assign_material(rt, trim_sg)
                safe_poly("polyBevel", rt + ".e[*]", offset=0.03, segments=1)

    # style detail: windows with recessed panels below
    x_positions = [-5.2, -1.7, 1.7, 5.2]
    for floor in range(3):
        y = 5.0 + floor * 2.7
        for wi, wx in enumerate(x_positions):
            add_window(grp, "b03_win_{0}_{1}".format(floor + 1, wi + 1), x_offset + wx, y, depth * 0.5 + 0.14, 2.0, 1.8, trim_sg, glass_sg, mullions=(2, 1))
            panel = safe_poly("polyCube", n="b03_panel_{0}_{1}".format(floor + 1, wi + 1), w=1.7, h=0.7, d=0.2)
            if panel:
                pt = panel[0]
                cmds.parent(pt, grp)
                cmds.move(x_offset + wx, y - 1.25, depth * 0.5 + 0.18, pt, absolute=True)
                assign_material(pt, trim_sg)

    # style detail: belly band between floors 1 and 2
    belly = safe_poly("polyCube", n="b03_belly_band", w=width + 0.6, h=0.5, d=0.7)
    if belly:
        bt = belly[0]
        cmds.parent(bt, grp)
        cmds.move(x_offset, 6.2, depth * 0.5 + 0.18, bt, absolute=True)
        assign_material(bt, trim_sg)

    # style detail: carved capitals on entrance columns using three-tier extrusions
    for side in (-1, 1):
        col = safe_poly("polyCylinder", n="b03_column_{0}".format("l" if side < 0 else "r"), r=0.22, h=2.8, sx=8)
        if col:
            ct = col[0]
            cmds.parent(ct, grp)
            cmds.move(x_offset + side * 1.9, 1.4, depth * 0.5 + 0.45, ct, absolute=True)
            assign_material(ct, trim_sg)
            for tier in range(3):
                cap = safe_poly("polyCube", n="b03_capital_{0}_{1}".format("l" if side < 0 else "r", tier), w=0.5 + tier * 0.08, h=0.12, d=0.5 + tier * 0.08)
                if cap:
                    cpt = cap[0]
                    cmds.parent(cpt, grp)
                    cmds.move(x_offset + side * 1.9, 2.8 + tier * 0.12, depth * 0.5 + 0.45, cpt, absolute=True)
                    assign_material(cpt, trim_sg)

    # style detail: octagonal corner turret with conical roof
    turret = safe_poly("polyCylinder", n="b03_turret", r=1.4, h=5.0, sx=8)
    if turret:
        tt = turret[0]
        cmds.parent(tt, grp)
        cmds.move(x_offset + width * 0.5 - 1.5, height - 1.5, depth * 0.5 - 1.8, tt, absolute=True)
        assign_material(tt, stone_sg)
    roof = safe_poly("polyCylinder", n="b03_turret_roof", r=1.6, h=2.2, sx=8, sz=1)
    if roof:
        rt = roof[0]
        cmds.parent(rt, grp)
        cmds.move(x_offset + width * 0.5 - 1.5, height + 1.6, depth * 0.5 - 1.8, rt, absolute=True)
        cmds.scale(1.0, 1.0, 1.0, rt)
        safe_poly("polyExtrude", rt + ".f[9]", sx=0.01, sz=0.01)
        assign_material(rt, roof_sg)

    # style detail: corbelled cornice with toothed brick pattern
    for i in range(20):
        tooth = safe_poly("polyCube", n="b03_corbel_{0}".format(i + 1), w=0.5, h=0.35, d=0.45)
        if tooth:
            tt = tooth[0]
            cmds.parent(tt, grp)
            cmds.move(x_offset - width * 0.5 + 0.5 + i * 0.85, height - 0.2, depth * 0.5 + 0.35, tt, absolute=True)
            assign_material(tt, trim_sg)

    return grp


def create_neogrec_building(x_offset):
    grp = cmds.group(em=True, n="building_04_neogrec")
    width, depth, height = 15.0, 11.0, 14.5

    stone_sg = make_lambert("b04_stone", (0.52, 0.47, 0.39))
    trim_sg = make_lambert("b04_trim", (0.30, 0.26, 0.20))
    roof_sg = make_lambert("b04_roof", (0.16, 0.16, 0.18))
    glass_sg = make_lambert("b04_glass", (0.25, 0.33, 0.42))

    body = safe_poly("polyCube", n="b04_body", w=width, h=height, d=depth)
    if body:
        bt = body[0]
        cmds.parent(bt, grp)
        cmds.move(x_offset, height * 0.5, 0, bt, absolute=True)
        assign_material(bt, stone_sg)

    # style detail: flat roof with prominent projecting cornice
    cornice = safe_poly("polyCube", n="b04_cornice", w=width + 1.4, h=0.8, d=1.7)
    if cornice:
        ct = cornice[0]
        cmds.parent(ct, grp)
        cmds.move(x_offset, height - 0.2, depth * 0.5 + 0.4, ct, absolute=True)
        assign_material(ct, trim_sg)

    # style detail: frieze with triglyph-like notches every 0.5m
    triglyph_spacing = 0.5
    frieze_padding = 1.0
    notch_count = int((width + frieze_padding) / triglyph_spacing)
    for i in range(notch_count):
        notch = safe_poly("polyCube", n="b04_triglyph_notch_{0}".format(i + 1), w=0.12, h=0.25, d=0.2)
        if notch:
            nt = notch[0]
            cmds.parent(nt, grp)
            cmds.move(x_offset - width * 0.5 + 0.2 + i * triglyph_spacing, height - 0.25, depth * 0.5 + 0.95, nt, absolute=True)
            assign_material(nt, roof_sg)

    # style detail: fluted entrance columns using 8-sided cylinders and vertical cuts
    for side in (-1, 1):
        col = safe_poly("polyCylinder", n="b04_column_{0}".format("l" if side < 0 else "r"), r=0.16, h=3.2, sx=8)
        if col:
            ct = col[0]
            cmds.parent(ct, grp)
            cmds.move(x_offset + side * 1.6, 1.6, depth * 0.5 + 0.4, ct, absolute=True)
            assign_material(ct, trim_sg)
            for f in range(4):
                groove = safe_poly("polyCube", n="b04_flute_{0}_{1}".format("l" if side < 0 else "r", f), w=0.04, h=2.6, d=0.05)
                if groove:
                    gt = groove[0]
                    cmds.parent(gt, grp)
                    cmds.move(x_offset + side * 1.6 + (f - 1.5) * 0.05, 1.6, depth * 0.5 + 0.55, gt, absolute=True)
                    assign_material(gt, roof_sg)

    # style detail: deeply set windows in 3-4-3 arrangement (center trio narrower)
    rows = [4.3, 7.0, 9.7, 12.2]
    arrangement = [(-4.9, 1.8), (-2.6, 1.3), (-0.9, 1.3), (0.9, 1.3), (2.6, 1.3), (4.9, 1.8)]
    for ri, y in enumerate(rows):
        for wi, (wx, w) in enumerate(arrangement):
            add_window(grp, "b04_win_{0}_{1}".format(ri + 1, wi + 1), x_offset + wx, y, depth * 0.5 + 0.1, w, 1.8, trim_sg, glass_sg, mullions=(2, 2))
            recess = safe_poly("polyCube", n="b04_recess_{0}_{1}".format(ri + 1, wi + 1), w=w + 0.2, h=2.0, d=0.18)
            if recess:
                rt = recess[0]
                cmds.parent(rt, grp)
                cmds.move(x_offset + wx, y, depth * 0.5 + 0.02, rt, absolute=True)
                assign_material(rt, roof_sg)
                safe_poly("polyExtrude", rt + ".f[1]", ltz=-0.08)

            # style detail: incised geometric lintel decoration
            lintel = safe_poly("polyCube", n="b04_lintel_{0}_{1}".format(ri + 1, wi + 1), w=w + 0.35, h=0.26, d=0.18)
            if lintel:
                lt = lintel[0]
                cmds.parent(lt, grp)
                cmds.move(x_offset + wx, y + 1.05, depth * 0.5 + 0.18, lt, absolute=True)
                assign_material(lt, trim_sg)
                safe_poly("polyExtrude", lt + ".f[1]", ltz=-0.05)

    # style detail: paneled spandrels with inset bevel
    for ri in range(3):
        y = 5.65 + ri * 2.7
        for pi, px in enumerate([-5.0, -2.6, -0.8, 0.8, 2.6, 5.0]):
            panel = safe_poly("polyCube", n="b04_spandrel_{0}_{1}".format(ri + 1, pi + 1), w=1.5, h=0.6, d=0.15)
            if panel:
                pt = panel[0]
                cmds.parent(pt, grp)
                cmds.move(x_offset + px, y, depth * 0.5 + 0.16, pt, absolute=True)
                assign_material(pt, trim_sg)
                safe_poly("polyBevel", pt + ".e[*]", offset=0.01, segments=1)

    return grp


def create_queenanne_building(x_offset):
    grp = cmds.group(em=True, n="building_05_queenanne")
    width, depth, height = 16.0, 12.0, 13.5

    brick_sg = make_lambert("b05_brick", (0.42, 0.2, 0.16))
    wood_sg = make_lambert("b05_wood", (0.56, 0.44, 0.30))
    trim_sg = make_lambert("b05_trim", (0.70, 0.65, 0.58))
    roof_sg = make_lambert("b05_roof", (0.20, 0.18, 0.16))
    glass_blue = make_lambert("b05_glass_blue", (0.20, 0.30, 0.60))
    glass_red = make_lambert("b05_glass_red", (0.55, 0.20, 0.20))
    glass_green = make_lambert("b05_glass_green", (0.20, 0.50, 0.30))

    body = safe_poly("polyCube", n="b05_body", w=width, h=height, d=depth)
    if body:
        bt = body[0]
        cmds.parent(bt, grp)
        cmds.move(x_offset, height * 0.5, 0, bt, absolute=True)
        assign_material(bt, brick_sg)

    # style detail: horizontal wood siding band on upper floors
    siding = safe_poly("polyCube", n="b05_siding_band", w=width + 0.2, h=4.4, d=depth + 0.2)
    if siding:
        st = siding[0]
        cmds.parent(st, grp)
        cmds.move(x_offset, 10.8, 0, st, absolute=True)
        assign_material(st, wood_sg)
        for i in range(8):
            seam = safe_poly("polyCube", n="b05_siding_seam_{0}".format(i + 1), w=width + 0.3, h=0.04, d=0.2)
            if seam:
                sm = seam[0]
                cmds.parent(sm, grp)
                cmds.move(x_offset, 8.8 + i * 0.5, depth * 0.5 + 0.12, sm, absolute=True)
                assign_material(sm, trim_sg)

    # style detail: corner tower with pyramidal roof and finial
    tower = safe_poly("polyCylinder", n="b05_tower", r=1.8, h=9.0, sx=8)
    if tower:
        tt = tower[0]
        cmds.parent(tt, grp)
        cmds.move(x_offset + width * 0.5 - 2.0, 8.0, depth * 0.5 - 2.2, tt, absolute=True)
        assign_material(tt, wood_sg)
    pyr = safe_poly("polyCylinder", n="b05_tower_pyramid", r=2.0, h=2.8, sx=4)
    if pyr:
        pt = pyr[0]
        cmds.parent(pt, grp)
        cmds.rotate(0, 45, 0, pt, absolute=True)
        cmds.move(x_offset + width * 0.5 - 2.0, 13.0, depth * 0.5 - 2.2, pt, absolute=True)
        safe_poly("polyExtrude", pt + ".f[5]", sx=0.01, sz=0.01)
        assign_material(pt, roof_sg)
    finial = safe_poly("polyCylinder", n="b05_finial", r=0.08, h=0.8, sx=8)
    if finial:
        ft = finial[0]
        cmds.parent(ft, grp)
        cmds.move(x_offset + width * 0.5 - 2.0, 14.8, depth * 0.5 - 2.2, ft, absolute=True)
        assign_material(ft, trim_sg)

    # style detail: stained-glass 3x3 central window with varied colored panes
    pane_colors = [glass_blue, glass_red, glass_green]
    for row in range(3):
        for col in range(3):
            pane = safe_poly("polyPlane", n="b05_stained_pane_{0}_{1}".format(row + 1, col + 1), w=0.5, h=0.5, sx=1, sy=1)
            if pane:
                pt = pane[0]
                cmds.parent(pt, grp)
                cmds.move(x_offset - 1.5 + col * 0.55, 8.6 - row * 0.55, depth * 0.5 + 0.15, pt, absolute=True)
                assign_material(pt, pane_colors[(row + col) % len(pane_colors)])

    # style detail: fish-scale shingles on upper gable using overlapping cylinders
    for row in range(5):
        for col in range(7 - row):
            shingle = safe_poly("polyCylinder", n="b05_shingle_{0}_{1}".format(row + 1, col + 1), r=0.22, h=0.08, sx=10)
            if shingle:
                st = shingle[0]
                cmds.parent(st, grp)
                cmds.rotate(90, 0, 0, st, absolute=True)
                x_pos = x_offset - 3.0 + col * 0.55 + row * 0.27
                y_pos = 11.2 + row * 0.35
                cmds.move(x_pos, y_pos, depth * 0.5 + 0.3, st, absolute=True)
                assign_material(st, roof_sg)

    # style detail: wrap-around porch with columns on front and side, plus angled roof
    porch = safe_poly("polyCube", n="b05_porch_deck", w=7.0, h=0.3, d=3.8)
    if porch:
        pt = porch[0]
        cmds.parent(pt, grp)
        cmds.move(x_offset - 1.6, 0.2, depth * 0.5 + 1.3, pt, absolute=True)
        assign_material(pt, wood_sg)

    for side in range(2):
        side_x = x_offset - 4.8 if side == 0 else x_offset + 1.4
        for i in range(4):
            col = safe_poly("polyCylinder", n="b05_porch_col_{0}_{1}".format(side + 1, i + 1), r=0.11, h=2.5, sx=8)
            if col:
                ct = col[0]
                cmds.parent(ct, grp)
                z_pos = depth * 0.5 + (0.1 + i * 1.0)
                cmds.move(side_x, 1.4, z_pos, ct, absolute=True)
                assign_material(ct, trim_sg)

    porch_roof = safe_poly("polyCube", n="b05_porch_roof", w=7.2, h=0.25, d=4.0)
    if porch_roof:
        prt = porch_roof[0]
        cmds.parent(prt, grp)
        cmds.rotate(-12, 0, 0, prt, absolute=True)
        cmds.move(x_offset - 1.6, 3.0, depth * 0.5 + 1.0, prt, absolute=True)
        assign_material(prt, roof_sg)

    # style detail: round oculus in gable apex
    oculus = safe_poly("polyCylinder", n="b05_oculus", r=0.65, h=0.18, sx=16)
    if oculus:
        ot = oculus[0]
        cmds.parent(ot, grp)
        cmds.rotate(90, 0, 0, ot, absolute=True)
        cmds.move(x_offset + 3.4, 12.4, depth * 0.5 + 0.2, ot, absolute=True)
        assign_material(ot, trim_sg)

    # style detail: ornamental spindle/fretwork grid under eaves
    for i in range(12):
        spindle = safe_poly("polyCylinder", n="b05_spindle_{0}".format(i + 1), r=0.05, h=0.7, sx=8)
        if spindle:
            st = spindle[0]
            cmds.parent(st, grp)
            cmds.move(x_offset - width * 0.5 + 1.0 + i * 1.2, height - 0.6, depth * 0.5 + 0.7, st, absolute=True)
            assign_material(st, trim_sg)

    return grp


def create_environment():
    # style detail: sidewalk grid plane spanning all buildings
    sidewalk = safe_poly("polyPlane", n="city_sidewalk", w=110, h=24, sx=44, sy=12)
    if sidewalk:
        st = sidewalk[0]
        cmds.move(40, 0, 0, st, absolute=True)
        cmds.rotate(-90, 0, 0, st, absolute=True)
        safe_merge_vertices(st + ".vtx[*]", d=0.0001)
        side_sg = make_lambert("env_sidewalk", (0.45, 0.45, 0.45))
        assign_material(st, side_sg)

    curb = safe_poly("polyCube", n="street_curb", w=110, h=0.35, d=0.9)
    if curb:
        ct = curb[0]
        cmds.move(40, 0.18, 8.6, ct, absolute=True)
        curb_sg = make_lambert("env_curb", (0.36, 0.36, 0.38))
        assign_material(ct, curb_sg)

    return [sidewalk[0] if sidewalk else None, curb[0] if curb else None]


def main():
    ensure_layer("lgt_buildings")
    ensure_layer("lgt_collision")

    builders = [
        create_classic_building,
        create_italianate_building,
        create_romanesque_building,
        create_neogrec_building,
        create_queenanne_building,
    ]

    groups = []
    for i, builder in enumerate(builders):
        x_pos = i * 20.0
        grp = builder(x_pos)
        groups.append(grp)

    env_nodes = create_environment()

    for grp in groups:
        if grp and cmds.objExists(grp):
            cmds.editDisplayLayerMembers("lgt_buildings", grp, noRecurse=False)

    for node in env_nodes:
        if node and cmds.objExists(node):
            cmds.editDisplayLayerMembers("lgt_collision", node, noRecurse=False)

    print("Building generation complete: 5 Brooklyn-style brownstones created.")


if __name__ == "__main__":
    main()
