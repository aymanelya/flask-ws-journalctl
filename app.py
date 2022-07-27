from crypt import methods
from flask import Flask, render_template, request

from flask_sock import Sock
import subprocess
import json

app = Flask(__name__)
sock = Sock(app)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 5}


sentTxs = {}
currentBlock = 0
lastBlock = 0

@app.route('/')
def index():
    data = {
        'page_title': 'ws-example',
        'ws_url': 'ws://127.0.0.1:5000/log'
    }
    return render_template('base.html', data=data)


@app.route('/newBlock', methods = ['POST'])
def newBlock():
    global currentBlock
    data = request.json
    print("data",data)
    # currentBlock = data
    # print("new block",currentBlock,data)
    
# @sock.route('/updatedReserves')
# def updatedReserves(ws):
#     global lastBlock
#     data = ws.receive()
#     lastBlock = data
#     print("updatedReserves lastBlock",lastBlock,data)


@sock.route('/log')
def log(ws):
    # data = ws.receive()
    # payload = json.loads(data)

    with subprocess.Popen(
            ['''journalctl -u osmosisd  -f  | grep -oP 'module=mempool msg={"Txs":\["\K([^ ]+)(?="\])\''''],
            stdout=subprocess.PIPE, shell=True, bufsize=1,
            universal_newlines=True
    ) as process:
        print('subprocess executed')
        for line in process.stdout:
            line = line.rstrip()
            if line not in sentTxs:
                if currentBlock>0 and lastBlock>0 and currentBlock==lastBlock:
                    ws.send(line)
                    sentTxs[line]=1
            # try:
            #     payload = {
            #         'title': 'journalctl',
            #         'message': line,
            #         'success': True
            #     }
            #     ws.send(json.dumps(payload))
            # except BaseException as e:
            #     payload = {
            #         'error': str(e) + '\n',
            #         'success': False
            #     }
            #     ws.send(payload)
    print('WS closed')


if __name__ == '__main__':
    app.config.update(
        DEBUG=True,
    )
    app.run(host="0.0.0.0", port=5000)
