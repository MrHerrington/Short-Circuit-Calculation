# -*- coding: utf-8 -*-
import argparse
import re
import ShortCircuitCalc.database as db
from ShortCircuitCalc.tools import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('arg', help='List of members')
    args = parser.parse_args()
    parsing_args = list(map(lambda x: eval(x.group(0)), re.finditer(r'\w+([^)])*[)]', args.arg)))

    print(Calculator(parsing_args).three_phase_current_short_circuit)


if __name__ == '__main__':
    main()
