#!/usr/bin/env python3
"""
Query and download SGDP chr22 data from Seven Bridges CGC
"""
from sevenbridges import Api
import json

# Authenticate
api = Api(
    url='https://cgc-api.sbgenomics.com/v2',
    token='13c18bea870a4783b7f3c1b71ac36184'
)

# List all projects to find SGDP
print("=== Available Projects ===")
projects = api.projects.list()
for proj in projects:
    print(f"  {proj.name}: {proj.id}")
    if 'SGDP' in proj.name or 'sgdp' in proj.name.lower():
        sgdp_project = proj
        print(f"    ^ Found SGDP project!")

# If SGDP project found, list files
if 'sgdp_project' in locals():
    print(f"\n=== Files in SGDP Project ===")
    files = sgdp_project.get_files()

    chr22_files = []
    metadata_files = []

    for f in files:
        size_gb = f.size / (1024**3) if f.size else 0
        print(f"  {f.name} ({size_gb:.2f} GB)")

        # Filter for chr22 and metadata
        if 'chr22' in f.name.lower() or '22' in f.name:
            chr22_files.append(f)
        if 'metadata' in f.name.lower():
            metadata_files.append(f)

    print(f"\n=== Chr22 Files Found ({len(chr22_files)}) ===")
    total_size = 0
    for f in chr22_files:
        size_gb = f.size / (1024**3) if f.size else 0
        print(f"  {f.name}: {size_gb:.2f} GB")
        total_size += f.size if f.size else 0

    print(f"\n=== Metadata Files Found ({len(metadata_files)}) ===")
    for f in metadata_files:
        size_gb = f.size / (1024**3) if f.size else 0
        print(f"  {f.name}: {size_gb:.2f} GB")
        total_size += f.size if f.size else 0

    total_gb = total_size / (1024**3)
    print(f"\n=== Total Size: {total_gb:.2f} GB ===")

    if total_gb < 5:
        print(f"✓ Under 5GB threshold - proceeding with download")

        # Save file info to JSON for download script
        download_list = {
            'chr22_files': [{'id': f.id, 'name': f.name, 'size': f.size} for f in chr22_files],
            'metadata_files': [{'id': f.id, 'name': f.name, 'size': f.size} for f in metadata_files]
        }

        with open('download_list.json', 'w') as out:
            json.dump(download_list, out, indent=2)

        print(f"✓ File list saved to download_list.json")
    else:
        print(f"✗ Exceeds 5GB threshold - need to download selectively")
        print("  Query available to refine search")
else:
    print("✗ SGDP project not found")
