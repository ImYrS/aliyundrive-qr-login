# AliyunDrive QR Login

Obtain a `refresh token` for AliyunDrive by logging in through QR code scanning.

# 阿里云盘二维码登录

通过扫码登陆获取阿里云盘 `refresh token`.

## Feature | 特性

- Out of the box | 开箱即用
- No privacy risk | 无隐私风险
- No extra service required | 不需要额外服务

## Important | 重要

Refresh tokens will never be saved or uploaded to any server.

Only required parameters for log in will be saved in `database.db`.

And it can not be used to log in again or get any personal information.

You can find more details in `modules/login.py`.

Refresh token 永远不会被保存或上传到任何服务器.

只有登陆所需的参数会被保存在 `database.db` 中.

并且它不能用于再次登陆或获取任何个人信息.

你可以在 `modules/login.py` 中找到更多细节.

## Self-hosted | 自托管

1. Install dependencies | 安装依赖

    ```bash
    pip install -r requirements.txt
    ```

2. Run | 运行

    ```bash
    python app.py
    ```
