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
from oci_adbs_utility import convert_no_utc_to_dubai, convert_utc_to_dubai

# List all compartments in the tenancy
def list_compartments(identity_client, tenancy_id):
    compartments = []
    compartment_response = identity_client.list_compartments(
        tenancy_id, 
        compartment_id_in_subtree=True, 
        access_level="ACCESSIBLE"
    )

    # Add root compartment (tenancy)
    compartments.append({
        "id": tenancy_id,
        "name": "root",
        "description": "Tenancy root compartment"
    })
    for compartment in compartment_response.data:
        if compartment.lifecycle_state == "ACTIVE":
            compartments.append({
                "id": compartment.id,
                "name": compartment.name,
                "description": compartment.description
            })
    return compartments

# List all dbcs databases in a compartment
def list_dbcs_databases(database_client, compartment_id):
    pdbs = database_client.list_pluggable_databases(compartment_id=compartment_id).data
    pluggable_databases = []
        # Collect PDB details
    for pdb in pdbs:
        cdb = database_client.get_database(pdb.container_database_id).data
        if cdb.db_system_id != None:
            back_up_date = cdb.last_backup_timestamp
            if cdb.last_backup_timestamp == None:
                back_up_date = "None"
            db_system = database_client.get_db_system(cdb.db_system_id).data
            pluggable_databases.append({
                "pdb_name": pdb.pdb_name,
                "container_id": pdb.container_database_id,
                "lifecycle_state": pdb.lifecycle_state,
                "open_mode": pdb.open_mode,
                "cdb_name": cdb.db_name,
                "auto_backup": cdb.db_backup_config.auto_backup_enabled if cdb.db_backup_config else "None" ,
                "last_backup_timestamp": str(convert_utc_to_dubai(str(back_up_date))) if cdb.last_backup_timestamp else "None" ,
                "last_failed_backup_timestamp": cdb.last_failed_backup_timestamp,
                "hostname": db_system.hostname,
                "version": db_system.version,
                "database_edition": db_system.database_edition,
                "last_patch_history_entry_id": db_system.last_patch_history_entry_id,
                "maintenance_window": db_system.maintenance_window
            })
        else:
            pluggable_databases.append({
            "pdb_name": pdb.pdb_name,
            "container_id": pdb.container_database_id,
            "lifecycle_state": pdb.lifecycle_state,
            "open_mode": pdb.open_mode,
            "cdb_name": cdb.db_name,
            "auto_backup": cdb.db_backup_config.auto_backup_enabled,
            "last_backup_timestamp": cdb.last_backup_timestamp,
            "last_failed_backup_timestamp": cdb.last_failed_backup_timestamp
        })
    
    # db = database_client.list_databases(compartment_id=compartment_id).data
    # db_databases = []
    # databases = []
    # db_instances = database_client.list_db_systems(compartment_id)
    #     # Collect PDB details
    # for cdb in db:
    #     db_databases.append({
    #         "db_name": cdb.db_name,
    #         "pdb_name": cdb.pdb_name,
    #         "id": cdb.id,
    #         "db_system_id":cdb.db_system_id,
    #         "lifecycle_state": cdb.lifecycle_state
    #         })    
    # for dbcs in db_instances.data:
    #     if dbcs.lifecycle_state != "TERMINATED":
    #          # Fetch pluggable databases for the current DB system              
    #         # Append ADB details to the list
    #         print("fetching database details")
    #         databases.append({
    #             "id": dbcs.id,
    #             "display_name": dbcs.display_name,
    #             "hostname": dbcs.hostname,
    #             "lifecycle_state": dbcs.lifecycle_state,
    #             "last_patch_history": dbcs.last_patch_history_entry_id,
    #             "last_maintenance_run_id": dbcs.last_maintenance_run_id,
    #             "next_maintenance_run_id": dbcs.next_maintenance_run_id
    #             })            
    return pluggable_databases


# List all autonomous databases in a compartment
def list_autonomous_databases(database_client, compartment_id):
    databases = []
    adb_response = database_client.list_autonomous_databases(compartment_id)

    for adb in adb_response.data:
        if adb.lifecycle_state != "TERMINATED":
            # Extracting next maintenance window if available
            begin_time = adb.time_maintenance_begin
            end_time = adb.time_maintenance_end
            # Append ADB details to the list
            print("fetching database details")
            databases.append({
                "id": adb.id,
                "display_name": adb.display_name,
                "db_name": adb.db_name,
                "lifecycle_state": adb.lifecycle_state,
                "patch_type": adb.autonomous_maintenance_schedule_type,
                "type": "dedicated" if adb.is_dedicated else "serverless",
                "next_maintenance_begin": str(convert_utc_to_dubai(str(begin_time))) if begin_time else "N/A",
                "next_maintenance_end": str(convert_utc_to_dubai(str(end_time))) if end_time else "N/A",
                "last_patch": list_adb_patch(adb.id,compartment_id,database_client)
            })

    return databases

def list_adb_patch(autonomous_db_ocid, comp_id, database_client):
    patch = []
    try:
        maintenance_runs = database_client.list_maintenance_runs(
        comp_id,  # Compartment ID (usually same as tenancy)
        target_resource_id=autonomous_db_ocid,  # Your Autonomous DB OCID
        sort_by="TIME_ENDED",
        sort_order="ASC",
        )
        if maintenance_runs.data:
            # Get the last patch (assuming patches are returned in chronological order)
            last_maintenance_run = maintenance_runs.data[-1]
            
            patch.append({
                "patch_id": last_maintenance_run.id,
                "description": last_maintenance_run.display_name,
                "time_started": "" + str(convert_no_utc_to_dubai(last_maintenance_run.time_started.strftime("%m/%d/%Y, %H:%M:%S"))),
                "time_ended": "" + str(convert_no_utc_to_dubai(last_maintenance_run.time_ended.strftime("%m/%d/%Y, %H:%M:%S"))),
                "life_cycle_state": last_maintenance_run.lifecycle_state,
                "type": last_maintenance_run.maintenance_type,
                "sub-type": last_maintenance_run.maintenance_subtype
            })
    except Exception as inst:
        patch.append({
                "patch_id": "",
                "description": "",
                "time_started": "",
                "time_ended": "",
                "life_cycle_state": "",
                "type": "",
                "sub-type": ""
            })
    return patch

def json_to_html(json_data):
    # Start HTML content
    html_content = """
    <html>
    <head>
        <style>
            table {font-family: Suiss, GE_SS_Two, Roboto, Arial, sans-serif; border-collapse: collapse; width: 100%; color:#353738; font-size: smaller;}
            th, td {border: 0.5px solid #dddddd; text-align: left; padding: 8px;}
            th {background-color: #353738; color: #fff;}
            h2 {font-family: Suiss, GE_SS_Two, Roboto, Arial, sans-serif; border-collapse: collapse; width: 100%; color:#e00800; font-size:large;}
        </style>
    </head>
    <body>
    <h2>Autonomous Database Information</h2>
    <table>
        <tr>
            <th>Compartment Name</th>
            <th>Display Name</th>
            <th>DB Name</th>
            <th>Lifecycle State</th>
            <th>Patch Type</th>
            <th>Type</th>
            <th>Physical Server</th>
            <th>Next Maintenance Begin</th>
            <th>Next Maintenance End</th>
            <th>Last Patch Description</th>
            <th>Patch Time Started</th>
            <th>Patch Time Ended</th>
            <th>Patch Lifecycle State</th>
            <th>Patch Type</th>
            <th>Patch Sub-type</th>
        </tr>
    """

    # Iterate through the compartments
    for compartment in json_data:
        compartment_name = compartment.get("compartment_name")
        compartment_id = compartment.get("compartment_id")

        # Iterate through the autonomous databases in the compartment
        for adb in compartment.get("autonomous_databases", []):
            adb_id = adb.get("id")
            display_name = adb.get("display_name")
            db_name = adb.get("db_name")
            lifecycle_state = adb.get("lifecycle_state")
            patch_type = adb.get("patch_type")
            adb_type = adb.get("type")
            physical_server = adb.get("physical_server")
            next_maintenance_begin = adb.get("next_maintenance_begin")
            next_maintenance_end = adb.get("next_maintenance_end")

            # Iterate through the last patch details
            for patch in adb.get("last_patch", []):
                patch_id = patch.get("patch_id")
                patch_description = patch.get("description")
                patch_time_started = patch.get("time_started")
                patch_time_ended = patch.get("time_ended")
                patch_lifecycle_state = patch.get("life_cycle_state")
                patch_type = patch.get("type")
                patch_subtype = patch.get("sub-type")

                # Add a row for each autonomous database
                html_content += f"""
                <tr>
                    <td>{compartment_name}</td>
                    <td>{display_name}</td>
                    <td>{db_name}</td>
                    <td>{lifecycle_state}</td>
                    <td>{patch_type}</td>
                    <td>{adb_type}</td>
                    <td>{physical_server}</td>
                    <td>{next_maintenance_begin}</td>
                    <td>{next_maintenance_end}</td>
                    <td>{patch_description}</td>
                    <td>{patch_time_started}</td>
                    <td>{patch_time_ended}</td>
                    <td>{patch_lifecycle_state}</td>
                    <td>{patch_type}</td>
                    <td>{patch_subtype}</td>
                </tr>
                """

    # End the HTML content
    html_content += """
    </table>
    </body>
    </html>
    """

    return html_content

# Function to upload a file to Object Storage
def upload_file_to_object_storage(object_storage_client, namespace, bucket_name, object_name, file_payload):
    # Open the file to upload
    content_stream = io.BytesIO(file_payload.encode("utf-8"))
    object_storage_client.put_object(
            namespace,
            bucket_name,
            object_name,
            put_object_body=content_stream
        )
    logging.info(f"File '{object_name}' uploaded to bucket '{bucket_name}'")

# Function to update or assign physical server attribute
def update_physical_server(data):
    # Dictionary to map unique next_maintenance_begin times to physical servers
    maintenance_map = {}
    server_counter = 1

    # Iterate over compartments and databases
    for compartment in data:
        for db in compartment["autonomous_databases"]:
            next_maintenance = db.get("next_maintenance_begin")
            current_server = db.get("physical_server")

            # If next_maintenance is already mapped, update with existing server
            if next_maintenance in maintenance_map:
                db["physical_server"] = maintenance_map[next_maintenance]
            else:
                # If current_server is already assigned, use it; otherwise, assign a new server
                if current_server:
                    maintenance_map[next_maintenance] = current_server
                else:
                    new_server = f"server{server_counter}"
                    maintenance_map[next_maintenance] = new_server
                    db["physical_server"] = new_server
                    server_counter += 1

    return data

def send_email(object_storage_client,notification_client,signer,namespace,bucket_name,object_name, topic_id, email_subject):
    # Create Pre-Authenticated Request (PAR)
   
    time_expires = datetime.utcnow() + timedelta(days=7)
 
    par_response = object_storage_client.create_preauthenticated_request(
    namespace_name=namespace,
    bucket_name=bucket_name,
    create_preauthenticated_request_details=oci.object_storage.models.CreatePreauthenticatedRequestDetails(
        name="change_this_name",
        access_type="AnyObjectRead",
        time_expires=time_expires,
        bucket_listing_action="ListObjects",
        object_name=object_name))
   
    logging.info(par_response.data)
 
    par_url = f"https://objectstorage.{signer.region}.oraclecloud.com{par_response.data.access_uri}{par_response.data.object_name}"
 
    # Send Notification
    message = f"Your report is available for download: {par_url}"
    notification_client.publish_message(
        topic_id=topic_id,
        message_details=oci.ons.models.MessageDetails(
            title=email_subject,
            body=message
        )
    )
    logging.info("Notification sent successfully!")
