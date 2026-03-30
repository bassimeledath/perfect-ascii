#!/usr/bin/env python3
"""ascii-render: pixel-perfect ASCII diagram renderer.

Reads JSON from stdin, writes ASCII to stdout.
Four modes: diagram, table, layers, sequence.
"""

import json
import sys

MAX_WIDTH = 78

# ---------------------------------------------------------------------------
# Character grid
# ---------------------------------------------------------------------------

class Grid:
    """2D character grid that grows as needed."""

    def __init__(self):
        self.rows = []  # list of list of chars

    def ensure(self, r, c):
        while len(self.rows) <= r:
            self.rows.append([])
        while len(self.rows[r]) <= c:
            self.rows[r].append(' ')

    def put(self, r, c, ch):
        if c < 0 or r < 0:
            return
        self.ensure(r, c)
        self.rows[r][c] = ch

    def put_str(self, r, c, s):
        for i, ch in enumerate(s):
            self.put(r, c + i, ch)

    def render(self):
        lines = []
        for row in self.rows:
            line = ''.join(row).rstrip()
            lines.append(line)
        # Strip trailing empty lines
        while lines and lines[-1] == '':
            lines.pop()
        return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Box renderer
# ---------------------------------------------------------------------------

def draw_box(grid, top, left, width, label, body=None):
    """Draw a box onto the grid.

    width includes the border chars (minimum 2 for +...+).
    """
    inner = width - 2  # space between | and |

    # Top border
    grid.put(top, left, '+')
    for c in range(1, width - 1):
        grid.put(top, left + c, '-')
    grid.put(top, left + width - 1, '+')

    # Label row (centered)
    r = top + 1
    pad_total = inner - len(label)
    pad_left = pad_total // 2
    grid.put(r, left, '|')
    grid.put_str(r, left + 1, ' ' * pad_left + label + ' ' * (inner - pad_left - len(label)))
    grid.put(r, left + width - 1, '|')

    next_row = top + 2

    if body is not None:
        # Separator
        grid.put(next_row, left, '+')
        for c in range(1, width - 1):
            grid.put(next_row, left + c, '-')
        grid.put(next_row, left + width - 1, '+')
        next_row += 1

        # Body lines (left-aligned)
        for line in body:
            grid.put(next_row, left, '|')
            text = ' ' + line
            text = text + ' ' * (inner - len(text))
            grid.put_str(next_row, left + 1, text)
            grid.put(next_row, left + width - 1, '|')
            next_row += 1

    # Bottom border
    grid.put(next_row, left, '+')
    for c in range(1, width - 1):
        grid.put(next_row, left + c, '-')
    grid.put(next_row, left + width - 1, '+')


def box_height(label, body=None):
    """Compute the height of a box including borders."""
    h = 3  # top border + label + bottom border
    if body:
        h += 1 + len(body)  # separator + body lines
    return h


def box_min_width(label, body=None):
    """Compute the minimum width of a box including borders."""
    max_content = len(label)
    if body:
        for line in body:
            max_content = max(max_content, len(line))
    return max_content + 4  # | + space + content + space + |


# ---------------------------------------------------------------------------
# Collision detection helpers for connector routing
# ---------------------------------------------------------------------------

def _v_seg_blocked(box_positions, col, r1, r2, exclude):
    """True if vertical line at col from r1..r2 intersects any box."""
    top, bot = min(r1, r2), max(r1, r2)
    for bid, (bt, bl, bw, bh) in box_positions.items():
        if bid in exclude:
            continue
        if bl <= col < bl + bw and top < bt + bh and bot >= bt:
            return True
    return False


def _h_seg_blocked(box_positions, row, c1, c2, exclude):
    """True if horizontal line at row from c1..c2 intersects any box."""
    left, right = min(c1, c2), max(c1, c2)
    for bid, (bt, bl, bw, bh) in box_positions.items():
        if bid in exclude:
            continue
        if bt <= row < bt + bh and left < bl + bw and right >= bl:
            return True
    return False


def _find_clear_col(box_positions, r1, r2, preferred, exclude):
    """Find column near preferred that's clear for vertical travel r1..r2."""
    if not _v_seg_blocked(box_positions, preferred, r1, r2, exclude):
        return preferred
    for offset in range(1, MAX_WIDTH):
        for col in (preferred + offset, preferred - offset):
            if 0 <= col < MAX_WIDTH and not _v_seg_blocked(box_positions, col, r1, r2, exclude):
                return col
    return preferred


# ---------------------------------------------------------------------------
# Diagram mode
# ---------------------------------------------------------------------------

def render_diagram(data):
    title = data.get('title', '')
    boxes_list = data.get('boxes', [])
    grid_layout = data.get('grid', [])
    connectors = data.get('connectors', [])
    lanes = data.get('lanes', [])

    # Compute lane label margin
    lane_margin = 0
    if lanes:
        max_lane_len = max((len(l) for l in lanes), default=0)
        if max_lane_len > 0:
            lane_margin = max_lane_len + 3  # "label | "

    # Build box lookup
    box_map = {}
    for b in boxes_list:
        box_map[b['id']] = b

    # Determine grid dimensions
    num_rows = len(grid_layout)
    num_cols = max((len(row) for row in grid_layout), default=0)

    # Normalize grid rows to same length
    for row in grid_layout:
        while len(row) < num_cols:
            row.append(None)

    # Compute column widths and row heights
    col_widths = [0] * num_cols
    row_heights = [0] * num_rows
    col_spacing = 3
    row_spacing = 2

    for ri, row in enumerate(grid_layout):
        for ci, cell in enumerate(row):
            if cell and cell in box_map:
                b = box_map[cell]
                bw = box_min_width(b['label'], b.get('body'))
                bh = box_height(b['label'], b.get('body'))
                col_widths[ci] = max(col_widths[ci], bw)
                row_heights[ri] = max(row_heights[ri], bh)

    # Ensure minimum sizes
    for ci in range(num_cols):
        if col_widths[ci] == 0:
            col_widths[ci] = 6
    for ri in range(num_rows):
        if row_heights[ri] == 0:
            row_heights[ri] = 3

    # Check width and reduce spacing if needed
    total_w = sum(col_widths) + col_spacing * (num_cols - 1) if num_cols > 1 else sum(col_widths)
    if total_w + lane_margin > MAX_WIDTH and col_spacing > 1:
        col_spacing = 1
        total_w = sum(col_widths) + col_spacing * (num_cols - 1) if num_cols > 1 else sum(col_widths)

    # Compute positions
    x_positions = []  # left x for each column
    x = lane_margin
    for ci in range(num_cols):
        x_positions.append(x)
        x += col_widths[ci] + col_spacing

    y_positions = []  # top y for each row
    y = 0
    if title:
        y = 2  # leave room for title
    for ri in range(num_rows):
        y_positions.append(y)
        y += row_heights[ri] + row_spacing

    # Draw
    g = Grid()

    # Title
    if title:
        g.put_str(0, lane_margin, title)

    # Record box positions for connector routing
    box_positions = {}  # id -> (top, left, width, height)

    for ri, row in enumerate(grid_layout):
        for ci, cell in enumerate(row):
            if cell and cell in box_map:
                b = box_map[cell]
                bw = box_min_width(b['label'], b.get('body'))
                bh = box_height(b['label'], b.get('body'))
                # Center the box within its grid cell
                cell_w = col_widths[ci]
                offset_x = (cell_w - bw) // 2
                bx = x_positions[ci] + offset_x
                by = y_positions[ri]
                draw_box(g, by, bx, bw, b['label'], b.get('body'))
                box_positions[cell] = (by, bx, bw, bh)

    # Draw lane labels
    if lanes:
        max_ll = max((len(l) for l in lanes), default=0)
        for ri in range(num_rows):
            if ri < len(lanes) and lanes[ri]:
                label_y = y_positions[ri] + row_heights[ri] // 2
                g.put_str(label_y, 0, lanes[ri].rjust(max_ll))
                g.put_str(label_y, max_ll + 1, '|')

    # Draw connectors (lines first, then labels on top)
    used_label_extents = set()
    deferred_labels = []
    for conn in connectors:
        from_id = conn['from']
        to_id = conn['to']
        label = conn.get('label', '')

        if from_id not in box_positions or to_id not in box_positions:
            continue

        draw_connector(g, box_positions, from_id, to_id, label, grid_layout,
                       used_label_extents, deferred_labels)

    for lr, lc, ltext in deferred_labels:
        g.put_str(lr, lc, ltext)

    return g.render()


def find_grid_pos(grid_layout, box_id):
    """Find the (row, col) of a box in the grid."""
    for ri, row in enumerate(grid_layout):
        for ci, cell in enumerate(row):
            if cell == box_id:
                return (ri, ci)
    return None


def draw_connector(g, box_positions, from_id, to_id, label, grid_layout,
                   used_label_extents=None, deferred_labels=None):
    """Draw a connector between two boxes, routing around obstacles."""
    from_pos = box_positions[from_id]
    to_pos = box_positions[to_id]

    from_grid = find_grid_pos(grid_layout, from_id)
    to_grid = find_grid_pos(grid_layout, to_id)

    if from_grid is None or to_grid is None:
        return

    from_gr, from_gc = from_grid
    to_gr, to_gc = to_grid

    ft, fl, fw, fh = from_pos
    tt, tl, tw, th = to_pos
    exclude = {from_id, to_id}

    def place_label(r, c, text):
        if not text:
            return

        def is_clear(lr, lc, length):
            # Check against other label extents
            if used_label_extents is not None:
                for (er, ec_start, ec_end) in used_label_extents:
                    if lr == er and lc < ec_end and lc + length > ec_start:
                        return False
            # Check against box positions
            for bid, (bt, bl, bw, bh) in box_positions.items():
                if bt <= lr < bt + bh and lc < bl + bw and lc + length > bl:
                    return False
            return True

        # Try original position, then nearby alternates
        candidates = [
            (r, c),
            (r, c + 1),
            (r, c + 2),
            (r - 1, c),
            (r + 1, c),
            (r, c - len(text) - 1),
            (r, c - len(text) - 2),
            (r - 1, c + 2),
            (r + 1, c + 2),
            (r - 2, c),
            (r + 2, c),
            (r - 1, c - len(text) - 1),
            (r + 1, c - len(text) - 1),
        ]
        placed = False
        for cr, cc in candidates:
            if cr >= 0 and cc >= 0 and is_clear(cr, cc, len(text)):
                r, c = cr, cc
                placed = True
                break

        if not placed:
            return  # Skip label rather than overwrite boxes

        if used_label_extents is not None:
            used_label_extents.add((r, c, c + len(text)))
        if deferred_labels is not None:
            deferred_labels.append((r, c, text))
        else:
            g.put_str(r, c, text)

    if from_gc == to_gc:
        # Same column - vertical connector
        going_down = to_gr > from_gr

        if going_down:
            start_r = ft + fh
            end_r = tt - 1
            col = fl + fw // 2
        else:
            start_r = tt + th
            end_r = ft - 1
            col = fl + fw // 2

        if not _v_seg_blocked(box_positions, col, start_r, end_r, exclude):
            # Straight vertical line - path is clear
            for r in range(start_r, end_r + 1):
                g.put(r, col, '|')
            if going_down:
                g.put(end_r, col, 'v')
            else:
                g.put(start_r, col, '^')
            if label:
                place_label(start_r + (end_r - start_r) // 2, col + 2, label)
        else:
            # Route around obstacles via detour column
            top_gr = min(from_gr, to_gr)
            bot_gr = max(from_gr, to_gr)

            all_obs = []
            for ri in range(top_gr + 1, bot_gr):
                for ci in range(len(grid_layout[ri])):
                    cell = grid_layout[ri][ci]
                    if cell and cell in box_positions and cell not in exclude:
                        all_obs.append(box_positions[cell])

            # Also check pixel-level collisions for non-grid-aligned boxes
            if not all_obs:
                for bid, bpos in box_positions.items():
                    if bid not in exclude:
                        bt, bl, bw, bh = bpos
                        if bl <= col < bl + bw and start_r < bt + bh and end_r >= bt:
                            all_obs.append(bpos)

            if not all_obs:
                # Fallback: draw straight
                for r in range(start_r, end_r + 1):
                    g.put(r, col, '|')
                if going_down:
                    g.put(end_r, col, 'v')
                else:
                    g.put(start_r, col, '^')
            else:
                # Work top-to-bottom regardless of direction
                if going_down:
                    src_t, src_l, src_w, src_h = ft, fl, fw, fh
                    dst_t, dst_l, dst_w, dst_h = tt, tl, tw, th
                else:
                    src_t, src_l, src_w, src_h = tt, tl, tw, th
                    dst_t, dst_l, dst_w, dst_h = ft, fl, fw, fh

                src_center = src_l + src_w // 2
                dst_center = dst_l + dst_w // 2

                exit_r = src_t + src_h
                first_obs_top = min(it for it, _, _, _ in all_obs)
                turn1_r = max(exit_r, first_obs_top - 1)

                last_obs_bottom = max(it + ih for it, _, _, ih in all_obs)
                entry_r = dst_t - 1
                turn2_r = min(entry_r, last_obs_bottom)

                # Find a clear detour column (verified against ALL boxes)
                max_right = max(il + iw for _, il, iw, _ in all_obs)
                min_left = min(il for _, il, _, _ in all_obs)
                preferred = max_right + 2
                detour_col = _find_clear_col(box_positions, turn1_r, turn2_r,
                                             preferred, exclude)
                if detour_col >= MAX_WIDTH:
                    detour_col = _find_clear_col(box_positions, turn1_r, turn2_r,
                                                 min_left - 3, exclude)

                # Segment 1: vertical from source
                for r in range(exit_r, turn1_r):
                    g.put(r, src_center, '|')

                # Segment 2: horizontal to detour column
                for c in range(min(src_center, detour_col),
                               max(src_center, detour_col) + 1):
                    g.put(turn1_r, c, '-')
                g.put(turn1_r, src_center, '+')
                g.put(turn1_r, detour_col, '+')

                # Segment 3: vertical along detour column
                for r in range(turn1_r + 1, turn2_r):
                    g.put(r, detour_col, '|')

                # Segment 4: horizontal back to dest
                for c in range(min(dst_center, detour_col),
                               max(dst_center, detour_col) + 1):
                    g.put(turn2_r, c, '-')
                g.put(turn2_r, detour_col, '+')
                g.put(turn2_r, dst_center, '+')

                # Segment 5: vertical to dest entry
                for r in range(turn2_r + 1, entry_r + 1):
                    g.put(r, dst_center, '|')

                # Arrow
                if going_down:
                    g.put(entry_r, dst_center, 'v')
                else:
                    g.put(exit_r, src_center, '^')

                # Label
                if label:
                    label_r = turn1_r + (turn2_r - turn1_r) // 2
                    place_label(label_r, detour_col + 2, label)

    elif from_gr == to_gr:
        # Same row - horizontal connector
        row = ft + fh // 2
        going_right = to_gc > from_gc

        if going_right:
            start_c = fl + fw
            end_c = tl - 1
        else:
            start_c = tl + tw
            end_c = fl - 1

        if not _h_seg_blocked(box_positions, row, start_c, end_c, exclude):
            for c in range(min(start_c, end_c), max(start_c, end_c) + 1):
                g.put(row, c, '-')
            if going_right:
                g.put(row, end_c, '>')
            else:
                g.put(row, start_c, '<')
            if label:
                mid_c = min(start_c, end_c) + abs(end_c - start_c) // 2 - len(label) // 2
                place_label(row - 1, mid_c, label)
        else:
            # Detour above or below obstacle boxes
            src_center = fl + fw // 2
            dst_center = tl + tw // 2

            obs_top = min(ft, tt)
            obs_bot = max(ft + fh, tt + th)
            for bid, (bt, bl, bw, bh) in box_positions.items():
                if bid in exclude:
                    continue
                if bt <= row < bt + bh:
                    lo = min(start_c, end_c)
                    hi = max(start_c, end_c)
                    if lo < bl + bw and hi >= bl:
                        obs_top = min(obs_top, bt)
                        obs_bot = max(obs_bot, bt + bh)

            detour_r = obs_top - 1
            if detour_r < 0:
                detour_r = obs_bot

            # Vertical from source to detour
            if detour_r < ft:
                v_start = ft - 1
            else:
                v_start = ft + fh
            for r in range(min(v_start, detour_r), max(v_start, detour_r) + 1):
                g.put(r, src_center, '|')
            g.put(v_start, src_center, '+')

            # Horizontal along detour
            for c in range(min(src_center, dst_center),
                           max(src_center, dst_center) + 1):
                g.put(detour_r, c, '-')
            g.put(detour_r, src_center, '+')
            g.put(detour_r, dst_center, '+')

            # Vertical from detour to dest
            if detour_r < tt:
                v_end = tt - 1
                arrow = 'v'
            else:
                v_end = tt + th
                arrow = '^'
            for r in range(min(detour_r, v_end), max(detour_r, v_end) + 1):
                g.put(r, dst_center, '|')
            g.put(v_end, dst_center, arrow)

            if label:
                mid_c = min(src_center, dst_center) + abs(dst_center - src_center) // 2 - len(label) // 2
                place_label(detour_r - 1, mid_c, label)

    else:
        # Different row and column - L-shape
        going_right = to_gc > from_gc
        going_down = to_gr > from_gr

        # --- Option A: horizontal-first L-shape ---
        exit_r = ft + fh // 2
        exit_c = (fl + fw) if going_right else (fl - 1)
        entry_c = tl + tw // 2
        entry_r = (tt - 1) if going_down else (tt + th)

        h_ok = not _h_seg_blocked(box_positions, exit_r, exit_c, entry_c, exclude)
        v_ok = h_ok and not _v_seg_blocked(box_positions, entry_c, exit_r, entry_r, exclude)

        if h_ok and v_ok:
            seg_left = min(exit_c, entry_c)
            seg_right = max(exit_c, entry_c)
            for c in range(seg_left, seg_right + 1):
                g.put(exit_r, c, '-')
            g.put(exit_r, entry_c, '+')

            if going_down:
                for r in range(exit_r + 1, entry_r + 1):
                    g.put(r, entry_c, '|')
                g.put(entry_r, entry_c, 'v')
            else:
                for r in range(entry_r, exit_r):
                    g.put(r, entry_c, '|')
                g.put(entry_r, entry_c, '^')

            if label:
                if going_right:
                    place_label(exit_r - 1, exit_c + 1, label)
                else:
                    place_label(exit_r - 1, exit_c - len(label), label)

        else:
            # --- Option B: vertical-first L-shape ---
            alt_exit_c = fl + fw // 2
            alt_exit_r = (ft + fh) if going_down else (ft - 1)
            alt_entry_r = tt + th // 2
            alt_entry_c = (tl - 1) if going_right else (tl + tw)

            v_ok2 = not _v_seg_blocked(box_positions, alt_exit_c,
                                       alt_exit_r, alt_entry_r, exclude)
            h_ok2 = v_ok2 and not _h_seg_blocked(box_positions, alt_entry_r,
                                                  alt_exit_c, alt_entry_c, exclude)

            if v_ok2 and h_ok2:
                v_top = min(alt_exit_r, alt_entry_r)
                v_bot = max(alt_exit_r, alt_entry_r)
                for r in range(v_top, v_bot + 1):
                    g.put(r, alt_exit_c, '|')

                h_left = min(alt_exit_c, alt_entry_c)
                h_right = max(alt_exit_c, alt_entry_c)
                for c in range(h_left, h_right + 1):
                    g.put(alt_entry_r, c, '-')

                g.put(alt_entry_r, alt_exit_c, '+')

                if going_right:
                    g.put(alt_entry_r, alt_entry_c, '>')
                else:
                    g.put(alt_entry_r, alt_entry_c, '<')

                if label:
                    mid_r = (alt_exit_r + alt_entry_r) // 2
                    place_label(mid_r, alt_exit_c + 2, label)

            else:
                # --- Option C: 3-segment H-V-H detour ---
                src_exit_r = ft + fh // 2
                dst_entry_r = tt + th // 2
                src_exit_c = (fl + fw) if going_right else (fl - 1)
                dst_entry_c = (tl - 1) if going_right else (tl + tw)

                mid_col = (src_exit_c + dst_entry_c) // 2
                clear_col = _find_clear_col(
                    box_positions,
                    min(src_exit_r, dst_entry_r),
                    max(src_exit_r, dst_entry_r),
                    mid_col, exclude)

                # Horizontal from source to clear_col
                for c in range(min(src_exit_c, clear_col),
                               max(src_exit_c, clear_col) + 1):
                    g.put(src_exit_r, c, '-')
                g.put(src_exit_r, clear_col, '+')

                # Vertical along clear_col
                for r in range(min(src_exit_r, dst_entry_r) + 1,
                               max(src_exit_r, dst_entry_r)):
                    g.put(r, clear_col, '|')

                # Horizontal from clear_col to dest
                for c in range(min(clear_col, dst_entry_c),
                               max(clear_col, dst_entry_c) + 1):
                    g.put(dst_entry_r, c, '-')
                g.put(dst_entry_r, clear_col, '+')

                # Arrow
                if going_right:
                    g.put(dst_entry_r, dst_entry_c, '>')
                else:
                    g.put(dst_entry_r, dst_entry_c, '<')

                if label:
                    mid_r = (src_exit_r + dst_entry_r) // 2
                    place_label(mid_r, clear_col + 2, label)


# ---------------------------------------------------------------------------
# Table mode
# ---------------------------------------------------------------------------

def _cell_text(cell):
    """Extract text from a cell (plain string or {"text": ..., "span": N})."""
    if isinstance(cell, dict):
        return str(cell.get('text', ''))
    return str(cell)


def _cell_span(cell):
    """Extract span from a cell (default 1)."""
    if isinstance(cell, dict):
        return cell.get('span', 1)
    return 1


def _row_logical_cols(row):
    """Number of logical columns a row occupies (counting spans)."""
    return sum(_cell_span(cell) for cell in row)


def render_table(data):
    headers = data.get('headers', [])
    aligns = data.get('align', [])
    rows = data.get('rows', [])
    separator_after = data.get('separator_after', [])
    footer = data.get('footer', None)

    # Gather all rows for width computation
    all_rows = headers + rows
    if footer:
        all_rows = all_rows + [footer]

    if not all_rows:
        return ''

    num_cols = max(_row_logical_cols(r) for r in all_rows)

    # Normalize rows to fill missing columns
    for r in all_rows:
        while _row_logical_cols(r) < num_cols:
            r.append('')

    # Normalize aligns
    while len(aligns) < num_cols:
        aligns.append('left')

    # Compute column widths - first pass: non-spanning cells only
    col_widths = [0] * num_cols
    for r in all_rows:
        ci = 0
        for cell in r:
            span = min(_cell_span(cell), num_cols - ci)
            if span == 1:
                col_widths[ci] = max(col_widths[ci], len(_cell_text(cell)))
            ci += span

    # Second pass: distribute extra width needed by spanning cells
    for r in all_rows:
        ci = 0
        for cell in r:
            span = min(_cell_span(cell), num_cols - ci)
            if span > 1:
                needed = len(_cell_text(cell))
                # Available content width: col_widths + padding + internal separators
                available = sum(col_widths[ci:ci+span]) + 3 * (span - 1)
                if needed > available:
                    extra = needed - available
                    per_col = extra // span
                    remainder = extra % span
                    for s in range(span):
                        col_widths[ci + s] += per_col + (1 if s < remainder else 0)
            ci += span

    # Add padding (1 space each side)
    padded_widths = [w + 2 for w in col_widths]

    # Total width including separators
    total_width = sum(padded_widths) + num_cols + 1

    # Auto-split if too wide
    if total_width > MAX_WIDTH and num_cols > 2:
        return render_table_split(data, padded_widths, num_cols)

    lines = []

    def _row_suppress(row_data):
        """Column indices where + should be suppressed (internal to a span)."""
        suppress = set()
        ci = 0
        for cell in row_data:
            span = min(_cell_span(cell), num_cols - ci)
            for s in range(1, span):
                suppress.add(ci + s)
            ci += span
        return suppress

    def sep_line(row_data=None):
        suppress = _row_suppress(row_data) if row_data else set()
        parts = ['+']
        for ci in range(num_cols):
            parts.append('-' * padded_widths[ci])
            if (ci + 1) in suppress:
                parts.append('-')
            else:
                parts.append('+')
        lines.append(''.join(parts))

    def data_line(row_data):
        parts = ['|']
        ci = 0
        for cell in row_data:
            text = _cell_text(cell)
            span = min(_cell_span(cell), num_cols - ci)
            # Combined width: sum of spanned padded_widths + internal separators
            combined_pw = sum(padded_widths[ci:ci+span]) + (span - 1)
            w = combined_pw - 2  # content width
            align = aligns[ci] if ci < len(aligns) else 'left'
            if align == 'right':
                formatted = text.rjust(w)
            elif align == 'center':
                formatted = text.center(w)
            else:
                formatted = text.ljust(w)
            parts.append(' ' + formatted + ' ')
            parts.append('|')
            ci += span
        lines.append(''.join(parts))

    # Collect all rendered rows for top/bottom border context
    all_rendered = []
    if headers:
        all_rendered.extend(headers)
    all_rendered.extend(rows)
    if footer:
        all_rendered.append(footer)
    first_row = all_rendered[0] if all_rendered else None
    last_row = all_rendered[-1] if all_rendered else None

    # Top border (reflects first row)
    sep_line(first_row)

    # Headers
    for hi, hrow in enumerate(headers):
        data_line(hrow)

    # Separator after headers (reflects next row below)
    if -1 in separator_after or (headers and not separator_after):
        next_row = rows[0] if rows else (footer if footer else None)
        sep_line(next_row)

    # Data rows
    for ri, row in enumerate(rows):
        data_line(row)
        if ri in separator_after:
            next_row = rows[ri + 1] if ri + 1 < len(rows) else (footer if footer else None)
            sep_line(next_row)

    # Footer
    if footer:
        sep_line(footer)
        data_line(footer)

    # Bottom border (reflects last row)
    sep_line(last_row)

    return '\n'.join(lines)


def render_table_split(data, padded_widths, num_cols):
    """Split a wide table into multiple tables, repeating the first column."""
    headers = data.get('headers', [])
    aligns = data.get('align', [])
    rows = data.get('rows', [])
    separator_after = data.get('separator_after', [])
    footer = data.get('footer', None)

    while len(aligns) < num_cols:
        aligns.append('left')

    # Compute safe split points (don't split within a span)
    all_data_rows = headers + rows
    if footer:
        all_data_rows = all_data_rows + [footer]
    safe_splits = set(range(1, num_cols))
    for r in all_data_rows:
        ci = 0
        for cell in r:
            span = _cell_span(cell)
            for s in range(1, span):
                safe_splits.discard(ci + s)
            ci += span

    # Figure out how to split: first column is always included
    first_col_width = padded_widths[0] + 2  # +2 for the | borders
    splits = []
    current_group = [0]
    current_width = first_col_width

    for ci in range(1, num_cols):
        needed = padded_widths[ci] + 1  # +1 for the | separator
        if current_width + needed > MAX_WIDTH and len(current_group) > 1 and ci in safe_splits:
            splits.append(current_group)
            current_group = [0]
            current_width = first_col_width
        current_group.append(ci)
        current_width += needed

    if current_group:
        splits.append(current_group)

    def extract_cells(row, group):
        """Extract cells from row whose start column is in the group."""
        group_set = set(group)
        result = []
        ci = 0
        for cell in row:
            span = _cell_span(cell)
            if ci in group_set:
                result.append(cell)
            ci += span
        return result

    results = []
    for group in splits:
        sub_data = {
            'headers': [extract_cells(h, group) for h in headers],
            'align': [aligns[ci] for ci in group],
            'rows': [extract_cells(r, group) for r in rows],
            'separator_after': separator_after,
        }
        if footer:
            sub_data['footer'] = extract_cells(footer, group)
        results.append(render_table(sub_data))

    return '\n\n'.join(results)


# ---------------------------------------------------------------------------
# Layers mode (dedicated renderer with centered rows + bus connectors)
# ---------------------------------------------------------------------------

def render_layers(data):
    title = data.get('title', '')
    levels = data.get('levels', [])
    connections = data.get('connections', 'between_layers')

    # Compute layer label margin
    max_label_len = max((len(lev.get('label', '')) for lev in levels), default=0)
    label_margin = 0
    if max_label_len > 0:
        label_margin = max_label_len + 3  # "label | "
    available_width = MAX_WIDTH - label_margin

    g = Grid()
    y = 0
    if title:
        g.put_str(0, label_margin, title)
        y = 2

    row_spacing = 2
    level_positions = []  # list of (y, row_height, [(x, w, h), ...])

    for li, level in enumerate(levels):
        boxes = level['boxes']
        widths = [box_min_width(b) for b in boxes]
        heights = [box_height(b) for b in boxes]

        spacing = 3
        total_w = sum(widths) + spacing * max(0, len(boxes) - 1)
        if total_w > available_width and spacing > 1:
            spacing = 1
            total_w = sum(widths) + spacing * max(0, len(boxes) - 1)

        start_x = label_margin + max(0, (available_width - total_w) // 2)
        row_height = max(heights) if heights else 3

        box_positions = []
        x = start_x
        for bi, (lbl_text, bw, bh) in enumerate(zip(boxes, widths, heights)):
            draw_box(g, y, x, bw, lbl_text)
            box_positions.append((x, bw, bh))
            x += bw + spacing

        # Draw layer label
        lbl = level.get('label', '')
        if lbl and label_margin > 0:
            label_y = y + row_height // 2
            g.put_str(label_y, 0, lbl.rjust(max_label_len))
            g.put_str(label_y, max_label_len + 1, '|')

        level_positions.append((y, row_height, box_positions))
        y += row_height + row_spacing

    # Draw connectors between adjacent levels
    if connections == 'between_layers':
        for li in range(len(level_positions) - 1):
            top_y, top_rh, top_boxes = level_positions[li]
            bot_y, bot_rh, bot_boxes = level_positions[li + 1]

            gap_start = top_y + top_rh  # first row below top boxes
            gap_end = bot_y - 1         # last row above bottom boxes
            mid_row = gap_start + (gap_end - gap_start) // 2

            top_centers = [x + w // 2 for x, w, h in top_boxes]
            bot_centers = [x + w // 2 for x, w, h in bot_boxes]

            if (len(top_boxes) == 1) != (len(bot_boxes) == 1):
                # Bus pattern for fan-out (1:N) or fan-in (N:1)
                all_centers = top_centers + bot_centers
                left_c = min(all_centers)
                right_c = max(all_centers)
                for tc in top_centers:
                    for r in range(gap_start, mid_row):
                        g.put(r, tc, '|')
                for c in range(left_c, right_c + 1):
                    g.put(mid_row, c, '-')
                for center in all_centers:
                    g.put(mid_row, center, '+')
                for bc in bot_centers:
                    for r in range(mid_row + 1, gap_end + 1):
                        g.put(r, bc, '|')
                    g.put(gap_end, bc, 'v')

            else:
                # N:N (including 1:1): match by index
                for i in range(min(len(top_boxes), len(bot_boxes))):
                    tc = top_centers[i]
                    bc = bot_centers[i]
                    if tc == bc:
                        for r in range(gap_start, gap_end + 1):
                            g.put(r, tc, '|')
                        g.put(gap_end, tc, 'v')
                    else:
                        for r in range(gap_start, mid_row):
                            g.put(r, tc, '|')
                        min_c = min(tc, bc)
                        max_c = max(tc, bc)
                        for c in range(min_c, max_c + 1):
                            g.put(mid_row, c, '-')
                        g.put(mid_row, tc, '+')
                        g.put(mid_row, bc, '+')
                        for r in range(mid_row + 1, gap_end + 1):
                            g.put(r, bc, '|')
                        g.put(gap_end, bc, 'v')

    return g.render()


# ---------------------------------------------------------------------------
# Sequence diagram mode
# ---------------------------------------------------------------------------

def render_sequence(data):
    """Render a sequence diagram with actors, lifelines, and message arrows."""
    actors = data.get('actors', [])
    messages = data.get('messages', [])
    notes = data.get('notes', [])

    if not actors:
        return ''

    g = Grid()
    num_actors = len(actors)

    # Actor box widths
    actor_widths = [len(a) + 4 for a in actors]

    # Minimum center-to-center spacing: must fit labels and boxes
    min_spacing = 16
    for msg in messages:
        min_spacing = max(min_spacing, len(msg.get('label', '')) + 6)
    for i in range(num_actors - 1):
        needed = (actor_widths[i] + actor_widths[i + 1]) // 2 + 2
        min_spacing = max(min_spacing, needed)

    # Constrain to MAX_WIDTH
    total_w = min_spacing * (num_actors - 1) + max(actor_widths)
    if total_w > MAX_WIDTH:
        min_spacing = max(12, (MAX_WIDTH - max(actor_widths)) // max(1, num_actors - 1))

    # Compute actor center columns
    centers = []
    x = actor_widths[0] // 2
    for i in range(num_actors):
        centers.append(x)
        if i < num_actors - 1:
            x += min_spacing

    # Draw actor boxes at top
    for i, actor in enumerate(actors):
        w = actor_widths[i]
        left = centers[i] - w // 2
        draw_box(g, 0, left, w, actor)

    # Build timeline: messages with notes interleaved after specified indices
    note_map = {}
    for note in notes:
        idx = note.get('after_message', len(messages) - 1)
        note_map.setdefault(idx, []).append(note)

    y = 4  # start after actor boxes (3 rows) + 1 gap
    row_spacing = 2
    events = []

    for mi, msg in enumerate(messages):
        events.append((y, 'msg', msg))
        y += row_spacing
        if mi in note_map:
            for note in note_map[mi]:
                events.append((y, 'note', note))
                y += 4  # 3 for note box + 1 gap for next message label

    total_height = y + 1

    # Draw lifelines
    for i in range(num_actors):
        for r in range(3, total_height):
            g.put(r, centers[i], '|')

    # Draw events
    for y_pos, evt_type, evt in events:
        if evt_type == 'msg':
            _draw_seq_message(g, centers, actors, evt, y_pos)
        elif evt_type == 'note':
            _draw_seq_note(g, centers, actors, evt, y_pos)

    return g.render()


def _draw_seq_message(g, centers, actors, msg, y):
    """Draw a message arrow on the sequence diagram."""
    from_name = msg['from']
    to_name = msg['to']
    label = msg.get('label', '')
    style = msg.get('style', 'solid')

    if from_name not in actors or to_name not in actors:
        return

    from_x = centers[actors.index(from_name)]
    to_x = centers[actors.index(to_name)]

    if from_x == to_x:
        return

    going_right = to_x > from_x
    if going_right:
        start_c = from_x + 1
        end_c = to_x - 1
    else:
        start_c = to_x + 1
        end_c = from_x - 1

    # Draw line
    if style == 'dashed':
        for c in range(start_c, end_c + 1):
            g.put(y, c, '-' if (c - start_c) % 2 == 0 else ' ')
    else:
        for c in range(start_c, end_c + 1):
            g.put(y, c, '-')

    # Arrow head (overwrites lifeline char)
    if going_right:
        g.put(y, to_x, '>')
    else:
        g.put(y, to_x, '<')

    # Label above arrow, centered between lifelines
    mid = (from_x + to_x) // 2
    label_start = mid - len(label) // 2
    g.put_str(y - 1, label_start, label)


def _draw_seq_note(g, centers, actors, note, y):
    """Draw a note box between two actors on the sequence diagram."""
    between = note.get('between', [])
    text = note.get('text', '')

    if len(between) < 2:
        return
    if between[0] not in actors or between[1] not in actors:
        return

    idx1 = actors.index(between[0])
    idx2 = actors.index(between[1])
    left_x = centers[min(idx1, idx2)] + 2
    right_x = centers[max(idx1, idx2)] - 2
    note_w = right_x - left_x

    if note_w < 6:
        return  # too narrow for any note
    if note_w < len(text) + 4:
        text = text[:note_w - 4]
    draw_box(g, y, left_x, note_w, text)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print('Error: Invalid JSON input: {}'.format(e), file=sys.stderr)
        sys.exit(1)

    if 'diagram' in data:
        result = render_diagram(data['diagram'])
    elif 'table' in data:
        result = render_table(data['table'])
    elif 'layers' in data:
        result = render_layers(data['layers'])
    elif 'sequence' in data:
        result = render_sequence(data['sequence'])
    else:
        print('Error: JSON must contain a "diagram", "table", "layers", or "sequence" key.', file=sys.stderr)
        sys.exit(1)

    # Width enforcement — fail fast if any line exceeds the limit
    lines = result.split('\n')
    for i, line in enumerate(lines):
        if len(line) > MAX_WIDTH:
            print('Error: Line {} is {} chars wide (max {}). Shorten labels or reduce columns.'.format(
                i + 1, len(line), MAX_WIDTH), file=sys.stderr)
            sys.exit(1)

    print(result)


if __name__ == '__main__':
    main()
