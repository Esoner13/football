from contextlib import closing

import psycopg2
from flask import request
from flask_restplus import Namespace, Resource
from psycopg2 import extras as extras

from restplus import api
from utilities import response_case, CONNECT_CONF, find_id, get_json_from_psql


goals_ns = Namespace('Goals', description='goals endpoints')

goals_parser = api.parser()
goals_parser.add_argument(
    name='goal_id',
    required=False,
    type=int,
)

create_goal_parser = api.parser()
create_goal_parser.add_argument(
    name='match_id',
    required=True,
    type=int,
)
create_goal_parser.add_argument(
    name='player_id',
    required=True,
    type=int,
)
create_goal_parser.add_argument(
    name='time',
    required=True,
    type=str,
    default='01:02:04'
)

@goals_ns.route('')
class Goals(Resource):
    """Общая информация по голам."""

    @api.expect(goals_parser)
    @api.doc(responses={
        200: response_case(
            desc='Информация по голам успешно найдена',
            resp=[
                {
                    "id": 1,
                    "match_id": 1,
                    "player_id": 10,
                    "time": "01:21:28"
                },
            ]
        ),
        400: response_case(
            desc='Неправильные входные данные',
            resp={
                'message': 'Input payload validation failed',
                'errors': {
                    'goal_id': 'invalid literal for int() with base 10: some_value'
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
        """Эндпоинт отдает информацию обо всех голах, если не указан goal_id.
        Если он указан, то отдает информацию по голу."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                input_data = goals_parser.parse_args(request)
                goal_id = input_data['goal_id']
                if not goal_id:
                    cursor.execute('SELECT * FROM goals')
                    data = cursor.fetchall()
                    return get_json_from_psql(data)
                else:
                    cursor.execute('SELECT * FROM goals WHERE id = %s', (goal_id,))
                    data = cursor.fetchall()
                    if data:
                        return get_json_from_psql(data)
                    else:
                        return {
                                   'message': 'Input payload validation failed',
                                   'errors': {
                                       'goal_id': 'Goal_id not exist'
                                   },
                               }, 400


    @api.expect(create_goal_parser)
    @api.doc(responses={
        200: response_case(
            desc='Гол успешно добавлен',
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
    def post(self):
        """Эндпоинт для добавления нового гола."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor() as cursor:
                input_data = create_goal_parser.parse_args(request)
                try:
                    cursor.execute(
                        'INSERT INTO goals(match_id, player_id, time) '
                        'VALUES (%s, %s, %s)',
                        (input_data['match_id'], input_data['player_id'], input_data['time'])
                    )
                    conn.commit()
                    return {'success': True}
                except psycopg2.errors.ForeignKeyViolation as error:
                    conn.rollback()
                    return {
                        'message': 'Input payload validation failed',
                        'errors': {
                            find_id(error):
                                'Id does not exist'
                        }
                    }, 400
                except Exception:
                    conn.rollback()
                    raise Exception
