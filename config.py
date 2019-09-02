from sqlalchemy import create_engine, text

db = {
    'user': 'root',
    'password': 'wlrkq159',
    'host': 'localhost',
    'port': 3306,
    'database': 'miniter'
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

JWT_SECRET_KEY = 'secret'
UPLOAD_FOLDER = '/home/geuno/Projects/UploadFolder'

# S3_BUCKET = "test"
# S3_ACCESS_KEY = "test_access_key"
# S3_SECRET_KEY = "test_secret_key"
# S3_BUCKET_URL = f"https://s3.ap-northeast-2.amazonaws.com/test/"


test_db = {
    'user': 'test',
    'password': 'wlrkq159',
    'host': 'localhost',
    'port': 3306,
    'database': 'miniter_test'
}


test_config = {
    "DB_URL": f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
    'JWT_SECRET_KEY': 'secret',
    'S3_BUCKET': "python-backend-miniter-test",
    'S3_ACCESS_KEY': "AKIAVIHW737LNCJWFCWQ",
    'S3_SECRET_KEY': "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",
    'S3_BUCKET_URL': f"https://s3.ap-northeast-2.amazonaws.com/{S3_BUCKET}/"
}
