from dotenv import dotenv_values
config = dotenv_values(".env")

port = 5555
max_task = 10000
auto_refresh = True
# db='flower.db' #sqlite database to store the task results and states

basic_auth = [f'admin:{config["CELERY_FLOWER_PASSWORD"]}']