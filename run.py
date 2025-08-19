import uvicorn
from config import config

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config['HOST'],
        port=config['PORT'],
        reload=config['DEBUG'],
        log_level="info"
    ) 