## RLTuner
> This is a code artifact for searching optimal precision using reinforcement learning. This includes a genetic algorithm implementation and Precimonious for evaluation.

### Table of Contents

* 1 [Requirements](#1-requirements)

* 2 [Setup environment via Docker](#2-setup-environment-via-docker)   
    * 2.1 [Clone this GitHub repository](#21-clone-this-github-repository)    
    * 2.2 [Pull the docker image](#22-pull-the-docker-image)  
    * 2.3 [Run and start a Docker container](#23-run-and-start-a-docker-container)    
    * 2.4 [Raw Data](#24-data)

* 3 [Case study](#3-case-study)
    * 3.1 [RLTuner](#31-rltuner)
    * 3.2 [Precimonious](#32-precimonious)
    * 3.3 [Genetic Algorithm](#33-genetic-algorithm)

### 1 Requirements
- 40GB free disk
- Ubuntu 20.04
- Docker 24.0.7

### 2 Setup environment via Docker
#### 2.1 Clone GitHub repository
Clone the GitHub repository to your local directory. The docker will be also mounted via the local path.

    git clone https://github.com/anonymousdev434/anonyrl.git <YOUR LOCAL PATH>


#### 2.2 Pull the docker image

    docker pull anonymousdev123/anonymousdev:latest
Note: The size of the docker image is around 28.4GB.

#### 2.3 Run and start a Docker container

    docker run -v <YOUR LOCAL PATH>:/root/home -ti --name <CONTAINER NAME> anonymousdev123/anonymousdev
    docker start -i <CONTAINER NAME>

Note: `<YOUR LOCAL PATH>` should be the same `<YOUR LOCAL PATH>` as in [step 2.1](#21-clone-this-github-repository).
The option '**-v**' is used to mount a volume between the container and the host. This allows the Docker container to access and modify files from the GitHub repository cloned to your local path.

#### 2.4 Data

After the experiments, the result files are saved in the <code>results-eps=4</code> directory.
The <code>eps</code> means epsilon, which is an error range. <code>eps=4</code> means that the result should be in $10^4$. 

This is an example route for Arclength result in RLTuner. 

    cd /root/home/RLTuner/funarc/run/results-eps=4

- <code>*.json</code>: the precision configurations for the benchmark
    - <code>VALID_*.json</code>: successfully executed configuration within a given error range
    - <code>INVALID_*.json</code>: successfully executed configuration but the result is not in the error range
    - <code>FAIL_*.json</code>: execution fail        
- <code>best_speedup_funarc_5.txt</code>: the best speedup of the benchmark
- <code>qlearning-20241011-180319.log</code>: the log file about execution result and running time

### 3. Case study
<!-- The approximate running time could be different depending on the machine. -->

#### 3.1 RLTuner

Plese note that we have five different settings for RLTuner as following:
1. <code>Naive</code>
2. <code>Best</code>
3. <code>BestReuse</code>
4. <code>2ndBest</code>
5. <code>NonTermEpisode</code>

Here is the example command when you want to run <code>Arclength</code> in setting <code>Best</code>.

    python3 run.py funarc 10 Best


<details>
<summary>Expected terminal output from the start:</summary>

    include.json is generated.
    rm -f *.out  *.txt  *output
    Plugin arg size = 6
    Output path = ./
    Output file name = config.json
    Input file name = funarc.c
    Output file created - ./config.json
    Output file created - ./search_config.json
    /usr/bin/ld: /usr/bin/../lib/gcc/x86_64-linux-gnu/9/../../../x86_64-linux-gnu/crt1.o: in function `_start':
    (.text+0x24): undefined reference to `main'
    clang-12: error: linker command failed with exit code 1 (use -v to see invocation)
    ** Searching for valid configuration using delta-debugging algorithm
    -------- running config 0 --------
    Plugin arg size = 4
    Output path = ../tempscripts/
    Input config  = config_temp.json
    No file created!
    /usr/bin/ld: /usr/bin/../lib/gcc/x86_64-linux-gnu/9/../../../x86_64-linux-gnu/crt1.o: in function `_start':
    (.text+0x24): undefined reference to `main'
    clang-12: error: linker command failed with exit code 1 (use -v to see invocation)
    rm -f funarc *.txt *.out
    gcc -o funarc funarc.c -lm
    Round 1:
    VERIFICATION SUCCESSFUL
    Zeta is     5.7957763224130E+00
    Error is    4.2908825959056E-15
    runtime: 1.394898
    mv config_temp.json results-eps=4/VALID_config_funarc_0.json
    Round 2:
    VERIFICATION SUCCESSFUL
</details>

This is the expected terminal output from the beginning. The format will remain consistent across all test cases, including <code>RLTuner</code>, <code>Precimonious</code>, and <code>Genetic Algorithm</code>.


<details>
<summary>Part of the terminal output:</summary>

    Round 1:
    VERIFICATION SUCCESSFUL
    Zeta is     5.7957763224130E+00
    Error is    4.2908825959056E-15
    runtime: 1.019484
    mv config_temp.json results-eps=0.5/VALID_config_funarc_2.json
    Average runtime = 1.019484 s
    result: 1
    runtime: 1.019484
    speedup: 0.016017118385760077
    Reward: 1
    q_table:    call12-main-sqrt  ...  localVar9-main-dppi
    0               0.0  ...                  0.0

    [1 rows x 12 columns]
    ----------State: 0  Steps: 2------------
    non-greedy action_name: call12-main-sqrt
    updated_config:
    ['call12', 'main', 'sqrt', 'float']
    ['call4', 'fun', 'sin', 'double']
    ['localVar1', 'fun', 'x', 'double']
    ['localVar10', 'main', 's1', 'double']
    ['localVar11', 'main', 'err', 'double']
    ['localVar2', 'fun', 't1', 'float']
    ['localVar3', 'fun', 'd1', 'double']
    ['localVar5', 'main', 'cpu_time_used', 'double']
    ['localVar6', 'main', 'h', 'double']
    ['localVar7', 'main', 't1', 'double']
    ['localVar8', 'main', 't2', 'double']
    ['localVar9', 'main', 'dppi', 'double']
</details>

You can check which variables are selected and the updated configuration via the terminal output.
This is an example of the terminal output for <code>Arclength</code> in <code>RLTuner</code>.

<details>
<summary>Expected terminal output of <code>RLTuner</code> at the end:</summary>

    ---------- State: 13 ------------
    S: 13
    selected_actions: localVar3-fun-d1
    S_: 49
    q_predict: -9.9
    q_target: -99.0
    updated q value: -8.91
    best_speedup: State 8, 0.2638965867393793
    Already tried the best speedup state: 8
    FAIL_RESTAT_FLAG: 1 | greedy policy: 0.5 | learning rate: 0.1 | discount factor: 0.95
    0.2638965867393793
</details>

This is the expected terminal output at the end of execution for all benchmarks.

##### 3.1.1 Arclength  <!--  (approx. 40min) -->

    cd /root/home/RLTuner
    python3 run.py funarc 10 [setting_name]

##### 3.1.2 Blackscholes

    cd /root/home/RLTuner
    python3 run.py blackscholes 10 [setting_name]

##### 3.1.3 CFD

    cd /root/home/RLTuner
    python3 run.py euler3d 10 [setting_name]

##### 3.1.4 CG

    cd /root/home/RLTuner
    python3 run.py cg 10 [setting_name]

##### 3.1.5 Hotspot

    cd /root/home/RLTuner
    python3 run.py hotspot 10 [setting_name]

##### 3.1.6 HPCCG

    cd /root/home/RLTuner
    python3 run.py HPCCG 10 [setting_name]

##### 3.1.7 Kmeans

    cd /root/home/RLTuner
    python3 run.py kmeans 10 [setting_name]

##### 3.1.8 LULESH

    cd /root/home/RLTuner
    python3 run.py lulesh 300 [setting_name]

##### 3.1.9 LavaMD

    cd /root/home/RLTuner
    python3 run.py lavaMD 10 [setting_name]


#### 3.2 Precimonious

At the end of execution, the expected terminal output across benchmarks is as follows:
<details>
<summary>Expected terminal output of <code>Precimonious</code> at the end:</summary>

    mv config_temp.json results-eps=4/INVALID_config_funarc_13.json
    Average runtime = 0.922489 s
    ../dd2.py:246: FutureWarning: The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.
    df = df.append(df_item, ignore_index = True)
    {'call12': {'file': 'funarc.c', 'function': 'main', 'lines': ['61'], 'location': '../scripts/funarc.c:61:17', 'name': 'sqrt', 'switch': 'sqrtf', 'type': ['float', 'float']}, 'call4': {'file': 'funarc.c', 'function': 'fun', 'lines': ['20'], 'location': '../scripts/funarc.c:20:15', 'name': 'sin', 'switch': 'sinf', 'type': ['float', 'float']}, 'localVar1': {'file': 'funarc.c', 'function': 'fun', 'lines': ['10', '15', '20'], 'location': 'parmVar', 'name': 'x', 'type': 'float'}, 'localVar10': {'file': 'funarc.c', 'function': 'main', 'lines': ['50', '55', '61', '73', '77', '82', '87'], 'location': 'localVar', 'name': 's1', 'type': 'double', 'switch': 'sqrt'}, 'localVar11': {'file': 'funarc.c', 'function': 'main', 'lines': ['71', '73', '74', '78', '88'], 'location': 'localVar', 'name': 'err', 'type': 'double', 'switch': 'sin'}, 'localVar2': {'file': 'funarc.c', 'function': 'fun', 'lines': ['12', '15', '20', '23'], 'location': 'localVar', 'name': 't1', 'type': 'double'}, 'localVar3': {'file': 'funarc.c', 'function': 'fun', 'lines': ['13', '19', '20'], 'location': 'localVar', 'name': 'd1', 'type': 'float', 'switch': 'sqrt'}, 'localVar5': {'file': 'funarc.c', 'function': 'main', 'lines': ['35', '92', '94'], 'location': 'localVar', 'name': 'cpu_time_used', 'type': 'float', 'switch': 'sin'}, 'localVar6': {'file': 'funarc.c', 'function': 'main', 'lines': ['46', '57', '60', '61'], 'location': 'localVar', 'name': 'h', 'type': 'float'}, 'localVar7': {'file': 'funarc.c', 'function': 'main', 'lines': ['47', '53', '54', '56', '61', '62'], 'location': 'localVar', 'name': 't1', 'type': 'float'}, 'localVar8': {'file': 'funarc.c', 'function': 'main', 'lines': ['48', '60', '61', '62'], 'location': 'localVar', 'name': 't2', 'type': 'float'}, 'localVar9': {'file': 'funarc.c', 'function': 'main', 'lines': ['49', '54', '57'], 'location': 'localVar', 'name': 'dppi', 'type': 'float'}} 0.9457749 5
    Check dd2_valid_funarc.json for the valid configuration file
</details>

##### 3.2.1 Arclength

    cd /root/home/Precimonious
    python3 run.py funarc 10

##### 3.2.2 Blackscholes

    cd /root/home/Precimonious
    python3 run.py blackscholes 10

##### 3.2.3 CFD

    cd /root/home/Precimonious
    python3 run.py euler3d 10

##### 3.2.4 CG

    cd /root/home/Precimonious
    python3 run.py cg 10

##### 3.2.5 Hotspot

    cd /root/home/Precimonious
    python3 run.py hotspot 10

##### 3.2.6 HPCCG

    cd /root/home/Precimonious
    python3 run.py HPCCG 10

##### 3.2.7 Kmeans

    cd /root/home/Precimonious
    python3 run.py kmeans 10

##### 3.2.8 LULESH

    cd /root/home/Precimonious
    python3 run.py lulesh 300

##### 3.2.9 LavaMD

    cd /root/home/Precimonious
    python3 run.py lavaMD 10

#### 3.3 Genetic Algorithm

At the end of execution, the expected terminal output across benchmarks is as follows:
<details>
<summary>Expected terminal output of <code>Genetic Algorithm</code> at the end:</summary>

    Elite individual kept since generation 7
    Elite individual kept since generation 8
    Elite individual kept since generation 9
    Elite individual kept since generation 10
    Original Score: 1.0281168 Elite Score: 0.9989411
    Speedup: 2.8377806879529732%
    Last Generation, Config 0 Runtime: 1.0796917 Result: 1
    Last Generation, Config 1 Runtime: 0.9989411 Result: 1
    Visited Individuals: 4754
</details>

##### 3.3.1 Arclength

    cd /root/home/GeneticAlgorithm
    python3 run.py funarc 10

##### 3.3.2 Blackscholes

    cd /root/home/GeneticAlgorithm
    python3 run.py blackscholes 10

##### 3.3.3 CFD

    cd /root/home/GeneticAlgorithm
    python3 run.py euler3d 10

##### 3.3.4 CG

    cd /root/home/GeneticAlgorithm
    python3 run.py cg 10

##### 3.3.5 Hotspot

    cd /root/home/GeneticAlgorithm
    python3 run.py hotspot 10

##### 3.3.6 HPCCG

    cd /root/home/GeneticAlgorithm
    python3 run.py HPCCG 10

##### 3.3.7 Kmeans

    cd /root/home/GeneticAlgorithm
    python3 run.py kmeans 10

##### 3.3.8 LULESH

    cd /root/home/GeneticAlgorithm
    python3 run.py lulesh 300

##### 3.3.9 LavaMD

    cd /root/home/GeneticAlgorithm
    python3 run.py lavaMD 10
