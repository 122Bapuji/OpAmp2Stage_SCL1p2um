* Small-Signal Transient Simulation
.lib '/home/vlsi_bbn/open_source_scl_c1d/open_pdks/scl_c1d/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/spice/opamp_2stage.spice'

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

E_buf inm 0 vout 0 1.0

* 2.45V to 2.55V step (100 mV step)
Vin inp 0 pulse(2.45 2.55 100n 1n 1n 300n 700n)

x1 inp inm vout vdd vss opamp_2stage

.control
tran 0.1n 800n
wrdata /mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/simulations/tran_small.dat v(inp) v(vout)

meas tran v_max_ss MAX v(vout) FROM=100n TO=400n
let ov_ss = (v_max_ss - 2.55) / 0.10 * 100
echo TRAN_SMALL_MEAS: OV_SS=$&ov_ss V_MAX_SS=$&v_max_ss
.endc
.end
