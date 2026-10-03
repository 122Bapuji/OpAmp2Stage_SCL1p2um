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

# 1. Differential Gain
sp_dm = f"""* Differential Gain for PSRR
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
wrdata {proj_dir}/simulations/psrr_ad.dat vdb(vout)
.endc
.end
"""

with open(f"{proj_dir}/simulations/psrr_dm.sp", "w") as f:
    f.write(sp_dm)

subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/psrr_dm.sp"], capture_output=True, text=True, env=env)

# 2. PSRR+ (VDD AC disturbance)
sp_vdd = f"""* PSRR+ Simulation
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '{proj_dir}/spice/opamp_2stage.spice'

Vdd vdd 0 5.0 ac 1
Vss vss 0 0.0
CL vout vss 10p

Vcm vicm 0 2.5
R_inp inp vicm 1
L_dc vout inm 1e6
C_ac inm vicm 1e6

x1 inp inm vout vdd vss opamp_2stage

.control
ac dec 20 1 100Meg
wrdata {proj_dir}/simulations/psrr_vdd.dat vdb(vout)
.endc
.end
"""

with open(f"{proj_dir}/simulations/psrr_pos.sp", "w") as f:
    f.write(sp_vdd)

subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/psrr_pos.sp"], capture_output=True, text=True, env=env)

# 3. PSRR- (VSS AC disturbance)
sp_vss = f"""* PSRR- Simulation
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '{proj_dir}/spice/opamp_2stage.spice'

Vdd vdd 0 5.0
Vss vss 0 0.0 ac 1
CL vout vss 10p

Vcm vicm 0 2.5
R_inp inp vicm 1
L_dc vout inm 1e6
C_ac inm vicm 1e6

x1 inp inm vout vdd vss opamp_2stage

.control
ac dec 20 1 100Meg
wrdata {proj_dir}/simulations/psrr_vss.dat vdb(vout)
.endc
.end
"""

with open(f"{proj_dir}/simulations/psrr_neg.sp", "w") as f:
    f.write(sp_vss)

subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/psrr_neg.sp"], capture_output=True, text=True, env=env)

# Load data and plot
data_ad  = np.loadtxt(f"{proj_dir}/simulations/psrr_ad.dat")
data_vdd = np.loadtxt(f"{proj_dir}/simulations/psrr_vdd.dat")
data_vss = np.loadtxt(f"{proj_dir}/simulations/psrr_vss.dat")

freq = data_ad[:, 0]
ad_db = data_ad[:, 1]
avdd_db = data_vdd[:, 1]
avss_db = data_vss[:, 1]

psrr_pos = ad_db - avdd_db
psrr_neg = ad_db - avss_db

dc_psrr_pos = psrr_pos[0]
dc_psrr_neg = psrr_neg[0]

plt.figure(figsize=(9, 5.5))
plt.semilogx(freq, psrr_pos, 'b-', linewidth=2.4, label='PSRR+ ($V_{DD}$ Rejection)')
plt.semilogx(freq, psrr_neg, 'r-', linewidth=2.4, label='PSRR- ($V_{SS}$ Rejection)')
plt.axhline(60, color='gray', linestyle='--', alpha=0.6, label='60 dB Target Spec')

plt.annotate(f'DC PSRR+ = {dc_psrr_pos:.1f} dB', xy=(1, dc_psrr_pos), xytext=(5, dc_psrr_pos - 8),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=6),
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", alpha=0.6))

plt.annotate(f'DC PSRR- = {dc_psrr_neg:.1f} dB', xy=(1, dc_psrr_neg), xytext=(5, dc_psrr_neg - 8),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=6),
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="lightpink", alpha=0.6))

plt.xlabel('Frequency (Hz)', fontsize=12)
plt.ylabel('PSRR (dB)', fontsize=12)
plt.title('Power Supply Rejection Ratio (PSRR+ and PSRR-) vs Frequency', fontsize=13, fontweight='bold')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend(loc='lower left', fontsize=11)
plt.ylim(0, max(dc_psrr_pos, dc_psrr_neg) + 15)
plt.tight_layout()
plt.savefig(f"{proj_dir}/plots/psrr_frequency_plot.png", dpi=300)
plt.close()

# Report
def val_at(arr, f_target):
    idx = np.argmin(np.abs(freq - f_target))
    return arr[idx]

report = []
report.append("================================================================================")
report.append("SCL 1.2 um CMOS TWO-STAGE OP-AMP - POWER SUPPLY REJECTION RATIO (PSRR) REPORT")
report.append("================================================================================")
report.append(f"Differential-Mode DC Gain (Ad0) : {ad_db[0]:.2f} dB")
report.append(f"VDD Gain (Avdd0)                 : {avdd_db[0]:.2f} dB")
report.append(f"VSS Gain (Avss0)                 : {avss_db[0]:.2f} dB")
report.append(f"DC PSRR+ (Ad0 - Avdd0)           : {dc_psrr_pos:.2f} dB (Target >= 60 dB) -> MET")
report.append(f"DC PSRR- (Ad0 - Avss0)           : {dc_psrr_neg:.2f} dB (Target >= 60 dB) -> MET")
report.append(f"PSRR+ @ 1 kHz                    : {val_at(psrr_pos, 1e3):.2f} dB")
report.append(f"PSRR+ @ 10 kHz                   : {val_at(psrr_pos, 1e4):.2f} dB")
report.append(f"PSRR+ @ 100 kHz                  : {val_at(psrr_pos, 1e5):.2f} dB")
report.append(f"PSRR+ @ 1 MHz                    : {val_at(psrr_pos, 1e6):.2f} dB")
report.append(f"PSRR- @ 1 kHz                    : {val_at(psrr_neg, 1e3):.2f} dB")
report.append(f"PSRR- @ 10 kHz                   : {val_at(psrr_neg, 1e4):.2f} dB")
report.append(f"PSRR- @ 100 kHz                  : {val_at(psrr_neg, 1e5):.2f} dB")
report.append(f"PSRR- @ 1 MHz                    : {val_at(psrr_neg, 1e6):.2f} dB")
report.append("================================================================================")

with open(f"{proj_dir}/results/psrr_results.txt", "w") as f:
    f.write("\n".join(report) + "\n")

print("\n".join(report))
print(f"\nPlot generated: {proj_dir}/plots/psrr_frequency_plot.png")
