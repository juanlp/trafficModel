import numpy as np

from geometry.rect import Rect
from geometry.point import Point
import settings


class Visualizer:
    def __init__(self, world, canvas, carText):
        self.world = world
        self.canvas = canvas
        self.carText = carText
        self.canvas_height = settings.setDict["canvas_height"]
        self.canvas_width = settings.setDict["canvas_width"]
        self.distance = settings.setDict["grid_size"]
        self.scale = 1
        self.debug = False
        self.drawGrid()
        self.drawWorld()

    def drawPolyLine(self, pointList: list, ID):
        convertList = [(point.x, point.y) for point in pointList]
        self.canvas.create_polygon(convertList, fill=settings.setDict["color"]["road"],
                                   outline=settings.setDict["color"]["grid"], tag=ID)

    def rotate(self, angle, coords, center):
        for point in coords:
            point.x -= center.x
            point.y -= center.y
            R = np.matrix([[np.cos(-angle), -np.sin(-angle)],
                           [np.sin(-angle), np.cos(-angle)]])
            P = np.matrix([point.x, point.y])
            transform = np.dot(P, R)
            point.x = transform[0, 0] + center.x
            point.y = transform[0, 1] + center.y

    def drawIntersection(self, intersection):
        self.canvas.create_rectangle(intersection.rect.x, intersection.rect.y, intersection.rect.x + intersection.rect.width,
                                     intersection.rect.y + intersection.rect.height, fill=settings.setDict["color"]["road"],
                                     outline=settings.setDict["color"]["grid"], tag=intersection.id)

    def drawGrid(self):
        for y in range(0, self.canvas_height, self.distance):
            for x in range(0, self.canvas_width, self.distance):
                self.canvas.create_rectangle(x, y, x + self.distance, y + self.distance,
                                             fill=settings.setDict["color"]["background"], outline=settings.setDict["color"]["grid"])

    def drawRoad(self, road):
        sourceSide = road.sourceSide
        targetSide = road.targetSide
        leftLine = road.leftmostLane.leftBorder
        self.canvas.create_line(leftLine.source.x, leftLine.source.y, leftLine.target.x, leftLine.target.y,
                                fill=settings.setDict["color"]["road_mark"], width=3)
        rightLine = road.rightmostLane.rightBorder
        self.canvas.create_line(rightLine.source.x, rightLine.source.y, rightLine.target.x,
                                rightLine.target.y, fill=settings.setDict["color"]["grid"])
        self.drawPolyLine([sourceSide.source, sourceSide.target,
                           targetSide.source, targetSide.target], road.id)
        self.canvas.create_line(leftLine.source.x, leftLine.source.y, leftLine.target.x,
                                leftLine.target.y, fill=settings.setDict["color"]["road"])

        for lane in road.lanes[1:]:
            line = lane.rightBorder
            self.canvas.create_line(line.source.x, line.source.y, line.target.x,
                                    line.target.y, fill=settings.setDict['color']['lane_mark'], dash=(10, 10))

    def drawWorld(self):
        for intersection in self.world.intersections.values():
            self.drawIntersection(intersection)

        for road in self.world.roads.values():
            self.drawRoad(road)

    def drawCar(self, car):
        angle = car.direction
        center = car.coords
        rect = Rect(0, 0, car.length * self.scale, car.width * self.scale)
        rect.center(Point(0, 0))
        coords = [Point(center.x + rect.left(), center.y + rect.top()),
                  Point(center.x + rect.left(), center.y + rect.bottom()),
                  Point(center.x + rect.right(), center.y + rect.bottom()),
                  Point(center.x + rect.right(), center.y + rect.top())]
        self.rotate(angle, coords, center)
        splitCoords = [(point.x, point.y) for point in coords]
        otherCoords = []
        for point in coords:
            otherCoords.append(point.x)
            otherCoords.append(point.y)
        if not self.canvas.find_withtag(car.id):
            self.canvas.create_polygon(splitCoords, fill=car.color, tag=car.id)
        else:
            ID = self.canvas.find_withtag(car.id)
            if car.alive:
                self.canvas.coords(ID, *otherCoords)
            else:
                self.world.removeCar(car)
                self.canvas.delete(ID)

        if self.debug is True:
            if car.trajectory.temp and not self.canvas.find_withtag(car.id + '_curve'):
                if car.trajectory.temp.lane:
                    curve = car.trajectory.temp.lane
                    self.drawCurve(curve, car.id)
                    if curve.O:
                        self.drawCircle(curve.O, 1 * self.scale, car.id)
                    if curve.Q:
                        self.drawCircle(curve.Q, 1 * self.scale, car.id)

            if self.canvas.find_withtag(car.id + '_curve') and \
                    car.trajectory.isChangingLanes is False:
                ID = self.canvas.find_withtag(car.id + '_curve')
                for subId in ID:
                    self.canvas.delete(subId)

    def drawCurve(self, curve, ID):
        pointsNum = 10
        prePoint = curve.getPoint(0)
        for i in range(pointsNum):
            point = curve.getPoint(i / pointsNum)
            self.canvas.create_line(prePoint.x, prePoint.y, point.x, point.y,
                                    fill=settings.setDict['color']['curve'], tag=ID + '_curve')
            prePoint = point

    def drawCircle(self, center, delimeter, ID):
        self.canvas.create_oval(center.x - delimeter, center.y - delimeter,
                                center.x + delimeter, center.y + delimeter, fill=settings.setDict['color']['curve'], tag=ID + '_curve')

    def clearPath(self):
        for car in self.world.cars.values():
            if self.canvas.find_withtag(car.id + '_curve'):
                ID = self.canvas.find_withtag(car.id + '_curve')
                for subId in ID:
                    self.canvas.delete(subId)
