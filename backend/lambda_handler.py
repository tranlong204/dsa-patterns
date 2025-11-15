"""
AWS Lambda handler for FastAPI application
"""
from mangum import Mangum
from app.main import app

# Create ASGI handler for Lambda
handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    from mangum import Mangum
    handler = Mangum(app)

