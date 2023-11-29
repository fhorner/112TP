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
        self.type = 'WASP'
        self.radius = 50 #approximate for wasp dimensions
        self.spriteCounter = 0
        self.spriteStepCounter = 0
        #only want to call these once to increase efficiency
        self.spritesRight = getSprites(self.type, 'RIGHT')
        self.spritesLeft = getSprites(self.type, 'LEFT')
        self.id = x 

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
            elif not self.target.onScreen:
                self.target = None
            #if target is same as other bee, drop it
            #this is not working as expected
            for bee in app.helperBees:
                #if it's not you
                if (self.id != bee.id and 
                    #and it has the same target as you
                    self.target == bee.target):
                    #drop the target
                    self.target = None
                    break

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

    def beeMove(self, app):
        #step depends on distance: faster when farther from target
        #just divide distance by constant so it constantly rescales
        if self.targetX != None:
            self.dx = self.targetX - self.x
            self.dy = self.targetY - (self.y + 20) #offset so aims with feet
            newX = self.x + self.dx/10
            newY = self.y + self.dy/10
            #these have slightly different offsets based on size of sprite
            if self.radius < newX and newX < app.width - self.radius:
                self.x = newX
            if self.radius < newY and newY < app.height - self.radius:
                self.y = newY
    
    #sprite animation based on Mike's tutorial:
    #https://piazza.com/class/lkq6ivek5cg1bc/post/2231
    def iterateSpriteCounter(self):
        self.spriteStepCounter += 1
        #sprites need different base speeds since different num of frames
        modSpeed = 8 if self.type == 'WASP' else 6
        #speed is distance per step
        if self.targetX == None:
            speed = 1
        else:
            speed = Bee.getDistance(self.x, self.y, self.targetX, self.targetY)
        #this is where fly speed will change
        if self.spriteStepCounter >= modSpeed - math.log(speed): 
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
        self.type = 'BEE'
        self.spritesRight = getSprites(self.type, 'RIGHT')
        self.spritesLeft = getSprites(self.type, 'LEFT')
        self.health = 100
        self.radius = 45 #approximate for sprite dimensions
        
    def drawPollenStash(self):
        for idx in range(len(self.pollenStash)):
            #draw at top left
            circleX = 20 + idx * 25
            circleY = 20
            drawCircle(circleX, circleY, 10, fill = self.pollenStash[idx])

    def drawHealthBar(self, app):
        length = (app.width/3) * (self.health/100)
        drawRect(app.width*.6, 15, length, 15, fill = 'darkRed')

    def checkKilledByWasp(self, app):
        for bee in app.helperBees:
            distance = Bee.getDistance(self.x, self.y, bee.x, bee.y)
            if distance < self.radius + bee.radius:
                app.gameOver = True


    def playerOnStep(self, app):
        self.beeMove(app)
        self.iterateSpriteCounter()
        self.checkKilledByWasp(app)
        #health bar decrements
        self.health -= .05
        if self.health <= 0:
            app.gameOver = True
    
class Flower:
    def __init__(self, x, y, type, color, app):
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
        self.id = app.onStepCounter

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
    return Flower(x, y, type, color, app)

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

def getHelperBees(app, numBees):
    for i in range(numBees):
        newBee = Bee(random.randrange(app.width), random.randrange(app.height))
        app.helperBees += [newBee]

#I referenced this post for how to loop through multiple files and open each
#https://stackoverflow.com/questions/55446133/opening-multiple-images-on-pil-with-a-for-loop
def getSprites(animal, direction): 
        spritesList = []
        for i in range(6):
            frame = Image.open('%s_FLY_%s/%s.png' % (animal, direction, i+1))
            sprite = CMUImage(frame)
            spritesList.append(sprite)
        return spritesList

def resetApp(app):
    app.onStepCounter = 0
    app.playerX = app.width/2
    app.playerY = app.height/2
    app.targetX = None
    app.targetY = None
    app.player = Player(app.playerX, app.playerY)
    app.flowers = [generateFlower(app, random.randrange(app.height)),
                   generateFlower(app, random.randrange(app.height)),
                   generateFlower(app, random.randrange(app.height)),
                   generateFlower(app, random.randrange(app.height)),
                   ]
    app.helperBees = []
    getHelperBees(app, 0)
    app.gameOver = False

### Animation functions
def onAppStart(app):
    app.width = 700
    app.height = 700
    app.flowerColors = ['blue', 'pink', 'yellow']
    resetApp(app)

   

def onStep(app):
    if not app.gameOver:
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
    if app.gameOver:
        drawRect(app.width/2, app.height/2, app.width * .5, app.width * .5,
                 align = 'center', fill = 'black', opacity = 50,
                 border = 'black', borderWidth = 3)
        drawLabel('You lost! :(', app.width/2, app.height/2, size = 24, 
                  bold = True, fill = 'white')
        drawLabel('Press r to reset.', app.width/2, app.height/2 + 25, 
                  size = 18, fill = 'white')
    
def onMouseMove(app, mouseX, mouseY):
    app.player.targetX = mouseX
    app.player.targetY = mouseY

def onKeyPress(app, key):
    if key == 'b':
        #add new wasp (without overwriting existing bees)
        getHelperBees(app, 1)
    if key == 'm':
        #minus a wasp
        app.helperBees.pop()
    if key == 'r':
        resetApp(app)
    

def main():
    runApp()
    
main()