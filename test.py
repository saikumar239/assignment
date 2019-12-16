import json
import urllib.parse
import boto3
import logging
import json
from botocore.vendored import requests

print('Loading function')

s3 = boto3.client('s3')
ssm_client = boto3.client("ssm")
data_parameter = {}
dict = {}
bucket = "code-test-saiku1"
SUCCESS = "SUCCESS"
FAILED = "FAILED"


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s: %(message)s')

    try:
        reason_data = ""
        parameter = ssm_client.get_parameter(Name='UserName', WithDecryption=False)
        print("parameter values are {} " .format(parameter))
        dict['Name'] = parameter['Parameter']['Name']
        dict['Value'] = parameter['Parameter']['Value']
        data_parameter = json.dumps(dict)
        print(data_parameter)
        response = s3.put_object(Bucket=bucket, Key='myList001', Body=data_parameter)
        response_data = {
            'AccountId': event['AWSAccountId'],

        }
        send(
                        event=event,
                        context=context,
                        response_status=SUCCESS,
                        response_data=response_data,
                        reason_data=reason_data
                    )
    except Exception as e:
        print(e)
        print('Error in creation. Make sure they exist and your bucket is in the same region as this function.')
        return False
def send(self, event, context, response_status, response_data, reason_data):
        '''
        Send status to the cloudFormation
        Template.
        '''
        print("Inside send method")
        response_url = event['ResponseURL']

        response_body = {}
        response_body['Status'] = response_status
        response_body['Reason'] = reason_data + ' See the details in CloudWatch Log Stream: ' + \
                                  context.log_stream_name
        response_body['PhysicalResourceId'] = event['PhysicalResourceId']
        response_body['StackId'] = event['StackId']
        response_body['RequestId'] = event['RequestId']
        response_body['LogicalResourceId'] = event['LogicalResourceId']
        response_body['Data'] = response_data

        json_responsebody = json.dumps(response_body)

        print("Response body:{}".format(json_responsebody))

        headers = {
            'content-type': '',
            'content-length': str(len(json_responsebody))
        }

        try:
            response = requests.put(response_url,
                                    data=json_responsebody,
                                    headers=headers)
            print("Status code:{} ".format(response.reason))
        except Exception as exception:
            print("send(..) failed executing requests.put(..):{} ".format(str(exception)))

