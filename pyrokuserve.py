from rokucontroller import RokuController
from sanic import Sanic, response
from sanic_openapi import swagger_blueprint, openapi_blueprint, doc

app = Sanic()

# swagger docs
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)

app.config.API_VERSION = "0.1.0"
app.config.API_TITLE = "pyRokuServer API"
app.config.API_DESCRIPTION = "pyRokuServer API"
app.config.API_TERMS_OF_SERVICE = "Use with caution!"
app.config.API_PRODUCES_CONTENT_TYPES = ["application/json"]
app.config.API_CONTACT_EMAIL = "roku@ling-li.com"

rokuc = RokuController()


@app.get("/device/list/", strict_slashes=True)
@doc.summary("returns list of available devices")
# @app.route('/device/list', methods=['GET'])
async def devices_list(request):
    return response.json(rokuc.get_devices(), status=200)


@app.route("/device/<device_id:int>/commandlist/", strict_slashes=True)
@doc.summary("returns list of available commands for the specified roku device")
async def get_commands(request, device_id):
    try:
        return response.json({"message": rokuc.get_commands(device_id)}, status=200)
    except Exception as e:
        return response.json({"ERROR": e}, status=400)


@app.route("/device/<device_id:int>/command/<command:[a-z]+>", strict_slashes=True)
async def exec_command(request, device_id, command):
    try:
        msg = rokuc.exec_command(device_id, command)
        return response.json({"message": msg}, status=200)
    except Exception as e:
        return response.json({"ERROR": e}, status=400)


@app.route("/device/<device_id:int>/apps/list/", strict_slashes=True)
async def apps_list(request, device_id):
    try:
        return response.json(rokuc.get_apps(device_id), status=200)
    except Exception as e:
        return response.json({"error": str(e)}, status=400)


@app.route("/device/<device_id:int>/apps/launch/<app_id:int>", strict_slashes=True)
async def launch_app(request, device_id, app_id):
    try:
        return response.json(rokuc.launch_app(device_id, app_id), status=200)
    except Exception as e:
        return response.json({"ERROR": str(e)}, status=400)


@app.route("/device/<device_id:int>/activeapp/", strict_slashes=True)
async def active_app(request, device_id):
    try:
        return response.json(rokuc.activeapp(device_id), status=200)
    except Exception as e:
        return response.json({"ERROR": str(e)}, status=400)


@app.route("/device/<deviceid:int>/literal/", methods=["POST"], strict_slashes=True)
async def literal(request, device_id):
    try:
        return response.json(rokuc.literal(device_id=device_id), status=200)
    except Exception as e:
        return response.json({"ERROR": str(e)}, status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
