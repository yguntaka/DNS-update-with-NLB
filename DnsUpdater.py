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
elb = boto3.client('elbv2')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    responseData={}
    try:
        if event['RequestType'] == 'Delete':
            print("Request Type:",event['RequestType'])
            ELBID=event['ResourceProperties']['ELBID']
            print ("Deleting NLB:", ELBID, "Invoke on-prem DNS api here")
            #HostedZoneID=get_elb(ELBID)
            #responseData={'HostedZoneID':HostedZoneID}
            print("This print message will be replaced by your api call to on-prem DNS")
        elif event['RequestType'] == 'Create':
            print("Request Type:",event['RequestType'])
            ELBID=event['ResourceProperties']['ELBID']
            HostedZoneID=get_elb(ELBID)
            responseData={'HostedZoneID':HostedZoneID}
            print("This print message will be replaced by your api call to on-prem DNS")
        elif event['RequestType'] == 'Update':
            print("Request Type:",event['RequestType'])
            ELBID=event['ResourceProperties']['ELBID']
            HostedZoneID=get_elb(ELBID)
            responseData={'HostedZoneID':HostedZoneID}
            print("This print message will be replaced by your api call to on-prem DNS")
        responseStatus = 'SUCCESS'
    except Exception as e:
        print('Failed to process:', e)
        responseStatus = 'FAILED'
        responseData = {'Failed': 'Something bad happened.'}
    send(event, context, responseStatus, responseData)

def get_elb(ELBID):
    response = elb.describe_load_balancers(
    Names=[
        ELBID,
        ],
    )

    print("Printing the Hosted Zone Id & DNS Name for this NLB ....")
    HostedZoneID=response["LoadBalancers"][0]['CanonicalHostedZoneId']
    DnsName=response["LoadBalancers"][0]['DNSName']
    print("HostedZoneID--> ",HostedZoneID, " DNSName--> ",DnsName)
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
