from flask import Flask, render_template, jsonify, Response
from mcstatus import JavaServer
import requests

app = Flask(__name__)

SERVER_CONFIG = {
    "name": "Industrial",
    "ip": "88.99.104.215",
    "port": 25566,
    "version": "1.5.2",
    "wipe": "30.03.2025",
    "max_players": 100
}

def get_server_status():
    try:
        srv = JavaServer.lookup(f"{SERVER_CONFIG['ip']}:{SERVER_CONFIG['port']}")
        q = srv.query()
        return {
            "online": True,
            "players": q.players.names or [],
            "online_count": q.players.online
        }
    except:
        return {
            "online": False,
            "players": [],
            "online_count": 0
        }

@app.route('/')
def index():
    return render_template('index.html', server=SERVER_CONFIG)

@app.route('/status')
def status():
    st = get_server_status()
    return jsonify({**SERVER_CONFIG, **st})

@app.route('/api/player_head/<string:player_name>')
def player_head(player_name):
    """
    Проксируем голову игрока с mix-servers API (или любого другого),
    чтобы не было CORS-проблем и можно было легко кешировать на своём сервере.
    """
    url = f"https://files.mix-servers.com/web/skins/{player_name}.png"
    r = requests.get(url)
    if r.status_code != 200:
        # если не нашли — возвращаем заглушку
        return Response(status=404)
    return Response(r.content, mimetype='image/png',
                    headers={"Cache-Control": "public, max-age=3600"})

if __name__ == '__main__':
    app.run(debug=True)
