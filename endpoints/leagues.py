import json
from contextlib import closing

import psycopg2
from flask import request
from flask_restplus import Namespace, Resource
from psycopg2 import extras as extras

from restplus import api
from utilities import response_case, get_json_from_psql, CONNECT_CONF


leagues_ns = Namespace('Leagues', description='leagues endpoints')

leagues_parser = api.parser()
leagues_parser.add_argument(
    name='league_id',
    required=False,
    type=int,
)

@leagues_ns.route('')
class Leagues(Resource):
    """Общая информация по лигам."""

    @api.expect(leagues_parser)
    @api.doc(responses={
        200: response_case(
            desc='Информация по лигам успешно найдена',
            resp=[
                {
                    "id": 1,
                    "name": "English Premier League"
                }
            ]
        ),
        400: response_case(
            desc='Неправильные входные данные',
            resp={
                'message': 'Input payload validation failed',
                'errors': {
                    'league_id': 'invalid literal for int() with base 10: some_value'
                }
            }
        ),
        404: response_case(
            desc='Неизвестный ендпоинт',
            resp={
                'message': 'The requested URL was not found on the server. If you entered the URL '
                           'manually please check your spelling and try again.',
                'success': False,
            }
        ),
        500: response_case(
            desc='Внутреняя ошибка сервера',
            resp={
                'message': 'Internal Server Error',
                'success': False,
            }
        ),

    })
    def get(self):
        """Эндпоинт отдает информацию обо всех лигах, если не указан league_id.
        Если он указан, то отдает информацию по лиге."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                input_data = leagues_parser.parse_args(request)
                league_id = input_data['league_id']
                if not league_id:
                    cursor.execute('SELECT * FROM leagues')
                    data = cursor.fetchall()
                    return get_json_from_psql(data)
                else:
                    cursor.execute('SELECT * FROM leagues WHERE id = %s', (league_id,))
                    data = cursor.fetchall()
                    if data:
                        return get_json_from_psql(data)
                    else:
                        return {
                                   'message': 'Input payload validation failed',
                                   'errors': {
                                       'league_id': 'League_id not exist'
                                   },
                               }, 400
