from rokucontroller import RokuController
from sanic import Sanic, response

app = Sanic()

rokuc = RokuController()


@app.route('/device/list', methods=['GET'])
async def devices_list(request):
    return response.json(rokuc.get_devices(), status=200)


@app.route('/device/<device_id:int>/commandlist/')
async def get_commands(request, device_id):
    try:
        return response.json({'message': rokuc.get_commands(device_id)}, status=200)
    except Exception as e:
        return response.json({'ERROR': e}, status=400)


@app.route('/device/<device_id:int>/command/<command:[a-z]+>')
async def exec_command(request, device_id, command):
    try:
        msg = rokuc.exec_command(device_id, command)
        return response.json({'message': msg}, status=200)
    except Exception as e:
        return response.json({'ERROR': e}, status=400)


@app.route('/device/<device_id:int>/apps/list')
async def apps_list(request, device_id):
    try:
        return response.json(rokuc.get_apps(device_id), status=200)
    except Exception as e:
        return response.json({'error': str(e)}, status=400)


@app.route('/device/<device_id:int>/apps/launch/<app_id:int>')
async def launch_app(request, device_id, app_id):
    try:
        return response.json(rokuc.launch_app(device_id, app_id), status=200)
    except Exception as e:
        return response.json({'ERROR': str(e)}, status=400)


@app.route('/device/<device_id:int>/activeapp')
async def active_app(request, device_id):
    try:
        return response.json(rokuc.activeapp(device_id), status=200)
    except Exception as e:
        return response.json({'ERROR': str(e)}, status=400)


@app.route('/device/<deviceid:int>/literal', methods=['POST'])
async def literal(request, device_id):
    try:
        return response.json(rokuc.literal(device_id=device_id), status=200)
    except Exception as e:
        return response.json({'ERROR': str(e)}, status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
