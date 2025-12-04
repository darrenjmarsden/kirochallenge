from mangum import Mangum
from main import app

# Wrap FastAPI app with Mangum for Lambda
handler = Mangum(app, lifespan="off")
