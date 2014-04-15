import sys

from ground_control.major_tom.dummy_source import MajorTom

if __name__ == '__main__':
    MajorTom().run(port=int(sys.argv[1]) if len(sys.argv) > 1 else 10101)
