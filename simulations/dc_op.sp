* DC Operating Point Simulation
.lib '/home/vlsi_bbn/open_source_scl_c1d/open_pdks/scl_c1d/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/spice/opamp_2stage.spice'

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
