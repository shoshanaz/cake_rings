#!/usr/bin/env python3
import inkex
from inkex import Circle, Group, ShapeElement, TextElement, Tspan

class CakeRingsExtension(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--unit_size", type=float, default=0.5, help="Size of each grid square")

    def effect(self):
        selected = self.svg.selected.values()
        if not selected:
            raise inkex.AbortExtension("Please select the grid squares in Inkscape.")

        # Gather all shape elements (unpacking groups if needed)
        elements_to_process = []
        for node in selected:
            if isinstance(node, Group):
                elements_to_process.extend(node.xpath('.//*'))
            else:
                elements_to_process.append(node)

        squares = []
        for node in elements_to_process:
            if isinstance(node, ShapeElement):
                bbox = node.bounding_box()
                if bbox:
                    cx = (bbox.left + bbox.right) / 2
                    cy = (bbox.top + bbox.bottom) / 2
                    style = node.style
                    fill = style.get('fill')
                    if fill and str(fill) != 'none':
                        squares.append({'cx': cx, 'cy': cy, 'left': bbox.left, 'fill': str(fill)})

        if not squares:
            raise inkex.AbortExtension("No valid filled shapes found in selection.")

        # Find unique Y coordinates (rows) and X coordinates (columns)
        y_coords = sorted(list(set(round(sq['cy'], 2) for sq in squares)))
        x_coords = sorted(list(set(round(sq['cx'], 2) for sq in squares)))
        
        if not y_coords or not x_coords:
            raise inkex.AbortExtension("Could not determine grid structure.")

        num_rows = len(y_coords)
        num_cols = len(x_coords)

        # Convert user's input size into SVG user units (pixels)
        user_unit_size_str = f"{self.options.unit_size}in"
        grid_step = self.svg.unittouu(user_unit_size_str)

        # Map each square to its grid row and column indices based on sorted coordinates
        grid_map = {}
        for sq in squares:
            r_idx = min(range(len(y_coords)), key=lambda i: abs(y_coords[i] - sq['cy']))
            c_idx = min(range(len(x_coords)), key=lambda i: abs(x_coords[i] - sq['cx']))
            grid_map[(r_idx, c_idx)] = sq['fill']

        master_group = Group()
        self.svg.get_current_layer().append(master_group)
        master_group.set('id', 'all_cake_layers_left_axis')

        # Find the global minimum X (the left edge of the entire pattern) to use as the universal rotation axis
        min_x_global = min(sq['left'] for sq in squares)
        
        # Dimensions and spacing for the output layout grid (3 rows wrap)
        max_layer_width = num_cols * grid_step * 2.2
        max_layer_height = num_cols * grid_step * 2.2
        items_per_row = 3

        # Generate distinct cake layers (one for each row index, from top to bottom)
        for row_idx in range(num_rows):
            layer_group = Group()
            master_group.append(layer_group)
            layer_group.set('id', f'cake_layer_row_{row_idx + 1}')

            # Calculate grid position (column and row in the output layout)
            layout_col = row_idx % items_per_row
            layout_row = row_idx // items_per_row

            # Offset each ring group neatly in a multi-row layout
            layout_offset_x = layout_col * max_layer_width
            layout_offset_y = layout_row * max_layer_height

            # The center of the concentric circles for this layer aligns with the offset
            layer_cx = min_x_global + layout_offset_x
            layer_cy = y_coords[0] + layout_offset_y

            # Build color spans outward from column 0 (the left edge) to the rightmost column
            full_spans = []
            for c_idx in range(num_cols):
                outer_radius = (c_idx + 1) * grid_step
                cell_color = grid_map.get((row_idx, c_idx), '#F5F5DC')
                full_spans.append({'r': outer_radius, 'fill': cell_color})

            # Merge adjacent rings if they share the exact same color, tracking band thickness (count of grid cells)
            merged_rings = []
            if full_spans:
                curr_color = full_spans[0]['fill']
                curr_r = full_spans[0]['r']
                curr_thickness = 1
                
                for span in full_spans[1:]:
                    if span['fill'] == curr_color:
                        curr_r = span['r']
                        curr_thickness += 1
                    else:
                        merged_rings.append({'r': curr_r, 'fill': curr_color, 'thickness': curr_thickness})
                        curr_color = span['fill']
                        curr_r = span['r']
                        curr_thickness = 1
                merged_rings.append({'r': curr_r, 'fill': curr_color, 'thickness': curr_thickness})

            # Draw circles from outside-in so smaller inner rings layer correctly on top in SVG
            merged_rings.reverse()

            for span in merged_rings:
                if span['r'] > 0:
                    circle = Circle()
                    circle.set('cx', layer_cx)
                    circle.set('cy', layer_cy)
                    circle.set('r', span['r'])
                    circle.style = {'fill': span['fill'], 'stroke': '#000000', 'stroke-width': '0.5'}
                    layer_group.append(circle)

                    # Add a larger, clear text label showing the exact number of joined units for this ring band
                    text = TextElement()
                    text.set('x', layer_cx - span['r'] + (grid_step * 0.4))
                    text.set('y', layer_cy - 3)
                    text.style = {
                        'font-size': '24px',
                        'font-weight': 'bold',
                        'font-family': 'sans-serif',
                        'fill': '#000000',
                        'text-anchor': 'right'
                    }
                    tspan = Tspan()
                    tspan.text = str(span['thickness'])
                    text.append(tspan)
                    layer_group.append(text)

if __name__ == '__main__':
    CakeRingsExtension().run()