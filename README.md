# ociadbs
README: Oracle Cloud Infrastructure (OCI) Database Reporting Script

This repository contains a Python script that generates JSON and HTML reports detailing all Autonomous Databases (ADBs) and Database Cloud Service (DBCS) instances across all compartments in an OCI tenancy. The reports include information on:

Patching Window/Status
Backup Configuration and Status
The reports can be used for auditing, monitoring, and compliance purposes.

Prerequisites

Before using this script, ensure you have the following:

1. Python 3.x installed
2 OCI CLI and SDK Installed
3. OCI Tenancy User with Necessary Permissions
The user must have the required policies to list and describe databases unless they are administrator. Policies might look like this:
Allow group <group_name> to inspect autonomous-database-family in tenancy
Allow group <group_name> to inspect database-family in tenancy


Features
Supports all compartments in the tenancy
Ensures a comprehensive view of all databases.
Generates JSON and HTML Reports
Provides human-readable (HTML) and machine-readable (JSON) output.
Includes Detailed Information
Covers patching windows, current patch status, and backup details for each database.

Installation
Clone this repository:

git clone https://github.com/ociadbs.git
cd ociadbs
Install the required dependencies:

OCI Configuration Setup
To run the script, you must set up OCI configuration for your client. Follow these steps:
1. Generate an API Key
oci setup config
2. Add the Key to OCI
Copy the public key generated in the previous step.
Log in to the OCI Console, navigate to Identity > Users, and click on your user.
Under the API Keys tab, add the public key.
3. Verify the Configuration
Test the setup by running:
oci iam availability-domain list --config-file ~/.oci/config

