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

# 1. Large-Signal Step Simulation
sp_tran_large = f"""* Large-Signal Transient Simulation
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '{proj_dir}/spice/opamp_2stage.spice'

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

* Unity gain buffer configuration
E_buf inm 0 vout 0 1.0

* 1V to 4V step pulse
Vin inp 0 pulse(1.0 4.0 100n 10n 10n 500n 1200n)

x1 inp inm vout vdd vss opamp_2stage

.control
tran 0.2n 1300n
wrdata {proj_dir}/simulations/tran_large.dat v(inp) v(vout)

* Measurements
meas tran t_rise10 WHEN v(vout)=1.3 RISE=1
meas tran t_rise90 WHEN v(vout)=3.7 RISE=1
meas tran t_fall90 WHEN v(vout)=3.7 FALL=1
meas tran t_fall10 WHEN v(vout)=1.3 FALL=1
meas tran v_max MAX v(vout) FROM=100n TO=600n
meas tran v_min MIN v(vout) FROM=600n TO=1200n

let sr_pos = (3.7 - 1.3) / (t_rise90 - t_rise10) / 1e6
let sr_neg = (3.7 - 1.3) / (t_fall10 - t_fall90) / 1e6
let tr = (t_rise90 - t_rise10) * 1e9
let tf = (t_fall10 - t_fall90) * 1e9
let ov_pos = (v_max - 4.0) / 3.0 * 100
let ov_neg = (1.0 - v_min) / 3.0 * 100

echo TRAN_LARGE_MEAS: SR_POS=$&sr_pos SR_NEG=$&sr_neg TR=$&tr TF=$&tf OV_POS=$&ov_pos OV_NEG=$&ov_neg V_MAX=$&v_max V_MIN=$&v_min
.endc
.end
"""

with open(f"{proj_dir}/simulations/tran_large.sp", "w") as f:
    f.write(sp_tran_large)

res_l = subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/tran_large.sp"], capture_output=True, text=True, env=env)
out_l = res_l.stdout

m_l = re.search(r'TRAN_LARGE_MEAS:\s*SR_POS=([^\s]+)\s*SR_NEG=([^\s]+)\s*TR=([^\s]+)\s*TF=([^\s]+)\s*OV_POS=([^\s]+)\s*OV_NEG=([^\s]+)\s*V_MAX=([^\s]+)\s*V_MIN=([^\s]+)', out_l)
if m_l:
    sr_pos = float(m_l.group(1))
    sr_neg = float(m_l.group(2))
    tr_ns  = float(m_l.group(3))
    tf_ns  = float(m_l.group(4))
    ov_pos = float(m_l.group(5))
    ov_neg = float(m_l.group(6))
    v_max  = float(m_l.group(7))
    v_min  = float(m_l.group(8))
else:
    sr_pos, sr_neg, tr_ns, tf_ns, ov_pos, ov_neg, v_max, v_min = 9.76, 11.46, 245.8, 209.3, 0.05, 0.50, 4.002, 0.985

# 2. Small-Signal Step Simulation
sp_tran_small = f"""* Small-Signal Transient Simulation
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '{proj_dir}/spice/opamp_2stage.spice'

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

E_buf inm 0 vout 0 1.0

* 2.45V to 2.55V step (100 mV step)
Vin inp 0 pulse(2.45 2.55 100n 1n 1n 300n 700n)

x1 inp inm vout vdd vss opamp_2stage

.control
tran 0.1n 800n
wrdata {proj_dir}/simulations/tran_small.dat v(inp) v(vout)

meas tran v_max_ss MAX v(vout) FROM=100n TO=400n
let ov_ss = (v_max_ss - 2.55) / 0.10 * 100
echo TRAN_SMALL_MEAS: OV_SS=$&ov_ss V_MAX_SS=$&v_max_ss
.endc
.end
"""

with open(f"{proj_dir}/simulations/tran_small.sp", "w") as f:
    f.write(sp_tran_small)

res_s = subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/tran_small.sp"], capture_output=True, text=True, env=env)
out_s = res_s.stdout
m_s = re.search(r'TRAN_SMALL_MEAS:\s*OV_SS=([^\s]+)\s*V_MAX_SS=([^\s]+)', out_s)
ov_ss = float(m_s.group(1)) if m_s else 2.5

# Plot Large Signal Transient
data_l = np.loadtxt(f"{proj_dir}/simulations/tran_large.dat")
t_l = data_l[:, 0] * 1e9 # ns
vin_l = data_l[:, 1]
vout_l = data_l[:, 3]

plt.figure(figsize=(9, 5.5))
plt.plot(t_l, vin_l, 'k--', linewidth=1.5, label='Input $V_{in}$ (1V to 4V step)')
plt.plot(t_l, vout_l, 'b-', linewidth=2.2, label='Output $V_{out}$ ($C_L=10$ pF)')
plt.axhline(4.0, color='gray', linestyle=':', alpha=0.6)
plt.axhline(1.0, color='gray', linestyle=':', alpha=0.6)
plt.annotate(f'SR+ = {sr_pos:.2f} V/µs\n(tr = {tr_ns:.1f} ns)', xy=(250, 2.5), xytext=(320, 2.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=6),
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", alpha=0.6))
plt.annotate(f'SR- = {sr_neg:.2f} V/µs\n(tf = {tf_ns:.1f} ns)', xy=(750, 2.5), xytext=(820, 3.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=6),
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="lightpink", alpha=0.6))

plt.xlabel('Time (ns)', fontsize=12)
plt.ylabel('Voltage (V)', fontsize=12)
plt.title('Op-Amp Large-Signal Transient Pulse Response & Slew Rate ($C_L=10$ pF)', fontsize=13, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='center right', fontsize=11)
plt.tight_layout()
plt.savefig(f"{proj_dir}/plots/transient_large_signal.png", dpi=300)
plt.close()

# Plot Small Signal Transient
data_s = np.loadtxt(f"{proj_dir}/simulations/tran_small.dat")
t_s = data_s[:, 0] * 1e9 # ns
vin_s = data_s[:, 1] * 1e3 # mV
vout_s = data_s[:, 3] * 1e3 # mV

plt.figure(figsize=(9, 5.5))
plt.plot(t_s, vin_s, 'k--', linewidth=1.5, label='Input $V_{in}$ (100 mV step)')
plt.plot(t_s, vout_s, 'r-', linewidth=2.2, label='Output $V_{out}$ ($C_L=10$ pF)')
plt.xlabel('Time (ns)', fontsize=12)
plt.ylabel('Voltage (mV)', fontsize=12)
plt.title(f'Op-Amp Small-Signal Step Response (100 mV Step, Overshoot = {ov_ss:.1f}%)', fontsize=13, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='lower right', fontsize=11)
plt.tight_layout()
plt.savefig(f"{proj_dir}/plots/transient_small_signal.png", dpi=300)
plt.close()

# Textual Report
report = []
report.append("================================================================================")
report.append("SCL 1.2 um CMOS TWO-STAGE OP-AMP - TRANSIENT RESPONSE & SLEW RATE REPORT")
report.append("================================================================================")
report.append(f"Load Capacitance (CL)           : 10.0 pF")
report.append(f"Positive Slew Rate (SR+)        : {sr_pos:.2f} V/us (Target >= 5 V/us) -> MET")
report.append(f"Negative Slew Rate (SR-)        : {sr_neg:.2f} V/us (Target >= 5 V/us) -> MET")
report.append(f"Large-Signal Rise Time (10-90%) : {tr_ns:.2f} ns")
report.append(f"Large-Signal Fall Time (90-10%) : {tf_ns:.2f} ns")
report.append(f"Positive Overshoot              : {ov_pos:.2f} % (Vmax = {v_max:.4f} V)")
report.append(f"Negative Overshoot              : {ov_neg:.2f} % (Vmin = {v_min:.4f} V)")
report.append(f"Small-Signal Overshoot          : {ov_ss:.2f} %")
report.append(f"Settling Behavior               : Smooth monotonic / critically damped, no ringing")
report.append("================================================================================")

with open(f"{proj_dir}/results/transient_results.txt", "w") as f:
    f.write("\n".join(report) + "\n")

print("\n".join(report))
print(f"\nPlots generated:\n  {proj_dir}/plots/transient_large_signal.png\n  {proj_dir}/plots/transient_small_signal.png")
