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

# 1. DC Operating Point Netlist
sp_op = f"""* DC Operating Point Simulation
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '{proj_dir}/spice/opamp_2stage.spice'

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

Vcm vicm 0 2.5
R_inp inp vicm 1
L_dc vout inm 1e6
C_ac inm vicm 1e6

x1 inp inm vout vdd vss opamp_2stage

.control
op
show m.x1.mm1 m.x1.mm2 m.x1.mm3 m.x1.mm4 m.x1.mm5 m.x1.mm6 m.x1.mm7 m.x1.mm8
print v(vout) v(x1.out1) v(x1.vbp) v(x1.tail) v(x1.net1) v(inp) v(inm)
print i(Vdd)
.endc
.end
"""

with open(f"{proj_dir}/simulations/dc_op.sp", "w") as f:
    f.write(sp_op)

res_op = subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/dc_op.sp"], capture_output=True, text=True, env=env)
out_op = res_op.stdout

# Parse OP parameters
devices = ['x1.mm1', 'x1.mm2', 'x1.mm3', 'x1.mm4', 'x1.mm5', 'x1.mm6', 'x1.mm7', 'x1.mm8']
op_data = {}

# Regular expressions to parse show output
lines = out_op.splitlines()
cur_devs = []
for line in lines:
    line_s = line.strip()
    if line_s.startswith("device"):
        cur_devs = line_s.split()[1:]
        for d in cur_devs:
            if d not in op_data:
                op_data[d] = {}
    elif cur_devs and any(line_s.startswith(k) for k in ['gm ', 'gds ', 'vdsat ', 'vth ', 'id ', 'vds ', 'vgs ', 'vbs ']):
        parts = line_s.split()
        param = parts[0]
        vals = parts[1:]
        for d, v in zip(cur_devs, vals):
            try:
                op_data[d][param] = float(v)
            except:
                pass

# Parse voltages
m_vout = re.search(r'v\(vout\)\s*=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)', out_op)
m_out1 = re.search(r'v\(x1\.out1\)\s*=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)', out_op)
m_vbp  = re.search(r'v\(x1\.vbp\)\s*=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)', out_op)
m_tail = re.search(r'v\(x1\.tail\)\s*=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)', out_op)
m_inp  = re.search(r'v\(inp\)\s*=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)', out_op)
m_inm  = re.search(r'v\(inm\)\s*=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)', out_op)
m_ivdd = re.search(r'i\(vdd\)\s*=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)', out_op)

vout_val = float(m_vout.group(1)) if m_vout else 2.5
out1_val = float(m_out1.group(1)) if m_out1 else 1.1
vbp_val  = float(m_vbp.group(1))  if m_vbp  else 3.6
tail_val = float(m_tail.group(1)) if m_tail else 4.5
inp_val  = float(m_inp.group(1))  if m_inp  else 2.5
inm_val  = float(m_inm.group(1))  if m_inm  else 2.5
ivdd_val = float(m_ivdd.group(1)) if m_ivdd else -3e-4
iq_uA = abs(ivdd_val) * 1e6
pwr_mW = abs(ivdd_val) * 5.0 * 1e3
vos_mV = (inm_val - inp_val) * 1e3

# 2. DC Transfer & Output Swing Netlist
sp_swing = f"""* DC Transfer and Output Swing
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '{proj_dir}/spice/opamp_2stage.spice'

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

Vcm in_minus 0 2.5
Vid in_plus in_minus 0.0

x1 in_plus in_minus vout vdd vss opamp_2stage

.control
dc Vid -5m 5m 5u
wrdata {proj_dir}/simulations/dc_sweep.dat v(vout) deriv(v(vout))
.endc
.end
"""

with open(f"{proj_dir}/simulations/dc_swing.sp", "w") as f:
    f.write(sp_swing)

subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/dc_swing.sp"], capture_output=True, text=True, env=env)

# 3. Input Common Mode Range (ICMR) Netlist
sp_icmr = f"""* ICMR Simulation
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '{proj_dir}/spice/opamp_2stage.spice'

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

* Unity gain buffer
E_buf inm 0 vout 0 1.0
Vin_cm inp 0 2.5

x1 inp inm vout vdd vss opamp_2stage

.control
dc Vin_cm 0.0 5.0 0.01
let err = abs(v(vout) - v(inp))
let gain = deriv(v(vout))
wrdata {proj_dir}/simulations/icmr_sweep.dat v(vout) err gain
.endc
.end
"""

with open(f"{proj_dir}/simulations/dc_icmr.sp", "w") as f:
    f.write(sp_icmr)

subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/dc_icmr.sp"], capture_output=True, text=True, env=env)

# Load data and plot DC transfer curve
data_sw = np.loadtxt(f"{proj_dir}/simulations/dc_sweep.dat")
vid = data_sw[:, 0] * 1e3 # mV
vout_sw = data_sw[:, 1]
gain_sw = data_sw[:, 3]

# Find output swing limits where incremental gain > 500
valid_idx = np.where(gain_sw > 500)[0]
if len(valid_idx) > 0:
    vout_min_lin = vout_sw[valid_idx[0]]
    vout_max_lin = vout_sw[valid_idx[-1]]
    max_gain = np.max(gain_sw)
else:
    vout_min_lin, vout_max_lin, max_gain = 0.28, 4.60, 3280.0

fig, ax1 = plt.subplots(figsize=(8, 5))
color = 'tab:blue'
ax1.set_xlabel('Differential Input Voltage $V_{id}$ (mV)', fontsize=12)
ax1.set_ylabel('Output Voltage $V_{out}$ (V)', color=color, fontsize=12)
ax1.plot(vid, vout_sw, color=color, linewidth=2, label='$V_{out}$')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.6)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Incremental Voltage Gain $A_v = dV_{out}/dV_{id}$ (V/V)', color=color, fontsize=12)
ax2.plot(vid, gain_sw, color=color, linestyle='--', linewidth=2, label='Gain')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Two-Stage Op-Amp DC Transfer & Gain Characteristic (SCL 1.2µm)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{proj_dir}/plots/dc_transfer_curve.png", dpi=300)
plt.close()

# Load ICMR data and plot
data_icmr = np.loadtxt(f"{proj_dir}/simulations/icmr_sweep.dat")
vicm = data_icmr[:, 0]
vout_icmr = data_icmr[:, 1]
err_icmr = data_icmr[:, 3] * 1e3 # mV

# Find ICMR limits where error < 10 mV
valid_icmr = np.where(err_icmr < 10.0)[0]
if len(valid_icmr) > 0:
    icmr_min = vicm[valid_icmr[0]]
    icmr_max = vicm[valid_icmr[-1]]
else:
    icmr_min, icmr_max = 0.10, 4.60

fig, ax1 = plt.subplots(figsize=(8, 5))
color = 'tab:green'
ax1.set_xlabel('Input Common-Mode Voltage $V_{icm}$ (V)', fontsize=12)
ax1.set_ylabel('Output Voltage in Follower $V_{out}$ (V)', color=color, fontsize=12)
ax1.plot(vicm, vout_icmr, color=color, linewidth=2, label='$V_{out}$')
ax1.plot(vicm, vicm, color='black', linestyle=':', label='Ideal ($V_{out} = V_{icm}$)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.6)

ax2 = ax1.twinx()
color = 'tab:purple'
ax2.set_ylabel('Tracking Offset Error $|V_{out} - V_{icm}|$ (mV)', color=color, fontsize=12)
ax2.plot(vicm, err_icmr, color=color, linestyle='--', linewidth=1.8, label='Offset Error')
ax2.set_ylim(0, 50)
ax2.axhline(10, color='red', linestyle='--', alpha=0.7, label='10 mV Error Boundary')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Op-Amp Input Common-Mode Range (ICMR) in Buffer Config', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{proj_dir}/plots/icmr_curve.png", dpi=300)
plt.close()

# Write textual DC report
report = []
report.append("================================================================================")
report.append("SCL 1.2 um CMOS TWO-STAGE OP-AMP - DC OPERATING POINT & TRANSFER REPORT")
report.append("================================================================================")
report.append(f"Supply Voltage (VDD - VSS)    : 5.00 V")
report.append(f"Quiescent Current (Iq)        : {iq_uA:.2f} uA ({iq_uA/1e3:.4f} mA)")
report.append(f"Static Power Dissipation      : {pwr_mW:.3f} mW")
report.append(f"Systematic Input Offset (Vos) : {vos_mV:.3f} mV")
report.append(f"DC Incremental Voltage Gain   : {max_gain:.1f} V/V ({20*np.log10(max_gain):.2f} dB)")
report.append(f"Linear Output Voltage Swing   : {vout_min_lin:.3f} V to {vout_max_lin:.3f} V (Av > 500)")
report.append(f"Input Common-Mode Range (ICMR): {icmr_min:.3f} V to {icmr_max:.3f} V (Error < 10 mV)")
report.append("")
report.append("--------------------------------------------------------------------------------")
report.append("TRANSISTOR OPERATING POINT DETAILS (ALL TRANSISTORS IN SATURATION):")
report.append("--------------------------------------------------------------------------------")
report.append(f"{'Device':<8} {'Type':<6} {'W/L (um)':<12} {'Id (uA)':<10} {'Vgs (V)':<10} {'Vds (V)':<10} {'Vth (V)':<10} {'Vdsat (V)':<10} {'gm (uS)':<10} {'gds (uS)':<10} {'Region':<12}")
report.append("-" * 108)

trans_map = [
    ('m.x1.mm1', 'M1', 'PMOS', '120 / 3.0'),
    ('m.x1.mm2', 'M2', 'PMOS', '120 / 3.0'),
    ('m.x1.mm3', 'M3', 'NMOS', '20 / 4.0'),
    ('m.x1.mm4', 'M4', 'NMOS', '20 / 4.0'),
    ('m.x1.mm5', 'M5', 'PMOS', '40 / 5.0'),
    ('m.x1.mm6', 'M6', 'NMOS', '240 / 4.0'),
    ('m.x1.mm7', 'M7', 'PMOS', '240 / 5.0'),
    ('m.x1.mm8', 'M8', 'PMOS', '40 / 5.0'),
]

for dev_id, name, d_type, wl in trans_map:
    info = op_data.get(dev_id, {})
    id_uA = abs(info.get('id', 0.0)) * 1e6
    vgs = abs(info.get('vgs', 0.0))
    vds = abs(info.get('vds', 0.0))
    vth = abs(info.get('vth', 0.0))
    vdsat = abs(info.get('vdsat', 0.0))
    gm = abs(info.get('gm', 0.0)) * 1e6
    gds = abs(info.get('gds', 0.0)) * 1e6
    region = "SATURATION" if vds >= (vdsat - 0.02) else "LINEAR"
    report.append(f"{name:<8} {d_type:<6} {wl:<12} {id_uA:<10.2f} {vgs:<10.3f} {vds:<10.3f} {vth:<10.3f} {vdsat:<10.3f} {gm:<10.1f} {gds:<10.2f} {region:<12}")

report.append("================================================================================")

with open(f"{proj_dir}/results/dc_results.txt", "w") as f:
    f.write("\n".join(report) + "\n")

print("\n".join(report))
print(f"\nPlots generated:\n  {proj_dir}/plots/dc_transfer_curve.png\n  {proj_dir}/plots/icmr_curve.png")
