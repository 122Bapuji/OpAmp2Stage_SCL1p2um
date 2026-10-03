v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
* Instance of opamp_2stage
* Symbol pins: INP at (-60, -20), INM at (-60, 20), VOUT at (60, 0), VDD at (0, -40), VSS at (0, 40)
C {opamp_2stage.sym} 200 0 0 0 {name=x1}
C {lab_pin.sym} 200 -40 0 0 {name=l_x1_vdd lab=VDD}
C {lab_pin.sym} 200 40 0 0 {name=l_x1_vss lab=VSS}
C {lab_pin.sym} 140 -20 0 0 {name=l_x1_inp lab=INP}
C {lab_pin.sym} 140 20 0 0 {name=l_x1_inm lab=INM}
C {lab_pin.sym} 260 0 0 0 {name=l_x1_vout lab=VOUT}

* Power supplies
C {vsource.sym} -200 -100 0 0 {name=V_VDD value=5.0 savecurrent=false}
C {lab_pin.sym} -200 -130 0 0 {name=l_vdd lab=VDD}
C {lab_pin.sym} -200 -70 0 0 {name=l_vss1 lab=VSS}

C {vsource.sym} -200 50 0 0 {name=V_VSS value=0.0 savecurrent=false}
C {lab_pin.sym} -200 20 0 0 {name=l_vss2 lab=VSS}
C {gnd.sym} -200 80 0 0 {name=gnd1 lab=GND}

* Load Capacitor
C {capa.sym} 320 0 0 0 {name=CL value=10p}
C {lab_pin.sym} 320 -30 0 0 {name=l_cl_top lab=VOUT}
C {lab_pin.sym} 320 30 0 0 {name=l_cl_bot lab=VSS}

* Common Mode Voltage
C {vsource.sym} -100 -100 0 0 {name=V_CM value=2.5 savecurrent=false}
C {lab_pin.sym} -100 -130 0 0 {name=l_vcm_p lab=VCM}
C {lab_pin.sym} -100 -70 0 0 {name=l_vcm_m lab=VSS}

* Signal Source (AC and Pulse)
C {vsource.sym} 0 -100 0 0 {name=V_SIG value="dc 0 ac 1 pulse(1.0 4.0 100n 10n 10n 500n 1200n)" savecurrent=false}
C {lab_pin.sym} 0 -130 0 0 {name=l_vsig_p lab=INP}
C {lab_pin.sym} 0 -70 0 0 {name=l_vsig_m lab=VCM}

* Middlebrook DC feedback from VOUT to INM
C {ind.sym} 200 120 1 0 {name=L_DC m=1 value=1e6}
C {lab_pin.sym} 170 120 0 0 {name=l_ldc_p lab=VOUT}
C {lab_pin.sym} 230 120 0 0 {name=l_ldc_m lab=INM}

C {capa.sym} 230 180 0 0 {name=C_AC m=1 value=1e6}
C {lab_pin.sym} 230 150 0 0 {name=l_cac_p lab=INM}
C {lab_pin.sym} 230 210 0 0 {name=l_cac_m lab=VCM}

* Model and Control Blocks
C {code_shown.sym} -300 -300 0 0 {name=MODEL_INCLUDE
only_toplevel=true
value="* SCL 1.2um Technology Models
.lib '/home/vlsi_bbn/open_source_scl_c1d/open_pdks/scl_c1d/libs.tech/ngpsice/model/hspice/models49/header.lib' NOM
"}

C {code_shown.sym} -300 100 0 0 {name=SIM_COMMANDS
only_toplevel=true
value="* Simulation Commands
.control
set color0=white
set color1=black
set color2=blue
set color3=red
op
ac dec 20 1 100Meg
plot db(vout) title 'AC Gain (dB)'
tran 0.5n 1500n
plot v(inp) v(vout) title 'Transient Large-Signal Step (CL=10pF)'
.endc
"}
