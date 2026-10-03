* ICMR Simulation
.lib '/home/vlsi_bbn/open_source_scl_c1d/open_pdks/scl_c1d/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/spice/opamp_2stage.spice'

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
wrdata /mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/simulations/icmr_sweep.dat v(vout) err gain
.endc
.end
