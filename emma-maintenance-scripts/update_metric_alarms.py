from shared import config
from shared.aws_util import get_aws_cloudwatch_client

client = get_aws_cloudwatch_client()

alarms = client.describe_alarms(AlarmNamePrefix='QA')

for alarm in alarms['MetricAlarms']:
    print('Metric alarm ' + alarm['AlarmName'])
    client.delete_alarms(AlarmNames=[alarm['AlarmName']])

    # dimensions = alarm['Dimensions']
    # new_dimensions = [dim for dim in dimensions if not ('DomainName' == dim.get('Name'))]
    # new_dimensions.append({"Name": "DomainName", "Value": "emma-nonlive"})
    # client.put_metric_alarm(
    #     AlarmName=alarm['AlarmName'].replace('QA', 'Nonlive'),
    #     # AlarmDescription=alarm['AlarmDescription'].replace('QA','Nonlive'),
    #     ActionsEnabled=alarm['ActionsEnabled'],
    #     OKActions=alarm['OKActions'],
    #     AlarmActions=alarm['AlarmActions'],
    #     InsufficientDataActions=alarm['InsufficientDataActions'],
    #     MetricName=alarm['MetricName'],
    #     Namespace=alarm['Namespace'],
    #     Statistic=alarm['Statistic'],
    #     Dimensions=new_dimensions,
    #     Period=alarm['Period'],
    #     EvaluationPeriods=alarm['EvaluationPeriods'],
    #     DatapointsToAlarm=alarm['DatapointsToAlarm'],
    #     Threshold=alarm['Threshold'],
    #     ComparisonOperator=alarm['ComparisonOperator'],
    #     Tags=[
    #         {'Key': 'env', 'Value': 'nonlive'},
    #         {'Key': 'product', 'Value': 'emma'},
    #     ]
    # )
