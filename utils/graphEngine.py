import math
import csv
from typing import List
from dataclasses import dataclass

@dataclass
class Point:
    x : int
    y : int
    cost : int

class GraphEngine:
    def __init__(self):
        file_path = "data/data.csv"
        data = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                data = [row for row in reader]
                self.N = len(data)-1 # = 76
                self.id_map = {} # {index, point_id}
                self.points = [] # 76 Point info
                self.demand = [] # 76 cost info
                self.dist = [[0.0 for _ in range(self.N)] for _ in range(self.N)] # 76 * 76 Dance info

                for index in range(1, len(data)):
                    self.id_map[index-1] = data[index][0]
                    point = data[index]
                    self.points.append(Point(int(point[1]),int(point[2]),int(point[3])))
                    self.demand.append(int(point[3]))

                for i in range(0, len(self.points)):
                    for j in range(0, len(self.points)):
                        self.dist[i][j] = math.sqrt((self.points[i].x - self.points[j].x) ** 2 + (self.points[i].y - self.points[j].y) ** 2)
        except FileNotFoundError:
            print(f"file '{file_path}' is not found")
        except Exception as e:
            print(f"Error while reading csv file: {e}")

    def getRouteDiatance(self, result: List[int]) -> float:
        sum = 0
        for i in range(1, len(result)):
            sum += self.dist[result[i-1]][result[i]]
        return sum
    
    '''
    1. Check start and end point is DEPOT
    2. Check all point traversed
    3. Check cost is not bigger than 25
    '''
    def isValidResult(self, result: List[int]) -> bool:
        sum_cost = 0
        if result[0] != 0:
            print(f"start point is not DEPOT")
            return False
        if result[-1] != 0:
            print(f"end point is not DEPOT")
            return False
        visited = [False for _ in range(76)]
        for ind in result:
            visited[ind] = True
        for i in range(76):
            if visited[i] is False:
                print(f"point {i} not traversed")
                return False
        for ind in result:
            if ind == 0:
                sum_cost = 0
            else:
                sum_cost += self.demand[ind]
                if sum_cost > 25: 
                    print(f"cost is bigger than 25 < {sum_cost}")
                    return False
        return True

    def writeCsv(self, result: List[int], prefix = "default"):
        if self.isValidResult(result) is False:
            return
        score = self.getRouteDiatance(result)
        ret = []
        for ind in result:
            ret.append(self.id_map[ind])
        data = [["point_id"]] + [[point_id] for point_id in ret]
        file_path = f"results/{prefix}_{score}_submission.csv"
        try:
            with open(file_path, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)
        except Exception as e:
            print(f"Error while writing csv file: {e}")
