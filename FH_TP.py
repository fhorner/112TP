# fhorner term project
# Bee Game

from cmu_graphics import *
import math
import random
from PIL import Image

### Classes

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
        self.spritesRight = []
        self.spritesLeft = []
        self.spriteCounter = 0
        self.spriteStepCounter = 0
        self.type = 'wasp'
 
    def drawBee(self, app):
        #bee and wasp images from gamedeveloperstudio.com
        #https://www.gamedeveloperstudio.com/graphics/viewgraphic.php?page-name=Bee-sprite&item=1f4d185v1k0y341h2g
        #https://www.gamedeveloperstudio.com/graphics/viewgraphic.php?page-name=Enemy-wasp-game-sprite&item=1n6t1l594k8t2s995b
        #sprite animation based on Mike's tutorial:
        #https://piazza.com/class/lkq6ivek5cg1bc/post/2231
        if self.dx >= 0: #draw right facing
            if self.type == 'wasp':
                sprite = app.waspSpritesRight[self.spriteCounter]
            else:
                sprite = app.beeSpritesRight[self.spriteCounter]
            drawImage(sprite, self.x, self.y, align = 'center')
        else: #draw left facing
            if self.type == 'wasp':
                sprite = app.waspSpritesLeft[self.spriteCounter]
            else:
                sprite = app.beeSpritesLeft[self.spriteCounter]
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
                    #additionally check that bee has correct pollen 
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
            self.dx = self.targetX - self.x
            self.dy = self.targetY - (self.y + 20) #offset so aims with feet
            self.x += self.dx/15
            self.y += self.dy/15
            print(self.dx/15)
    
    #sprite animation based on Mike's tutorial:
    #https://piazza.com/class/lkq6ivek5cg1bc/post/2231
    def iterateSpriteCounter(self, app, animal):
        self.spriteStepCounter += 1
        #speed is distance per step
        speed = 1 if self.targetX == None else Bee.getDistance(self.x, self.y, self.targetX, self.targetY)
        print(speed)
        if animal == 'wasp':
            if self.spriteStepCounter >= 8 - math.log(speed): #this is where fly speed will change
                self.spriteCounter = (1 + self.spriteCounter) % len(app.waspSpritesRight)
                self.spriteStepCounter = 0
        if animal == 'bee':
            if self.spriteStepCounter >= 6 - math.log(speed): #this is where fly speed will change
                self.spriteCounter = (1 + self.spriteCounter) % len(app.beeSpritesRight)
                self.spriteStepCounter = 0

    def beeOnStep(self, app):
        self.iterateSpriteCounter(app, 'wasp')
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
            if self.type == 'bee':
                self.health = (self.health + 5) % 100

    def pollinate(self, app):
        for flower in app.flowers:
            #check if close enough to give/gather pollen
            if Bee.getDistance(self.x, self.y+50, flower.x, flower.y) < 40:   
                #if flower is type givesPollen and has pollen: gather pollen
                if flower.type == 'givesPollen' and flower.hasPollen:
                    self.gatherPollen(flower)
                #if flower is type needsPollen and does not have pollen: give 
                elif flower.type == 'needsPollen' and not flower.hasPollen:
                    self.givePollen(flower)

class Player(Bee): #subclass of Bee
    def __init__(self, x, y):
        super().__init__(x,y)
        self.health = 100
        self.type = 'bee'
        
    def drawPollenStash(self):
        for idx in range(len(self.pollenStash)):
            #draw at top left
            circleX = 20 + idx * 25
            circleY = 20
            drawCircle(circleX, circleY, 10, fill = self.pollenStash[idx])

    def drawHealthBar(self, app):
        length = (app.width/2 - 10) * (self.health/100)
        drawRect(app.width/2, 15, length, 15, fill = 'darkRed')

    def playerOnStep(self, app):
        self.beeMove()
        self.iterateSpriteCounter(app, 'bee')
        #health bar decrements
        self.health -= .05
    
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
        xOffset = 100 *  (math.sin(.01 * self.y))
        self.y -= 2
        self.x = self.startX + xOffset

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

# y needs to be specified for starting flowers
def generateFlower(app, y):
    x = random.randrange(app.width)
    type = random.choice(['givesPollen', 'needsPollen'])
    color = random.choice(app.flowerColors)
    return Flower(x, y, type, color)

def generateFlowerWrapper(app):
    y = app.height + 30
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

#I referenced this post for how to loop through multiple files and open each
#https://stackoverflow.com/questions/55446133/opening-multiple-images-on-pil-with-a-for-loop
def getSprites(animal, direction): 
        spritesList = []
        for i in range(6):
            frame = Image.open('%s_FLY_%s/%s.png' % (animal, direction, i+1))
            sprite = CMUImage(frame)
            spritesList.append(sprite)
        return spritesList

### Animation functions
def onAppStart(app):
    app.width = 700
    app.height = 700
    app.playerX = app.width/2
    app.playerY = app.height/2
    app.beeSpritesRight = getSprites('BEE', 'RIGHT')
    app.beeSpritesLeft = getSprites('BEE', 'LEFT')
    app.waspSpritesRight = getSprites('WASP', 'RIGHT')
    app.waspSpritesLeft = getSprites('WASP', 'LEFT')
    app.targetX = None
    app.targetY = None
    app.player = Player(app.playerX, app.playerY)
    app.flowerColors = ['blue', 'pink', 'yellow']
    app.flowers = [generateFlower(app, random.randrange(app.height)),
                   generateFlower(app, random.randrange(app.height)),
                   generateFlower(app, random.randrange(app.height)),
                   generateFlower(app, random.randrange(app.height)),
                   ]
    app.helperBees = [Bee(random.randrange(app.width), 
                            random.randrange(app.height)),
                      Bee(random.randrange(app.width), 
                            random.randrange(app.height))]
    app.onStepCounter = 0

def onStep(app):
    app.player.playerOnStep(app) #move bee towards cursor
    app.player.pollinate(app) 
    for flower in app.flowers:
        flower.flowerOnStep(app)
    for helper in app.helperBees:
        helper.beeOnStep(app)
        helper.pollinate(app)
    #slower steps
    app.onStepCounter += 1
    if app.onStepCounter % 50 == 0:
        generateFlowerWrapper(app)
        #also clear old flowers
        clearOldFlowers(app)

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = 'lightGreen')
    for flower in app.flowers:
        flower.drawFlower()
    for helper in app.helperBees:
        helper.drawBee(app)
        helper.drawPollenOnFeet()
    app.player.drawBee(app)
    app.player.drawPollenStash()
    app.player.drawPollenOnFeet()
    app.player.drawHealthBar(app)
    
def onMouseMove(app, mouseX, mouseY):
    app.player.targetX = mouseX
    app.player.targetY = mouseY
    

def main():
    runApp()
    
main()