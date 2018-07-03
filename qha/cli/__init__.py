from .parser import QHAArgumentParser
from .runner import QHARunner
#from .runner2 import QHARunner2
from .calculator import QHACalculator
from .plotter import QHAPlotter
from .converter import QHAConverter

def main():
    parser = QHAArgumentParser()

    qha_converter = QHAConverter()
    parser.add_program('convert', qha_converter)

    qha_runner = QHARunner()
    parser.add_program('run', qha_runner)

    #qha_runner2 = QHARunner2()
    qha_calculator = QHACalculator()
    parser.add_program('calculate', qha_calculator)

    qha_runner = QHAPlotter()
    parser.add_program('plot', qha_runner)

    namespace = parser.parse_args()

if __name__ == '__main__':
    main()