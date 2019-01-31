# encoding=utf-8
# att48 : 10628
# att532 : 27686

import math
import time
import random
import copy
import matplotlib.pyplot as plt

minCost = 2147483647
dimension = 0
cities = []

def readDataFromFile():
    data = []
    with open("../tc/bier127.tsp", 'r') as file:
        for line in file:
            if "NODE_COORD_SECTION" in line:
                break

        for line in file:
            if "EOF" in line:
                break
            lines_list = line.split()
            data.append((int(lines_list[1]), int(lines_list[2])))

        file.close()
    return data


def getDistance(i, j) :
    cord1 = cities[i]
    cord2 = cities[j]
    rij = math.sqrt( ( (cord1[0]-cord2[0])**2 + (cord1[1]-cord2[1])**2 ))
    tij = int(rij) + 1
    return tij


def calcuDistance(path) :
    dis = 0
    for i in range(1, len(path) ) :
        dis += getDistance(path[i-1], path[i])
    dis += getDistance(path[0], path[dimension-1])
    return dis


# return the after swap distance - now distance
def compareDistanceAfterSwap(path, pos1, pos2) :
    if pos2 == pos1 + 1 :
        oriDis = getDistance(path[pos1], path[(pos1-1)%dimension]) + getDistance(path[pos2], path[(pos2+1)%dimension])
        tarDis = getDistance(path[pos2], path[(pos1-1)%dimension]) + getDistance(path[pos1], path[(pos2+1)%dimension])
    elif (pos2+1)%dimension == pos1 :
        oriDis = getDistance(path[pos2], path[(pos2-1)%dimension]) + getDistance(path[pos1], path[(pos1+1)%dimension])
        tarDis = getDistance(path[pos1], path[(pos2-1)%dimension]) + getDistance(path[pos2], path[(pos1+1)%dimension])
    else :
        oriDis = getDistance(path[pos1], path[(pos1-1)%dimension]) + getDistance(path[pos1], path[(pos1+1)%dimension]) \
               + getDistance(path[pos2], path[(pos2-1)%dimension]) + getDistance(path[pos2], path[(pos2+1)%dimension])
        tarDis = getDistance(path[pos2], path[(pos1-1)%dimension]) + getDistance(path[pos2], path[(pos1+1)%dimension]) \
               + getDistance(path[pos1], path[(pos2-1)%dimension]) + getDistance(path[pos1], path[(pos2+1)%dimension])
    return tarDis - oriDis

    
def localsearch1() :
    path = [i for i in range(dimension)]
    random.shuffle(path)
    cost = calcuDistance(path)

    times=300000;
    while times > 0 :
        pos1 = int(random.random()*dimension)
        pos2 = int(random.random()*dimension)
        if pos1 > pos2 :
            pos1,pos2 = pos2,pos1
        if pos1 == pos2 :
            continue;
        offset = compareDistanceAfterSwap(path, pos1, pos2)
        if(offset < 0) :
            cost += offset;
            path[pos1],path[pos2] = path[pos2],path[pos1]
            print('cost ->', cost)
            showPath(path)
            plt.pause(0.001)
            plt.clf()
        times -= 1

    return cost, path

    
def localsearch2() :
    path = [i for i in range(dimension)]
    random.shuffle(path)
    cost = calcuDistance(path)
    times = 100000 
    while times > 0 :
        pos1 = int(random.random()*dimension)
        pos2 = int(random.random()*dimension)
        if pos1 > pos2 :
            pos1,pos2 = pos2,pos1
        if pos1==pos2 or (pos1==0 and pos2==dimension-1) :
            continue;
        offset = getDistance(path[pos1], path[(pos2+1)%dimension]) + getDistance(path[pos2], path[(pos1-1)%dimension]) - \
                getDistance(path[pos1], path[(pos1-1)%dimension]) - getDistance(path[pos2], path[(pos2+1)%dimension])
        if(offset<0) :
            cost += offset;
            while pos1 < pos2 :
                path[pos1],path[pos2] = path[pos2],path[pos1]
                pos1 += 1
                pos2 -= 1
            showPath(path, 'cost = ' + str(cost) + 'left times = ' + str(times))
            plt.pause(0.0001)
            plt.clf()
        times -= 1

    return cost, path
    
    
def showPath(path, desciption = '') :
    global cities
    x = []
    y = []
    for i in range(dimension) :
        x.append(cities[path[i]][0])
        y.append(cities[path[i]][1])
    plt.plot(x, y)
    plt.title(desciption)
    plt.draw()


if __name__ == '__main__':

    starttime = time.time()

    cities = readDataFromFile()

    dimension = len(cities)
    minPath = [i for i in range(dimension)]
    minCost = calcuDistance(minPath)

    for i in range(1) :
        cost, path = localsearch2()
        if cost < minCost :
            minCost, minPath = cost, path
    
    showPath(minPath, 'minCost ' + str(minCost))
    
    print('finally the cost is : ', minCost)
    print('finally the path is : ', minPath)

    endtime = time.time()
    print('use ', (endtime - starttime), 's')
