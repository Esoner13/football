import datetime
import json


CONNECT_CONF = {
    'dbname': 'football_crm',
    'user': 'postgres',
    'password': 'password',
    'host': '146.59.16.248'
}


def response_case(desc, resp):
    """Форматирование ответа апи."""
    return f"""
    {desc}:
    {json.dumps(resp)}
    """


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def find_id(error):
    return error.args[0].split('\n')[1].split('(')[1].split(')')[0]


def get_json_from_psql(data):
    return json.loads(json.dumps(data, cls=DateTimeEncoder))