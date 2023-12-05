# fhorner term project
# Bee Game
# Based on CMU 15-112 Scaffolded Bee Project:
# https://docs.google.com/document/d/1RK2QOc11oxlUyyxkOA0AdzSdKWcCD-W9D18Xr_x65ms/edit#heading=h.hwp65jpeckcu

from cmu_graphics import *
import math
import random
from PIL import Image

# Classes

## Bee Class ------------------------------------------------------------------

class Bee: 
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.target = None
        self.targetX = None
        self.targetY = None
        self.pollenStash = []
        self.type = 'WASP'
        self.radius = 50 #approximate for wasp dimensions
        self.spriteCounter = 0
        self.spriteStepCounter = 0
        #only want to call these once to increase efficiency
        self.spritesRight = getSprites(self.type, 'RIGHT')
        self.spritesLeft = getSprites(self.type, 'LEFT')
        self.id = x 
        self.baseSpeed =  8

    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Bee):
            return self.id == other.id
 
    def drawBee(self):
        #bee and wasp images from gamedeveloperstudio.com
        #https://www.gamedeveloperstudio.com/graphics/viewgraphic.php?page-name=Bee-sprite&item=1f4d185v1k0y341h2g
        #https://www.gamedeveloperstudio.com/graphics/viewgraphic.php?page-name=Enemy-wasp-game-sprite&item=1n6t1l594k8t2s995b
        #sprite animation based on Mike's tutorial:
        #https://piazza.com/class/lkq6ivek5cg1bc/post/2231
        if self.dx >= 0: #draw right facing
            sprite = self.spritesRight[self.spriteCounter]
            drawImage(sprite, self.x, self.y, align = 'center')
        else: #draw left facing
            sprite = self.spritesLeft[self.spriteCounter]
            drawImage(sprite, self.x, self.y, align = 'center')
        
    def drawPollenOnFeet(self): 
        for idx in range(len(self.pollenStash)):
            circleX = self.x - 30 + 10*idx
            circleY = self.y + 40
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
            elif self.target.y < 0 - self.target.radius:
                self.target = None
        elif self.target == None:
            smallestDistance = None
            bestFlower = None
            #loop through flowers
            for flower in app.flowers:
            #if ungathered or unpollinated, get distance
                if ((flower.type == 'givesPollen' and flower.hasPollen) or 
                    (flower.type == 'needsPollen' and not flower.hasPollen and 
                    #additionally check that bee has correct pollen 
                    flower.color in self.pollenStash)):
                    currDistance = Bee.getDistance(self.x, self.y, 
                                                   flower.x, flower.y)
                    if (smallestDistance == None or 
                        smallestDistance > currDistance):
                        smallestDistance = currDistance
                        bestFlower = flower
            #smallest distance becomes new target
            self.target = bestFlower
        #if target is same as other bee, drop it
        for bee in app.helperBees:
            if (self.id != bee.id and #if it's not you and same target as you
                self.target == bee.target):
                    self.target = None #drop the target
                    break

    def beeMove(self, app):
        #step depends on distance: faster when farther from target
        #just divide distance by constant so it constantly rescales
        if self.targetX != None:
            self.dx = self.targetX - self.x
            self.dy = self.targetY - (self.y + 20) #offset so aims with feet
            newX = self.x + self.dx/11
            newY = self.y + self.dy/11
            if self.radius < newX and newX < app.width - self.radius:
                self.x = newX
            if self.radius < newY and newY < app.height - self.radius:
                self.y = newY
    
    #sprite animation based on Mike's tutorial:
    #https://piazza.com/class/lkq6ivek5cg1bc/post/2231
    def iterateSpriteCounter(self):
        self.spriteStepCounter += 1
        #speed is distance per step
        if self.targetX == None:
            speed = 1
        else:
            speed = Bee.getDistance(self.x, self.y, self.targetX, self.targetY)
        #this is where fly speed will change
        if self.spriteStepCounter >= self.baseSpeed - math.log(speed): 
            self.spriteCounter = (1 + self.spriteCounter)%len(self.spritesRight)
            self.spriteStepCounter = 0

    def beeOnStep(self, app):
        self.iterateSpriteCounter()
        #pick target. This updates self.target
        self.helperChooseTarget(app)
        if self.target != None:
            self.targetX = self.target.x
            self.targetY = self.target.y
            self.beeMove(app)
        
    def gatherPollen(self, flower):
        #add correct color pollen to stash
        pollenType = flower.color
        self.pollenStash += [pollenType]
        #flower now has no pollen
        flower.hasPollen = False
        #remove oldest pollen if over 6
        if len(self.pollenStash) > 6:
            self.pollenStash.pop(0)

    def givePollen(self, flower):
        pollenType = flower.color
        if pollenType in self.pollenStash:
            #remove it from stash
            pollenIdx = self.pollenStash.index(pollenType)
            self.pollenStash.pop(pollenIdx)
            #flower now has pollen
            flower.hasPollen = True
            if self.type == 'BEE':
                if self.health + 5 > 100:
                    self.health = 100
                else: self.health += 5

    def pollinate(self, app):
        for flower in app.flowers:
            #check if close enough to give/gather pollen
            if Bee.getDistance(self.x, self.y+50, flower.x, flower.y) < self.radius:   
                #if flower is type givesPollen and has pollen: gather pollen
                if flower.type == 'givesPollen' and flower.hasPollen:
                    self.gatherPollen(flower)
                #if flower is type needsPollen and does not have pollen: give 
                elif flower.type == 'needsPollen' and not flower.hasPollen:
                    self.givePollen(flower)

## Player Subclass ------------------------------------------------------------

class Player(Bee): #subclass of Bee
    def __init__(self, x, y):
        super().__init__(x,y)
        self.type = 'BEE'
        self.spritesRight = getSprites(self.type, 'RIGHT')
        self.spritesLeft = getSprites(self.type, 'LEFT')
        self.health = 100
        self.radius = 45 #approximate for sprite dimensions
        self.baseSpeed = 6
        
    def drawPollenStash(self):
        for idx in range(len(self.pollenStash)):
            #draw at top left
            circleX = 20 + idx * 25
            circleY = 20
            drawCircle(circleX, circleY, 10, fill = self.pollenStash[idx])

    def drawHealthBar(self, app):
        if app.gameStatus == 'inPlay':
            length = (app.width/3) * (self.health/100)
            drawRect(app.width*.6, 15, length, 15, fill = 'fireBrick')
            drawRect(app.width*.6, 15, app.width/3, 15, fill = None, border = 'Black')

    def checkKilledByWasp(self, app):
        for bee in app.helperBees:
            distance = Bee.getDistance(self.x, self.y, bee.x, bee.y)
            if distance < self.radius + bee.radius:
                app.gameStatus = 'lost'

    def playerOnStep(self, app):
        self.beeMove(app)
        self.iterateSpriteCounter()
        self.checkKilledByWasp(app)
        #health bar decrements
        self.health -= .05
        if self.health <= 0:
            app.gameStatus = 'lost'

## Flower Class ---------------------------------------------------------------

class Flower:
    def __init__(self, x, y, type, color, app):
        self.x = x
        self.y = y
        self.type = type #givesPollen or needsPollen
        self.color = color
        #starting hasPollen determined by type
        self.hasPollen = True if type == 'givesPollen' else False
        self.radius = 15
        self.startX = x 
        self.id = x

    def __eq__(self, other):
        if isinstance(other, Flower):
            return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
      
    def drawFlower(self):
        if self.type == 'givesPollen':
            if self.hasPollen:
                drawCircle(self.x, self.y, self.radius + 6, 
                           fill = self.color, opacity=50)
                drawCircle(self.x, self.y, self.radius + 3, 
                           fill = 'darkSeaGreen')
                drawCircle(self.x, self.y, self.radius, fill = self.color)
            else:
                drawCircle(self.x, self.y, self.radius, fill = self.color)
        elif self.type == 'needsPollen':
            if not self.hasPollen:
                drawCircle(self.x, self.y, self.radius, fill = self.color)
                drawCircle(self.x, self.y, self.radius - 5, 
                           fill = 'darkSeaGreen')
            else:
                drawCircle(self.x, self.y, self.radius + 5, fill = self.color)
                drawCircle(self.x, self.y, self.radius, 
                           fill = 'darkSeaGreen')
                drawCircle(self.x, self.y, self.radius, 
                           fill = self.color, opacity= 25)
    
    #cite the scaffolded
    def flowerMove(self):
        xOffset = 100 *  (math.sin(.01 * self.y))
        self.y -= 1.5
        self.x = self.startX + xOffset
    
    def updateRadius(self): #based on pollination status
        if self.type == 'givesPollen':
            if self.hasPollen: 
                self.radius = 15
            else:
                newRadius = 30
                return newRadius
        if self.type == 'needsPollen':
            if not self.hasPollen: 
                self.radius = 20
            else: 
                newRadius = 30
                return newRadius

    def flowerOnStep(self, app):
        self.flowerMove()
        newRadius = self.updateRadius()
        if newRadius != None and app.onStepCounter % 3 == 0:
            if self.radius < newRadius:
                    self.radius += 1
        
### Main Animation Functions --------------------------------------------------
def onAppStart(app):
    app.gameStatus = "start" #start, inPlay, lost
    app.width = 800
    app.height = 800
    app.flowerColors = ['teal', 'lightCoral', 'gold']
    resetApp(app)

def onStep(app):
    if app.gameStatus == 'inPlay':
        app.player.playerOnStep(app) #move bee towards cursor
        app.player.pollinate(app) 
        for flower in app.flowers:
            flower.flowerOnStep(app)
        for helper in app.helperBees:
            helper.beeOnStep(app)
            helper.pollinate(app)
        #slower steps
        app.onStepCounter += 1
        if app.onStepCounter % 40 == 0:
            generateFlowerWrapper(app)
            #also clear old flowers
            clearOldFlowers(app)
            
def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = 'darkSeaGreen')
    if app.gameStatus == 'start':
        drawGameStart(app)
    if app.gameStatus == 'inPlay':
        drawInPlay(app)
    if app.gameStatus == 'lost':
        drawInPlay(app)
        drawYouLost(app)
        
def onMouseMove(app, mouseX, mouseY):
    app.player.targetX = mouseX
    app.player.targetY = mouseY

def onKeyPress(app, key):
    if app.gameStatus == 'inPlay':
        if key == 'w':
            #add new wasp
            getHelperBee(app)
        if key == 'm':
            #minus a wasp
            app.helperBees.pop()
    if key == 'r':
        app.gameStatus = 'inPlay'
        resetApp(app)
    if key == 's' and app.gameStatus == 'start':
        app.gameStatus = 'inPlay'

### App Helper Functions ------------------------------------------------------

def resetApp(app):
    app.onStepCounter = 0
    app.targetX = None
    app.targetY = None
    app.player = Player(app.width/2, app.height/2)
    app.flowers = []
    initialFlowers(app, 8)
    app.helperBees = []

def generateFlower(app, y):
    x = random.randrange(app.width)
    type = random.choice(['givesPollen', 'needsPollen'])
    color = random.choice(app.flowerColors)
    return Flower(x, y, type, color, app)

def generateFlowerWrapper(app):
    y = app.height + 30
    newFlower = generateFlower(app, y)
    app.flowers += [newFlower]

def clearOldFlowers(app):
    toRemove = []
    for flower in app.flowers:
        if flower.y < 0 - flower.radius:
            toRemove += [flower]
    for flower in toRemove:
        flowerIdx = app.flowers.index(flower)
        app.flowers.pop(flowerIdx)

def getHelperBee(app):
    newBee = Bee(random.randrange(app.width), 
                    random.randrange(app.height - 100))
    app.helperBees += [newBee]

def initialFlowers(app, numFlowers):
    for i in range(numFlowers):
            newFlower = generateFlower(app, random.randrange(app.height))
            app.flowers += [newFlower]

#I referenced this post for how to loop through multiple files and open each
#https://stackoverflow.com/questions/55446133/opening-multiple-images-on-pil-with-a-for-loop
def getSprites(animal, direction): 
        spritesList = []
        for i in range(6):
            frame = Image.open('%s_FLY_%s/%s.png' % (animal, direction, i+1))
            sprite = CMUImage(frame)
            spritesList.append(sprite)
        return spritesList

def drawGameStart(app):
    for flower in app.flowers:
        flower.drawFlower()
    drawRect(app.width/2, app.height/2, app.width * .7, app.width * .7,
            align = 'center', fill = 'black', opacity = 50)
    drawRect(app.width/2, app.height/2, app.width * .7, app.width * .7,
            align = 'center', fill = None, border = 'White', borderWidth = 5)
    drawLabel('The Bee Game', app.width/2, app.height/3, font = 'arial',
              size = 24, bold = True, fill = 'white')
    drawLabel('Pollinate the flowers to keep your health up!',  
              app.width/2, app.height/2, font = 'montserrat', 
              size = 18, fill = 'white')
    drawLabel("Press 'w' to add wasp enemies, and 'm' to subtract a wasp." , 
               app.width/2, app.height/2 + 30, font = 'montserrat',
              size = 18, fill = 'white')
    drawLabel("Don't let them eat you!" , app.width/2, app.height/2 + 60, 
              font = 'montserrat', size = 18, fill = 'white')
    drawLabel("Press 's' to start." , app.width/2, app.height/2 +90, 
              font = 'montserrat', size = 18, fill = 'white')
    #add images
    bee = Image.open('BEE_FLY_RIGHT/1.png')
    bee = CMUImage(bee)
    drawImage(bee, app.width*.25, app.height*.25, align = 'center')
    wasp = Image.open('WASP_FLY_LEFT/1.png')
    wasp = CMUImage(wasp)
    drawImage(wasp, app.width*.75, app.height*.75, align = 'center')

def drawInPlay(app):
    for flower in app.flowers:
        flower.drawFlower()
    for helper in app.helperBees:
        helper.drawBee()
        helper.drawPollenOnFeet()
    app.player.drawBee()
    app.player.drawPollenStash()
    app.player.drawPollenOnFeet()
    app.player.drawHealthBar(app)

def drawYouLost(app):
    drawRect(app.width/2, app.height/2, app.width * .5, app.width * .5,
            align = 'center', fill = 'black', opacity = 50,
            border = 'black', borderWidth = 3)
    drawLabel('You lost! :(', app.width/2, app.height/2, size = 24, 
            bold = True, fill = 'white')
    drawLabel('Press r to reset.', app.width/2, app.height/2 + 25, 
            size = 18, fill = 'white')



def main():
    runApp()
    
main()

