import connexion
from connexion.resolver import RestyResolver

# Create the application instance
application = connexion.App(__name__)

# Read the spec file to configure the endpoints
application.add_api('docs/openapi.yaml', resolver=RestyResolver('api'))

if __name__ == '__main__':
    application.run(debug=True)