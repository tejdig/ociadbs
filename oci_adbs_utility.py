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
import oci
import io
import os
import json
import sys
import pytz
import copy
from datetime import datetime, timedelta

# Define the UTC and Dubai timezones
utc = pytz.utc
dubai_tz = pytz.timezone('Asia/Dubai')

# Function to convert UTC string to Dubai time
def convert_no_utc_to_dubai(utc_string):
    # Parse the UTC datetime string into a datetime object
    utc_datetime = datetime.strptime(utc_string, "%m/%d/%Y, %H:%M:%S")
    utc_datetime = utc_datetime.replace(tzinfo=utc)
    
    # Convert the UTC datetime to Dubai time
    dubai_datetime = utc_datetime.astimezone(dubai_tz)
    
    return dubai_datetime

def convert_utc_to_dubai(utc_string):
    # Parse the UTC datetime string with offset
    utc_datetime = datetime.fromisoformat(utc_string)
    
    # Convert the UTC datetime to Dubai time
    dubai_datetime = utc_datetime.astimezone(dubai_tz)
    
    return dubai_datetime
