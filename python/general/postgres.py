def start_postgres():
    import os

    commands = [
        "docker",
        "start",
        "bbdb"
    ]
    command = ' '.join(commands)
    stream_docker = os.popen(command)
    docker_bbdb_id = stream_docker.read().rstrip()

    print('Started docker with id '+docker_bbdb_id)
    return docker_bbdb_id



def connect_to_bbdb():
    from sqlalchemy import create_engine
    from psycopg2 import connect
    import os
    import time

    stream = os.popen('docker ps --filter "name=bbdb"')
    output = stream.read()
    bbdb_running = 'bbdb' in output

    if (bbdb_running==False):
        print('Starting up bbdb...  this will take a minute')
        os.popen('docker start bbdb')
        while (bbdb_running==False):
            time.sleep(5)
            stream = os.popen('docker ps --filter "name=bbdb"')
            output = stream.read()
            bbdb_running = 'bbdb' in output
        print('Done!')

    engine = create_engine("postgresql://postgres:Pass2021!@localhost/bbdb")
    return engine.connect()
