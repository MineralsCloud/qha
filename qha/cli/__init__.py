from .parser import QHAArgumentParser
from .runner import QHARunner
from .runner2 import QHARunner2
from .plotter import QHAPlotter
from .converter import QHAConverter

def main():
    parser = QHAArgumentParser()

    qha_converter = QHAConverter()
    parser.add_program('convert', qha_converter)

    qha_runner = QHARunner()
    parser.add_program('run', qha_runner)

    qha_runner2 = QHARunner2()
    parser.add_program('run2', qha_runner2)

    qha_runner = QHAPlotter()
    parser.add_program('plot', qha_runner)

    namespace = parser.parse_args()

if __name__ == '__main__':
    main()