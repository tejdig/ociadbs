"""
Author: Tejas Joshi
Organization: Oracle Corp.
Date: 2024-10-22
Location: London, UK
Copyright: © 2024 Oracle Corp. All rights reserved.
This script performs the following:
11. Uses OCI APIs to gather Patching information about Oracle Autonomous Databases
2. Produces HTML and JSON report for all ADBs across all compartments in a tenancy for planned and last patching cycles
"""

import logging
import io
import oci
import os
import json
import sys
import copy
from datetime import datetime, timedelta
from oci_adbs_utility import convert_no_utc_to_dubai, convert_utc_to_dubai
from oci_db_fleet_management import *

def main():
    # Initialize OCI configuration
    config = oci.config.from_file("~/.oci/config", "DEFAULT")
    # Get the tenancy OCID (root compartment OCID)
    tenancy_id = config["tenancy"]
    # Initialize the Identity and Database clients
    identity_client = oci.identity.IdentityClient(config)
    database_client = oci.database.DatabaseClient(config)
    compartment_list = list_compartments(identity_client, tenancy_id)
    compartment_data = []
    for compartment in compartment_list:
        print(f"finding databases in compartment {compartment['name']}")
        db_list = list_dbcs_databases(database_client, compartment["id"])
        if len(db_list) != 0:
            compartment_data.append({
                "compartment_name": compartment["name"],
                "compartment_id": compartment["id"],
                "database_databases": db_list
            })
    print(json.dumps(compartment_data, indent=4))


if __name__ == "__main__":
    main()
