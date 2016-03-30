from aiohttp import web

async def handle(request):
    name = request.match_info.get('name', "world")
    text = "Hello, " + name
    return web.Response(body=text.encode('utf-8'))

async def handle_root(request):
    text = "Hello, world"
    return web.Response(body=text.encode('utf-8'))

app = web.Application()
app.router.add_route('GET', '/', handle_root)
app.router.add_route('GET', '/{name}', handle)

web.run_app(app)
