v {xschem version=3.4.8RC file_version=1.3}
G {}
K {type=subcircuit
format="@name @pinlist @symname"
template="name=x1"
}
V {}
S {}
F {}
E {}
* Global / Subcircuit Port Pins
C {ipin.sym} -300 -200 0 0 {name=p1 lab=INP}
C {ipin.sym} -300 -180 0 0 {name=p2 lab=INM}
C {opin.sym} -300 -160 0 0 {name=p3 lab=VOUT}
C {ipin.sym} -300 -140 0 0 {name=p4 lab=VDD}
C {ipin.sym} -300 -120 0 0 {name=p5 lab=VSS}
C {pmos4_p_c1d.sym} -200 -100 0 0 {name=M8 W=40u L=5.0u nf=1 mult=1 model=P spiceprefix=M}
C {lab_pin.sym} -180 -70 0 0 {name=l_M8_d lab=vbp}
C {lab_pin.sym} -220 -100 0 0 {name=l_M8_g lab=vbp}
C {lab_pin.sym} -180 -130 0 0 {name=l_M8_s lab=VDD}
C {lab_pin.sym} -180 -100 0 0 {name=l_M8_b lab=VDD}
C {pmos4_p_c1d.sym} -100 -100 0 0 {name=M5 W=40u L=5.0u nf=1 mult=1 model=P spiceprefix=M}
C {lab_pin.sym} -80 -70 0 0 {name=l_M5_d lab=tail}
C {lab_pin.sym} -120 -100 0 0 {name=l_M5_g lab=vbp}
C {lab_pin.sym} -80 -130 0 0 {name=l_M5_s lab=VDD}
C {lab_pin.sym} -80 -100 0 0 {name=l_M5_b lab=VDD}
C {pmos4_p_c1d.sym} -100 0 0 0 {name=M1 W=120u L=3.0u nf=1 mult=1 model=P spiceprefix=M}
C {lab_pin.sym} -80 30 0 0 {name=l_M1_d lab=net1}
C {lab_pin.sym} -120 0 0 0 {name=l_M1_g lab=INM}
C {lab_pin.sym} -80 -30 0 0 {name=l_M1_s lab=tail}
C {lab_pin.sym} -80 0 0 0 {name=l_M1_b lab=VDD}
C {pmos4_p_c1d.sym} 0 0 0 0 {name=M2 W=120u L=3.0u nf=1 mult=1 model=P spiceprefix=M}
C {lab_pin.sym} 20 30 0 0 {name=l_M2_d lab=out1}
C {lab_pin.sym} -20 0 0 0 {name=l_M2_g lab=INP}
C {lab_pin.sym} 20 -30 0 0 {name=l_M2_s lab=tail}
C {lab_pin.sym} 20 0 0 0 {name=l_M2_b lab=VDD}
C {nmos4_n_c1d.sym} -100 100 0 0 {name=M3 W=20u L=4.0u nf=1 mult=1 model=N spiceprefix=M}
C {lab_pin.sym} -80 70 0 0 {name=l_M3_d lab=net1}
C {lab_pin.sym} -120 100 0 0 {name=l_M3_g lab=net1}
C {lab_pin.sym} -80 130 0 0 {name=l_M3_s lab=VSS}
C {lab_pin.sym} -80 100 0 0 {name=l_M3_b lab=VSS}
C {nmos4_n_c1d.sym} 0 100 0 0 {name=M4 W=20u L=4.0u nf=1 mult=1 model=N spiceprefix=M}
C {lab_pin.sym} 20 70 0 0 {name=l_M4_d lab=out1}
C {lab_pin.sym} -20 100 0 0 {name=l_M4_g lab=net1}
C {lab_pin.sym} 20 130 0 0 {name=l_M4_s lab=VSS}
C {lab_pin.sym} 20 100 0 0 {name=l_M4_b lab=VSS}
C {pmos4_p_c1d.sym} 200 -50 0 0 {name=M7 W=240u L=5.0u nf=1 mult=1 model=P spiceprefix=M}
C {lab_pin.sym} 220 -20 0 0 {name=l_M7_d lab=VOUT}
C {lab_pin.sym} 180 -50 0 0 {name=l_M7_g lab=vbp}
C {lab_pin.sym} 220 -80 0 0 {name=l_M7_s lab=VDD}
C {lab_pin.sym} 220 -50 0 0 {name=l_M7_b lab=VDD}
C {nmos4_n_c1d.sym} 200 50 0 0 {name=M6 W=240u L=4.0u nf=1 mult=1 model=N spiceprefix=M}
C {lab_pin.sym} 220 20 0 0 {name=l_M6_d lab=VOUT}
C {lab_pin.sym} 180 50 0 0 {name=l_M6_g lab=out1}
C {lab_pin.sym} 220 80 0 0 {name=l_M6_s lab=VSS}
C {lab_pin.sym} 220 50 0 0 {name=l_M6_b lab=VSS}
C {res.sym} -200 50 0 0 {name=Rbias value=95k}
C {lab_pin.sym} -200 20 0 0 {name=l_rbias_p lab=vbp}
C {lab_pin.sym} -200 80 0 0 {name=l_rbias_m lab=VSS}
C {capa.sym} 100 -20 0 0 {name=Cc m=1 value=3.5p}
C {lab_pin.sym} 100 -50 0 0 {name=l_cc_p lab=out1}
C {lab_pin.sym} 100 10 0 0 {name=l_cc_m lab=rz_node}
C {res.sym} 100 60 0 0 {name=Rz value=3.2k}
C {lab_pin.sym} 100 30 0 0 {name=l_rz_p lab=rz_node}
C {lab_pin.sym} 100 90 0 0 {name=l_rz_m lab=VOUT}
C {code_shown.sym} -300 -300 0 0 {name=SIZING_TABLE
only_toplevel=false
value="* SCL 1.2um Two-Stage CMOS Op-Amp
* M1, M2 (Diff Pair): W=120um, L=3.0um (PMOS)
* M3, M4 (Active Load): W=20um, L=4.0um (NMOS)
* M5 (Tail Current): W=40um, L=5.0um (PMOS)
* M6 (Stage 2 CS): W=240um, L=4.0um (NMOS)
* M7 (Stage 2 Load): W=240um, L=5.0um (PMOS)
* M8 (Bias Diode): W=40um, L=5.0um (PMOS)
* Rbias = 95k, Cc = 3.5pF, Rz = 3.2k
"}
