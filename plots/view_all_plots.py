#!/usr/bin/env python3
"""
SCL 1.2 um CMOS Op-Amp: Interactive Graph Viewer
Displays all generated simulation waveforms and verification plots.
"""

import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

plot_files = [
    ("AC Frequency Response (Bode Gain & Phase)", "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/plots/ac_bode_plot.png"),
    ("DC Transfer Curve & Linear Gain", "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/plots/dc_transfer_curve.png"),
    ("Large-Signal Step Response & Slew Rate", "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/plots/transient_large_signal.png"),
    ("Small-Signal Step Response & Settling", "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/plots/transient_small_signal.png"),
    ("Common-Mode Rejection Ratio (CMRR)", "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/plots/cmrr_frequency_plot.png"),
    ("Power Supply Rejection Ratio (PSRR+ / PSRR-)", "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/plots/psrr_frequency_plot.png"),
    ("Input Common-Mode Range (ICMR)", "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/plots/icmr_curve.png"),
    ("15-Corner PVT Robustness Overlay", "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/plots/corner_comparison_plot.png"),
]

fig, axes = plt.subplots(4, 2, figsize=(18, 16))
fig.canvas.manager.set_window_title("SCL 1.2 um CMOS Op-Amp - Complete Verification Waveforms")
plt.subplots_adjust(left=0.04, right=0.96, top=0.95, bottom=0.03, hspace=0.25, wspace=0.15)

for idx, (title, path) in enumerate(plot_files):
    row = idx // 2
    col = idx % 2
    ax = axes[row, col]
    if os.path.exists(path):
        img = mpimg.imread(path)
        ax.imshow(img)
        ax.set_title(title, fontsize=12, fontweight='bold', pad=6)
        ax.axis('off')
    else:
        ax.text(0.5, 0.5, f"Plot not found:\n{os.path.basename(path)}", ha='center', va='center')
        ax.axis('off')

print("Displaying all generated simulation waveforms. Close the window when finished.")
plt.show()
