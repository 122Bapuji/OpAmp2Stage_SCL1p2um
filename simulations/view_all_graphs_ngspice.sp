* ==============================================================================
* SCL 1.2 um CMOS Two-Stage Op-Amp - Comprehensive Multi-Analysis & Interactive Plots
* ==============================================================================
.lib '/home/vlsi_bbn/open_source_scl_c1d/open_pdks/scl_c1d/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/spice/opamp_2stage_subckt.spice'

* ------------------------------------------------------------------------------
* Circuit 1: AC Open-Loop Frequency Response
* ------------------------------------------------------------------------------
x_ac inp_ac inm_ac vout_ac vdd 0 opamp_2stage
V_vdd vdd 0 5.0
V_cm_ac vcm_ac 0 2.5
V_sig_ac inp_ac vcm_ac dc 0 ac 1
L_dc_ac inm_ac vout_ac 1e6
C_ac_ac inm_ac vcm_ac 1e6
CL_ac vout_ac 0 10p

* ------------------------------------------------------------------------------
* Circuit 2: DC Transfer Characteristic
* ------------------------------------------------------------------------------
x_dc inp_dc inm_dc vout_dc vdd 0 opamp_2stage
V_cm_dc inm_dc 0 2.5
V_in_dc inp_dc 0 2.5
CL_dc vout_dc 0 10p

* ------------------------------------------------------------------------------
* Circuit 3: Transient Closed-Loop Large-Signal Step
* ------------------------------------------------------------------------------
x_tran inp_tran vout_tran vout_tran vdd 0 opamp_2stage
V_sig_tran inp_tran 0 pulse(1.0 4.0 100n 10n 10n 500n 1200n)
CL_tran vout_tran 0 10p

* ------------------------------------------------------------------------------
* Circuit 4: CMRR (Differential vs Common-Mode)
* ------------------------------------------------------------------------------
* Differential Mode
x_diff inp_diff inm_diff vout_diff vdd 0 opamp_2stage
V_cm_diff vcm_diff 0 2.5
V_sig_diff_p inp_diff vcm_diff dc 0 ac 0.5
V_sig_diff_m inm_diff vcm_diff dc 0 ac -0.5
CL_diff vout_diff 0 10p

* Common Mode
x_cm in_cm in_cm vout_cm vdd 0 opamp_2stage
V_sig_cm in_cm 0 dc 2.5 ac 1.0
CL_cm vout_cm 0 10p

* ------------------------------------------------------------------------------
* Circuit 5: PSRR (VDD and VSS Disturbance)
* ------------------------------------------------------------------------------
* VDD ripple
V_vdd_dist vdd_dist 0 dc 5.0 ac 1.0
x_psrr_p inp_p inm_p vout_psrr_p vdd_dist 0 opamp_2stage
V_in_p inp_p 0 2.5
V_in_m inm_p 0 2.5
CL_psrr_p vout_psrr_p 0 10p

* VSS ripple
V_vss_dist vss_dist 0 dc 0.0 ac 1.0
x_psrr_m inp_m inm_m vout_psrr_m vdd vss_dist opamp_2stage
V_in_pm inp_m 0 2.5
V_in_mm inm_m 0 2.5
CL_psrr_m vout_psrr_m 0 10p

* ------------------------------------------------------------------------------
* Ngspice Interactive Control & Multi-Plotting Script
* ------------------------------------------------------------------------------
.control
set color0 = white
set color1 = black
set color2 = blue
set color3 = red
set color4 = green
set nobreak

echo "================================================================================"
echo "SCL 1.2 um OP-AMP: RUNNING COMPREHENSIVE SIMULATIONS FOR NGSPICE PLOTS"
echo "================================================================================"

* 1. AC Analysis
echo "--> Running AC Analysis (10 Hz - 100 MHz)..."
ac dec 20 10 100Meg
let gain_db = db(vout_ac)
let phase_deg = (180 / 3.141592653589793) * cph(vout_ac)
let cmrr_db = db(vout_diff) - db(vout_cm)
let psrr_p_db = db(vout_diff) - db(vout_psrr_p)
let psrr_m_db = db(vout_diff) - db(vout_psrr_m)

* 2. DC Sweep
echo "--> Running DC Sweep (VIN: 2.495 V - 2.505 V)..."
dc V_in_dc 2.495 2.505 10u

* 3. Transient Analysis
echo "--> Running Transient Analysis (0 - 1500 ns)..."
tran 0.5n 1500n

echo "================================================================================"
echo "LAUNCHING ALL NGSPICE INTERACTIVE GRAPH WINDOWS..."
echo "================================================================================"

* Switch back to transient and plot
setplot tran1
plot v(inp_tran) v(vout_tran) title '1. Transient Step Response (CL = 10 pF)' xlabel 'Time (s)' ylabel 'Voltage (V)'

* Switch to DC and plot
setplot dc1
plot v(vout_dc) vs v(inp_dc) title '2. DC Transfer Curve' xlabel 'Input Voltage (V)' ylabel 'Output Voltage (V)'

* Switch to AC and plot Gain, Phase, CMRR, PSRR
setplot ac1
plot gain_db title '3. AC Open-Loop Gain (dB)' xlabel 'Frequency (Hz)' ylabel 'Gain (dB)'
plot phase_deg title '4. AC Open-Loop Phase (deg)' xlabel 'Frequency (Hz)' ylabel 'Phase (deg)'
plot cmrr_db title '5. Common-Mode Rejection Ratio (CMRR in dB)' xlabel 'Frequency (Hz)' ylabel 'CMRR (dB)'
plot psrr_p_db psrr_m_db title '6. Power Supply Rejection Ratio: PSRR+ and PSRR- (dB)' xlabel 'Frequency (Hz)' ylabel 'PSRR (dB)'

echo "All 6 ngspice graph windows displayed!"
.endc
.end
