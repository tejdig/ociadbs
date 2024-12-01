# ociadbs
# Oracle Autonomous Database Patching Report Script

## Overview
**Author**: Tejas Joshi  
**Organization**: Oracle Corp.  
**Date**: October 22, 2024  
**Location**: London, UK  
**Copyright**: © 2024 Oracle Corp. All rights reserved.
This repository is to host oci python code for creating consolidated reports for fleet management of autonomous database
This script is designed to interact with Oracle Cloud Infrastructure (OCI) APIs to extract patching details for Oracle Autonomous Databases (ADB) within a tenancy. The output includes reports in **HTML** and **JSON** formats, providing insights into planned and past patching cycles for all ADBs across all compartments.

---

## Features

1. **Data Extraction**:
   - Uses OCI APIs to gather patching information for Oracle Autonomous Databases.

2. **Time Zone Conversion**:
   - Converts UTC timestamps to Dubai timezone for localized reporting.

3. **Reporting**:
   - Produces detailed patching reports in:
     - **HTML** format for human-readable summaries.
     - **JSON** format for programmatic use and analysis.

4. **Comprehensive Coverage**:
   - Covers all compartments within a tenancy.

---

## Requirements

- **OCI Python SDK**: Ensure the Oracle Cloud Infrastructure SDK is installed.  
  ```bash
  pip install oci
