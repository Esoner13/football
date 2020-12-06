from endpoints import matches_ns, goals_ns, leagues_ns, players_ns, stadiums_ns, teams_ns
from restplus import application, api


api.add_namespace(goals_ns, path='/goals')
api.add_namespace(matches_ns, path='/matches')
api.add_namespace(leagues_ns, path='/leagues')
api.add_namespace(players_ns, path='/players')
api.add_namespace(stadiums_ns, path='/stadiums')
api.add_namespace(teams_ns, path='/teams')

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=False)
