import json
import PageRank
import numpy as np
from collections import OrderedDict
from functools import reduce
import os

inputFolder = 'data'
inputFile = 'callgraph.json'
resultFolder = 'output'
resultFile = 'call-graph-rank-no-seeds.json'
func2id = {}
id2func = {}
counter = 0


def read():
    with open(os.path.join(inputFolder, inputFile)) as readFile:
        data = json.load(readFile)
        return data


def data2matrix(data):
    global func2id, id2func, counter

    callers = reduce((lambda x, key: (x | set(data[key]))), data.keys(), set())
    callees = set(data.keys())
    functions = callees | callers

    for function in functions:
        if function not in func2id:
            func2id[function] = counter
            id2func[counter] = function
            counter += 1

    N = len(func2id)
    M = np.zeros((N, N))

    for function in func2id:
        if function in data:
            # caller calls function
            # calculate through column
            for caller in data[function]:
                M[func2id[caller], func2id[function]] = 1.0 / len(data[function])
        else:
            for i in xrange(N):
                M[i, func2id[function]] = 1.0 / N
    return M


def main():
    data = read()
    M = data2matrix(data)
    v = PageRank.pagerank(M, 0.001, 0.85)
    funcDict = {}
    for i in xrange(counter):
        funcDict[id2func[i]] = v[i][0]
    funcDict = OrderedDict(sorted(funcDict.items(), key=lambda t: -t[1]))
    with open(os.path.join(resultFolder, resultFile), 'w') as pageRankFile:
        json.dump(funcDict, pageRankFile, indent=4)


if __name__ == '__main__':
    main()
