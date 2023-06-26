"""
    @Author: ImYrS Yang
    @Date: 2023/6/27
    @Copyright: @ImYrS
"""

from uuid import uuid4
import logging
from base64 import b64decode
from json import loads, dumps
from typing import Optional

import peewee
from flask import request
import requests

from modules import common
from modules.types import LoginRequestState
from modules.database import LoginRequest


def create_login_request() -> tuple[dict, int]:
    """创建登录请求"""
    uuid = str(uuid4())

    try:
        r = requests.get(
            'https://passport.aliyundrive.com/newlogin/qrcode/generate.do',
            params={
                'appName': 'aliyun_drive',
                'fromSite': '52',
                'appEntrance': 'web',
            }
        )

        data = r.json()['content']['data']
        t = data['t']
        ck = data['ck']
        content = data['codeContent']
    except (requests.RequestException, KeyError) as e:
        logging.error(f'创建登录请求失败: {e}')
        return {'code': 507, 'message': '创建登录请求失败.'}, 500

    try:
        login_request = LoginRequest.create(
            uuid=uuid,
            t=t,
            ck=ck,
            content=content,
            created_at=common.now(),
        )
    except peewee.PeeweeException as e:
        logging.error(f'创建登录请求失败: {e}')
        return {'code': 507, 'message': '创建登录请求失败.'}, 500

    return {
        'code': 200,
        'data': {
            'uuid': login_request.uuid,
            'content': login_request.content,
            'state': login_request.state,
            'created_at': login_request.created_at,
        }
    }, 200


def query_login_request(login_request: LoginRequest) -> Optional[dict]:
    """
    查询登录请求

    :param login_request:
    :return:
    """
    r = requests.post(
        'https://passport.aliyundrive.com/newlogin/qrcode/query.do',
        params={
            'appName': 'aliyun_drive',
            'fromSite': '52',
            '_bx-v': '2.0.31',
        },
        data={
            't': login_request.t,
            'ck': login_request.ck,
        }
    )

    data = r.json()['content']['data']

    old_state = login_request.state
    new_state = LoginRequestState.Unknown

    if data['qrCodeStatus'] == 'NEW':
        new_state = LoginRequestState.Pending
    elif data['qrCodeStatus'] == 'SCANED':
        new_state = LoginRequestState.Scanned
    elif data['qrCodeStatus'] == 'CONFIRMED':
        new_state = LoginRequestState.Confirmed
    elif data['qrCodeStatus'] == 'EXPIRED':
        new_state = LoginRequestState.Expired
    elif data['qrCodeStatus'] == 'CANCELED':
        new_state = LoginRequestState.Canceled

    if new_state != old_state:
        login_request.state = new_state
        login_request.save()

    user_data = {}
    if new_state == LoginRequestState.Confirmed:
        user = loads(b64decode(dumps(data['bizExt'])).decode('gb18030'))['pds_login_result']
        user_data['username'] = user['userName']
        user_data['refresh_token'] = user['refreshToken']

        if 'nickName' in user:
            user_data['username'] = user['nickName']

        if 'avatar' in user:
            user_data['avatar'] = user['avatar']

    return user_data or None


def get_login_request() -> tuple[dict, int]:
    """查询登录结果"""
    try:
        uuid = request.args['uuid']
    except (TypeError, KeyError, ValueError):
        return {'code': 400, 'message': '参数错误.'}, 400

    try:
        login_request = LoginRequest.get(LoginRequest.uuid == uuid)
    except peewee.DoesNotExist:
        return {'code': 404, 'message': '登录请求不存在.'}, 404
    except peewee.PeeweeException as e:
        logging.error(f'查询登录请求失败: {e}')
        return {'code': 507, 'message': '查询登录请求失败.'}, 500

    if common.now() > login_request.created_at + 1000 * 60 * 5:
        login_request.state = LoginRequestState.Expired
        login_request.save()

    user = None

    if login_request.state in (
        LoginRequestState.Pending,
        LoginRequestState.Scanned,
    ):
        try:
            user = query_login_request(login_request)
        except requests.exceptions.RequestException as e:
            logging.error(f'查询登录请求失败: {e}')
            return {'code': 507, 'message': '查询登录请求失败.'}, 500

    return {
        'code': 200,
        'data': {
            'uuid': login_request.uuid,
            'content': login_request.content,
            'state': login_request.state,
            'created_at': login_request.created_at,
            'user': user,
        }
    }, 200
