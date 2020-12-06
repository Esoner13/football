import json
from contextlib import closing

import psycopg2
from flask import request
from flask_restplus import Namespace, Resource
from psycopg2 import extras as extras

from restplus import api
from utilities import response_case, get_json_from_psql, CONNECT_CONF


teams_ns = Namespace('Teams', description='teams endpoints')

teams_parser = api.parser()
teams_parser.add_argument(
    name='team_id',
    required=False,
    type=int,
)

update_team_parser = api.parser()
update_team_parser.add_argument(
    name='id',
    required=True,
    type=int,
)
update_team_parser.add_argument(
    name='coach',
    required=True,
    type=str,
)

@teams_ns.route('')
class Teams(Resource):
    """Общая информация по командам."""

    @api.expect(teams_parser)
    @api.doc(responses={
        200: response_case(
            desc='Информация по командам успешно найдена',
            resp=[
                {
                    "id": 1,
                    "stadium_id": 1,
                    "name": "Bayern",
                    "coach": "Muller Fritz",
                    "city": "Munchen"
                }
            ]
        ),
        400: response_case(
            desc='Неправильные входные данные',
            resp={
                'message': 'Input payload validation failed',
                'errors': {
                    'team_id': 'invalid literal for int() with base 10: some_value'
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
        """Эндпоинт отдает информацию обо всех командах, если не указан team_id.
        Если он указан, то отдает информацию по команде."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                input_data = teams_parser.parse_args(request)
                team_id = input_data['team_id']
                if not team_id:
                    cursor.execute('SELECT * FROM teams')
                    data = cursor.fetchall()
                    return get_json_from_psql(data)
                else:
                    cursor.execute('SELECT * FROM teams WHERE id = %s', (team_id,))
                    data = cursor.fetchall()
                    if data:
                        return get_json_from_psql(data)
                    else:
                        return {
                                   'message': 'Input payload validation failed',
                                   'errors': {
                                       'team_id': 'Team_id not exist'
                                   },
                               }, 400

    @api.expect(update_team_parser)
    @api.doc(responses={
        200: response_case(
            desc='Команда успешно обновлена',
            resp={
                'success': True,
            }
        ),
        400: response_case(
            desc='Неправильные входные данные',
            resp={
                'message': 'Input payload validation failed',
                'errors': {
                    'player_id': 'invalid literal for int() with base 10: some_value'
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
    def put(self):
        """Эндпоинт для обновления тренера команды."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                input_data = update_team_parser.parse_args(request)
                cursor.execute(
                    'SELECT id '
                    'FROM teams '
                    'WHERE id = %s',
                    (input_data['id'],)
                )
                is_team_exist = cursor.fetchall()
                if not is_team_exist:
                    return {
                        'message': 'Input payload validation failed',
                        'errors': {
                            'id': 'Team does not exist'
                        }
                    }, 400

                try:
                    cursor.execute(
                        'UPDATE teams '
                        'SET coach = %s '
                        'WHERE id = %s',
                        (input_data['coach'], input_data['id'],)
                    )
                    conn.commit()
                    return {
                        'success': True
                    }
                except Exception:
                    conn.rollback()
                    raise Exception
