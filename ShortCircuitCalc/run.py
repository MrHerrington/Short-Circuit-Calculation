# -*- coding: utf-8 -*-
import logging
import argparse
import re

from ShortCircuitCalc.tools import *


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('arg', help='List of members')
    args = parser.parse_args()
    parsing_args = list(map(lambda x: eval(x.group(0)), re.finditer(r'\w+([^)])*[)]', args.arg)))

    logger.info(Calculator(parsing_args).three_phase_current_short_circuit)


if __name__ == '__main__':
    main()
