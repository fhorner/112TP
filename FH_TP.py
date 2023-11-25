# fhorner term project
# Bee Game

from cmu_graphics import *
import math
import random

### Classes

class Bee: 
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target = None
        self.targetX = None
        self.targetY = None
        self.pollenStash = []
        self.radius = 30
        self.color = 'red'
 
    def drawBee(self):
        drawCircle(self.x, self.y, self.radius, fill = self.color)

    def drawPollenOnFeet(self): 
        for idx in range(len(self.pollenStash)):
            circleX = self.x - self.radius + 10*idx
            circleY = self.y + self.radius
            drawCircle(circleX, circleY, 10, fill = self.pollenStash[idx])

    @staticmethod
    def getDistance(x1, y1, x2, y2):
        return(((x2 - x1)**2 + (y2 - y1)**2)**.5)

    def helperChooseTarget(self, app):
        if self.target != None:
            #if it gives pollen but doesn't have pollen, drop as target
            if (self.target.type == 'givesPollen' and
               not self.target.hasPollen):
                self.target = None
            #if it needs pollen but already has pollen, drop as target
            elif (self.target.type == 'needsPollen' and 
                  self.target.hasPollen):
                    self.target = None
            #if target off screen, drop as target
            elif not self.target.onScreen:
                self.target = None
        elif self.target == None:
            smallestDistance = None
            bestFlower = None
            #loop through flowers
            for flower in app.flowers:
            #if ungathered or unpollinated, get distance
                if ((flower.type == 'givesPollen' and
                     flower.hasPollen) or 
                    (flower.type == 'needsPollen' and 
                    not flower.hasPollen and 
                    #additionally check that it has correct pollen 
                    flower.color in self.pollenStash)):
                    currDistance = Bee.getDistance(self.x, self.y, flower.x, flower.y)
                    if (smallestDistance == None or 
                        smallestDistance > currDistance):
                        smallestDistance = currDistance
                        bestFlower = flower
            #smallest distance becomes new target
            self.target = bestFlower

    def beeMove(self):
        #step depends on distance: faster when farther from target
        #just divide distance by constant so it constantly rescales
        if self.targetX != None:
            dx = abs(self.x - self.targetX)
            dy = abs(self.y - self.targetY)
            if self.targetX > self.x:
                self.x += dx/20
            else:
                self.x -= dx/20
            if self.targetY > self.y:
                self.y += dy/20
            else:
                self.y -= dy/20

    def beeOnStep(self, app):
        #pick target. This updates self.target
        self.helperChooseTarget(app)
        if self.target != None:
            self.targetX = self.target.x
            self.targetY = self.target.y
            self.beeMove()

    def gatherPollen(self, flower):
        #add correct color pollen to stash
        pollenType = flower.color
        self.pollenStash += [pollenType]
        #flower now has no pollen
        flower.hasPollen = False

    def givePollen(self, flower):
        pollenType = flower.color
        if pollenType in self.pollenStash:
            #remove it from stash
            pollenIdx = self.pollenStash.index(pollenType)
            self.pollenStash.pop(pollenIdx)
            #flower now has pollen
            flower.hasPollen = True

    def pollinate(self, app):
        for flower in app.flowers:
            #check if close enough to give/gather pollen
            if Bee.getDistance(self.x, self.y, flower.x, flower.y) < 20:   
                #if flower is type givesPollen and has pollen: gather pollen
                if flower.type == 'givesPollen' and flower.hasPollen:
                    self.gatherPollen(flower)
                #if flower is type needsPollen and does not have pollen: give 
                elif flower.type == 'needsPollen' and not flower.hasPollen:
                    self.givePollen(flower)

class Player(Bee): #subclass of Bee
    def __init__(self, x, y, targetX, targetY):
        super().__init__(x,y)
        self.color = 'orange'
        self.health = 100
        
    def drawPollenStash(self):
        for idx in range(len(self.pollenStash)):
            #draw at top left
            circleX = 20 + idx * 25
            circleY = 20
            drawCircle(circleX, circleY, 10, fill = self.pollenStash[idx])

    def drawHealthBar(self, app):
        length = (app.width/2 - 10) * (self.health/100)
        drawRect(app.width/2, 15, length, 15, fill = 'darkRed')

    def playerOnStep(self):
        self.beeMove()
    
class Flower:
    def __init__(self, x, y, type, color):
        self.x = x
        self.y = y
        self.type = type #givesPollen or needsPollen
        self.color = color
        #starting hasPollen determined by type
        self.hasPollen = True if type == 'givesPollen' else False
        self.radius = 15
        #used in sinusoidal movement pattern
        self.startX = x 
        self.stepY = 1
        self.stepX = 1
        self.onScreen = True
      
    def drawFlower(self):
        if self.type == 'givesPollen':
            if self.hasPollen:
                drawCircle(self.x, self.y, self.radius + 6, 
                           fill = self.color, opacity=50)
                drawCircle(self.x, self.y, self.radius + 3, fill = 'lightGreen')
                drawCircle(self.x, self.y, self.radius, fill = self.color)
            else:
                drawCircle(self.x, self.y, self.radius, fill = self.color)
        elif self.type == 'needsPollen':
            if not self.hasPollen:
                drawCircle(self.x, self.y, self.radius, fill = self.color)
                drawCircle(self.x, self.y, self.radius - 5, fill = 'lightGreen')
            else:
                drawCircle(self.x, self.y, self.radius + 5, fill = self.color)
                drawCircle(self.x, self.y, self.radius, fill = 'lightGreen')
                drawCircle(self.x, self.y, self.radius, 
                           fill = self.color, opacity= 25)
    
    def flowerMove(self):
        self.y -= self.stepY
        self.x += self.stepX
        rightBound = self.startX + 100
        leftBound = self.startX - 100
        if self.x >= rightBound:
            self.stepX *= -1
        elif self.x <= leftBound:
            self.stepX *= -1

        #trying to scale the speed and failing
        # self.y -= self.stepY
        # self.x += self.stepX
        # rightBound = self.startX + 100
        # leftBound = self.startX - 100
        # if self.x >= rightBound:
        #     dx = abs(self.x - leftBound)
        #     self.stepX *= -1 * (math.ceil(dx/50))
        # elif self.x <= leftBound:
        #     dx = abs(self.x - rightBound)
        #     self.stepX *= -1 * (math.ceil(dx/50))

    def updateOnScreen(self, app): 
        if self.x < 0 - self.radius or self.x > app.width + self.radius:
            self.onScreen = False
        elif self.y < 0 - self.radius or self.y > app.height + self.radius:
            self.onScreen = False
    
    def updateRadius(self): #based on pollination status
        if self.type == 'givesPollen':
            if self.hasPollen: self.radius = 15
            else: self.radius = 20
        if self.type == 'needsPollen':
            if self.hasPollen: self.radius = 20
            else: self.radius = 15

    def flowerOnStep(self, app):
        self.flowerMove()
        self.updateOnScreen(app)
        self.updateRadius()
        
### App Helper Functions

#y needs to be specified for starting flowers
def generateFlower(app, y):
    x = random.randrange(app.width)
    type = random.choice(['givesPollen', 'needsPollen'])
    color = random.choice(app.flowerColors)
    return Flower(x, y, type, color)

def generateFlowerWrapper(app):
    y = app.height - 30
    newFlower = generateFlower(app, y)
    app.flowers += [newFlower]

def clearOldFlowers(app):
    toRemove = []
    for flower in app.flowers:
        if flower.y < -30:
            toRemove += [flower]
    for flower in toRemove:
        flowerIdx = app.flowers.index(flower)
        app.flowers.pop(flowerIdx)

### Animation functions
def onAppStart(app):
    app.width = 700
    app.height = 700
    app.playerX = app.width/2
    app.playerY = app.height/2
    app.targetX = None
    app.targetY = None
    app.player = Player(app.playerX, app.playerY, app.targetX, app.targetY)
    app.flowerColors = ['blue', 'pink', 'yellow']
    app.flowers = [generateFlower(app, random.randrange(app.height)),
                   generateFlower(app, random.randrange(app.height)),
                   generateFlower(app, random.randrange(app.height)),
                   generateFlower(app, random.randrange(app.height)),]
    app.helperBees = [Bee(random.randrange(app.width), 
                            random.randrange(app.height)),
                      Bee(random.randrange(app.width), 
                            random.randrange(app.height))]
    app.onStepCounter = 0

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = 'lightGreen')
    for flower in app.flowers:
        flower.drawFlower()
    for helper in app.helperBees:
        helper.drawBee()
        helper.drawPollenOnFeet()
    app.player.drawBee()
    app.player.drawPollenStash()
    app.player.drawPollenOnFeet()
    app.player.drawHealthBar(app)
    
def onMouseMove(app, mouseX, mouseY):
    app.player.targetX = mouseX
    app.player.targetY = mouseY

def onStep(app):
    app.player.playerOnStep() #move bee towards cursor
    app.player.pollinate(app) 
    for flower in app.flowers:
        flower.flowerOnStep(app)
    for helper in app.helperBees:
        helper.beeOnStep(app)
        helper.pollinate(app)
    #slower steps
    app.onStepCounter += 1
    if app.onStepCounter % 60 == 0:
        generateFlowerWrapper(app)
        #also clear old flowers
        clearOldFlowers(app)
    
    #health bar decrements
    app.player.health -= .05

def main():
    runApp()
    
main()