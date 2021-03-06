# command line used:
# python ../plot_restart.py good.list .minisat.out .psat_stats_{2,4,8}_r{100,50,m100}.out

import sys
import itertools

import numpy as np
import matplotlib.pyplot as plt

SAT         = 0
UNSAT       = 1
TIMEOUT     = 2

def get_status(filename):
    status = -1
    lines = open(filename, 'rt').read().split('\n')
    for l in lines:
        if l.strip() == 'SATISFIABLE':
            status = SAT
            break
        elif l.strip() == 'UNSATISFIABLE':
            status = UNSAT
            break
        elif l.strip() == 'INDETERMINATE':
            status = TIMEOUT
            break
    assert status != -1

    time = -1
    for l in lines:
        if l.strip().startswith('CPU time'):
            words = l.split()
            time = float(words[3])
    assert time != -1
    return status, time

def strip_cnfgz(str):
    if str.endswith('.cnf.gz'):
        return str[:-7]
    else:
        return str

def compare(filename, suffixes):
    stats = []
    times = []
    for pos, s in enumerate(suffixes):
        fullname = filename + s
        status, time = get_status(fullname)
        stats.append(status)
        times.append(time)

    bs = stats[0]
    for s in stats:
        assert s == bs, 'SAT SOLVER BUG!'
    t0 = times[0]

    speedups = []
    for t in times[1:]:
        speedup = t0 / t
        speedups.append(speedup)

    speed_strings = ('%-40s & ' % strip_cnfgz(filename)) + (' & '.join([('%6.1f' % s) for s in speedups])) + ' \\\\'
    print speed_strings
    return times

def add(t1, t2):
    return [x+y for x,y in itertools.izip(t1, t2)]

def plot_all(filename, suffixes):
    filelist = []
    for line in open(filename, 'rt'):
        if line.strip():
            filelist.append(line.strip())

    t = [0] * len(suffixes)
    all_times = []
    for s in suffixes:
        total_time = 0
        for f in filelist:
            fullname = f + s
            status, time = get_status(fullname)
            total_time +=time
        print s, total_time
        all_times.append(total_time)

    times = [ all_times[0] / t for t in all_times[1:]]

    max = len(times)
    b1 = times[0:max:3]
    b2 = times[1:max:3]
    b3 = times[2:max:3]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    rects = []

    p1 = np.arange(3) + 0.15
    p2 = np.arange(3) + 0.4
    p3 = np.arange(3) + 0.65

    r1 = ax.bar(p1, b1, width=0.25, color='green')
    r2 = ax.bar(p2, b2, width=0.25, color='blue')
    r3 = ax.bar(p3, b3, width=0.25, color='red')

    ax.set_ylim((0,3.5))

    ax.legend((r1[0], r2[0], r3[0]), ('base restart interval=100', 'base restart interval=50', 'base restart interval=mixed (100/50)'), loc='best')
    ax.set_xticks([0.5, 1.5, 2.5])
    ax.set_xticklabels(['n=2', 'n=4', 'n=8'], size='large')

    ax.set_ylabel('Speedup over Minisat 2.2', size='large')
    ax.set_xlabel('Number of cores', size='large')
    ax.grid(True)

    plt.savefig('restart_speedup1.pdf')
    plt.show()

plot_all(sys.argv[1], sys.argv[2:])
