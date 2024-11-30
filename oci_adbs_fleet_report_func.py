"""
Author: Tejas Joshi
Organization: Oracle Corp.
Date: 2024-10-22
Location: London, UK
Copyright: © 2024 Oracle Corp. All rights reserved.
This script performs the following:
This code can be used as func.py to create oci functions
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

def handler(ctx, data: io.BytesIO = None):
    logging.info("at the start of the handler")
    # Initialize OCI configuration
    signer = oci.auth.signers.get_resource_principals_signer()
    object_storage_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    # Initialize the Identity and Database clients
    identity_client = oci.identity.IdentityClient(config={}, signer=signer)
    database_client = oci.database.DatabaseClient(config={}, signer=signer)
    notification_client = oci.ons.NotificationDataPlaneClient(config={}, signer=signer)
    # Get the tenancy OCID (root compartment OCID)
    tenancy_id = os.getenv("root_id")
    
    # Specify your namespace (you can get this from the OCI Console)
    namespace = os.getenv("namespace")

    # Name of the Object Storage bucket
    bucket_name = os.getenv("bucket_name")

    # File to upload (this is the local file path)
    file_prefix = os.getenv("file_prefix")
    
     # Name of the Object Storage bucket
    topic_id = os.getenv("topic_id")

    compartment_list = list_compartments(identity_client, tenancy_id)
    print("number of compatments found " + str(compartment_list.count))
    logging.info("in the handler after getting compartments")
    compartment_data = []

    for compartment in compartment_list:
        adb_list = list_autonomous_databases(database_client, compartment["id"])
        if len(adb_list) != 0:
            print(compartment["name"])
            compartment_data.append({
                "compartment_name": compartment["name"],
                "compartment_id": compartment["id"],
                "autonomous_databases": adb_list
            })

    #Add Physical Servers
    updated_data = update_physical_server(copy.deepcopy(compartment_data))
    # Convert JSON data to HTML
    html_output = json_to_html(updated_data)
    # The name of the object in Object Storage (how the file will be named in the bucket)
    object_name = "Reports/" + file_prefix + datetime.today().strftime('%Y-%m-%d_%H:%M:%S') + ".html"
    # Call the function to upload the file
    upload_file_to_object_storage(object_storage_client, namespace, bucket_name, object_name, html_output)
    logging.info("HTML file created successfully & uploaded!")
    #namespace = object_storage_client.get_namespace().data
    #bucket_name = 'your_bucket_name'
    #object_name = 'your_file.txt'
    email_subject = "File Available for Download"
    send_email(object_storage_client,notification_client,signer,namespace,bucket_name,object_name, topic_id, email_subject)
    return response.Response(
        ctx, response_data=json.dumps(
            {"message": html_output}),
        headers={"Content-Type": "application/json"}
    )