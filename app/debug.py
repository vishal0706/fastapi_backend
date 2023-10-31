import uvicorn

from app.server.config import config

if __name__ == '__main__':
    port = int(config.PORT)
    uvicorn.run('main:app', host='0.0.0.0', port=port, reload=True, log_config=None, log_level='critical')
