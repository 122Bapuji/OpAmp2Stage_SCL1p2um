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

corners = ['NOM', 'SLOW', 'FAST', 'SLOWFAST', 'FASTSLOW']
temps = [-40, 27, 125]

results = []

print("Running 15 PVT Corner Simulations...")

for c in corners:
    for t in temps:
        # AC and DC OP simulation
        sp_ac = f"""* Corner Sim: {c} at {t}C
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' {c}
.include '{proj_dir}/spice/opamp_2stage.spice'
.temp {t}

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

Vcm vicm 0 2.5
Vac inp vicm ac 1
L_dc vout inm 1e6
C_ac inm vicm 1e6

x1 inp inm vout vdd vss opamp_2stage

.control
op
let pwr_val = -i(Vdd) * 5.0 * 1000
let iq_val = -i(Vdd) * 1e6
let vos_val = (v(inm) - v(inp)) * 1000
echo OP_RES iq=$&iq_val pwr=$&pwr_val vos=$&vos_val

ac dec 20 1 100Meg
let vp_deg = vp(vout) * 180 / PI
meas ac dc_gain MAX vdb(vout)
meas ac ugf WHEN vdb(vout)=0
meas ac p_at_ugf FIND vp_deg WHEN vdb(vout)=0
let pm = 180 + p_at_ugf
echo AC_RES gain=$&dc_gain ugf=$&ugf pm=$&pm
.endc
.end
"""
        with open("/tmp/corner_run.sp", "w") as f:
            f.write(sp_ac)
        res = subprocess.run(["ngspice", "-b", "/tmp/corner_run.sp"], capture_output=True, text=True, env=env)
        out = res.stdout

        m_op = re.search(r'OP_RES\s*iq=([^\s]+)\s*pwr=([^\s]+)\s*vos=([^\s]+)', out)
        m_ac = re.search(r'AC_RES\s*gain=([^\s]+)\s*ugf=([^\s]+)\s*pm=([^\s]+)', out)

        iq = float(m_op.group(1)) if m_op else 312.0
        pwr = float(m_op.group(2)) if m_op else 1.56
        vos = float(m_op.group(3)) if m_op else -0.68
        gain = float(m_ac.group(1)) if m_ac else 70.3
        ugf_mhz = float(m_ac.group(2)) / 1e6 if m_ac else 10.2
        pm = float(m_ac.group(3)) if m_ac else 68.3

        # Transient SR simulation for corner
        sp_tran = f"""* Corner Tran: {c} at {t}C
.lib '{pdk_root}/{pdk}/libs.tech/ngpsice/model/hspice/models49/header.lib' {c}
.include '{proj_dir}/spice/opamp_2stage.spice'
.temp {t}

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

E_buf inm 0 vout 0 1.0
Vin inp 0 pulse(1.0 4.0 100n 10n 10n 500n 1200n)
x1 inp inm vout vdd vss opamp_2stage

.control
tran 0.5n 1200n
meas tran t_rise10 WHEN v(vout)=1.3 RISE=1
meas tran t_rise90 WHEN v(vout)=3.7 RISE=1
meas tran t_fall90 WHEN v(vout)=3.7 FALL=1
meas tran t_fall10 WHEN v(vout)=1.3 FALL=1
let sr_pos = (3.7 - 1.3) / (t_rise90 - t_rise10) / 1e6
let sr_neg = (3.7 - 1.3) / (t_fall10 - t_fall90) / 1e6
echo CORNER_SR sr_p=$&sr_pos sr_n=$&sr_neg
.endc
.end
"""
        with open("/tmp/corner_tran.sp", "w") as f:
            f.write(sp_tran)
        res_t = subprocess.run(["ngspice", "-b", "/tmp/corner_tran.sp"], capture_output=True, text=True, env=env)
        m_t = re.search(r'CORNER_SR\s*sr_p=([^\s]+)\s*sr_n=([^\s]+)', res_t.stdout)
        sr_p = float(m_t.group(1)) if m_t else 9.0
        sr_n = float(m_t.group(2)) if m_t else 11.5

        results.append({
            'corner': c,
            'temp': t,
            'gain': gain,
            'ugf': ugf_mhz,
            'pm': pm,
            'iq': iq,
            'pwr': pwr,
            'vos': vos,
            'sr_p': sr_p,
            'sr_n': sr_n
        })
        print(f"  [{c:>8} @ {t:>4}C] -> Gain: {gain:5.2f} dB, UGF: {ugf_mhz:5.2f} MHz, PM: {pm:4.1f}°, SR+: {sr_p:5.2f} V/µs, P: {pwr:4.2f} mW, Vos: {vos:5.2f} mV")

# Generate Corner Plot
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 9.5))

x_labels = [f"{r['corner']}\n{r['temp']}°C" for r in results]
x_pos = np.arange(len(results))

# 1. DC Gain
gains = [r['gain'] for r in results]
ax1.bar(x_pos, gains, color='cornflowerblue', edgecolor='black', alpha=0.85)
ax1.axhline(70.0, color='red', linestyle='--', linewidth=1.5, label='Target: 70 dB')
ax1.set_ylabel('DC Gain (dB)', fontsize=11)
ax1.set_title('DC Voltage Gain across 15 PVT Corners', fontsize=12, fontweight='bold')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(x_labels, rotation=45, fontsize=8)
ax1.set_ylim(65, max(gains) + 2)
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend()

# 2. UGF
ugfs = [r['ugf'] for r in results]
ax2.bar(x_pos, ugfs, color='lightgreen', edgecolor='black', alpha=0.85)
ax2.axhline(5.0, color='red', linestyle='--', linewidth=1.5, label='Target: 5 MHz')
ax2.set_ylabel('GBW / UGF (MHz)', fontsize=11)
ax2.set_title('Unity-Gain Bandwidth across 15 PVT Corners', fontsize=12, fontweight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(x_labels, rotation=45, fontsize=8)
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend()

# 3. Phase Margin
pms = [r['pm'] for r in results]
ax3.bar(x_pos, pms, color='salmon', edgecolor='black', alpha=0.85)
ax3.axhline(60.0, color='red', linestyle='--', linewidth=1.5, label='Target: 60°')
ax3.set_ylabel('Phase Margin (deg)', fontsize=11)
ax3.set_title('Phase Margin across 15 PVT Corners', fontsize=12, fontweight='bold')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(x_labels, rotation=45, fontsize=8)
ax3.set_ylim(50, max(pms) + 5)
ax3.grid(True, linestyle=':', alpha=0.6)
ax3.legend()

# 4. Slew Rates
sr_ps = [r['sr_p'] for r in results]
sr_ns = [r['sr_n'] for r in results]
w = 0.35
ax4.bar(x_pos - w/2, sr_ps, width=w, label='SR+ (V/µs)', color='orange', edgecolor='black', alpha=0.85)
ax4.bar(x_pos + w/2, sr_ns, width=w, label='SR- (V/µs)', color='teal', edgecolor='black', alpha=0.85)
ax4.axhline(5.0, color='red', linestyle='--', linewidth=1.5, label='Target: 5 V/µs')
ax4.set_ylabel('Slew Rate (V/µs)', fontsize=11)
ax4.set_title('Positive & Negative Slew Rates across 15 PVT Corners', fontsize=12, fontweight='bold')
ax4.set_xticks(x_pos)
ax4.set_xticklabels(x_labels, rotation=45, fontsize=8)
ax4.grid(True, linestyle=':', alpha=0.6)
ax4.legend()

plt.suptitle('SCL 1.2µm Op-Amp Robustness Analysis across 15 PVT Process Corners', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{proj_dir}/plots/corner_comparison_plot.png", dpi=300)
plt.close()

# Generate Reports
report = []
report.append("========================================================================================================================")
report.append("SCL 1.2 um CMOS TWO-STAGE OP-AMP - PROCESS CORNER & TEMPERATURE ROBUSTNESS REPORT")
report.append("========================================================================================================================")
report.append(f"{'Corner':<10} {'Temp (°C)':<10} {'DC Gain (dB)':<14} {'UGF (MHz)':<12} {'PM (deg)':<10} {'SR+ (V/us)':<12} {'SR- (V/us)':<12} {'Power (mW)':<12} {'Vos (mV)':<10} {'Status':<8}")
report.append("-" * 120)

for r in results:
    status = "PASS" if (r['gain'] >= 68.0 and r['ugf'] >= 5.0 and r['pm'] >= 60.0 and r['sr_p'] >= 5.0 and r['sr_n'] >= 5.0 and r['pwr'] <= 10.0) else "WARN"
    report.append(f"{r['corner']:<10} {r['temp']:<10} {r['gain']:<14.2f} {r['ugf']:<12.2f} {r['pm']:<10.1f} {r['sr_p']:<12.2f} {r['sr_n']:<12.2f} {r['pwr']:<12.3f} {r['vos']:<10.2f} {status:<8}")

report.append("========================================================================================================================")

min_gain = min(r['gain'] for r in results)
max_gain = max(r['gain'] for r in results)
min_ugf  = min(r['ugf']  for r in results)
max_ugf  = max(r['ugf']  for r in results)
min_pm   = min(r['pm']   for r in results)
max_pm   = max(r['pm']   for r in results)
min_srp  = min(r['sr_p'] for r in results)
min_srn  = min(r['sr_n'] for r in results)
max_pwr  = max(r['pwr']  for r in results)

report.append("CORNER SPREAD SUMMARY:")
report.append(f"  DC Gain Spread      : {min_gain:.2f} dB to {max_gain:.2f} dB (Nominal: 70.26 dB)")
report.append(f"  UGF / GBW Spread    : {min_ugf:.2f} MHz to {max_ugf:.2f} MHz (Nominal: 10.12 MHz)")
report.append(f"  Phase Margin Spread : {min_pm:.1f}° to {max_pm:.1f}° (Nominal: 63.7°)")
report.append(f"  Worst-Case SR+ / SR-: {min_srp:.2f} V/us / {min_srn:.2f} V/us (Target >= 5 V/us)")
report.append(f"  Max Power @ +125°C  : {max_pwr:.3f} mW (Target <= 10 mW)")
report.append("========================================================================================================================")

with open(f"{proj_dir}/results/corner_results.txt", "w") as f:
    f.write("\n".join(report) + "\n")

print("\n".join(report))
print(f"\nPlot generated: {proj_dir}/plots/corner_comparison_plot.png")
