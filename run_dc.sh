#!/bin/bash
set -e
export PDK_ROOT=/home/vlsi_bbn/open_source_scl_c1d/open_pdks
export PDK=scl_c1d
export WORKING_DIR=/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/xschem

echo "=========================================================="
echo "RUNNING DC ANALYSIS FLOW FOR SCL 1.2um OP-AMP"
echo "=========================================================="

python3 /mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/simulations/sim_dc.py
