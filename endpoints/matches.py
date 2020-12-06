from contextlib import closing

import psycopg2
from flask import request
from flask_restplus import Namespace, Resource
from psycopg2 import extras as extras

from restplus import api
from utilities import response_case, get_json_from_psql, CONNECT_CONF, find_id


matches_ns = Namespace('Matches', description='matches endpoints')

matches_parser = api.parser()
matches_parser.add_argument(
    name='match_id',
    required=False,
    type=int,
)

create_match_parser = api.parser()
create_match_parser.add_argument(
    name='league_id',
    required=True,
    type=int,
)
create_match_parser.add_argument(
    name='host_team_id',
    required=True,
    type=int,
)
create_match_parser.add_argument(
    name='guest_team_id',
    required=True,
    type=int,
)
create_match_parser.add_argument(
    name='stadium_id',
    required=True,
    type=int,
)
create_match_parser.add_argument(
    name='date',
    required=True,
    type=str,
    default='2020-01-30'
)
create_match_parser.add_argument(
    name='tour',
    required=True,
    type=int,
)

@matches_ns.route('')
class Matches(Resource):
    """Общая информация по матчам."""

    @api.expect(matches_parser)
    @api.doc(responses={
        200: response_case(
            desc='Информация по матчам успешно найдена',
            resp=[
                {
                    'id': 1,
                    'league_id': 1,
                    'host_team_id': 1,
                    'guest_team_id': 2,
                    'stadium_id': 1,
                    'date': '2017-08-06',
                    'tour': 1
                }
            ]
        ),
        400: response_case(
            desc='Неправильные входные данные',
            resp={
                'message': 'Input payload validation failed',
                'errors': {
                    'match_id': 'invalid literal for int() with base 10: some_value'
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
        """Эндпоинт отдает информацию обо всех матчах, если не указан match_id.
        Если он указан, то отдает информацию по матчу."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                input_data = matches_parser.parse_args(request)
                match_id = input_data['match_id']
                if not match_id:
                    cursor.execute('SELECT * FROM matches')
                    data = cursor.fetchall()
                    return get_json_from_psql(data)
                else:
                    cursor.execute('SELECT * FROM matches WHERE id = %s', (match_id,))
                    data = cursor.fetchall()
                    if data:
                        return get_json_from_psql(data)
                    else:
                        return {
                                   'message': 'Input payload validation failed',
                                   'errors': {
                                       'match_id': 'Match_id not exist'
                                   },
                               }, 400

    @api.expect(create_match_parser)
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
        """Эндпоинт для создания нового матча."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor() as cursor:
                input_data = create_match_parser.parse_args(request)

                if input_data['host_team_id'] == input_data['guest_team_id']:
                    return {
                        'message': 'Input payload validation failed',
                        'errors': {
                            'host_team_id': "Team can't play against itself",
                            'guest_team_id': "Team can't play against itself"
                        }
                    }, 400

                try:
                    cursor.execute(
                        'INSERT INTO matches(league_id, host_team_id, guest_team_id, '
                        'stadium_id, date, tour) '
                        'VALUES (%s, %s, %s, %s, %s, %s)',
                        (input_data['league_id'], input_data['host_team_id'],
                         input_data['guest_team_id'], input_data['stadium_id'],
                         input_data['date'], input_data['tour'])
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
