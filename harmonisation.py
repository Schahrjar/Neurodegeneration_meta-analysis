#!/usr/bin/env python3



# Shahryar Alavi
# UCL Institute of Neurology, London, UK



# GWAS summary statistics have different formats. For doing sumstats data QC and meta-analysis we need our data to be integrated.
# Using GWASLab, the data format could be converted to GCTA-COJO format.



import os
import json
import logging
import gwaslab as gl
from datetime import datetime

# ----------------------- Load Configuration -----------------------
with open("harmonisation/harmonisation_config.json", "r", encoding="utf-8") as cfg_file:
    config = json.load(cfg_file)

INPUT_DIR = config["input_dir"]
METADATA_FILE = config["metadata_file"]
SAMPLE_SIZE_META_FILE = config["sample_size_meta_file"]
OUTPUT_DIR = config["output_dir"]
LOG_FILE = config["log_file"]
BUILD = config.get("genome_build", "38")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------- Logging Setup -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ----------------------- Load Input Files -----------------------
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

try:
    with open(SAMPLE_SIZE_META_FILE, "r", encoding="utf-8") as f:
        sample_size_meta = json.load(f)
except FileNotFoundError:
    logging.warning("Sample size meta file not found. Proceeding without it.")
    sample_size_meta = {}

# ----------------------- Column Mapping -----------------------
standard_to_key = {
    "MARKERNAME": "rsid",
    "CHROMOSOME": "chrom",
    "POSITION": "pos",
    "EA": "ea",
    "NEA": "nea",
    "BETA": "beta",
    "SE": "se",
    "P": "p",
    "EAF": "eaf",
    "N": "n"
}

required_keys = ["rsid", "chrom", "pos", "p"]

# ----------------------- Processing Files -----------------------
processed_count = 0
skipped_count = 0

for entry in metadata:
    filename = entry["filename"]
    filepath = os.path.join(INPUT_DIR, filename)
    column_map = {col["standardized"]: col["original"] for col in entry["columns"]}
    base_name = os.path.splitext(filename)[0]
    output_file = os.path.join(OUTPUT_DIR, f"{base_name}_harmonised.tsv")

    # Build kwargs for gl.Sumstats
    sumstats_kwargs = {
        key: column_map[std]
        for std, key in standard_to_key.items()
        if std in column_map and std != "N"
    }

    # Handle "N" (sample size)
    if "N" in column_map:
        sumstats_kwargs["n"] = column_map["N"]
    elif filename in sample_size_meta:
        sumstats_kwargs["n"] = sample_size_meta[filename]
        logging.info(f"{filename}: Using sample size from meta file: {sample_size_meta[filename]}")
    else:
        logging.warning(f"{filename}: No 'N' column or meta entry. Proceeding without 'n'.")
        # "n" remains unset

    # Check required keys
    missing = [k for k in required_keys if k not in sumstats_kwargs]
    if missing:
        logging.error(f"{filename}: Missing required columns: {missing}. Skipping file.")
        skipped_count += 1
        continue

    try:
        logging.info(f"Processing file: {filename}")
        sumstats = gl.Sumstats(filepath, **sumstats_kwargs, build=BUILD)

        # Optional GWASLab operations here
        # Check data and standardise data:
        sumstats.basic_check(remove=True, remove_dup=True)
        # Get lead variants:
        print(sumstats.get_lead(sig_level=1e-8, anno=True))
        # Reformat the columns:
        sumstats.sort_column(order=["rsID", "EA", "NEA", "EAF", "N", "CHR", "POS", "BETA", "SE", "P"])
        

        statDF = sumstats.data.iloc[:, 0:10]
        statDF.to_csv(output_file, sep="\t", index=False)
        logging.info(f"{filename}: Harmonised data saved to {output_file}")
        processed_count += 1

    except Exception as e:
        logging.exception(f"{filename}: Failed to process file due to error.")
        skipped_count += 1
        continue

# ----------------------- Final Summary -----------------------
summary = (
    "\n--- GWASLab Batch Processing Summary ---\n"
    f"Total files:      {len(metadata)}\n"
    f"Processed:        {processed_count}\n"
    f"Skipped:          {skipped_count}\n"
    f"Output directory: {OUTPUT_DIR}\n"
    f"Log file:         {LOG_FILE}\n"
)
logging.info(summary.strip())
print(summary)
