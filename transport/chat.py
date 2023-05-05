from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from .auth import login_required
from .db import get_db
import json
import os
import uuid
import time
from flask_sockets import Sockets

bp = Blueprint('chat', __name__,url_prefix='/chat')
sockets = Sockets()

def init_app(app):
    sockets.init_app(app)

@bp.route('/index')
def index():
    return render_template('chat/index.html')

# 存储所有客户端的 WebSocket 连接
clients = []

# WebSocket 事件处理函数
@sockets.route('/ws')
def chat_socket(ws):
    # 将新的 WebSocket 连接加入 clients 列表
    clients.append(ws)

    while not ws.closed:
        try:
            message = ws.receive()
            if message:
                # 将消息广播给所有客户端
                for client in clients:
                    client.send(message)
        except:
            # 发生错误时，将 WebSocket 连接从 clients 列表中删除
            clients.remove(ws)
            break
