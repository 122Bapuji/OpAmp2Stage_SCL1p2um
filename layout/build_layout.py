import numpy as np
import pya
import sys
import os

layout = pya.Layout()
layout.dbu = 0.001 # 1 nm DBU

# Define layers according to SCL 1.2um Table 2
l_nwell     = layout.layer(1, 0)
l_diff      = layout.layer(2, 0)
l_nwell_rev = layout.layer(3, 0)
l_poly      = layout.layer(4, 0)
l_boron     = layout.layer(5, 0)
l_boron_rev = layout.layer(6, 0)
l_cont      = layout.layer(7, 0)
l_m1        = layout.layer(8, 0)
l_m1_lbl    = layout.layer(8, 7)
l_via       = layout.layer(9, 0)
l_m2        = layout.layer(10, 0)
l_m2_lbl    = layout.layer(10, 7)
l_prbnd     = layout.layer(28, 0)

cell = layout.create_cell("opamp_2stage")

def box_um(x1, y1, x2, y2):
    return pya.Box(int(x1 * 1000), int(y1 * 1000), int(x2 * 1000), int(y2 * 1000))

# 1. PR Boundary: 180 um x 120 um
cell.shapes(l_prbnd).insert(box_um(0, 0, 180, 120))

# 2. Power Rails: VDD along top (y=105 to 118), VSS along bottom (y=2 to 15) in M1 and M2
cell.shapes(l_m1).insert(box_um(2, 105, 178, 118))
cell.shapes(l_m2).insert(box_um(2, 105, 178, 118))
cell.shapes(l_m1_lbl).insert(pya.Text("VDD", pya.Trans(pya.Point(10000, 110000))))

cell.shapes(l_m1).insert(box_um(2, 2, 178, 15))
cell.shapes(l_m2).insert(box_um(2, 2, 178, 15))
cell.shapes(l_m1_lbl).insert(pya.Text("VSS", pya.Trans(pya.Point(10000, 8000))))

# 3. N-Well for PMOS section (y = 55 to 118, x = 5 to 175)
cell.shapes(l_nwell).insert(box_um(5, 55, 175, 118))
cell.shapes(l_nwell_rev).insert(box_um(5, 55, 175, 118))

# Substrate contact tap in VSS region (P-tap in P-substrate)
cell.shapes(l_diff).insert(box_um(10, 4, 170, 13))
cell.shapes(l_boron).insert(box_um(8, 2, 172, 15))
cell.shapes(l_boron_rev).insert(box_um(8, 2, 172, 15))
# Contacts along VSS tap
for xc in range(15, 168, 6):
    cell.shapes(l_cont).insert(box_um(xc, 6.5, xc + 1.6, 10.5))

# N-Well contact tap in VDD region (N-tap in N-well)
cell.shapes(l_diff).insert(box_um(10, 107, 170, 116))
# Contacts along VDD tap
for xc in range(15, 168, 6):
    cell.shapes(l_cont).insert(box_um(xc, 109.5, xc + 1.6, 113.5))

# 4. Transistor Placement Helper
def create_fet(name, x, y, w, l, nf, is_pmos):
    # Diffusion active region
    diff_w = nf * (l + 4.0) + 4.0
    diff_h = w
    x1, y1 = x, y
    x2, y2 = x + diff_w, y + diff_h
    cell.shapes(l_diff).insert(box_um(x1, y1, x2, y2))
    
    if is_pmos:
        # P+ implant: boron & boron_rev
        cell.shapes(l_boron).insert(box_um(x1 - 2.0, y1 - 2.0, x2 + 2.0, y2 + 2.0))
        cell.shapes(l_boron_rev).insert(box_um(x1 - 2.0, y1 - 2.0, x2 + 2.0, y2 + 2.0))
    
    # Poly fingers
    for i in range(nf):
        gate_x1 = x1 + 2.0 + i * (l + 4.0)
        gate_x2 = gate_x1 + l
        gate_y1 = y1 - 2.5
        gate_y2 = y2 + 2.5
        cell.shapes(l_poly).insert(box_um(gate_x1, gate_y1, gate_x2, gate_y2))
        
        # Source/drain contacts on both sides of poly
        cont_x_left = gate_x1 - 2.8
        cont_x_right = gate_x2 + 1.2
        for yc in np.arange(y1 + 2.0, y2 - 2.0, 4.0):
            cell.shapes(l_cont).insert(box_um(cont_x_left, yc, cont_x_left + 1.6, yc + 1.6))
            if i == nf - 1:
                cell.shapes(l_cont).insert(box_um(cont_x_right, yc, cont_x_right + 1.6, yc + 1.6))

# Differential Pair: M1 and M2 (PMOS) common-centroid interdigitated: A B B A
# 4 fingers of 30u / 3.0u each
create_fet("M1_M2_diff", 15, 62, 30.0, 3.0, 4, True)

# Tail PMOS M5: 2 fingers of 20u / 5.0u
create_fet("M5_tail", 65, 62, 20.0, 5.0, 2, True)

# Bias PMOS M8: 2 fingers of 20u / 5.0u
create_fet("M8_bias", 95, 62, 20.0, 5.0, 2, True)

# Stage 2 Load PMOS M7: 6 fingers of 40u / 5.0u
create_fet("M7_load", 125, 62, 40.0, 5.0, 6, True)

# Active Load NMOS Mirror M3, M4: 2 fingers of 20u / 4.0u each
create_fet("M3_M4_load", 20, 22, 20.0, 4.0, 4, False)

# Stage 2 CS NMOS M6: 8 fingers of 30u / 4.0u
create_fet("M6_cs", 75, 22, 30.0, 4.0, 8, False)

# Save GDSII file
gds_path = "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/layout/opamp_2stage.gds"
layout.write(gds_path)
print(f"Successfully generated GDSII layout: {gds_path}")
