import itertools
import copy

from model.lane import Lane
from model.intersection import Intersection


class Road():
    id_generator = itertools.count(1)

    def __init__(self, source: Intersection, target: Intersection):
        self.id = "road_" + str(next(self.id_generator))
        self.source = source
        self.target = target
        self.lanes = []
        self.lanesNumber = None
        self.update()

    def copy(self):
        return copy.deepcopy(self)

    @property
    def length(self):
        return (self.targetSide.target - self.sourceSide.source).length

    @property
    def leftmostLane(self):
        return self.lanes[-1]

    @property
    def rightmostLane(self):
        return self.lanes[0]

    def getTurnDirection(self, other: Intersection):
        assert self.target is other.source
        side1 = self.targetSideId
        side2 = other.sourceSideId
        # 0 - right, 1 - forward, 2 - left
        turnNumber = (side2 - side1 - 1 + 8) % 3
        return turnNumber

    def update(self):
        self.sourceSideId = self.source.rect.getSectorId(
            self.target.rect.center())
        self.sourceSide = self.source.rect.getSide(
            self.sourceSideId).subsegment(0.5, 1.0)
        self.targetSideId = self.target.rect.getSectorId(
            self.source.rect.center())
        self.targetSide = self.target.rect.getSide(
            self.targetSideId).subsegment(0, 0.5)
        self.lanesNumber = 2
        sourceSplits = self.sourceSide.split(self.lanesNumber, True)
        targetSplits = self.targetSide.split(self.lanesNumber, False)

        if self.lanes is not None or len(self.lanes) < self.lanesNumber:
            copyCarPositionsList = [lane.carsPositions for lane in self.lanes]
            self.lanes.clear()
            for i in range(self.lanesNumber):
                self.lanes.append(Lane(sourceSplits[i], targetSplits[i], self))
                if i < len(copyCarPositionsList):
                    self.lanes[i].carsPositions = copyCarPositionsList[i]

        for i in range(self.lanesNumber):
            self.lanes[i].sourceSegment = sourceSplits[i]
            self.lanes[i].targetSegment = targetSplits[i]
            self.lanes[i].leftmostAdjacent = self.lanes[-1]
            self.lanes[i].rightmostAdjacent = self.lanes[0]
            self.lanes[i].id += str(i + 1)
            self.lanes[i].update()
