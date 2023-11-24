# fhorner term project
# Bee Game

from cmu_graphics import *
import math
import random

### Classes

class Player: 
    def __init__(self, x, y, targetX, targetY):
        self.x = x
        self.y = y
        self.targetX = targetX
        self.targetY = targetY
        self.pollenStash = []
        self.radius = 30
        
    def drawPlayer(self):
        drawCircle(self.x, self.y, self.radius, fill = 'orange')

    def drawPollenStash(self):
        for idx in range(len(self.pollenStash)):
            #draw at top left
            circleX = 20 + idx * 25
            circleY = 20
            drawCircle(circleX, circleY, 10, fill = self.pollenStash[idx])
            #draw under bee
            circleX = self.x - self.radius + 10*idx
            circleY = self.y + self.radius
            drawCircle(circleX, circleY, 10, fill = self.pollenStash[idx])

        
    def playerOnStep(self):
        #move bee towards target
        #step depends on distance: faster when farther from target
        if self.targetX != None:
            dx = abs(self.x - self.targetX)
            dy = abs(self.y - self.targetY)

            #stepSize = distance**.25
            if self.targetX > self.x:
                self.x += dx/20
            else:
                self.x -= dx/20
                
            if self.targetY > self.y:
                self.y += dy/20
            else:
                self.y -= dy/20
    
    def pollinate(self, flowersList):
        for flower in flowersList:
            #check if close enough to give/gather pollen
            if getDistance(self.x, self.y, flower.x, flower.y) < 20:   
                #if flower is type givesPollen and has pollen: gather pollen
                if flower.type == 'givesPollen' and flower.hasPollen:
                    gatherPollen(self, flower)
                #if flower is type needsPollen and does not have pollen: give 
                elif flower.type == 'needsPollen' and not flower.hasPollen:
                    givePollen(self, flower)
        
#type = givesPollen or needsPollen

class Flower:
    def __init__(self, x, y, type, color):
        self.x = x
        self.y = y
        self.type = type
        self.color = color
        #starting hasPollen determined by type
        self.hasPollen = True if type == 'givesPollen' else False
        self.radius = 30

      
    def drawFlower(self):
        if self.type == 'givesPollen':
            if self.hasPollen:
                drawCircle(self.x, self.y, 33, fill = self.color, opacity=50)
                drawCircle(self.x, self.y, 28, fill = 'white')
                drawCircle(self.x, self.y, 25, fill = self.color)
            else:
                drawCircle(self.x, self.y, 35, fill = self.color)
        elif self.type == 'needsPollen':
            if not self.hasPollen:
                drawCircle(self.x, self.y, 30, fill = self.color)
                drawCircle(self.x, self.y, 25, fill = 'white')
            else:
                drawCircle(self.x, self.y, 37, fill = self.color)
                drawCircle(self.x, self.y, 30, fill = 'white')
                drawCircle(self.x, self.y, 30, fill = self.color, opacity= 25)

    def flowerOnStep(self):
        self.y -= 2
                

### Helpers

def getDistance(x1, y1, x2, y2):
    return(((x2 - x1)**2 + (y2 - y1)**2)**.5)

def gatherPollen(player, flower):
    #add correct color pollen to stash
    pollenType = flower.color
    player.pollenStash += [pollenType]
    #flower now has no pollen
    flower.hasPollen = False
    
def givePollen(player, flower):
    pollenType = flower.color
    if pollenType in player.pollenStash:
        #remove it from stash
        pollenIdx = player.pollenStash.index(pollenType)
        player.pollenStash.pop(pollenIdx)
        #flower now has pollen
        flower.hasPollen = True

def generateFlower(app): #x, y, type, color
    x = random.randrange(app.width)
    y = app.height - 30
    type = random.choice(['givesPollen', 'needsPollen'])
    color = random.choice(app.flowerColors)
    newFlower = Flower(x, y, type, color)
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
    app.flowers = []
    app.flowerColors = ['blue', 'pink', 'yellow']
    app.onStepCounter = 0

    
def redrawAll(app):
    for flower in app.flowers:
        flower.drawFlower()
    app.player.drawPlayer()
    app.player.drawPollenStash()
    
def onMouseMove(app, mouseX, mouseY):
    app.player.targetX = mouseX
    app.player.targetY = mouseY


def onStep(app):
    app.player.playerOnStep() #move bee towards cursor
    app.player.pollinate(app.flowers) 
    for flower in app.flowers:
        flower.flowerOnStep()
    #slower steps
    app.onStepCounter += 1
    if app.onStepCounter % 60 == 0:
        generateFlower(app)
        #also clear old flowers
        clearOldFlowers(app)
    
    #health bar decrements
    #bird approaches bee (constant time)

def main():
    runApp()
    
main()