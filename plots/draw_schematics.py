#!/usr/bin/env python3
"""
Generate publication-quality circuit schematic diagrams for:
1. Two-Stage CMOS Op-Amp Core (opamp_schematic.png)
2. Open-Loop & Closed-Loop Testbench (tb_opamp_schematic.png)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_nmos(ax, x, y, name, w_l, arrow_out=True):
    # Gate
    ax.plot([x - 0.6, x - 0.2], [y, y], 'k-', lw=1.5)
    ax.plot([x - 0.2, x - 0.2], [y - 0.5, y + 0.5], 'k-', lw=2.2)
    # Channel
    ax.plot([x, x], [y - 0.6, y + 0.6], 'k-', lw=2.5)
    # Drain (top)
    ax.plot([x, x + 0.4], [y + 0.4, y + 0.4], 'k-', lw=1.5)
    ax.plot([x + 0.4, x + 0.4], [y + 0.4, y + 0.8], 'k-', lw=1.5)
    # Source (bottom)
    ax.plot([x, x + 0.4], [y - 0.4, y - 0.4], 'k-', lw=1.5)
    ax.plot([x + 0.4, x + 0.4], [y - 0.4, y - 0.8], 'k-', lw=1.5)
    # Arrow on source pointing out
    if arrow_out:
        ax.annotate('', xy=(x + 0.25, y - 0.4), xytext=(x + 0.05, y - 0.4),
                    arrowprops=dict(arrowstyle="->", color="k", lw=1.5, mutation_scale=12))
    # Labels
    ax.text(x - 0.3, y + 0.7, name, fontsize=11, fontweight='bold', color='darkblue')
    ax.text(x - 0.3, y + 0.4, w_l, fontsize=8.5, color='darkred')
    return (x - 0.6, y), (x + 0.4, y + 0.8), (x + 0.4, y - 0.8) # gate, drain, source

def draw_pmos(ax, x, y, name, w_l, arrow_in=True):
    # Gate with bubble
    ax.plot([x - 0.6, x - 0.3], [y, y], 'k-', lw=1.5)
    circle = patches.Circle((x - 0.25, y), 0.06, edgecolor='k', facecolor='white', lw=1.5)
    ax.add_patch(circle)
    ax.plot([x - 0.18, x - 0.18], [y - 0.5, y + 0.5], 'k-', lw=2.2)
    # Channel
    ax.plot([x, x], [y - 0.6, y + 0.6], 'k-', lw=2.5)
    # Source (top)
    ax.plot([x, x + 0.4], [y + 0.4, y + 0.4], 'k-', lw=1.5)
    ax.plot([x + 0.4, x + 0.4], [y + 0.4, y + 0.8], 'k-', lw=1.5)
    # Drain (bottom)
    ax.plot([x, x + 0.4], [y - 0.4, y - 0.4], 'k-', lw=1.5)
    ax.plot([x + 0.4, x + 0.4], [y - 0.4, y - 0.8], 'k-', lw=1.5)
    # Arrow on source pointing in
    if arrow_in:
        ax.annotate('', xy=(x + 0.05, y + 0.4), xytext=(x + 0.25, y + 0.4),
                    arrowprops=dict(arrowstyle="->", color="k", lw=1.5, mutation_scale=12))
    # Labels
    ax.text(x - 0.3, y + 0.7, name, fontsize=11, fontweight='bold', color='darkblue')
    ax.text(x - 0.3, y + 0.4, w_l, fontsize=8.5, color='darkred')
    return (x - 0.6, y), (x + 0.4, y - 0.8), (x + 0.4, y + 0.8) # gate, drain, source

def draw_resistor(ax, x, y, height, name, val):
    y1, y2 = y - height/2, y + height/2
    ax.plot([x, x], [y2, y2 - 0.2], 'k-', lw=1.5)
    ax.plot([x, x], [y1 + 0.2, y1], 'k-', lw=1.5)
    # zigzag
    n_pts = 6
    ys = [y2 - 0.2 - i * (height - 0.4)/(n_pts) for i in range(n_pts + 1)]
    xs = [x + (0.15 if i % 2 == 1 else -0.15 if i % 2 == 0 and i > 0 and i < n_pts else 0) for i in range(n_pts + 1)]
    xs[0] = x; xs[-1] = x
    ax.plot(xs, ys, 'k-', lw=1.8)
    ax.text(x + 0.25, y, f"{name}\n{val}", fontsize=9, va='center', fontweight='bold', color='darkgreen')
    return (x, y2), (x, y1)

def draw_capacitor(ax, x, y, width, name, val):
    x1, x2 = x - width/2, x + width/2
    ax.plot([x1, x - 0.1], [y, y], 'k-', lw=1.5)
    ax.plot([x + 0.1, x2], [y, y], 'k-', lw=1.5)
    ax.plot([x - 0.1, x - 0.1], [y - 0.3, y + 0.3], 'k-', lw=2.2)
    ax.plot([x + 0.1, x + 0.1], [y - 0.3, y + 0.3], 'k-', lw=2.2)
    ax.text(x, y + 0.35, f"{name} ({val})", fontsize=9, ha='center', fontweight='bold', color='darkgreen')
    return (x1, y), (x2, y)

def create_opamp_schematic():
    fig, ax = plt.subplots(figsize=(12, 8.5), dpi=300)
    ax.set_xlim(-1, 14)
    ax.set_ylim(-1, 10)
    ax.axis('off')

    # Title
    ax.text(6.5, 9.6, "SCL 1.2 µm CMOS Two-Stage Operational Amplifier",
            fontsize=15, fontweight='bold', ha='center', color='#003366')
    ax.text(6.5, 9.2, "Complete Circuit Schematic with Transistor Sizing and Device Parameters",
            fontsize=10.5, fontstyle='italic', ha='center', color='#555555')

    # Power Rails
    ax.plot([0.5, 12.5], [8.5, 8.5], 'r-', lw=2.5) # VDD
    ax.text(0.3, 8.5, "VDD (5V)", fontsize=11, fontweight='bold', va='center', ha='right', color='red')
    
    ax.plot([0.5, 12.5], [0.5, 0.5], 'b-', lw=2.5) # VSS
    ax.text(0.3, 0.5, "VSS (0V)", fontsize=11, fontweight='bold', va='center', ha='right', color='blue')

    # 1. Bias Branch
    # M8 (PMOS Diode) at x=2.0, y=7.0
    g8, d8, s8 = draw_pmos(ax, 1.8, 7.2, "M8", "40u/5.0u")
    ax.plot([s8[0], s8[0]], [s8[1], 8.5], 'k-', lw=1.5) # Source to VDD
    # Diode tie
    ax.plot([d8[0], g8[0] - 0.2], [d8[1], d8[1]], 'k-', lw=1.5)
    ax.plot([g8[0] - 0.2, g8[0] - 0.2], [d8[1], g8[1]], 'k-', lw=1.5)
    ax.plot([g8[0] - 0.2, g8[0]], [g8[1], g8[1]], 'k-', lw=1.5)
    
    # Rbias from d8 to VSS
    rtop, rbot = draw_resistor(ax, d8[0], 3.8, 2.0, "Rbias", "95 kΩ")
    ax.plot([d8[0], rtop[0]], [d8[1], rtop[1]], 'k-', lw=1.5)
    ax.plot([rbot[0], rbot[0]], [rbot[1], 0.5], 'k-', lw=1.5)

    # Bias connection line (vbp) across to M5 and M7
    vbp_y = g8[1]
    ax.plot([g8[0] - 0.2, 10.4], [vbp_y, vbp_y], 'm--', lw=1.4)
    ax.text(2.6, vbp_y + 0.15, "net_bias (vbp)", fontsize=9, color='purple', fontweight='bold')

    # 2. Stage 1: Tail Current Source M5 at x=5.0, y=7.2
    g5, d5, s5 = draw_pmos(ax, 4.8, 7.2, "M5", "40u/5.0u")
    ax.plot([s5[0], s5[0]], [s5[1], 8.5], 'k-', lw=1.5)
    ax.plot([g5[0], g5[0]], [g5[1], vbp_y], 'k-', lw=1.5) # gate to vbp
    ax.plot(g5[0], vbp_y, 'ko', ms=4)

    # 3. Differential Pair: M1, M2 at y=4.8
    # Tail connection
    tail_x = d5[0]
    tail_y = 5.8
    ax.plot([d5[0], tail_x], [d5[1], tail_y], 'k-', lw=1.5)
    ax.plot([tail_x - 1.2, tail_x + 1.2], [tail_y, tail_y], 'k-', lw=1.5)
    ax.plot(tail_x, tail_y, 'ko', ms=4)
    ax.text(tail_x + 0.1, tail_y + 0.2, "tail (3.75V)", fontsize=8, color='#333333')

    # M1 (PMOS) at x=3.8, y=4.8
    g1, d1, s1 = draw_pmos(ax, 3.6, 4.8, "M1", "120u/3.0u")
    ax.plot([s1[0], s1[0]], [s1[1], tail_y], 'k-', lw=1.5)
    # INM input terminal
    ax.plot([g1[0], g1[0] - 0.8], [g1[1], g1[1]], 'k-', lw=1.5)
    ax.plot(g1[0] - 0.8, g1[1], 'rs', ms=6)
    ax.text(g1[0] - 0.9, g1[1], "IN- (INM)", fontsize=10, fontweight='bold', ha='right', va='center', color='darkred')

    # M2 (PMOS) at x=6.2, y=4.8
    g2, d2, s2 = draw_pmos(ax, 6.0, 4.8, "M2", "120u/3.0u")
    ax.plot([s2[0], s2[0]], [s2[1], tail_y], 'k-', lw=1.5)
    # INP input terminal
    ax.plot([g2[0], g2[0] - 0.8], [g2[1], g2[1]], 'k-', lw=1.5)
    ax.plot(g2[0] - 0.8, g2[1], 'gs', ms=6)
    ax.text(g2[0] - 0.9, g2[1], "IN+ (INP)", fontsize=10, fontweight='bold', ha='right', va='center', color='darkgreen')

    # 4. Active Current Mirror Load: M3, M4 (NMOS) at y=2.0
    # M3 (diode connected) at x=3.8, y=2.0
    g3, d3, s3 = draw_nmos(ax, 3.6, 2.0, "M3", "20u/4.0u")
    ax.plot([s3[0], s3[0]], [s3[1], 0.5], 'k-', lw=1.5)
    ax.plot([d1[0], d3[0]], [d1[1], d3[1]], 'k-', lw=1.5) # drain M1 to drain M3
    ax.text(d1[0] - 0.15, 3.4, "net1", fontsize=8, color='#555555', ha='right')
    
    # Diode tie M3
    ax.plot([d3[0], g3[0] - 0.2], [3.2, 3.2], 'k-', lw=1.5)
    ax.plot([g3[0] - 0.2, g3[0] - 0.2], [3.2, g3[1]], 'k-', lw=1.5)
    ax.plot([g3[0] - 0.2, g3[0]], [g3[1], g3[1]], 'k-', lw=1.5)
    ax.plot(d3[0], 3.2, 'ko', ms=4)

    # M4 at x=6.2, y=2.0
    g4, d4, s4 = draw_nmos(ax, 6.0, 2.0, "M4", "20u/4.0u")
    ax.plot([s4[0], s4[0]], [s4[1], 0.5], 'k-', lw=1.5)
    ax.plot([d2[0], d4[0]], [d2[1], d4[1]], 'k-', lw=1.5) # drain M2 to drain M4
    
    # Mirror gate bus
    ax.plot([g3[0], g4[0]], [g3[1], g4[1]], 'k-', lw=1.5)
    ax.plot(g3[0], g3[1], 'ko', ms=4)

    # High impedance Node 1 (out1)
    node1_y = 3.4
    ax.plot(d4[0], node1_y, 'ko', ms=5)
    ax.text(d4[0] - 0.1, node1_y + 0.2, "Node 1 (out1)", fontsize=9, fontweight='bold', color='navy', ha='right')

    # 5. Stage 2: Driver M6 (NMOS) at x=11.0, y=2.5
    g6, d6, s6 = draw_nmos(ax, 10.8, 2.5, "M6", "240u/4.0u")
    ax.plot([s6[0], s6[0]], [s6[1], 0.5], 'k-', lw=1.5)
    # Connection from Node 1 to Gate M6
    ax.plot([d4[0], g6[0]], [node1_y, node1_y], 'k-', lw=1.5)
    ax.plot([g6[0], g6[0]], [node1_y, g6[1]], 'k-', lw=1.5)

    # Stage 2: Active Load M7 (PMOS) at x=11.0, y=7.0
    g7, d7, s7 = draw_pmos(ax, 10.8, 7.0, "M7", "240u/5.0u")
    ax.plot([s7[0], s7[0]], [s7[1], 8.5], 'k-', lw=1.5)
    # Gate M7 to vbp
    ax.plot([g7[0], g7[0]], [g7[1], vbp_y], 'k-', lw=1.5)
    ax.plot(g7[0], vbp_y, 'ko', ms=4)

    # Output Node VOUT
    ax.plot([d7[0], d6[0]], [d7[1], d6[1]], 'k-', lw=1.8)
    vout_y = 4.8
    ax.plot(d6[0], vout_y, 'ko', ms=5)
    ax.plot([d6[0], 12.8], [vout_y, vout_y], 'k-', lw=2.0)
    ax.plot(12.8, vout_y, 'bs', ms=7)
    ax.text(12.9, vout_y, "VOUT", fontsize=11, fontweight='bold', va='center', color='darkblue')

    # 6. Miller Compensation: Cc + Rz in series
    # From Node 1 to VOUT
    c_left, c_right = draw_capacitor(ax, 8.2, 5.8, 1.2, "Cc", "3.5 pF")
    rz_top, rz_bot = draw_resistor(ax, 9.6, 5.8, 1.4, "Rz", "3.2 kΩ")
    
    # Node 1 to Cc
    ax.plot([7.2, 7.2], [node1_y, 5.8], 'k-', lw=1.5)
    ax.plot([7.2, c_left[0]], [5.8, c_left[1]], 'k-', lw=1.5)
    ax.plot(7.2, node1_y, 'ko', ms=4)

    # Cc to Rz
    ax.plot([c_right[0], rz_top[0]], [c_right[1], rz_top[1]], 'k-', lw=1.5)

    # Rz to VOUT
    ax.plot([rz_bot[0], 11.2], [rz_bot[1], rz_bot[1]], 'k-', lw=1.5)
    ax.plot([11.2, 11.2], [rz_bot[1], vout_y], 'k-', lw=1.5)
    ax.plot(11.2, vout_y, 'ko', ms=4)

    # External Load Capacitor CL = 10 pF
    cl_l, cl_r = draw_capacitor(ax, 12.4, 2.5, 0.8, "CL", "10 pF")
    ax.plot([12.4, 12.4], [vout_y, cl_l[1] + 0.3], 'k--', lw=1.3)
    ax.plot([12.4, 12.4], [cl_l[1] - 0.3, 0.5], 'k--', lw=1.3)
    ax.plot(12.4, vout_y, 'ko', ms=4)
    ax.plot(12.4, 0.5, 'ko', ms=4)
    ax.text(12.6, 1.5, "(Load)", fontsize=8, color='#666666')

    # Annotations
    ax.text(4.2, 0.8, "Stage 1: Differential Transconductance Stage", fontsize=9.5, fontweight='bold', color='#004080')
    ax.text(10.0, 0.8, "Stage 2: Gain Stage", fontsize=9.5, fontweight='bold', color='#004080')

    out_path = "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/plots/opamp_schematic.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor='white', bbox_inches='tight')
    plt.close()
    print("Generated crisp schematic:", out_path)

def create_tb_schematic():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.set_xlim(-1, 13)
    ax.set_ylim(-1, 9)
    ax.axis('off')

    # Title
    ax.text(6.0, 8.5, "Op-Amp Simulation Testbench Architecture (tb_opamp.sch)",
            fontsize=14, fontweight='bold', ha='center', color='#003366')
    ax.text(6.0, 8.1, "Hierarchical Open-Loop AC & Closed-Loop Transient Evaluation Setup",
            fontsize=10, fontstyle='italic', ha='center', color='#555555')

    # Central Op-Amp Symbol (Triangle)
    tri_x = [4.5, 4.5, 7.5, 4.5]
    tri_y = [2.5, 6.5, 4.5, 2.5]
    triangle = patches.Polygon(list(zip(tri_x, tri_y)), closed=True, edgecolor='#003366', facecolor='#E8EEF5', lw=2.5)
    ax.add_patch(triangle)
    
    # Internal opamp text
    ax.text(5.2, 4.5, "opamp_2stage\n(SCL 1.2µm)", fontsize=11, fontweight='bold', ha='center', va='center', color='#002244')
    
    # Terminal labels
    ax.text(4.7, 5.5, "+", fontsize=16, fontweight='bold', va='center', color='darkgreen')
    ax.text(4.7, 3.5, "−", fontsize=18, fontweight='bold', va='center', color='darkred')
    
    # Supply pins
    ax.plot([5.5, 5.5], [5.8, 7.2], 'k-', lw=1.5)
    ax.text(5.5, 7.4, "VDD (5V)", fontsize=9.5, fontweight='bold', ha='center', color='red')
    ax.plot([5.5, 5.5], [3.2, 1.8], 'k-', lw=1.5)
    ax.text(5.5, 1.5, "VSS (0V)", fontsize=9.5, fontweight='bold', ha='center', color='blue')

    # Non-inverting input INP (top)
    ax.plot([2.0, 4.5], [5.5, 5.5], 'k-', lw=1.8)
    ax.text(3.0, 5.7, "INP", fontsize=10, fontweight='bold', color='darkgreen')
    
    # Signal source V_SIG
    circle_sig = patches.Circle((2.0, 4.5), 0.4, edgecolor='k', facecolor='#F5F5F5', lw=1.5)
    ax.add_patch(circle_sig)
    ax.text(2.0, 4.5, "~", fontsize=16, ha='center', va='center', fontweight='bold')
    ax.plot([2.0, 2.0], [5.5, 4.9], 'k-', lw=1.5)
    ax.plot([2.0, 2.0], [4.1, 3.0], 'k-', lw=1.5)
    ax.text(1.3, 4.5, "V_SIG\n(AC=1V,\nPulse)", fontsize=8.5, ha='right', va='center', fontweight='bold')

    # Common mode source V_CM (2.5V)
    circle_cm = patches.Circle((2.0, 2.5), 0.4, edgecolor='k', facecolor='#F5F5F5', lw=1.5)
    ax.add_patch(circle_cm)
    ax.text(2.0, 2.5, "DC", fontsize=9, ha='center', va='center', fontweight='bold')
    ax.plot([2.0, 2.0], [3.0, 2.9], 'k-', lw=1.5)
    ax.plot([2.0, 2.0], [2.1, 1.2], 'k-', lw=1.5)
    ax.text(1.3, 2.5, "V_CM\n(2.5 V)", fontsize=8.5, ha='right', va='center', fontweight='bold')

    # Ground at bottom of V_CM
    ax.plot([1.7, 2.3], [1.2, 1.2], 'k-', lw=2)
    ax.plot([1.85, 2.15], [1.05, 1.05], 'k-', lw=1.5)
    ax.plot([1.95, 2.05], [0.9, 0.9], 'k-', lw=1.2)

    # Inverting input INM (bottom)
    ax.plot([3.5, 4.5], [3.5, 3.5], 'k-', lw=1.8)
    ax.text(3.8, 3.2, "INM", fontsize=10, fontweight='bold', color='darkred')

    # Output VOUT
    ax.plot([7.5, 10.5], [4.5, 4.5], 'k-', lw=2.0)
    ax.plot(10.5, 4.5, 'bs', ms=7)
    ax.text(10.7, 4.5, "VOUT", fontsize=11, fontweight='bold', va='center', color='darkblue')

    # Load Capacitor CL = 10 pF
    draw_capacitor(ax, 10.0, 2.8, 0.8, "CL", "10 pF")
    ax.plot([10.0, 10.0], [4.5, 3.1], 'k-', lw=1.5)
    ax.plot([10.0, 10.0], [2.5, 1.2], 'k-', lw=1.5)
    ax.plot(10.0, 4.5, 'ko', ms=4)
    # Ground at CL bottom
    ax.plot([9.7, 10.3], [1.2, 1.2], 'k-', lw=2)
    ax.plot([9.85, 10.15], [1.05, 1.05], 'k-', lw=1.5)

    # Middlebrook Replica Feedback Network
    # Inductor L_DC from VOUT back to INM
    ax.plot([8.5, 8.5], [4.5, 6.8], 'k-', lw=1.5)
    ax.plot(8.5, 4.5, 'ko', ms=4)
    ax.plot([8.5, 7.0], [6.8, 6.8], 'k-', lw=1.5)
    
    # Inductor symbol
    ax.plot([7.0, 6.0], [6.8, 6.8], 'm-', lw=2.5)
    ax.text(6.5, 7.1, "L_DC (1 TH)", fontsize=9, fontweight='bold', color='purple', ha='center')
    
    ax.plot([6.0, 3.5], [6.8, 6.8], 'k-', lw=1.5)
    ax.plot([3.5, 3.5], [6.8, 3.5], 'k-', lw=1.5)
    ax.plot(3.5, 3.5, 'ko', ms=4)

    # AC grounding capacitor C_AC from INM to V_CM
    draw_capacitor(ax, 3.5, 2.0, 0.8, "C_AC", "1 TF")
    ax.plot([3.5, 3.5], [3.5, 2.3], 'k-', lw=1.5)
    ax.plot([3.5, 2.0], [1.7, 1.7], 'k-', lw=1.5)
    ax.plot([2.0, 2.0], [1.7, 2.1], 'k-', lw=1.5)

    # Explanatory box
    box_props = dict(boxstyle='round,pad=0.6', facecolor='#FFFBE6', edgecolor='#D4B106', lw=1.5)
    ax.text(6.0, -0.3,
            "Middlebrook Feedback Principle:\n"
            "• At DC (f=0): L_DC is short (0 Ω) and C_AC is open ==> 100% Negative Feedback locks DC operating point (VOUT = INM ≈ 2.5V).\n"
            "• At AC (f>1Hz): L_DC is open (~TH) and C_AC is short (~TF) ==> Feedback broken, yielding true Open-Loop AC Gain & Phase.",
            fontsize=8.5, ha='center', bbox=box_props, color='#333333')

    out_path = "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/plots/tb_opamp_schematic.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor='white', bbox_inches='tight')
    plt.close()
    print("Generated crisp testbench schematic:", out_path)

if __name__ == "__main__":
    create_opamp_schematic()
    create_tb_schematic()
