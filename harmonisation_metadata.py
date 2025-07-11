#!/usr/bin/env python3



# Shahryar Alavi
# UCL Institute of Neurology, London, UK


# The script creates a metadata based on the input summary statistics data and an input map file describing the column names of sumstats and the desired harmonised names.



import os
import csv
import json
import logging
from datetime import datetime

# --- Load configuration from JSON ---
with open("../harmonisatoin/harmonisation_column-check_config.json", "r", encoding="utf-8") as cfg:
    config = json.load(cfg)

data_dir = config["data_dir"]
harmonised_map_file = config["harmonised_map_file"]
output_metadata_file = config["output_metadata_file"]
log_file = config["log_file"]

# --- Set up logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()  # Console output
    ]
)

# --- Load harmonised column name mapping ---
with open(harmonised_map_file, "r", encoding="utf-8") as f:
    harmonised_map = json.load(f)

# Columns to ignore if missing
optional_columns = {"N"}

metadata = []
processed_count = 0
skipped_count = 0
total_files = 0

# --- Process each file ---
for filename in os.listdir(data_dir):
    if filename.endswith(".tsv") or filename.endswith(".txt"):
        total_files += 1
        filepath = os.path.join(data_dir, filename)
        logging.info(f"Processing file: {filename}")

        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)

                matched_columns = []
                used_columns = set()
                missing_columns = []

                for standard_name, candidates in harmonised_map.items():
                    found = [c for c in candidates if c in headers and c not in used_columns]

                    if found:
                        selected = found[0]
                        matched_columns.append({
                            "original": selected,
                            "standardized": standard_name
                        })
                        used_columns.add(selected)

                        if len(found) > 1:
                            warning = (
                                f"{filename}: Multiple matches for '{standard_name}' - "
                                f"{found}. Selected: '{selected}'"
                            )
                            logging.warning(warning)
                    else:
                        if standard_name not in optional_columns:
                            error = f"{filename}: No match found for standardized column '{standard_name}'"
                            logging.error(error)
                            missing_columns.append(standard_name)
                        else:
                            logging.info(f"{filename}: Optional column '{standard_name}' not found — skipping.")

                if missing_columns:
                    logging.error(
                        f"{filename}: Skipping file due to missing standardized columns: {missing_columns}"
                    )
                    skipped_count += 1
                    continue  # Skip this file

                metadata.append({
                    "filename": filename,
                    "columns": matched_columns
                })
                processed_count += 1

        except Exception as e:
            logging.exception(f"Error processing file {filename}: {e}")
            skipped_count += 1
            continue

# --- Save metadata ---
with open(output_metadata_file, "w", encoding="utf-8") as out:
    json.dump(metadata, out, indent=4)

# --- Summary ---
summary = (
    f"\nSummary:\n"
    f"Total files scanned:    {total_files}\n"
    f"Successfully processed: {processed_count}\n"
    f"Skipped due to errors:  {skipped_count}\n"
)

logging.info(summary.strip())
