import json
from contextlib import closing

import psycopg2
from flask import request
from flask_restplus import Namespace, Resource
from psycopg2 import extras as extras

from restplus import api
from utilities import response_case, get_json_from_psql, CONNECT_CONF


stadiums_ns = Namespace('Stadiums', description='stadiums endpoints')

stadiums_parser = api.parser()
stadiums_parser.add_argument(
    name='stadium_id',
    required=False,
    type=int,
)

@stadiums_ns.route('')
class Matches(Resource):
    """Общая информация по матчам."""

    @api.expect(stadiums_parser)
    @api.doc(responses={
        200: response_case(
            desc='Информация по стадионам успешно найдена',
            resp=[
                {
                    "id": 1,
                    "name": "Allianz Arena",
                    "capacity": 90000,
                    "year_of_foundation": 1968
                }
            ]
        ),
        400: response_case(
            desc='Неправильные входные данные',
            resp={
                'message': 'Input payload validation failed',
                'errors': {
                    'stadium_id': 'invalid literal for int() with base 10: some_value'
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
        """Эндпоинт отдает информацию обо всех стадионах, если не указан stadium_id.
        Если он указан, то отдает информацию по стадионе."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                input_data = stadiums_parser.parse_args(request)
                stadium_id = input_data['stadium_id']
                if not stadium_id:
                    cursor.execute('SELECT * FROM stadiums')
                    data = cursor.fetchall()
                    return get_json_from_psql(data)
                else:
                    cursor.execute('SELECT * FROM stadiums WHERE id = %s', (stadium_id,))
                    data = cursor.fetchall()
                    if data:
                        return get_json_from_psql(data)
                    else:
                        return {
                                   'message': 'Input payload validation failed',
                                   'errors': {
                                       'stadium_id': 'Stadium_id not exist'
                                   },
                               }, 400
