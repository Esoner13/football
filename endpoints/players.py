import datetime
from contextlib import closing

import psycopg2
from flask import request
from flask_restplus import Namespace, Resource
from psycopg2 import extras as extras

from restplus import api
from utilities import response_case, get_json_from_psql, CONNECT_CONF, find_id


players_ns = Namespace('Players', description='players endpoints')

players_parser = api.parser()
players_parser.add_argument(
    name='player_id',
    required=False,
    type=int,
)

add_player_parser = api.parser()
add_player_parser.add_argument(
    name='last_name',
    required=True,
    type=str,
    default='Sharon'
)
add_player_parser.add_argument(
    name='first_name',
    required=True,
    type=str,
    default='Micheline'
)
add_player_parser.add_argument(
    name='middle_name',
    required=True,
    type=str,
    default='Anabel'
)
add_player_parser.add_argument(
    name='date_of_birth',
    required=True,
    type=str,
    default='2017-11-28'
)
add_player_parser.add_argument(
    name='place_of_birth',
    required=True,
    type=str,
    default='Misty'
)
add_player_parser.add_argument(
    name='team_id',
    required=True,
    type=int,
    default=1
)
add_player_parser.add_argument(
    name='number',
    required=True,
    type=int,
    default=1
)
add_player_parser.add_argument(
    name='position',
    required=True,
    type=str,
    default='forward'
)
add_player_parser.add_argument(
    name='citizenship',
    required=True,
    type=str,
    default='British'
)
add_player_parser.add_argument(
    name='height',
    required=True,
    type=int,
    default=183
)
add_player_parser.add_argument(
    name='weight',
    required=True,
    type=int,
    default=88
)

update_player_parser = api.parser()
update_player_parser.add_argument(
    name='id',
    required=True,
    type=int,
)
update_player_parser.add_argument(
    name='number',
    required=False,
    type=int,
)
update_player_parser.add_argument(
    name='position',
    required=False,
    type=int,
)
update_player_parser.add_argument(
    name='citizenship',
    required=False,
    type=str,
)
update_player_parser.add_argument(
    name='height',
    required=False,
    type=int,
)
update_player_parser.add_argument(
    name='weight',
    required=False,
    type=int,
)

@players_ns.route('')
class Players(Resource):
    """Общая информация по матчам."""

    @api.expect(players_parser)
    @api.doc(responses={
        200: response_case(
            desc='Игрок успешно добавлен',
            resp=[
                {
                    "id": 2,
                    "last_name": "Daisie",
                    "first_name": "Mathilda",
                    "middle_name": "Vanni",
                    "date_of_birth": "2018-07-08",
                    "place_of_birth": "Dulcy",
                    "team_id": 1,
                    "number": 1,
                    "position": "midfielder",
                    "citizenship": "Dutch",
                    "height": 177,
                    "weight": 118
                }
            ]
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
    def get(self):
        """Эндпоинт отдает информацию обо всех игроках, если не указан player_id.
        Если он указан, то отдает информацию по игроку."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                input_data = players_parser.parse_args(request)
                player_id = input_data['player_id']
                if not player_id:
                    cursor.execute('SELECT * FROM players')
                    data = cursor.fetchall()
                    return get_json_from_psql(data)
                else:
                    cursor.execute('SELECT * FROM players WHERE id = %s', (player_id,))
                    data = cursor.fetchall()
                    if data:
                        return get_json_from_psql(data)
                    else:
                        return {
                                   'message': 'Input payload validation failed',
                                   'errors': {
                                       'player_id': 'Player_id not exist'
                                   },
                               }, 400

    @api.expect(add_player_parser)
    @api.doc(responses={
        200: response_case(
            desc='Игрок успешно добавлен',
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
        """Эндпоинт для создания нового игрока.
        1 игрок не может принадлежать нескольким командам."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor() as cursor:
                input_data = add_player_parser.parse_args(request)
                new_player = (
                    input_data['last_name'],
                    input_data['first_name'],
                    input_data['middle_name'],
                    datetime.datetime.strptime(input_data['date_of_birth'], '%Y-%m-%d').date(),
                    input_data['place_of_birth'],
                    input_data['position'],
                    input_data['citizenship'],
                    input_data['height'],
                    input_data['weight'],
                )

                cursor.execute('SELECT last_name, first_name, middle_name, date_of_birth, '
                               'place_of_birth, position, citizenship, height, '
                               'weight FROM players')
                all_players = cursor.fetchall()
                for player in all_players:
                    if new_player == player:
                        return {
                                   'message': 'Input payload validation failed',
                                   'errors': {
                                       'last_name': 'Player already in a some team',
                                       'first_name': 'Player already in a some team',
                                       'middle_name': 'Player already in a some team',
                                       'date_of_birth': 'Player already in a some team',
                                       'place_of_birth': 'Player already in a some team',
                                       'position': 'Player already in a some team',
                                       'citizenship': 'Player already in a some team',
                                       'height': 'Player already in a some team',
                                       'weight': 'Player already in a some team',
                                   }
                               }, 400

                cursor.execute(
                    'SELECT number '
                    'FROM players '
                    'WHERE team_id =  %s',
                    (input_data['team_id'],)
                )
                all_taken_numbers = cursor.fetchall()

                for taken_number in all_taken_numbers:
                    if taken_number[0] == input_data['number']:
                        return {
                                   'message': 'Input payload validation failed',
                                   'errors': {
                                       'position': "The player's number is occupied"
                                   }
                               }, 400
                try:
                    cursor.execute(
                        'INSERT INTO players(last_name, first_name, middle_name, date_of_birth, '
                        'place_of_birth, team_id, number, position, '
                        'citizenship, height, weight) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (
                            input_data['last_name'], input_data['first_name'],
                            input_data['middle_name'],
                            input_data['date_of_birth'], input_data['place_of_birth'],
                            str(input_data['team_id']), str(input_data['number']),
                            input_data['position'], input_data['citizenship'],
                            str(input_data['height']), str(input_data['weight']),
                        )
                    )
                    conn.commit()
                    return {
                        'success': True,
                    }
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


    @api.expect(update_player_parser)
    @api.doc(responses={
        200: response_case(
            desc='Игрок успешно обновлена',
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
        """Эндпоинт для обновления изменяемых данных игрока.
        Изменяемые данные: номер, позиция, гражданство, рост, вес."""
        with closing(psycopg2.connect(**CONNECT_CONF)) as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                input_data = update_player_parser.parse_args(request)
                cursor.execute(
                    'SELECT id '
                    'FROM players '
                    'WHERE id = %s',
                    (input_data['id'],)
                )
                is_player_exist = cursor.fetchall()
                if not is_player_exist:
                    return {
                        'message': 'Input payload validation failed',
                        'errors': {
                            'id': 'Player does not exist'
                        }
                    }, 400
                # если ни 1 изменяемый параметр не передали
                if not any([
                        input_data['number'], input_data['position'], input_data['citizenship'],
                        input_data['height'], input_data['weight']
                ]):
                    return {
                        'message': 'Input payload validation failed',
                        'errors': {
                            'number': 'All changeable fields are not entered'
                        }
                    }, 400

                try:
                    cursor.execute(
                        'UPDATE players '
                        'SET number = COALESCE(%s, number), position = COALESCE(%s, position), '
                        'citizenship = COALESCE(%s, citizenship), height = COALESCE(%s,height), '
                        'weight = COALESCE(%s,weight) '
                        'WHERE id = %s',
                        (input_data['number'], input_data['position'], input_data['citizenship'],
                         input_data['height'], input_data['weight'], input_data['id'], )
                    )
                    conn.commit()
                    return {
                        'success': True
                    }
                except Exception:
                    conn.rollback()
                    raise Exception
