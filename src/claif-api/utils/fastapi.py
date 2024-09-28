
from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from fastapi.openapi.utils import get_openapi
from utils.auth import limiter
from utils.env import OPENAPI_KEYCLOAK_SERVER_URL, KEYCLOAK_REALM


def init_fastapi_app() -> FastAPI:
    # Initialize and return FastAPI app
    app = FastAPI()
    app.add_middleware(SlowAPIMiddleware)
    app.state.limiter = limiter


    # Custom OpenAPI schema to include the OAuth2 Password Flow in Swagger UI
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="CLAIF API",
            version="0.1.0",
            description="API documentation with Keycloak OAuth2",
            routes=app.routes,
        )

        # Modify to use the correct public client password flow
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": f"{OPENAPI_KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
                        "scopes": {"openid": "OpenID Connect scope"},
                    }
                }
            }
        }

        # Apply security to all routes
        openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    # Override the FastAPI's default OpenAPI generator
    app.openapi = custom_openapi
    return app
