from app.core.config import settings

print(settings.APP_NAME)
print(settings.database_url)
print(settings.ENVIRONMENT)


# TO RUN:
# $env:ENVIRONMENT="DEV"; python -m app.main
