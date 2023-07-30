"""
    @Author: ImYrS Yang
    @Date: 2023/6/26
    @Copyright: @ImYrS
"""

import logging
import os
from typing import NoReturn, Optional

from configobj import ConfigObj
from flask import Flask, request, render_template
from flask_limiter import Limiter

from modules import common, database
from modules import login

__version__ = '0.1.1'
__commit__ = ''

os.environ['NO_PROXY'] = '*'

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

limiter = Limiter(app=app, key_func=lambda: common.get_real_ip(request.headers))

config = ConfigObj('./config.ini', encoding='utf-8')
debug_mode = config['dev'].as_bool('debug')

analytics = config['analytics']['content'] if config['analytics'].as_bool('enable') else ''


def init_logger(debug: Optional[bool] = False) -> NoReturn:
    """初始化日志系统"""
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log_format = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if debug else logging.INFO)
    ch.setFormatter(log_format)
    log.addHandler(ch)

    if not os.path.exists('./logs/'):
        os.mkdir(os.getcwd() + '/logs/')

    log_name = f'./logs/{common.formatted_time(secure_format=True)}.log'
    fh = logging.FileHandler(log_name, mode='a', encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(log_format)
    log.addHandler(fh)


def init_db() -> NoReturn:
    """初始化数据库"""
    database.db.connect()
    database.db.create_tables([database.LoginRequest])


def get_commit() -> Optional[str]:
    """获取当前 commit"""
    if not os.path.exists('.git'):
        return None

    commit = None

    try:
        with open('.git/refs/heads/main', 'r') as f:
            commit = f.read().strip()[0:7]
    except FileNotFoundError:
        pass

    return commit


def init() -> NoReturn:
    """初始化"""
    init_logger(debug_mode)

    if not os.path.exists('./database.db'):
        init_db()

    global __commit__
    __commit__ = get_commit() or ''


init()


@app.after_request
def after_request(response):
    """请求后执行"""
    if request.path.startswith('/api/'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '86400'

    return response


@app.teardown_request
def teardown_request(exception):
    """请求结束后执行"""
    if exception:
        logging.error(f'[Teardown] {exception}')


@app.route('/<path:path>', methods=['OPTIONS'])
def options(path):
    return path, 200


@app.errorhandler(429)
def ratelimit_handler(e):
    if 'application/json' in request.headers.get('Accept', ''):
        return {
            'code': 429,
            'message': 'Too many requests: ' + str(e.description),
            'message_human_readable': '请求过于频繁, 请稍后再试',
        }, 429

    return render_template('429.html', message=str(e.description)), 429


@app.route('/', methods=['GET'])
@limiter.limit('10/minute; 1/second')
def index():
    return render_template(
        'index.html',
        analytics=analytics,
        version=__version__,
        commit=__commit__,
    )


@app.route('/api/login', methods=['POST'])
@limiter.limit('1/5second')
def create():
    return login.create_login_request()


@app.route('/api/login', methods=['GET'])
@limiter.limit('120/10minute; 60/minute; 1/second')
def get():
    return login.get_login_request()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=debug_mode)
