from sqlalchemy import create_engine, text

# db = {
#     'user': 'root',
#     'password': 'wlrkq159',
#     'host': 'localhost',
#     'port': 3306,
#     'database': 'miniter'
# }
db = {
    'user': 'root',
    'password': 'wlrkq159',
    'host': 'python-backend-test.czxaclupuy9k.ap-northeast-2.rds.amazonaws.com',
    'port': 3306,
    'database': 'miniter'
}


# test_db = {
#     'user': 'test',
#     'password': 'wlrkq159',
#     'host': 'localhost',
#     'port': 3306,
#     'database': 'miniter_test'
# }

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

# test_config = {
#     "DB_URL": f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
#     'JWT_SECRET_KEY': 'secret'}
JWT_SECRET_KEY = 'secret'
