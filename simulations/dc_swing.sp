* DC Transfer and Output Swing
.lib '/home/vlsi_bbn/open_source_scl_c1d/open_pdks/scl_c1d/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/spice/opamp_2stage.spice'

Vdd vdd 0 5.0
Vss vss 0 0.0
CL vout vss 10p

Vcm in_minus 0 2.5
Vid in_plus in_minus 0.0

x1 in_plus in_minus vout vdd vss opamp_2stage

.control
dc Vid -5m 5m 5u
wrdata /mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/simulations/dc_sweep.dat v(vout) deriv(v(vout))
.endc
.end
