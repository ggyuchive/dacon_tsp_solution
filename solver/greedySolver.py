from utils.graphEngine import GraphEngine
from typing import List
from tqdm import tqdm
import random

class GreedySolver(GraphEngine):
    def __init__(self):
        super().__init__()

    '''
    indices is permutation between 1 to 75
    return route that go to DEPOT as little as possible
    '''
    def getGreedyRoute(self, indices: List[int]) -> List[int]:
        ret = []
        ret.append(0)
        sum_cost = 0
        for index in indices:
            if sum_cost + self.demand[index] > 25:
                ret.append(0)
                ret.append(index)
                sum_cost = self.demand[index]
            else:
                ret.append(index)
                sum_cost += self.demand[index]
        if ret[-1] != 0:
            ret.append(0)
        return ret
    
    def runRandomGreedy(self, loop: int):
        min_dist, min_dist_route = float('inf'), []
        for _ in tqdm(range(0, loop), desc="Random Greedy Processing"):
            indices = random.shuffle(list(range(1, 76)))
            ret = self.getGreedyRoute(indices)
            if min_dist > self.getRouteDiatance(ret):
                min_dist_route = ret
                min_dist = self.getRouteDiatance(ret)
                print(f"Distance: {self.getRouteDiatance(ret)}")
        self.writeCsv(min_dist_route, "random_greedy")
    
    '''
    get route of shortest distance including start/end DEPOT in O(N*2^N)
    '''
    def getTSP(self, indices: List[int]) -> List[int]:
        n = len(indices)
        INF = float('inf')
        dp = [[INF] * n for _ in range(1 << n)]
        dp[1][0] = 0
        parent = [[-1] * n for _ in range(1 << n)]
        for mask in range(1 << n):
            for u in range(n):
                if mask & (1 << u):
                    for v in range(n):
                        if not (mask & (1 << v)):
                            next_mask = mask | (1 << v)
                            cost = dp[mask][u] + self.dist[indices[u]][indices[v]]
                            if cost < dp[next_mask][v]:
                                dp[next_mask][v] = cost
                                parent[next_mask][v] = u
        mask = (1 << n) - 1
        curr_city = 0
        min_cost = INF
        for i in range(n):
            cost = dp[(1 << n) - 1][i] + self.dist[indices[i]][0]
            if cost < min_cost:
                min_cost = cost
                curr_city = i

        path = []
        mask = (1 << n) - 1
        while curr_city != -1:
            path.append(indices[curr_city])
            next_city = parent[mask][curr_city]
            mask &= ~(1 << curr_city)
            curr_city = next_city

        path.reverse()
        return path
    
    def groupNode(self, seed: int) -> List[List[int]]:
        group = [-1 for _ in range(76)]
        sum_cost = [0 for _ in range(76)]
        groupN = -1
        pointInfo = []
        for i in range(1, 76):
            for j in range(i+1, 76):
                pointInfo.append([self.dist[i][j], i, j])
        pointInfo.sort()
        random.seed(seed)
        for point in pointInfo:
            if random.random() < 0.75:
                i1, i2 = point[1], point[2]
                if group[i1] == -1 and group[i2] == -1:
                    groupN += 1
                    group[i1], group[i2] = groupN, groupN
                    sum_cost[groupN] += (self.demand[i1] + self.demand[i2])
                elif group[i1] == -1:
                    if sum_cost[group[i2]] + self.demand[i1] <= 25:
                        group[i1] = group[i2]
                        sum_cost[group[i2]] += self.demand[i1]
                elif group[i2] == -1:
                    if sum_cost[group[i1]] + self.demand[i2] <= 25:
                        group[i2] = group[i1]
                        sum_cost[group[i1]] += self.demand[i2]
                else:
                    if group[i1] != group[i2] and sum_cost[group[i1]] + sum_cost[group[i2]] <= 25:
                        sum_cost[group[i1]] += sum_cost[group[i2]]
                        sum_cost[group[i2]] = 0
                        grp = group[i2]
                        for i in range(1, 76):
                            if group[i] == grp:
                                group[i] = group[i1]
        ret = []
        for i in range(0, groupN+1):
            tmp = []
            for j in range(1, 76):
                if group[j] == i:
                    tmp.append(j)
            if len(tmp) > 0:
                ret.append(tmp)
        return ret
    
    def runTSPGreedy(self, loop: int):
        min_dist, min_dist_route = float('inf'), []
        for i in tqdm(range(0, loop), desc="TSP Greedy Processing"):
            groups = self.groupNode(i)
            route = [0]
            for group in groups:
                optimal_route = self.getTSP(group)
                route = route + optimal_route + [0]
            if min_dist > self.getRouteDiatance(route) and self.isValidResult(route):
                min_dist_route = route
                min_dist = self.getRouteDiatance(route)
                print(f"Distance: {self.getRouteDiatance(route)}")

        self.writeCsv(min_dist_route, "TSP_greedy")
        print(f"Distance: {self.getRouteDiatance(min_dist_route)}")
