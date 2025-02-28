import os
import sys
import time
import logging
from datetime import timedelta


start = time.time()
logging.basicConfig(filename='./timer.txt', format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

benchlist = [sys.argv[1]]
TIMEOUT = int(sys.argv[2])
setting = sys.argv[3].upper()

final_command = ''

for B in benchlist:
    logging.info(f"Bench --> {B}")
    for epsilon in [4]:
        _start = time.time()

        if setting == 'NAIVE':
            final_command = f'python3 ../../qlearning_Naive.py {B} config.json {TIMEOUT} {epsilon} A 1'
        elif setting == 'BEST':
            final_command = f'python3 ../../qlearning_Best.py {B} config.json {TIMEOUT} {epsilon} A 1'
        elif setting == 'BESTREUSE':
            final_command = f'python3 ../../qlearning_BestReuse.py {B} config.json {TIMEOUT} {epsilon} A 1'
        elif setting == '2NDBEST':
            final_command = f'python3 ../../qlearning_2ndBest.py {B} config.json {TIMEOUT} {epsilon} A 1'
        elif setting == 'NONTERMEPISODE':
            final_command = f'python3 ../../qlearning_NonTermEpisode.py {B} config.json {TIMEOUT} {epsilon} A 0'
        else:
            logging.error(f"Invalid setting: {setting}")
            sys.exit(1)
        
        os.system(f"cd {B}/run; \
                    python3 generate-include.py; \
                    python3 setup.py {B}; \
                    rm -f *.txt; \
                    python3 create-search-space.py {B}; \
                    {final_command}; \
                    ")
        _elapsed = (time.time() - _start)
        logging.info(f"      epsilon --> {epsilon}  time --> {str(timedelta(seconds=_elapsed))}")

elapsed = (time.time() - start)
logging.info(f"TOTAL TIME: {str(timedelta(seconds=elapsed))}")
