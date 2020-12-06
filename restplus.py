from flask import jsonify, Flask
from flask_restplus import Api
from werkzeug.exceptions import HTTPException


def _exc_handler(exc):
    if isinstance(exc, HTTPException):
        return jsonify({'success': False, 'message': exc.description}), exc.code
    return jsonify({'success': False, 'message': 'Internal Server Error.'}), 500


application = Flask(__name__)
application.config['RESTPLUS_VALIDATE'] = True
application.config['RESTPLUS_MASK_SWAGGER'] = True
application.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'

api = Api(
    application,
    title='Footbal CRM',
    description='Система для сохранения и ведения статистики футбола',
)


@application.errorhandler(Exception)
def handle_500(error):
    """Обработка ошибки 500."""
    return _exc_handler(error)