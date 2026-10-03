* PSRR- Simulation
.lib '/home/vlsi_bbn/open_source_scl_c1d/open_pdks/scl_c1d/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/spice/opamp_2stage.spice'

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
wrdata /mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/simulations/psrr_vss.dat vdb(vout)
.endc
.end
