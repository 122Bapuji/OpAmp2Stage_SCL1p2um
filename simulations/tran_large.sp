* Large-Signal Transient Simulation
.lib '/home/vlsi_bbn/open_source_scl_c1d/open_pdks/scl_c1d/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/spice/opamp_2stage.spice'

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
wrdata /mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/simulations/tran_large.dat v(inp) v(vout)

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
