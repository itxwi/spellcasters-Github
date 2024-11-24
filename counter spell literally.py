
import sys
import math
import time
import pygame as pyg
import os 
import random

"""

Spell creator

base:
Projectile allows all modifiers
landmine allows all modifiers

Modifiers:
duplicate (2 projectiles 1/2rd dnamage)
spread 180 (spread to the spell)
accelerate
decellerate

Payload:
Fire - more damage
Ice - freeze slow down
wind - knockback
"""


playerPos = [600,400]
playerRot = 0
lastShot = 0
playerHealth = 100
playerSpeed = 3

badguyimg = pyg.image.load(os.path.join('badguy.png'))
badguyimg = pyg.transform.scale(badguyimg,[40,40])

playerimg = pyg.image.load(os.path.join('wiz.png'))
playerimg = pyg.transform.scale(playerimg,[40,40])
movement = [False,False,False,False]
inCreator = False

bases = [
  'projectile',
  'landmine'
]

modifiers = [
  'triplicate',
  'accelerate',
]
payloads = [
  'fire',
  'slow',
  'wind'
]

currentSpell = []
projectiles = []
enemies = []
spellGui = []
pyg.init()
 
fps = 120
fpsClock = pyg.time.Clock()
 
width, height = 1200, 800
screen = pyg.display.set_mode((width, height))
def dist(point1,point2):
    return((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)**(1/2)
def inbounds(x,y):
    return True if 0<=y<=800 and 0<=x<=1200 else False
class Text:
    #everything in this game needs to be comic sans 
    def __init__ (self,pos,text,color,size,font = "Comic Sans MS"):
        self.pos = pos
        self.text = text
        self.color = color
        self.size = size
        self.font = font
    def draw(self):
        screen.blit(pyg.font.SysFont(self.font,self.size).render(self.text,True,self.color),self.pos)

class Button:
    def __init__(self, pos, size, text, color, text_color,spell = None):
        self.rect = pyg.Rect(pos[0], pos[1], size[0],size[1])
        self.pos = pos
        self.size = size
        self.color = color
        self.text = text
        self.text_color = text_color
        self.text_object = Text(self.rect.topleft, text, text_color, 15)
        self.prevclicked = False

        self.spell = spell
    def draw(self):
        pyg.draw.rect(screen, self.color, self.rect)
        self.text_object.draw()

    def clicked(self):
        mouse_pos = pyg.mouse.get_pos()
        if self.prevclicked == False and self.rect.collidepoint(mouse_pos) and pyg.mouse.get_pressed()[0]:
            self.prevclicked = True
            return True
        elif self.prevclicked == True and self.rect.collidepoint(mouse_pos) and not pyg.mouse.get_pressed()[0]:
            self.prevclicked = False
        return False
    
class Enemy():
    def __init__(self,pos,health=100,vel=[0,0]):
        self.pos = pos
        self.health = health
        self.vel = vel
        self.speed = 1
        self.effect = None
        self.rad = 40

        #fire
        self.lastdmg = 0
    def update(self):
        self.pos = [
            self.pos[0]+self.vel[0],
            self.pos[1]+self.vel[0]
        ]
        #friction
        self.vel = [
            self.vel[0]*.9,
            self.vel[0]*.9
        ]
        if abs(self.vel[0])<0.05:
            self.vel[0]=0
        if abs(self.vel[1])<0.05:
            self.vel[1]=0
        
        if self.pos[0] > playerPos[0]:
            self.pos[0]-=self.speed
        if self.pos[0] < playerPos[0]:
            self.pos[0] +=self.speed
        if self.pos[1] < playerPos[1]:
            self.pos[1] +=self.speed
        if self.pos[1] > playerPos[1]:
            self.pos[1] -=self.speed

        if self.effect:
            if self.effect == "slow":
                self.speed = .25
            if self.effect == "fire" and time.time()-self.lastdmg > .5:
                self.lastdmg = time.time()
                self.health -= 5
        if self.health <=0:
            try:
                enemies.remove(self)
            except:
                pass

        if dist(playerPos,self.pos)<self.rad+40:
            global playerHealth
            playerHealth-=5
            try:
                enemies.remove(self)
            except:
                pass
            
        badroted = pyg.transform.rotate(badguyimg,0)
        badrect = badroted.get_rect(center=self.pos)
        screen.blit(badroted, badrect)


class Projectile():
    def __init__(self,pos,rad,dmg,eff,vel=[0,0]):
        self.pos = pos
        self.vel = vel
        self.rad = rad
        self.dmg = dmg
        self.eff = eff #wind slow fire

        if self.eff == 'wind':
            self.col = [255,255,255]
            self.vel = [self.vel[0]*1.2,self.vel[1]*1.2]
        if self.eff == 'slow':
            self.col = [0,0,255]
            self.vel = [self.vel[0]*.8,self.vel[1]*.8]
        if self.eff == 'fire':
            self.col= [255,0,0]

    def update(self):
        self.pos = [
            self.pos[0]+self.vel[0],
            self.pos[1]+self.vel[1]
        ]
        if not inbounds(self.pos[0],self.pos[1]):
            try:
                enemies.remove(self)
            except:
                pass

        for enemy in enemies:
            if dist(self.pos,enemy.pos)<=self.rad+40:
                try:
                    projectiles.remove(self)
                except:
                    pass
                enemy.health -= self.dmg
                if self.eff!='wind':
                    enemy.effect = self.eff
                if self.eff == 'wind':
                    enemy.vel = [self.vel[0]*1,self.vel[1]*1]
                

        pyg.draw.circle(screen,self.col,self.pos,self.rad)

        

def drawSpellcreator():
    global spellMenu
    spellMenu = True
    #first row for bases
    for i,base in enumerate(bases):
        spellGui.append(Button([50+i*170,40],[120,40],base,[255,255,255],[0,0,0],spell=base))
    for i,modifier in enumerate(modifiers):
        spellGui.append(Button([50+i*170,90],[120,40],modifier,[255,255,255],[0,0,0],spell=modifier))
    for i,payload in enumerate(payloads):
        spellGui.append(Button([50+i*170,140],[120,50],payload,[255,255,255],[0,0,0],spell=payload))
    
    spellGui.append(Button([150,700],[120,50],"clear",[255,255,255],[0,0,0],spell=None))
    
def populate():
    for x in range(random.randint(1,10)):
        randx = random.randint(0,1200)
        randy = random.randint(0,800)
        enemies.append(Enemy([randx,randy]))


#setup
drawSpellcreator()
debounce = False
debounce2 = False

pressed = 0

while True:
    screen.fill((0, 0, 0))
    mousePos = pyg.mouse.get_pos()
    mouseState = pyg.mouse.get_pressed()
    if pressed==0:
        Text([0,400],'Press P for spells, space for next wave, make cool spells by clicking on the spells', [255,255,255],20).draw()
    
    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            exit()
        if event.type==pyg.KEYDOWN:
            if event.key == pyg.K_w:
                movement[0]=True
            if event.key ==pyg.K_a:
                movement[1]=True
            if event.key ==pyg.K_s:
                movement[2]=True
            if event.key ==pyg.K_d:
                movement[3]=True

            if event.key == pyg.K_p and debounce == False:
                inCreator = not inCreator
                debounce = True
                pressed+=1
            
            if event.key == pyg.K_SPACE and debounce2 == False:
                debounce2 = True
                print('lol')
                populate()

        if event.type==pyg.KEYUP:
            if event.key == pyg.K_w:
                movement[0]=False
            if event.key ==pyg.K_a:
                movement[1]=False
            if event.key ==pyg.K_s:
                movement[2]=False
            if event.key ==pyg.K_d:
                movement[3]=False
            if event.key == pyg.K_p:
                debounce = False
            if event.key == pyg.K_SPACE:
                debounce2 = False


        
    if inCreator:
        for obj in spellGui:
            obj.draw()
            if obj.clicked():
                if obj.spell:
                    currentSpell.append(obj.spell)
                else:
                    currentSpell = []
        
        if currentSpell:
            Text([0,400],' '.join(currentSpell), [255,255,255],20).draw()
    else:
        Text([0,0],f"health: {playerHealth}", [255,255,255],20).draw()
        if (mousePos[1]-playerPos[1]) !=0:
            playerRot = math.degrees(math.atan2((mousePos[0]-playerPos[0]),(mousePos[1]-playerPos[1])))-90
        
        if movement[0] and ((playerPos[1]-playerSpeed) > 0 and (playerPos[1]-playerSpeed) < 800):
            playerPos[1]-=playerSpeed
        if movement[1] and ((playerPos[0]-playerSpeed) > 0 and (playerPos[1]-playerSpeed) < 1200):
            playerPos[0]-=playerSpeed
        if movement[2] and ((playerPos[1]+playerSpeed) > 0 and (playerPos[1]+playerSpeed) < 800):
            playerPos[1]+=playerSpeed
        if movement[3] and ((playerPos[0]+playerSpeed) > 0 and (playerPos[0]+playerSpeed) < 1200):
            playerPos[0]+=playerSpeed
        
        playerrotated = pyg.transform.rotate(playerimg,playerRot)
        playerrect = playerrotated.get_rect(center=playerPos)
        screen.blit(playerrotated, playerrect)
        #print(playerRot)
        if time.time()-lastShot > 1:
            lastShot = time.time()
            stack = []
            for spell in currentSpell:
            

                #print(new_vel)

                stack.append(spell)
                if spell in payloads:
                    if any(spell in modifiers for spell in stack):
                        if 'triplicate' in stack:
                            for i in range(-1,2):
                                new_vel = [
                                    math.cos(math.radians(playerRot+i*7))*3,
                                    -math.sin(math.radians(playerRot+i*7))*3
                                ]
                                if 'landmine' in stack:
                                    new_vel = [0,0]
                                myproj = Projectile(playerPos,30,5,spell,new_vel)
                                projectiles.append(myproj)
                        if 'accelerate' in stack:
                            new_vel = [
                                math.cos(math.radians(playerRot))*3.5,
                                -math.sin(math.radians(playerRot))*3.5
                            ]
                            if 'landmine' in stack:
                                    new_vel = [0,0]
                            myproj = Projectile(playerPos,30,5,spell,new_vel)
                            projectiles.append(myproj)
                    else:
                        new_vel = [
                            math.cos(math.radians(playerRot))*3,
                            -math.sin(math.radians(playerRot))*3
                        ]
                        if 'landmine' in stack:
                                    new_vel = [0,0]
                        myproj = Projectile(playerPos,30,5,spell,new_vel)
                        projectiles.append(myproj)
                    stack.clear()
            
        for enemy in enemies:
            enemy.update()
        for projectile in projectiles:
            projectile.update()

    if playerHealth <=0:
        print("GAME OVER")
        exit()

        
    pyg.display.flip()
    fpsClock.tick(fps)