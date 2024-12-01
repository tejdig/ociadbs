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

# Oracle Database Reporting and Automation Script

## Overview

This script interacts with Oracle Cloud Infrastructure (OCI) APIs to provide comprehensive information about databases in an OCI tenancy. It gathers data on compartments, databases, maintenance schedules, and patching, then generates HTML and JSON reports. Additionally, it supports functionality for uploading files to Object Storage, sending email notifications, and updating physical server attributes.

---

## Features

1. **Compartment Management**:
   - Retrieves a list of all compartments in a tenancy.

2. **Database Information**:
   - Lists all databases (DBCS and Autonomous Databases) in specified compartments.
   - Extracts details like lifecycle state, patching history, backup schedule and maintenance schedules.

3. **Report Generation**:
   - Converts JSON data into a styled HTML report.

4. **File Management**:
   - Uploads generated files to OCI Object Storage.

5. **Notifications**:
   - Sends email notifications with pre-authenticated links to reports using oci notification service.

6. **Physical Server Mapping**:
   - Updates or assigns physical server attributes to databases based on maintenance schedules.

7. **Data Extraction**:
   - Uses OCI APIs to gather patching information for Oracle Autonomous Databases.

8. **Time Zone Conversion**:
   - Converts UTC timestamps to Dubai timezone for localized reporting.

9. **Reporting**:
   - Produces detailed patching reports in:
     - **HTML** format for human-readable summaries.
     - **JSON** format for programmatic use and analysis.

10. **Comprehensive Coverage**:
   - Covers all compartments within a tenancy.

---

## Requirements

- **OCI Python SDK**: Ensure the Oracle Cloud Infrastructure SDK is installed.  
  ```bash
  pip install oci
