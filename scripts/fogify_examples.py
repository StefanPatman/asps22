from pathlib import Path
from yaml import safe_load

from collections import defaultdict
import itertools

import sys
sys.path.append('./src/topology/')

from main import main
import scenario


for file in Path('examples').glob('*.yml'):

    output = Path('examples/fogified') / file.name

    print(f'{file} -> {output}')


    # reset counters
    scenario.counters = defaultdict(lambda: itertools.count(0, 1))

    with open(file) as stream:
        input = safe_load(stream)

    with open(output, 'w') as stream:
        main(input, visual=False, file=stream)
