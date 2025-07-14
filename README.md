[![GitHub release](https://img.shields.io/github/v/release/Schahrjar/Neurodegeneration_meta-analysis)](https://github.com/Schahrjar/Neurodegeneration_meta-analysis/releases/latest)
[![last commit](https://img.shields.io/github/last-commit/Schahrjar/Neurodegeneration_meta-analysis)](https://github.com/Schahrjar/Neurodegeneration_meta-analysis/commits/main)

# Neurodegeneration GWAS meta-analysis
This is a developing platform for analysis of genotype data and GWAS summary statistics (sumstats) on neurodegenerative diseases. With a growing number of GWASs on neurodegerative disorders, such as Alzheimer's and Parkinson's diseases, we aim at constructing a platform for a clean aggregation of these genotype and sumstats data to make a cohort inclusive of diverse ethnicities. This way we can better visualise the spectrum of human neurodegeration.

> [!NOTE]
> The concept of merging and QCing the genotype and sumstats data should be the same among various GWASs. Thus, you may use this tool in other GWASs on other traits rather than the neurodegeneration.

## 🔧 Features
- Mainly for meta-analysis on neurodegenerative disorders
- Prints a log file to follow up warnings/error to avoid unwanted results
- Dependencies are Python, GWASLab, etc.

## 🧠 Concept
There is not any consensus data format for GWAS sumstats, thus there is a need to harmonise sumstats data collected from multiple resources. This tool uses a user-defined map file of sumstats column names to harmonise all of the sumstats collected in the input directory. The harmonised data is then ready for QC and meta-analysis.\
Regarding that sumstats may lack some useful data, such as samples size, an option is provided to enable users to add sample size to the output harmonised sumstats where it can be retrieved from the sumstats' published material.

## 📦 Usage
Clone the repository:
```bash
git clone https://github.com/Schahrjar/Neurodegeneration_meta-analysis.git
cd Neurodegeneration_meta-analysis
chmod +x harmonisation_metadata.py harmonisation.py
```
Set the configuration files by editing the ones in the `harmonisation_configs/` directory. Then run `harmonisation_metadata.py` and `harmonisation.py`, respectively.

## 🗂️ Inputs
### Mandatory
* A directory where all of the tab-delimited sumstats text files are located.
* **harmonisation_map.json** file: this tool uses this map file to find the sumstats' columns representing the desigred info. The sumstats columns' header will be renamed to the  header names of this JSON map file after harmonisation.\
In sumstats where there are multiple columns for the same info, the tool takes the one that is entered ahead in this JSON map file.

### Optional
* **sample-size_meta.json** file: user may provide sample sizes for sumstats in which the sample size is not explicitly provided. This could improve the statistical power of the data in meta-analysis.

## 📜 Citation

This tool is released prior to our manuscript submission. This work has been done under supervision of Dr Maryam Shoai and Prof John Hardy, at the UCL Queen Square Institute of Neurology. You may contact [Shahryar Alavi](https://schahrjar.github.io/) for permission.
