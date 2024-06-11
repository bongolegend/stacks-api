# The number of worker processes for handling requests
workers = 2

# The type of workers to use
worker_class = 'uvicorn.workers.UvicornWorker'

# The application's entry point. The format is MODULE_NAME:VARIABLE_NAME
wsgi_app = 'src.app:app'

bind = '0.0.0.0:8000'

# Optionally, specify environment variables in the config file
# raw_env = [
#     'MY_ENV_VAR=value',  # example environment variable
# ]

# Logging configuration
loglevel = 'info'
# accesslog = 'logs/access.log'  # Assumes you have a 'logs' directory in your application root
# errorlog = 'logs/error.log'

# If you want more fine-grained control, you can specify the maximum number of requests a worker will handle before restarting
max_requests = 1000
