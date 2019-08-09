from __future__ import print_function
import json
import boto3
import urllib
from botocore.vendored import requests

SUCCESS = "SUCCESS"
FAILED = "FAILED"
# Credits: https://github.com/awslabs/aws-cloudformation-templates/tree/master/aws/solutions/lambda-backed-cloudformation-custom-resources/get_vpc_main_route_table_id

print('Loading function')
ec2 = boto3.client('ec2')
elb = boto3.client('elb')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    responseData={}
    try:
        if event['RequestType'] == 'Delete':
            print("Request Type:",event['RequestType'])
            ELBID=event['ResourceProperties']['ELBID']
            # Eventually, on-prem DNS update PUT or URL can go here
            # For now, calling the function to describe elb and get hosted zone id
            HostedZoneID=get_elb(ELBID)
            responseData={'HostedZoneID':HostedZoneID}
            print("Sending response to custom resource")
        elif event['RequestType'] == 'Create':
            print("Request Type:",event['RequestType'])
            ELBID=event['ResourceProperties']['ELBID']
            HostedZoneID=get_elb(ELBID)
            responseData={'HostedZoneID':HostedZoneID}
            print("Sending response to custom resource")
        elif event['RequestType'] == 'Update':
            print("Request Type:",event['RequestType'])
            ELBID=event['ResourceProperties']['ELBID']
            HostedZoneID=get_elb(ELBID)
            responseData={'HostedZoneID':HostedZoneID}
            print("Sending response to custom resource")
        responseStatus = 'SUCCESS'
    except Exception as e:
        print('Failed to process:', e)
        responseStatus = 'FAILED'
        responseData = {'Failed': 'Something bad happened.'}
    send(event, context, responseStatus, responseData)

def get_elb(ELBID):
    response = elb.describe_load_balancers(
    LoadBalancerNames=[
        ELBID, # this is where I am seeing errors in stack creation as the describe elb call cant find the nlb passed (FsNlb1)
        ],
    )
    print("Printing the Hosted Zone for this ELB ....")
    HostedZone=response['HostedZone'][1]['HostedZoneID']
    print(HostedZoneID)
    return HostedZoneID

# Include DNS Update URL/end point here.
def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']
    print(responseUrl)
    responseBody = {'Status': responseStatus,
                    'Reason': 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
                    'PhysicalResourceId': physicalResourceId or context.log_stream_name,
                    'StackId': event['StackId'],
                    'RequestId': event['RequestId'],
                    'LogicalResourceId': event['LogicalResourceId'],
                    'Data': responseData}
    json_responseBody = json.dumps(responseBody)
    print("Response body:\n" + json_responseBody)
    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }
    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))
