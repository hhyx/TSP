# encoding=utf-8

import math
import time
import random
import copy
import matplotlib.pyplot as plt
import sys

minCost = sys.maxsize
dimension = 0
cities = []
# 结果矩阵
res = []
oldT = 0

def readDataFromFile():
    data = []
    with open("../tc/bier127.tsp", 'r') as file:
        for line in file:
            # if "DIMENSION" in line:
                # dimesion = int(line[11:14])
                # matrix = [[0 for i in range(2)] for i in range(dimesion)]
            if "NODE_COORD_SECTION" in line:
                break

        for line in file:
            if "EOF" in line:
                break
            lines_list = line.split()
            data.append((int(lines_list[1]), int(lines_list[2])))

        file.close()
    return data


def getDistance(i, j):
    cord1 = cities[i]
    cord2 = cities[j]
    rij = math.sqrt( ( (cord1[0]-cord2[0])**2 + (cord1[1]-cord2[1])**2 ))
    tij = int(rij) + 1
    return tij


def calcuDistance(path):
    dis = 0
    for i in range(1, len(path)):
        dis += getDistance(path[i-1], path[i])
    dis += getDistance(path[0], path[dimension-1])
    return dis


def simulateAnneal():
    path = [i for i in range(dimension)]
    random.shuffle(path)
    cost = calcuDistance(path)
    T = 50
    oldT = T
    innerLoop = 1000
    while T > 10e-2:
        innerLoop *= 1.0001
        for i in range(int(innerLoop)):
            global res
            res.append(cost)
            # 生成新解
            pos1 = int(random.random()*dimension)
            pos2 = int(random.random()*dimension)
            if pos1 > pos2:
                pos1,pos2 = pos2,pos1
            if pos1 == pos2 or (pos1==0 and pos2==dimension-1):
                continue
            offset = getDistance(path[pos1], path[(pos2+1)%dimension]) + getDistance(path[pos2], path[(pos1-1)%dimension]) - \
                    getDistance(path[pos1], path[(pos1-1)%dimension]) - getDistance(path[pos2], path[(pos2+1)%dimension])
            
            # 测试是否接受新解
            recieve = offset < 0 or math.exp(-offset/(T*10)) > random.random()
            if recieve :
                cost += offset
                while pos1 < pos2:
                    path[pos1],path[pos2] = path[pos2],path[pos1]
                    pos1 += 1
                    pos2 -= 1

        showPath(path, 'Cost = ' + str(cost) + '   T = ' + str(round(T, 2)) + '    ' +
                 "     " + str(round(round((cost-118282)/118282, 4)*100, 2)) + '%')
        showCostDraw()
        plt.pause(0.00001)
        plt.clf()
        T *= 0.99

        # if T < oldT * 0.05:
        #     oldT = T
        #     T *= 2

    return cost, path

    
def showPath(path, desciption = ''):
    global cities
    x = []
    y = []
    plt.suptitle('Simulated Annealing', fontsize=16, fontweight='bold')
    for i in range(dimension):
        x.append(cities[path[i]][0])
        y.append(cities[path[i]][1])
    x.append(cities[path[0]][0])
    y.append(cities[path[0]][1])
    plt.subplot(211)
    plt.plot(x, y)
    plt.title(desciption)
    plt.draw()


def showCostDraw():
    global res
    plt.subplot(212)
    plt.tight_layout(13)
    plt.title("Path Length Change Curve")
    plt.plot([i for i in range(len(res))], res)
    plt.draw()
    
    
if __name__ == '__main__':

    starttime = time.time()
    cities = readDataFromFile()
    dimension = len(cities)
    minPath = [i for i in range(dimension)]
    minCost = calcuDistance(minPath)

    plt.figure(figsize=(6, 6))
    for i in range(1):
        cost, path = simulateAnneal()
        if cost < minCost:
            minCost, minPath = cost, path
    
    showPath(minPath, 'minCost ' + str(minCost))
    showCostDraw()
    plt.pause(10)
    print('finally the cost is : ', minCost)
    print('finally the path is : ', minPath)

    endtime = time.time()
    print('use ', (endtime - starttime), 's')
