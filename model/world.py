import random
import json
from model.car import Car
from model.road import Road
from model.intersection import Intersection
from geometry.rect import Rect
from geometry.curve import Curve


class World():
    def __init__(self):
        self.set()

    def set(self):
        self.intersections = {}
        self.roads = {}
        self.cars = {}
        self.carsNumber = 0
        self.time = 0
        self.graphList = {}

    def load(self):
        with open('map2.json') as data_file:
            map = json.load(data_file)
        self.carsNumber = map["carsNumber"]
        for info in map["intersections"].values():
            rect = Rect(info["position"]["x"], info["position"]["y"], info["position"]["width"], info["position"]["height"])
            intersection = Intersection(rect)
            intersection.id = info['id']
            self.addIntersection(intersection)


        for info in map["roads"].values():
            road = Road(self.intersections[info["source"]], self.intersections[info["target"]])
            road.id = info['id']
            self.addRoad(road)


    def refreshCar(self):
        if len(self.cars) < self.carsNumber:
            self.addRandomCar()
        if len(self.cars) > self.carsNumber:
            self.removeRandomCar()

    def addRandomCar(self):
        road = random.choice(list(self.roads.values()))
        if road is not None:
            lane = random.choice(road.lanes)
            if lane is not None:
                # self.addCar(Car(lane=lane, position=0))
                self.addCar(Car(graphList=self.graphList))

    def addCar(self, car):
        self.cars[car.id] = car

    def removeRandomCar(self):
        car = random.choice(list(self.cars.values()))
        if car is not None:
            car.alive = False

    def removeCar(self, car):
        self.cars.pop(car.id)

    def getIntersection(self, ID):
        return self.intersections[ID]

    def addIntersection(self, intersection):
        self.intersections[intersection.id] = intersection
        self.graphList[intersection.id] = dict()

    def addRoad(self, road):
        self.roads[road.id] = road
        self.graphList[road.source.id][road.target.id] = road
        road.source.roads.append(road)
        road.target.inRoads.append(road)
        road.update()

    def getRoad(self, ID):
        return self.roads[ID]

    def syncLane(self):
        for car in self.cars.values():
            for road in self.roads.values():
                for lane in road.lanes:
                    if car.trajectory.current.lane.id == lane.id:
                        relativePos = car.trajectory.current.relativePosition
                        car.trajectory.current.lane.sourceSegment = lane.sourceSegment
                        car.trajectory.current.lane.targetSegment = lane.targetSegment
                        car.trajectory.current.lane.update()
                        car.trajectory.current.position = car.trajectory.current.lane.length * relativePos

                    if car.trajectory.isChangingLanes and car.trajectory.next.lane is not None and car.trajectory.next.lane.id == lane.id:
                        car.trajectory.next.lane.sourceSegment = lane.sourceSegment
                        car.trajectory.next.lane.targetSegment = lane.targetSegment
                        car.trajectory.next.lane.update()
                    
                        
    def syncCurve(self):
        for car in self.cars.values():
            if car.trajectory.timeToMakeTurn() and car.trajectory.canEnterIntersection() and car.trajectory.isValidTurn():
                relativePos = car.trajectory.temp.relativePosition
                previousA = car.trajectory.temp.lane.A
                previousB = car.trajectory.temp.lane.B
                relativeA = car.trajectory.current.lane.getRelativePosition(previousA)
                relativeB = car.trajectory.next.lane.getRelativePosition(previousB)
                car.trajectory.current.position = relativeA * car.trajectory.current.lane.length
                car.trajectory.next.position = relativeB * car.trajectory.next.lane.length
                car.trajectory.temp.lane = car.trajectory.getCurve()
                car.trajectory.temp.position = car.trajectory.temp.lane.length * relativePos

    def generateMap(self):
        self.set()
        



    def onTick(self, delta):
        self.time += delta
        self.refreshCar()
        self.syncLane()
        self.syncCurve()
        for car in list(self.cars.values()):
            car.move(delta)








