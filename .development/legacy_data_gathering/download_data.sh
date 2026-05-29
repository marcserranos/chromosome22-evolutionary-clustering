#!/bin/bash
set -e

DATA_DIR="./data"
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

BASE_URL="https://sharehost.hms.harvard.edu/genetics/reich_lab/sgdp/"

echo "=== Downloading SGDP Chr22 Data ==="
echo ""

# Download metadata
echo "1. Downloading metadata file..."
curl -k -C - -o "SGDP_metadata.279public.21signedLetter.44Fan.samples.txt" \
  "${BASE_URL}SGDP_metadata.279public.21signedLetter.44Fan.samples.txt"
echo "✓ Metadata downloaded"

# Download BCF file
echo ""
echo "2. Downloading chr22 BCF file (0.94 GB - may take a few minutes)..."
curl -k -C - -o "chr.sgdp.pub.22.bcf" \
  "${BASE_URL}phased_data2021/chr.sgdp.pub.22.bcf"
echo "✓ BCF file downloaded"

# Download index file
echo ""
echo "3. Downloading BCF index file..."
curl -k -C - -o "chr.sgdp.pub.22.bcf.csi" \
  "${BASE_URL}phased_data2021/chr.sgdp.pub.22.bcf.csi"
echo "✓ Index file downloaded"

echo ""
echo "=== Download Complete ==="
ls -lh
