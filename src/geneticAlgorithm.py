import math
import random
import time
import matplotlib.pyplot as plt
import sys

# 距离矩阵
distance = []
# 城市矩阵
matrix = []
bestDistance = 0
bestGeneration = 0
greedLength = 0

ProbabilityCross = 0.9
ProbabilityMutation = 0.05
PopulationSize = 100
GenerationSize = 3000
# 结果矩阵
res = [[0 for i in range(PopulationSize)] for i in range (GenerationSize)]


# 计算两点距离
def getdistance(x1, y1, x2, y2):
    xd = x1 - x2
    yd = y1 - y2
    dis = math.sqrt(xd * xd + yd * yd)
    dis = int(dis) + 1
    return dis


# 计算路径长度
def path_length(lists):
    path = 0
    length = len(lists)
    for i in range(0, length):
        if i == length - 1:
            dis = distance[lists[i]][lists[0]]
        else:
            dis = distance[lists[i]][lists[i+1]]
        path += dis
    return path


def path_length2(lists):
    path = 0
    length = len(lists)
    for i in range(0, length-1):
        dis = distance[lists[i]][lists[i+1]]
        path += dis
    return path


def greedy():
    greed = [0 for i in range(len(distance))]
    for i in range(1, len(distance)):
        minpoint = i
        minpath = 10000000
        for j in range(0, len(distance)):
            if j not in greed and distance[greed[i-1]][j] < minpath:
                minpath = distance[greed[i-1]][j]
                minpoint = j
        greed[i] = minpoint
    return greed


class DA(object):
    def __init__(self):
        global ProbabilityCross, ProbabilityMutation, GenerationSize, PopulationSize
        self.PCross = ProbabilityCross  # 交叉概率
        self.PMutation = ProbabilityMutation  # 突变概率
        self.POPSIZE = PopulationSize  # 种群规模
        self.MAXGENS = GenerationSize  # 运行代数
        self.cityNum = 0  # 城市数
        self.oldPopulation = []  # 父代种群
        self.newPopulation = []  # 子代种群
        self.bestDistance = sys.maxsize  # 最佳长度
        self.bestPath = []  # 最佳路径
        self.fitness = [0 for i in range(self.POPSIZE)]  # 个体的适应度
        self.cfitness = [0 for i in range(self.POPSIZE)]  # 个体的累积概率
        self.generation = 0  # 当前代数

    # 初始化
    def init(self, path):
        random.seed()
        global distance, matrix
        file = open(path, 'r')
        for line in file:
            if "DIMENSION" in line:
                self.cityNum = int(line[11:14])
                matrix = [[0 for i in range(2)] for i in range(self.cityNum)]
            if "NODE_COORD_SECTION" in line:
                break
        for line in file:
            if "EOF" in line:
                break
            lines_list = line.split()
            matrix[int(lines_list[0]) - 1][0] = int(lines_list[1])
            matrix[int(lines_list[0]) - 1][1] = int(lines_list[2])
        file.close()
        self.oldPopulation = [[0 for i in range(self.cityNum)] for i in range(self.POPSIZE)]
        self.newPopulation = [[0 for i in range(self.cityNum)] for i in range(self.POPSIZE)]
        self.bestPath = [0 for i in range(self.cityNum)]
        distance = [[0 for i in range(self.cityNum)] for i in range(self.cityNum)]
        for i in range(0, self.cityNum):
            for j in range(i + 1, self.cityNum):
                distance[i][j] = getdistance(matrix[i][0], matrix[i][1], matrix[j][0], matrix[j][1])
                distance[j][i] = distance[i][j]
        for i in range(0, self.POPSIZE):
            for j in range(0, self.cityNum):
                self.newPopulation[i][j] = j
            random.shuffle(self.newPopulation[i])
        greed = greedy()
        global  greedLength
        greedLength = path_length(greed)

    # 评估 同时将子代变为父代
    def evaluate(self):
        generalpath = 0
        global res
        for i in range(self.POPSIZE):
            self.fitness[i] = path_length(self.newPopulation[i])
            res[self.generation][i] = self.fitness[i]
            generalpath += self.fitness[i]

        length = 0
        sortfitness = sorted(self.fitness)
        sortresult = [0 for i in range(self.POPSIZE)]
        cfitness = [0 for i in range(self.POPSIZE)]
        for i in range(self.POPSIZE):
            for j in range(self.POPSIZE):
                if sortfitness[i] == self.fitness[j]:
                    sortresult[i] = j
                    break
        for i in range(self.POPSIZE):
            length += self.fitness[i]
            cfitness[i] = float(length / generalpath)
        for i in range(self.POPSIZE):
            self.cfitness[i] = cfitness[self.POPSIZE-sortresult[i]-1]
            self.oldPopulation[i] = self.newPopulation[i]

    # 产生下一代 取当前种群最优放入下一代，其余通过轮盘赌挑选   同时更新最好情况
    def newChild(self):
        best = 0
        bestfitness = self.fitness[0]
        for i in range(1, self.POPSIZE):
            if bestfitness > self.fitness[i]:
                best = i
                bestfitness = self.fitness[i]
        if bestfitness < self.bestDistance:
            self.bestDistance = bestfitness
            self.bestPath = list(self.oldPopulation[best])

        global bestDistance, bestGeneration
        if bestDistance == self.bestDistance:
            bestGeneration += 1
            if bestGeneration > 150:
                bestGeneration = 0
                self.PMutation += 0.1
        else:
            bestDistance = self.bestDistance
            bestGeneration = 0

        self.newPopulation[0] = list(self.oldPopulation[best])
        for i in range(1, self.POPSIZE):
            ran = random.uniform(0,1)
            for j in range(self.POPSIZE):
                if ran < self.cfitness[j]:
                    self.newPopulation[i] = list(self.oldPopulation[j])
                    break

    # 种群进化
    def evolution(self):
        if self.generation % self.MAXGENS/5 == 0 and self.generation <= self.MAXGENS/5*3:
            for i in range(1, self.POPSIZE, 1):
                random.shuffle(self.newPopulation[i])
        for i in range(1, self.POPSIZE):
            ran = random.uniform(0,1)
            better = []
            if ran < self.PCross:
                ran = random.uniform(0,1)
                if ran < 0.4:
                    j = random.randint(0, self.POPSIZE-1)
                else:
                    j = 0
                DA.crossover(self, j, i)
                if path_length(self.newPopulation[i]) < path_length(self.newPopulation[0]):
                    better = list(self.newPopulation[i])

            ran = random.uniform(0, 1)
            if ran < self.PMutation:
                DA.mutation(self, i)
                if len(better):
                    if path_length(self.newPopulation[i]) < path_length(better):
                        better = list(self.newPopulation[i])
                        self.newPopulation[i] = list(self.newPopulation[0])
                        self.newPopulation[0] = list(better)
                    else:
                        self.newPopulation[i] = list(self.newPopulation[0])
                        self.newPopulation[0] = list(better)
                else:
                    if path_length(self.newPopulation[i]) < path_length(self.newPopulation[0]):
                        better = list(self.newPopulation[i])
                        self.newPopulation[i] = list(self.newPopulation[0])
                        self.newPopulation[0] = list(better)
            elif len(better):
                self.newPopulation[i] = list(self.newPopulation[0])
                self.newPopulation[0] = list(better)
        global greedLength
        if self.bestDistance < greedLength + 2000 or self.generation == self.MAXGENS/5*2:
            greedLength /= 2
            greed = greedy()
            for i in range(1, 10):
                self.newPopulation[i] = greed

    # 交叉
    def crossover(self, parent1, parent2):

        region = 5
        r = random.randint(0, region-1)
        # r = 0
        while True:
            r1 = random.randint((math.floor(self.cityNum/region))*r, (math.floor(self.cityNum/region))*(r+1))
            r2 = random.randint(r1, (math.floor(self.cityNum/region))*(r+1))
            cross1 = self.newPopulation[parent1][r1:r2]
            cross2 = self.newPopulation[parent2][r1:r2]
            if path_length2(cross1) <= path_length2(cross2):
                break

        ran = random.uniform(0,1)
        if ran <= 0.5:  # 部分映射交叉
            newGene2 = []
            gene = 0
            for i in range(0, self.cityNum):
                if gene == r1:
                    newGene2.extend(cross1)
                    gene += 1
                if self.newPopulation[parent1][i] not in cross1:
                    newGene2.extend([self.newPopulation[parent1][i]])
                    gene += 1
            self.newPopulation[parent2] = list(newGene2)
        else: # 随机打乱顺序交叉
            newGene2 = []
            random.shuffle(cross1)
            newGene2.extend(cross1)
            for i in range(r2, self.cityNum):
                if self.newPopulation[parent2][i] not in newGene2:
                    newGene2.extend([self.newPopulation[parent2][i]])
            for i in range(0, r2):
                if self.newPopulation[parent2][i] not in newGene2:
                    newGene2.extend([self.newPopulation[parent2][i]])
            self.newPopulation[parent2] = list(newGene2)

    # 变异
    def mutation(self, parent):
        r1 = random.randint(0, self.cityNum - 1)
        r2 = random.randint(0, self.cityNum - 1)
        if r1 > r2:
            r1, r2 = r2, r1
        ran = random.uniform(0,1)
        if ran < 0.8:
            while r1 < r2:
                self.newPopulation[parent][r1], self.newPopulation[parent][r2] = \
                    self.newPopulation[parent][r2], self.newPopulation[parent][r1]
                r1 += 1
                r2 -= 1
        elif ran < 0.9:
            self.newPopulation[parent][r1], self.newPopulation[parent][r2] = \
                self.newPopulation[parent][r2], self.newPopulation[parent][r1]
        else:
            for i in range(2):
                r1 = random.randint(0, self.cityNum - 1)
                r2 = random.randint(r1, self.cityNum - 1)
                self.newPopulation[parent][r1], self.newPopulation[parent][r2] = \
                    self.newPopulation[parent][r2], self.newPopulation[parent][r1]

    def display(self, isfinal):
        if isfinal == 1:
            plt.clf()
        x1 = [0 for i in range(tsp.cityNum + 1)]
        y1 = [0 for i in range(tsp.cityNum + 1)]
        for j in range(0, tsp.cityNum + 1):
            if j == tsp.cityNum:
                x1[j] = matrix[tsp.bestPath[0]][0]
                y1[j] = matrix[tsp.bestPath[0]][1]
            else:
                x1[j] = matrix[tsp.bestPath[j]][0]
                y1[j] = matrix[tsp.bestPath[j]][1]
        plt.suptitle('Genetic Algorithm', fontsize=16, fontweight='bold')
        plt.subplot(211)
        plt.plot(x1, y1)
        title = "Cost = " + str(tsp.bestDistance) + " Generation = " + str(tsp.generation) +\
                "     " + str(round(round((tsp.bestDistance - 118282) / 118282, 4) * 100, 2)) + '%'
        if isfinal == 1:
            title = "bestPath: " + str(tsp.bestDistance) + \
                 "     " + str(round(round((tsp.bestDistance - 118282) / 118282, 4) * 100, 2)) + '%'
        plt.title(title)
        plt.draw()

        plt.subplot(212)
        plt.tight_layout(13)
        plt.title("Path Length Change Curve")
        plt.xlabel("Generation")
        plt.ylabel("Cost")
        x = [0 for i in range(tsp.generation * PopulationSize)]
        y = [0 for i in range(tsp.generation * PopulationSize)]
        for i in range(tsp.generation):
            for j in range(PopulationSize):
                x[i * PopulationSize + j] = i
                y[i * PopulationSize + j] = res[i][j]
        plt.plot(x, y, '.')
        plt.draw()
        if isfinal == 1:
            plt.pause(50)
        else:
            plt.pause(0.01)

if __name__ == '__main__':
    starttime = time.time()
    endtime = time.time()
    # plt.figure(figsize=(6.5, 6))
    print("最短路径: bier127:118282")
    tsp = DA()
    tsp.init("../tc/bier127.tsp")
    print("遗传算法求解TSP问题, 遗传代数：", GenerationSize)
    while tsp.generation < tsp.MAXGENS:
        tsp.evaluate()
        tsp.newChild()
        tsp.evolution()
        tsp.generation += 1
        if tsp.generation % 50 == 0 or tsp.generation == 1:
            tsp.display(0)
            if tsp.generation == tsp.MAXGENS:
                print("bestDistance ", tsp.bestDistance)
                print("bestPath ", tsp.bestPath)
                tsp.display(1)
            plt.clf()
