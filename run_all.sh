#!/bin/bash
set -e
export PDK_ROOT=/home/vlsi_bbn/open_source_scl_c1d/open_pdks
export PDK=scl_c1d
export WORKING_DIR=/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um/xschem

echo "================================================================================"
echo "SCL 1.2um CMOS TWO-STAGE OP-AMP: FULL SIMULATION SUITE"
echo "================================================================================"

BASE_DIR=/mnt/g/VLSI_Projects/OpAmp2Stage_SCL1p2um

echo "[1/6] Running DC Operating Point & Transfer Analysis..."
$BASE_DIR/run_dc.sh

echo ""
echo "[2/6] Running AC Frequency Response Analysis..."
$BASE_DIR/run_ac.sh

echo ""
echo "[3/6] Running Large & Small Signal Transient Analysis..."
$BASE_DIR/run_transient.sh

echo ""
echo "[4/6] Running Common-Mode Rejection Ratio (CMRR) Analysis..."
$BASE_DIR/run_cmrr.sh

echo ""
echo "[5/6] Running Power Supply Rejection Ratio (PSRR) Analysis..."
$BASE_DIR/run_psrr.sh

echo ""
echo "[6/6] Running 15-Point PVT Process Corner Analysis..."
$BASE_DIR/run_corners.sh

echo ""
echo "================================================================================"
echo "ALL SIMULATIONS COMPLETED SUCCESSFULLY!"
echo "Results saved in: $BASE_DIR/results/"
echo "Plots saved in  : $BASE_DIR/plots/"
echo "================================================================================"
