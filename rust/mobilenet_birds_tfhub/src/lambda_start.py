import json
import boto3
import uuid


class SqsDao(object):
    _instance = None
    _queue = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self) -> None:
        sqs = boto3.resource('sqs')
        self._queue = sqs.get_queue_by_name(QueueName='mq_test.fifo')

    def sqs_send_msg(self, body: str) -> bool:
        response = self._queue.send_message(
            MessageBody=body,
            MessageGroupId='sqs_test2',
            MessageDeduplicationId=str(uuid.uuid4())
        )
        return response['ResponseMetadata']['HTTPStatusCode'] == 200


def record_handler(record: dict):
    body = record.get('body')
    msg_group_id = record.get('attributes', {}).get('MessageGroupId')
    # msg_dedup_id = record.get('attributes', {}).get('MessageDeduplicationId')
    res = True
    if msg_group_id == 'sqs_test' and body:
        res = SqsDao().sqs_send_msg(body)
        print("record_handler to sqs_test2 result %r" % res)
    return res


def lambda_handler(event, context):
    # TODO implement
    print(event)
    record_res_list = []
    for record in event['Records']:
        res = record_handler(record)
        record_res_list.append(res)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'result': 'ok',
            'successful': all(record_res_list)
        })
    }
