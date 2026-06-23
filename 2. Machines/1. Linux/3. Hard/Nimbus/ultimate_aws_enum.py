#!/usr/bin/env python3
"""
ultimate_aws_enum.py - Advanced AWS/LocalStack Enumeration

Enumerates all AWS services accessible via the provided credentials,
retrieving and displaying resource details, policies, tags, and more.

DO NOT USE OUTSIDE OF CTF.
SECURIY BEST PRACTICES NOT CONSIDERED IN THIS SCRIPT BY DESIGN INTENTIONALLY. 
IF YOU USE THIS SCRIPT - YOU WILL EXPOSE CONFIDENTIAL CONFIGURATION DATA.

"""

import boto3
import json
import sys
from botocore.exceptions import ClientError, EndpointConnectionError
from datetime import datetime
import pprint

# ============================================================
# CONFIGURATION
# ============================================================
AWS_ACCESS_KEY = "ASIAQX4PG7L2K9M3N5R8"
AWS_SECRET_KEY = "bXJ7K8mP/q2Hf+vN9wT4LcRe5Y1Aoz3DhU6gKjQs"
AWS_TOKEN = "IQoJb3JpZ2luX2VjEHQaCXVzLWVhc3QtMSJGMEQCIBhV9zPmK3wQjL4nT8vR2xY7AoFqUk5HsP6BeMcW1aDgAiAR4tNoXzKp8VnJqL7mC3xY9FhWdQ5GBPmRkX2vT8jY6yqsAQiK//////////8BEAEaDDAwMDAwMDAwMDAwMCIMNZ5tQ7vEX2pKlHfqKtoBQwK5HmBcN4gXjVrUe1Pk9YsZ7DqWfThN3bMRoLYyJsKn8GpVxAcQ5VeWk2HiqXbF6CnXmM4PdYpL3rJzKqGtNvBfHcWyXa8jPzTn5LRMkV1QbWdAyKpGfHzNvU8TmEcL2qPdRhJsKgGn3VyXmFbBcNJ7QrHe5VpDxKfM"
REGION = "us-east-1"
ENDPOINT = "http://aws.nimbus.htb"  # LocalStack endpoint

# ============================================================
# SETUP
# ============================================================
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    aws_session_token=AWS_TOKEN,
    region_name=REGION
)

# Global client cache to avoid re-creating
clients = {}

def get_client(service):
    """Get or create a boto3 client for the service with custom endpoint."""
    if service not in clients:
        clients[service] = session.client(service, endpoint_url=ENDPOINT)
    return clients[service]

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def print_header(title, char='=', length=80):
    """Print a section header."""
    print(f"\n{char * length}")
    print(f" {title} ".center(length, char))
    print(f"{char * length}")

def print_subheader(title):
    """Print a sub-section header."""
    print(f"\n--- {title} ---")

def print_json(data, indent=2):
    """Pretty-print JSON data."""
    print(json.dumps(data, indent=indent, default=str))

def safe_call(func, *args, **kwargs):
    """Call a function and return (success, result_or_error)."""
    try:
        result = func(*args, **kwargs)
        return True, result
    except ClientError as e:
        return False, f"ClientError: {e.response['Error']['Message']}"
    except EndpointConnectionError as e:
        return False, f"ConnectionError: {e}"
    except Exception as e:
        return False, f"Exception: {e}"

def paginate(client, method, **kwargs):
    """Automatically paginate results for methods that support pagination."""
    paginator = client.get_paginator(method.__name__)
    pages = paginator.paginate(**kwargs)
    results = []
    for page in pages:
        results.append(page)
    return results

# ============================================================
# SERVICE ENUMERATORS
# ============================================================

def enum_s3():
    """Enumerate S3: buckets, objects (first 10 per bucket), bucket policies, ACLs."""
    print_header("S3")
    client = get_client('s3')
    
    # List buckets
    success, buckets = safe_call(client.list_buckets)
    if not success:
        print(f"[-] Failed to list buckets: {buckets}")
        return
    bucket_list = buckets.get('Buckets', [])
    print(f"[+] Found {len(bucket_list)} bucket(s)")
    for bucket in bucket_list:
        name = bucket['Name']
        creation = bucket.get('CreationDate')
        print(f"\n  Bucket: {name} (Created: {creation})")
        
        # Try to get bucket location
        success, loc = safe_call(client.get_bucket_location, Bucket=name)
        if success:
            print(f"    Location: {loc.get('LocationConstraint', 'us-east-1')}")
        
        # Try to get bucket policy
        success, policy = safe_call(client.get_bucket_policy, Bucket=name)
        if success:
            print(f"    Policy: {policy.get('Policy')[:200]}..." if len(policy.get('Policy', '')) > 200 else policy)
        else:
            print(f"    Policy: Not set or denied")
        
        # Try to get ACL
        success, acl = safe_call(client.get_bucket_acl, Bucket=name)
        if success:
            grants = acl.get('Grants', [])
            print(f"    ACL Grants: {len(grants)}")
            for grant in grants[:3]:  # show first 3
                grantee = grant.get('Grantee', {})
                perm = grant.get('Permission')
                uri = grantee.get('URI', '')
                if uri:
                    print(f"      - {uri} : {perm}")
                else:
                    print(f"      - {grantee.get('ID', 'unknown')} : {perm}")
        
        # List objects (first 10)
        success, objects = safe_call(client.list_objects_v2, Bucket=name, MaxKeys=10)
        if success:
            contents = objects.get('Contents', [])
            print(f"    Objects (first {len(contents)}):")
            for obj in contents:
                key = obj['Key']
                size = obj.get('Size', 0)
                modified = obj.get('LastModified')
                print(f"      - {key} ({size} bytes, modified: {modified})")
        else:
            print(f"    Objects: {objects}")

def enum_ec2():
    """Enumerate EC2: instances, security groups, volumes, snapshots."""
    print_header("EC2")
    client = get_client('ec2')
    
    # Instances
    success, instances = safe_call(client.describe_instances)
    if success:
        reservations = instances.get('Reservations', [])
        total = sum(len(r.get('Instances', [])) for r in reservations)
        print(f"[+] Found {total} EC2 instance(s)")
        for res in reservations:
            for inst in res.get('Instances', []):
                print(f"\n  Instance ID: {inst.get('InstanceId')}")
                print(f"    State: {inst.get('State', {}).get('Name')}")
                print(f"    Type: {inst.get('InstanceType')}")
                print(f"    Image ID: {inst.get('ImageId')}")
                print(f"    Private IP: {inst.get('PrivateIpAddress')}")
                print(f"    Public IP: {inst.get('PublicIpAddress')}")
                print(f"    VPC ID: {inst.get('VpcId')}")
                print(f"    Subnet ID: {inst.get('SubnetId')}")
                tags = inst.get('Tags', [])
                if tags:
                    print(f"    Tags: {', '.join([f'{t["Key"]}={t["Value"]}' for t in tags])}")
                # Security groups
                sgs = inst.get('SecurityGroups', [])
                if sgs:
                    print(f"    Security Groups: {', '.join([sg['GroupId'] for sg in sgs])}")
    else:
        print(f"[-] Failed to describe instances: {instances}")
    
    # Security Groups
    success, sgs = safe_call(client.describe_security_groups)
    if success:
        groups = sgs.get('SecurityGroups', [])
        print(f"\n[+] Found {len(groups)} Security Group(s)")
        for sg in groups[:5]:  # show first 5
            print(f"  - {sg.get('GroupName')} ({sg.get('GroupId')}): {sg.get('Description')}")
            if sg.get('IpPermissions'):
                print(f"    Ingress Rules: {len(sg['IpPermissions'])}")
    else:
        print(f"[-] Failed to describe security groups: {sgs}")
    
    # Volumes
    success, vols = safe_call(client.describe_volumes)
    if success:
        volumes = vols.get('Volumes', [])
        print(f"\n[+] Found {len(volumes)} EBS Volume(s)")
        for vol in volumes[:5]:
            print(f"  - {vol.get('VolumeId')}: {vol.get('Size')} GiB, State: {vol.get('State')}, Attached to: {vol.get('Attachments', [{}])[0].get('InstanceId') if vol.get('Attachments') else 'None'}")
    else:
        print(f"[-] Failed to describe volumes: {vols}")
    
    # Snapshots (own only)
    success, snaps = safe_call(client.describe_snapshots, OwnerIds=['self'])
    if success:
        snapshots = snaps.get('Snapshots', [])
        print(f"\n[+] Found {len(snapshots)} Snapshot(s)")
        for snap in snapshots[:5]:
            print(f"  - {snap.get('SnapshotId')}: {snap.get('Description', 'N/A')}, Size: {snap.get('VolumeSize')} GiB")
    else:
        print(f"[-] Failed to describe snapshots: {snaps}")

def enum_lambda():
    """Enumerate Lambda: functions and their configurations."""
    print_header("Lambda")
    client = get_client('lambda')
    
    success, funcs = safe_call(client.list_functions)
    if success:
        functions = funcs.get('Functions', [])
        print(f"[+] Found {len(functions)} Lambda function(s)")
        for func in functions:
            print(f"\n  Function: {func.get('FunctionName')}")
            print(f"    Runtime: {func.get('Runtime')}")
            print(f"    Handler: {func.get('Handler')}")
            print(f"    Role: {func.get('Role')}")
            print(f"    Code Size: {func.get('CodeSize')} bytes")
            print(f"    Last Modified: {func.get('LastModified')}")
            # Get function URL if configured
            try:
                url_conf = client.get_function_url_config(FunctionName=func['FunctionName'])
                print(f"    Function URL: {url_conf.get('FunctionUrl')}")
            except:
                pass
    else:
        print(f"[-] Failed to list functions: {funcs}")

def enum_dynamodb():
    """Enumerate DynamoDB: tables, descriptions, item counts."""
    print_header("DynamoDB")
    client = get_client('dynamodb')
    
    success, tables = safe_call(client.list_tables)
    if success:
        table_names = tables.get('TableNames', [])
        print(f"[+] Found {len(table_names)} table(s)")
        for name in table_names:
            print(f"\n  Table: {name}")
            # Describe table
            success, desc = safe_call(client.describe_table, TableName=name)
            if success:
                table_info = desc.get('Table', {})
                print(f"    Status: {table_info.get('TableStatus')}")
                print(f"    Item Count: {table_info.get('ItemCount', 0)}")
                print(f"    Size (bytes): {table_info.get('TableSizeBytes', 0)}")
                print(f"    Attribute Definitions: {len(table_info.get('AttributeDefinitions', []))}")
                # Key schema
                keys = table_info.get('KeySchema', [])
                if keys:
                    print(f"    Key Schema: {', '.join([f'{k["AttributeName"]} ({k["KeyType"]})' for k in keys])}")
                # GSI/LSI counts
                gsi = table_info.get('GlobalSecondaryIndexes', [])
                lsi = table_info.get('LocalSecondaryIndexes', [])
                print(f"    Global Secondary Indexes: {len(gsi)}")
                print(f"    Local Secondary Indexes: {len(lsi)}")
            else:
                print(f"    Describe failed: {desc}")
    else:
        print(f"[-] Failed to list tables: {tables}")

def enum_sqs():
    """Enumerate SQS: queues, attributes, message counts."""
    print_header("SQS")
    client = get_client('sqs')
    
    success, queues = safe_call(client.list_queues)
    if success:
        queue_urls = queues.get('QueueUrls', [])
        print(f"[+] Found {len(queue_urls)} queue(s)")
        for url in queue_urls:
            print(f"\n  Queue URL: {url}")
            # Get queue attributes
            success, attrs = safe_call(client.get_queue_attributes, QueueUrl=url, AttributeNames=['All'])
            if success:
                attribs = attrs.get('Attributes', {})
                print(f"    Visibility Timeout: {attribs.get('VisibilityTimeout')}")
                print(f"    Message Retention: {attribs.get('MessageRetentionPeriod')} seconds")
                print(f"    Approx Messages: {attribs.get('ApproximateNumberOfMessages')}")
                print(f"    Approx Messages Not Visible: {attribs.get('ApproximateNumberOfMessagesNotVisible')}")
                print(f"    Delay Seconds: {attribs.get('DelaySeconds')}")
                if attribs.get('Policy'):
                    print(f"    Policy: {attribs.get('Policy')[:200]}..." if len(attribs.get('Policy', '')) > 200 else attribs.get('Policy'))
            else:
                print(f"    Get attributes failed: {attrs}")
    else:
        print(f"[-] Failed to list queues: {queues}")

def enum_sns():
    """Enumerate SNS: topics, subscriptions."""
    print_header("SNS")
    client = get_client('sns')
    
    success, topics = safe_call(client.list_topics)
    if success:
        topic_list = topics.get('Topics', [])
        print(f"[+] Found {len(topic_list)} topic(s)")
        for topic in topic_list:
            arn = topic.get('TopicArn')
            print(f"\n  Topic ARN: {arn}")
            # Get topic attributes
            success, attrs = safe_call(client.get_topic_attributes, TopicArn=arn)
            if success:
                attribs = attrs.get('Attributes', {})
                print(f"    Display Name: {attribs.get('DisplayName', 'N/A')}")
                print(f"    Owner: {attribs.get('Owner')}")
                print(f"    Subscriptions Pending: {attribs.get('SubscriptionsPending')}")
                print(f"    Subscriptions Confirmed: {attribs.get('SubscriptionsConfirmed')}")
                print(f"    Subscriptions Deleted: {attribs.get('SubscriptionsDeleted')}")
            # List subscriptions for topic
            success, subs = safe_call(client.list_subscriptions_by_topic, TopicArn=arn)
            if success:
                subscriptions = subs.get('Subscriptions', [])
                print(f"    Subscriptions: {len(subscriptions)}")
                for sub in subscriptions[:3]:
                    print(f"      - Protocol: {sub.get('Protocol')}, Endpoint: {sub.get('Endpoint')}, Arn: {sub.get('SubscriptionArn')}")
            else:
                print(f"    Subscriptions: {subs}")
    else:
        print(f"[-] Failed to list topics: {topics}")

def enum_rds():
    """Enumerate RDS: instances, clusters, snapshots."""
    print_header("RDS")
    client = get_client('rds')
    
    # DB instances
    success, dbs = safe_call(client.describe_db_instances)
    if success:
        instances = dbs.get('DBInstances', [])
        print(f"[+] Found {len(instances)} DB instance(s)")
        for inst in instances:
            print(f"\n  DB Instance: {inst.get('DBInstanceIdentifier')}")
            print(f"    Engine: {inst.get('Engine')} {inst.get('EngineVersion')}")
            print(f"    Class: {inst.get('DBInstanceClass')}")
            print(f"    Storage: {inst.get('AllocatedStorage')} GiB")
            print(f"    Status: {inst.get('DBInstanceStatus')}")
            print(f"    Endpoint: {inst.get('Endpoint', {}).get('Address')}:{inst.get('Endpoint', {}).get('Port')}")
            print(f"    Multi-AZ: {inst.get('MultiAZ')}")
            print(f"    VPC: {inst.get('DBSubnetGroup', {}).get('VpcId')}")
    else:
        print(f"[-] Failed to describe DB instances: {dbs}")
    
    # Snapshots
    success, snaps = safe_call(client.describe_db_snapshots)
    if success:
        snapshots = snaps.get('DBSnapshots', [])
        print(f"\n[+] Found {len(snapshots)} DB snapshot(s)")
        for snap in snapshots[:5]:
            print(f"  - {snap.get('DBSnapshotIdentifier')}: {snap.get('Engine')}, {snap.get('AllocatedStorage')} GiB, Created: {snap.get('SnapshotCreateTime')}")
    else:
        print(f"[-] Failed to describe DB snapshots: {snaps}")

def enum_iam():
    """Enumerate IAM: users, roles, policies, groups."""
    print_header("IAM")
    client = get_client('iam')
    
    # Users
    success, users = safe_call(client.list_users)
    if success:
        user_list = users.get('Users', [])
        print(f"[+] Found {len(user_list)} IAM user(s)")
        for user in user_list:
            print(f"\n  User: {user.get('UserName')}")
            print(f"    Arn: {user.get('Arn')}")
            print(f"    Created: {user.get('CreateDate')}")
            # List user policies
            success, policies = safe_call(client.list_user_policies, UserName=user['UserName'])
            if success:
                policy_names = policies.get('PolicyNames', [])
                print(f"    Inline Policies: {len(policy_names)}")
                for p in policy_names:
                    print(f"      - {p}")
            # Attached managed policies
            success, attached = safe_call(client.list_attached_user_policies, UserName=user['UserName'])
            if success:
                attached_policies = attached.get('AttachedPolicies', [])
                print(f"    Attached Managed Policies: {len(attached_policies)}")
                for p in attached_policies:
                    print(f"      - {p.get('PolicyName')} ({p.get('PolicyArn')})")
    else:
        print(f"[-] Failed to list users: {users}")
    
    # Roles
    success, roles = safe_call(client.list_roles)
    if success:
        role_list = roles.get('Roles', [])
        print(f"\n[+] Found {len(role_list)} IAM role(s)")
        for role in role_list[:5]:  # Limit display
            print(f"  - {role.get('RoleName')}: {role.get('Arn')}")
            print(f"    Trust Policy: {role.get('AssumeRolePolicyDocument')[:200]}..." if role.get('AssumeRolePolicyDocument') else "    Trust Policy: None")
    else:
        print(f"[-] Failed to list roles: {roles}")
    
    # Groups
    success, groups = safe_call(client.list_groups)
    if success:
        group_list = groups.get('Groups', [])
        print(f"\n[+] Found {len(group_list)} IAM group(s)")
        for group in group_list:
            print(f"  - {group.get('GroupName')}: {group.get('Arn')}")
    else:
        print(f"[-] Failed to list groups: {groups}")

def enum_secretsmanager():
    """Enumerate Secrets Manager: secrets and their values (first 10 chars)."""
    print_header("Secrets Manager")
    client = get_client('secretsmanager')
    
    success, secrets = safe_call(client.list_secrets)
    if success:
        secret_list = secrets.get('SecretList', [])
        print(f"[+] Found {len(secret_list)} secret(s)")
        for secret in secret_list:
            name = secret.get('Name')
            print(f"\n  Secret: {name}")
            print(f"    ARN: {secret.get('ARN')}")
            print(f"    Created: {secret.get('CreatedDate')}")
            print(f"    Last Changed: {secret.get('LastChangedDate')}")
            # Try to get secret value (may be restricted)
            try:
                val = client.get_secret_value(SecretId=name)
                if 'SecretString' in val:
                    secret_str = val['SecretString']
                    # Truncate for display
                    if len(secret_str) > 100:
                        secret_str = secret_str[:100] + '...'
                    print(f"    Secret Value (string): {secret_str}")
                elif 'SecretBinary' in val:
                    print(f"    Secret Value (binary): {len(val['SecretBinary'])} bytes")
            except ClientError as e:
                print(f"    Could not retrieve value: {e.response['Error']['Message']}")
    else:
        print(f"[-] Failed to list secrets: {secrets}")

def enum_ssm():
    """Enumerate SSM: parameters, documents."""
    print_header("SSM")
    client = get_client('ssm')
    
    # Parameters
    success, params = safe_call(client.describe_parameters, MaxResults=50)
    if success:
        param_list = params.get('Parameters', [])
        print(f"[+] Found {len(param_list)} SSM parameter(s)")
        for param in param_list[:10]:
            print(f"  - {param.get('Name')}: {param.get('Type')}, Version: {param.get('Version')}, Last Modified: {param.get('LastModifiedDate')}")
            # Try to get value
            try:
                val = client.get_parameter(Name=param['Name'], WithDecryption=True)
                value = val['Parameter']['Value']
                print(f"    Value: {value[:50]}..." if len(value) > 50 else f"    Value: {value}")
            except:
                pass
    else:
        print(f"[-] Failed to describe parameters: {params}")
    
    # Documents
    success, docs = safe_call(client.list_documents, MaxResults=50)
    if success:
        doc_list = docs.get('DocumentIdentifiers', [])
        print(f"\n[+] Found {len(doc_list)} SSM document(s)")
        for doc in doc_list[:5]:
            print(f"  - {doc.get('Name')}: Type: {doc.get('DocumentType')}, Owner: {doc.get('Owner')}")
    else:
        print(f"[-] Failed to list documents: {docs}")

def enum_kms():
    """Enumerate KMS: keys, aliases."""
    print_header("KMS")
    client = get_client('kms')
    
    # Keys
    success, keys = safe_call(client.list_keys, Limit=50)
    if success:
        key_list = keys.get('Keys', [])
        print(f"[+] Found {len(key_list)} KMS key(s)")
        for key in key_list:
            key_id = key.get('KeyId')
            print(f"\n  Key ID: {key_id}")
            # Describe key
            success, desc = safe_call(client.describe_key, KeyId=key_id)
            if success:
                meta = desc.get('KeyMetadata', {})
                print(f"    State: {meta.get('KeyState')}")
                print(f"    Origin: {meta.get('Origin')}")
                print(f"    Key Manager: {meta.get('KeyManager')}")
                print(f"    Enabled: {meta.get('Enabled')}")
                print(f"    Creation Date: {meta.get('CreationDate')}")
                print(f"    Description: {meta.get('Description', 'N/A')}")
            else:
                print(f"    Describe failed: {desc}")
    else:
        print(f"[-] Failed to list keys: {keys}")

def enum_cloudformation():
    """Enumerate CloudFormation: stacks, stack resources."""
    print_header("CloudFormation")
    client = get_client('cloudformation')
    
    success, stacks = safe_call(client.list_stacks, StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'CREATE_IN_PROGRESS'])
    if success:
        stack_list = stacks.get('StackSummaries', [])
        print(f"[+] Found {len(stack_list)} CloudFormation stack(s)")
        for stack in stack_list:
            print(f"\n  Stack: {stack.get('StackName')}")
            print(f"    Status: {stack.get('StackStatus')}")
            print(f"    Created: {stack.get('CreationTime')}")
            print(f"    Template Description: {stack.get('TemplateDescription', 'N/A')}")
            # List resources
            success, resources = safe_call(client.list_stack_resources, StackName=stack['StackName'])
            if success:
                res_list = resources.get('StackResourceSummaries', [])
                print(f"    Resources: {len(res_list)}")
                for res in res_list[:5]:
                    print(f"      - {res.get('LogicalResourceId')} ({res.get('ResourceType')}) -> {res.get('PhysicalResourceId', 'N/A')}")
    else:
        print(f"[-] Failed to list stacks: {stacks}")

def enum_cognito():
    """Enumerate Cognito: user pools, identity pools."""
    print_header("Cognito")
    # Cognito User Pools
    try:
        client = get_client('cognito-idp')
        success, pools = safe_call(client.list_user_pools, MaxResults=50)
        if success:
            pool_list = pools.get('UserPools', [])
            print(f"[+] Found {len(pool_list)} Cognito User Pool(s)")
            for pool in pool_list:
                print(f"  - {pool.get('Name')} (ID: {pool.get('Id')}), Status: {pool.get('Status')}, Lambda Config: {pool.get('LambdaConfig')}")
        else:
            print(f"[-] Failed to list user pools: {pools}")
    except Exception as e:
        print(f"[-] Cognito User Pools not accessible: {e}")
    
    # Identity Pools
    try:
        client = get_client('cognito-identity')
        success, pools = safe_call(client.list_identity_pools, MaxResults=50)
        if success:
            pool_list = pools.get('IdentityPools', [])
            print(f"\n[+] Found {len(pool_list)} Cognito Identity Pool(s)")
            for pool in pool_list:
                print(f"  - {pool.get('IdentityPoolName')} (ID: {pool.get('IdentityPoolId')})")
        else:
            print(f"[-] Failed to list identity pools: {pools}")
    except Exception as e:
        print(f"[-] Cognito Identity Pools not accessible: {e}")

def enum_other_services():
    """Enumerate additional services: SES, SageMaker, Glue, Athena, Kinesis, Firehose."""
    print_header("Additional Services")
    
    # SES
    try:
        client = get_client('ses')
        success, identities = safe_call(client.list_identities)
        if success:
            identities_list = identities.get('Identities', [])
            print(f"[+] SES Identities: {len(identities_list)}")
            for identity in identities_list[:5]:
                print(f"  - {identity}")
        else:
            print(f"[-] SES: {identities}")
    except Exception as e:
        print(f"[-] SES not accessible: {e}")
    
    # SageMaker
    try:
        client = get_client('sagemaker')
        success, notebooks = safe_call(client.list_notebook_instances, MaxResults=10)
        if success:
            instances = notebooks.get('NotebookInstances', [])
            print(f"\n[+] SageMaker Notebook Instances: {len(instances)}")
            for inst in instances:
                print(f"  - {inst.get('NotebookInstanceName')} ({inst.get('InstanceType')}) - Status: {inst.get('NotebookInstanceStatus')}")
        else:
            print(f"[-] SageMaker: {notebooks}")
    except Exception as e:
        print(f"[-] SageMaker not accessible: {e}")
    
    # Glue
    try:
        client = get_client('glue')
        success, databases = safe_call(client.get_databases)
        if success:
            dbs = databases.get('DatabaseList', [])
            print(f"\n[+] Glue Databases: {len(dbs)}")
            for db in dbs:
                print(f"  - {db.get('Name')}: {db.get('Description', '')}")
        else:
            print(f"[-] Glue: {databases}")
    except Exception as e:
        print(f"[-] Glue not accessible: {e}")
    
    # Athena
    try:
        client = get_client('athena')
        success, catalogs = safe_call(client.list_data_catalogs)
        if success:
            catalogs_list = catalogs.get('DataCatalogs', [])
            print(f"\n[+] Athena Data Catalogs: {len(catalogs_list)}")
            for cat in catalogs_list:
                print(f"  - {cat.get('CatalogName')} ({cat.get('Type')})")
        else:
            print(f"[-] Athena: {catalogs}")
    except Exception as e:
        print(f"[-] Athena not accessible: {e}")
    
    # Kinesis
    try:
        client = get_client('kinesis')
        success, streams = safe_call(client.list_streams)
        if success:
            stream_names = streams.get('StreamNames', [])
            print(f"\n[+] Kinesis Streams: {len(stream_names)}")
            for stream in stream_names:
                print(f"  - {stream}")
        else:
            print(f"[-] Kinesis: {streams}")
    except Exception as e:
        print(f"[-] Kinesis not accessible: {e}")
    
    # Firehose
    try:
        client = get_client('firehose')
        success, deliveries = safe_call(client.list_delivery_streams)
        if success:
            stream_names = deliveries.get('DeliveryStreamNames', [])
            print(f"\n[+] Firehose Delivery Streams: {len(stream_names)}")
            for stream in stream_names:
                print(f"  - {stream}")
        else:
            print(f"[-] Firehose: {deliveries}")
    except Exception as e:
        print(f"[-] Firehose not accessible: {e}")

def enum_cloudwatch():
    """Enumerate CloudWatch: alarms, logs groups, metrics."""
    print_header("CloudWatch")
    
    # Alarms
    try:
        client = get_client('cloudwatch')
        success, alarms = safe_call(client.describe_alarms)
        if success:
            alarm_list = alarms.get('MetricAlarms', [])
            print(f"[+] Found {len(alarm_list)} CloudWatch alarm(s)")
            for alarm in alarm_list[:5]:
                print(f"  - {alarm.get('AlarmName')}: {alarm.get('StateValue')} (Metric: {alarm.get('MetricName')})")
        else:
            print(f"[-] CloudWatch alarms: {alarms}")
    except Exception as e:
        print(f"[-] CloudWatch not accessible: {e}")
    
    # Log Groups
    try:
        client = get_client('logs')
        success, groups = safe_call(client.describe_log_groups, limit=20)
        if success:
            log_groups = groups.get('logGroups', [])
            print(f"\n[+] Found {len(log_groups)} CloudWatch Log Group(s)")
            for group in log_groups:
                print(f"  - {group.get('logGroupName')}: {group.get('storedBytes')} bytes, Retention: {group.get('retentionInDays')} days")
        else:
            print(f"[-] CloudWatch Logs: {groups}")
    except Exception as e:
        print(f"[-] CloudWatch Logs not accessible: {e}")

# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    print("=" * 80)
    print(" ULTIMATE AWS/LOCALSTACK ENUMERATION ".center(80, '='))
    print("=" * 80)
    print(f"Endpoint: {ENDPOINT}")
    print(f"Region: {REGION}")
    print(f"Time: {datetime.now()}")
    print("=" * 80)
    
    # List of all enumeration functions
    enum_functions = [
        enum_s3,
        enum_ec2,
        enum_lambda,
        enum_dynamodb,
        enum_sqs,
        enum_sns,
        enum_rds,
        enum_iam,
        enum_secretsmanager,
        enum_ssm,
        enum_kms,
        enum_cloudformation,
        enum_cognito,
        enum_cloudwatch,
        enum_other_services,
    ]
    
    for func in enum_functions:
        try:
            func()
        except Exception as e:
            print(f"\n[!] ERROR in {func.__name__}: {e}")
    
    print("\n" + "=" * 80)
    print(" ENUMERATION COMPLETE ".center(80, '='))
    print("=" * 80)

if __name__ == "__main__":
    main()
