from ShortCircuitCalc.config import *
import json
from collections import namedtuple


def db_access() -> str:
    """This function responsible for accessing the database.

    Returns:
        Return engine string with access info from security JSON file.

    """
    def __mysql_access() -> str:
        with open(CREDENTIALS_DIR, 'r', encoding='UTF-8') as file:
            temp = json.load(file)['db_access']
            login, password, db_name = temp['login'], temp['password'], temp['db_name']
            engine_string = f'mysql+pymysql://{login}:{password}@localhost/{db_name}?charset=utf8mb4'
        path_link = ROOT_DIR / SQLITE_DB_NAME
        if path_link.is_file():
            path_link.unlink()
            print(f"Existing SQLite database '{SQLITE_DB_NAME}' deleted!")
        return engine_string

    def __sqlite_access() -> str:
        return f'sqlite:///{ROOT_DIR}/{SQLITE_DB_NAME}'

    Param = namedtuple('Param', ('config_string', 'func', 'description'))

    db_dict = {
        None: Param('DB_EXISTING_CONNECTION = None', None, 'Existing connection not found!'),
        'MySQL': Param('DB_EXISTING_CONNECTION = MySQL', __mysql_access, 'MySQL database connected!'),
        'SQLite': Param('DB_EXISTING_CONNECTION = SQLite', __sqlite_access, 'SQLite database connected!'),
    }

    with open(CONFIG_DIR, 'r+', encoding='UTF-8') as config_file:
        current_config_data = config_file.read()
        if 'DB_EXISTING_CONNECTION = None' in current_config_data and not hasattr(db_access, 'engine_string'):
            print('Existing connection not found!')
            try:
                print('Accessing MySQL database...')
                print('Credentials initializing...')
                db_access.engine_string = db_dict['MySQL']
                print('Credentials initialized!')
            except FileNotFoundError:
                print('Credentials file for MySQL database not found!')
                print('Accessing SQLite database...')
                db_access.engine_string = db_dict['SQLite']

            updated_config_data = current_config_data.replace(
                'DB_EXISTING_CONNECTION = None',
                f"DB_EXISTING_CONNECTION = '{db_access.engine_string[0]}'", 1)
            config_file.seek(0)
            config_file.write(updated_config_data)

        print(db_access.engine_string[2])
        return db_access.engine_string[1]()


print(db_access())
print(db_access())
print(db_access())
print(db_access())
print(db_access())
