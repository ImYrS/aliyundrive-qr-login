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

from modules import common, database
from modules import login

__version__ = '0.0.1-alpha.1'

os.environ['NO_PROXY'] = '*'

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

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


init_logger(debug_mode)

if not os.path.exists('./database.db'):
    init_db()


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


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', analytics=analytics)


@app.route('/api/login', methods=['POST'])
def create():
    return login.create_login_request()


@app.route('/api/login', methods=['GET'])
def get():
    return login.get_login_request()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=debug_mode)
