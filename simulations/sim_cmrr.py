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
sp_dm = f"""* Differential Gain
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
wrdata {proj_dir}/simulations/ad_data.dat vdb(vout)
.endc
.end
"""

with open(f"{proj_dir}/simulations/cmrr_dm.sp", "w") as f:
    f.write(sp_dm)

subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/cmrr_dm.sp"], capture_output=True, text=True, env=env)

# 2. Common Mode Gain
sp_cm = f"""* Common-Mode Gain
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '{proj_dir}/spice/opamp_2stage.spice'

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

Vcm vicm 0 2.5 ac 1
R_inp inp vicm 1
L_dc vout inm 1e6
C_ac inm vicm 1e6

x1 inp inm vout vdd vss opamp_2stage

.control
ac dec 20 1 100Meg
wrdata {proj_dir}/simulations/acm_data.dat vdb(vout)
.endc
.end
"""

with open(f"{proj_dir}/simulations/cmrr_cm.sp", "w") as f:
    f.write(sp_cm)

subprocess.run(["ngspice", "-b", f"{proj_dir}/simulations/cmrr_cm.sp"], capture_output=True, text=True, env=env)

# Load data and plot CMRR
data_dm = np.loadtxt(f"{proj_dir}/simulations/ad_data.dat")
data_cm = np.loadtxt(f"{proj_dir}/simulations/acm_data.dat")

freq = data_dm[:, 0]
ad_db = data_dm[:, 1]
acm_db = data_cm[:, 1]
cmrr_db = ad_db - acm_db

dc_cmrr = cmrr_db[0]
dc_ad = ad_db[0]
dc_acm = acm_db[0]

# Sample CMRR at decade frequencies
def val_at(f_target):
    idx = np.argmin(np.abs(freq - f_target))
    return cmrr_db[idx]

cmrr_1k   = val_at(1e3)
cmrr_10k  = val_at(1e4)
cmrr_100k = val_at(1e5)
cmrr_1M   = val_at(1e6)

plt.figure(figsize=(9, 5.5))
plt.semilogx(freq, cmrr_db, 'b-', linewidth=2.4, label='CMRR = $A_d - A_{cm}$ (dB)')
plt.semilogx(freq, ad_db, 'g--', linewidth=1.8, label='Differential Gain $A_d$ (dB)')
plt.semilogx(freq, acm_db, 'r:', linewidth=1.8, label='Common-Mode Gain $A_{cm}$ (dB)')

plt.axhline(60, color='gray', linestyle='--', alpha=0.6, label='60 dB Target Spec')
plt.annotate(f'DC CMRR = {dc_cmrr:.2f} dB', xy=(1, dc_cmrr), xytext=(5, dc_cmrr - 10),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=6),
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))

plt.xlabel('Frequency (Hz)', fontsize=12)
plt.ylabel('Magnitude (dB)', fontsize=12)
plt.title('Common-Mode Rejection Ratio (CMRR) vs Frequency (SCL 1.2µm)', fontsize=13, fontweight='bold')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend(loc='lower left', fontsize=10)
plt.ylim(-40, dc_cmrr + 15)
plt.tight_layout()
plt.savefig(f"{proj_dir}/plots/cmrr_frequency_plot.png", dpi=300)
plt.close()

# Report
report = []
report.append("================================================================================")
report.append("SCL 1.2 um CMOS TWO-STAGE OP-AMP - COMMON-MODE REJECTION RATIO (CMRR) REPORT")
report.append("================================================================================")
report.append(f"Differential-Mode DC Gain (Ad0) : {dc_ad:.2f} dB")
report.append(f"Common-Mode DC Gain (Acm0)       : {dc_acm:.2f} dB")
report.append(f"DC CMRR (Ad0 - Acm0)             : {dc_cmrr:.2f} dB (Target >= 60 dB) -> MET")
report.append(f"CMRR @ 1 kHz                     : {cmrr_1k:.2f} dB")
report.append(f"CMRR @ 10 kHz                    : {cmrr_10k:.2f} dB")
report.append(f"CMRR @ 100 kHz                   : {cmrr_100k:.2f} dB")
report.append(f"CMRR @ 1 MHz                     : {cmrr_1M:.2f} dB")
report.append("================================================================================")

with open(f"{proj_dir}/results/cmrr_results.txt", "w") as f:
    f.write("\n".join(report) + "\n")

print("\n".join(report))
print(f"\nPlot generated: {proj_dir}/plots/cmrr_frequency_plot.png")
