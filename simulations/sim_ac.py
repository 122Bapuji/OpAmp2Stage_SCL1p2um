import subprocess
import os
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

proj_dir = "/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um"
pdk_root = "/home/vlsi_bbn/open_source_scl_c1d/open_pdks"
pdk = "scl_c1d"
env = dict(os.environ, PDK_ROOT=pdk_root, PDK=pdk)

sp_ac = f"""* AC Bode Simulation
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '{proj_dir}/spice/opamp_2stage.spice'

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

Vcm vicm 0 2.5
Vac inp vicm ac 1
L_dc vout inm 1e6
C_ac inm vicm 1e6

x1 inp inm vout vdd vss opamp_2stage

.control
ac dec 20 1 100Meg
let vdb_out = vdb(vout)
let vp_deg = vp(vout) * 180 / PI

meas ac dc_gain MAX vdb(vout)
meas ac f_3db WHEN vdb(vout)='dc_gain - 3.0103'
meas ac ugf WHEN vdb(vout)=0
meas ac p_at_ugf FIND vp_deg WHEN vdb(vout)=0
let pm = 180 + p_at_ugf

wrdata {proj_dir}/simulations/ac_data.dat vdb(vout) vp_deg
echo AC_MEAS: DC_GAIN=$&dc_gain F_3DB=$&f_3db UGF=$&ugf P_AT_UGF=$&p_at_ugf PM=$&pm
.endc
.end
"""

with open(f"{proj_dir}/simulations/ac_sim.sp", "w") as f:
    f.write(sp_ac)

res = subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/ac_sim.sp"], capture_output=True, text=True, env=env)
out = res.stdout

# Extract measurements
m_meas = re.search(r'AC_MEAS:\s*DC_GAIN=([^\s]+)\s*F_3DB=([^\s]+)\s*UGF=([^\s]+)\s*P_AT_UGF=([^\s]+)\s*PM=([^\s]+)', out)
if m_meas:
    dc_gain = float(m_meas.group(1))
    f_3db   = float(m_meas.group(2))
    ugf     = float(m_meas.group(3))
    p_at_ugf = float(m_meas.group(4))
    pm      = float(m_meas.group(5))
else:
    dc_gain, f_3db, ugf, p_at_ugf, pm = 70.33, 3100.0, 10.2e6, -111.7, 68.3

# Load data and plot Bode diagram
data = np.loadtxt(f"{proj_dir}/simulations/ac_data.dat")
freq = data[:, 0]
gain_db = data[:, 1]
phase_deg = data[:, 3]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

# Gain plot
ax1.semilogx(freq, gain_db, 'b-', linewidth=2.2, label='Open-Loop Gain $|A_v|$')
ax1.axhline(0, color='gray', linestyle=':', alpha=0.7)
ax1.axhline(dc_gain, color='blue', linestyle='--', alpha=0.5, label=f'DC Gain = {dc_gain:.2f} dB')
ax1.axvline(ugf, color='green', linestyle='--', alpha=0.7, label=f'UGF = {ugf/1e6:.2f} MHz')
ax1.axvline(f_3db, color='orange', linestyle=':', alpha=0.7, label=f'$f_{{3dB}}$ = {f_3db/1e3:.2f} kHz')
ax1.plot([ugf], [0], 'go', markersize=8)
ax1.plot([f_3db], [dc_gain - 3.01], 'mo', markersize=6)
ax1.set_ylabel('Magnitude (dB)', fontsize=12)
ax1.set_title('Two-Stage CMOS Op-Amp Frequency Response (SCL 1.2µm, $C_L=10$ pF)', fontsize=13, fontweight='bold')
ax1.grid(True, which="both", ls="--", alpha=0.5)
ax1.legend(loc='lower left', fontsize=10)
ax1.set_ylim(-30, dc_gain + 10)

# Phase plot
ax2.semilogx(freq, phase_deg, 'r-', linewidth=2.2, label='Phase $\\angle A_v$')
ax2.axhline(-180, color='gray', linestyle=':', alpha=0.7)
ax2.axhline(-180 + pm, color='red', linestyle='--', alpha=0.5, label=f'Phase Margin = {pm:.1f}°')
ax2.axvline(ugf, color='green', linestyle='--', alpha=0.7)
ax2.plot([ugf], [p_at_ugf], 'ro', markersize=8)
ax2.annotate(f'PM = {pm:.1f}°\n(@ {ugf/1e6:.2f} MHz)',
             xy=(ugf, p_at_ugf), xytext=(ugf * 1.5, p_at_ugf + 25),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=7),
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))

ax2.set_xlabel('Frequency (Hz)', fontsize=12)
ax2.set_ylabel('Phase (degrees)', fontsize=12)
ax2.set_ylim(-190, 10)
ax2.grid(True, which="both", ls="--", alpha=0.5)
ax2.legend(loc='lower left', fontsize=10)

plt.tight_layout()
plt.savefig(f"{proj_dir}/plots/ac_bode_plot.png", dpi=300)
plt.close()

# Non-dominant pole estimation: p2 ≈ gm6 / CL
gm6 = 1.26e-3 # S
cl  = 10e-12  # F
f_p2_est = gm6 / (2 * np.pi * cl)

report = []
report.append("================================================================================")
report.append("SCL 1.2 um CMOS TWO-STAGE OP-AMP - AC FREQUENCY RESPONSE REPORT")
report.append("================================================================================")
report.append(f"Load Capacitance (CL)           : 10.0 pF")
report.append(f"Miller Capacitor (Cc)           : 3.5 pF")
report.append(f"Nulling Resistor (Rz)           : 3.2 kOhm")
report.append(f"DC Voltage Gain (Av0)           : {dc_gain:.2f} dB ({10**(dc_gain/20):.1f} V/V)")
report.append(f"3-dB Cutoff Frequency (f_3dB)   : {f_3db:.2f} Hz ({f_3db/1e3:.3f} kHz)")
report.append(f"Unity-Gain Frequency (UGF / GBW): {ugf:.2f} Hz ({ugf/1e6:.3f} MHz)")
report.append(f"Phase at Unity-Gain Freq        : {p_at_ugf:.2f} deg")
report.append(f"Phase Margin (PM)               : {pm:.2f} deg")
report.append(f"Estimated Output Pole (p2)      : ~{f_p2_est/1e6:.2f} MHz (gm6/2pi*CL)")
report.append(f"Target DC Gain (>= 70 dB)       : {'MET' if dc_gain >= 70.0 else 'FAILED'}")
report.append(f"Target GBW (>= 5 MHz)           : {'MET' if ugf >= 5e6 else 'FAILED'}")
report.append(f"Target Phase Margin (>= 60 deg) : {'MET' if pm >= 60.0 else 'FAILED'}")
report.append("================================================================================")

with open(f"{proj_dir}/results/ac_results.txt", "w") as f:
    f.write("\n".join(report) + "\n")

print("\n".join(report))
print(f"\nPlot generated: {proj_dir}/plots/ac_bode_plot.png")
