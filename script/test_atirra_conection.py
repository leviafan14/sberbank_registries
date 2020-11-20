import fdb
try:#Проверка соединения с сервером FireBird 2.5 - ATIRRA
    atirra_connection_test= fdb.connect(dsn='192.168.0.13:ATIRRA', user='AMIGO', password='8845svma') # Подключение к серверу Atirra
    print('good')
except:
    print('bad')
