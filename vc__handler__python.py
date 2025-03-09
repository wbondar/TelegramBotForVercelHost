import main
from quart import Quart, request, Response
import os  # Добавляем импорт модуля os

app = Quart(__name__)

@app.route('/api/telegram', methods=['POST'])
async def handler():
    try:
        update = main.Update.de_json(await request.get_json(force=True), main.application.bot)
        await main.application.update_queue.put(update)
        await main.application.process_update(main.application.update_queue.get_nowait())
        return Response(status=200)
    except Exception:
        import traceback
        traceback.print_exc()
        return Response(status=500)
