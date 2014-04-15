import os
import argparse

from ground_control.psql_handle import PostgresHandle
from ground_control.plane_queue import PlaneQueue

def remove_tmp():
    if args.deltmp:
        for f in os.listdir('tmp/'):
            path = os.path.join('tmp/', f)

            try:
                if os.path.isfile(path):
                    os.unlink(path)
            except Exception:
                print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--airplane",  help="[HOST:PORT]")
    parser.add_argument("-s", "--psqlhost",  help="Host address of the Postgres server")
    parser.add_argument("-p", "--psqlport",  help="Port of the Postgres server")
    parser.add_argument("--flush",           help="Flushes all keys from the Postgres server", action="store_true")
    parser.add_argument("--deltmp",          help="Deletes the contents of the image directory", action="store_true")

    args = parser.parse_args()

    rhandle = None

    if args.deltmp:
        remove_tmp()

    if not os.path.exists('tmp/'):
        os.mkdir('tmp/')

    if args.psqlhost and args.psqlport:
        rhandle = PostgresHandle(args.psqlhost, args.psqlport)

        if args.flush:
            rhandle.empty_database()

    if args.airplane:
        PlaneQueue(args.airplane, rhandle).run_forever()
