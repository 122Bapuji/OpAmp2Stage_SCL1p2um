* AC Bode Simulation
.lib '/home/vlsi_bbn/open_source_scl_c1d/open_pdks/scl_c1d/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
.include '/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/spice/opamp_2stage.spice'

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
let vdb_out = vdb(vout)
let vp_deg = vp(vout) * 180 / PI

meas ac dc_gain MAX vdb(vout)
meas ac f_3db WHEN vdb(vout)='dc_gain - 3.0103'
meas ac ugf WHEN vdb(vout)=0
meas ac p_at_ugf FIND vp_deg WHEN vdb(vout)=0
let pm = 180 + p_at_ugf

wrdata /mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/simulations/ac_data.dat vdb(vout) vp_deg
echo AC_MEAS: DC_GAIN=$&dc_gain F_3DB=$&f_3db UGF=$&ugf P_AT_UGF=$&p_at_ugf PM=$&pm
.endc
.end
