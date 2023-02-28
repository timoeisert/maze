import pygame
import sys
import math
import pickle

class Button:
	def __init__(self, image, xpos, ypos):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = xpos
		self.rect.y = ypos
	def draw(self,screen):
		screen.blit(self.image, self.rect)



#General setup
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption("MAZE")
#1088 x 1024
screen =  pygame.display.set_mode([1024+64,1024])


#Level setup
bgcolor = (163,163,163)

#Height and width of the grid (Needs to be 2^x). Reccomended max:64
gridsize = 16
matrix = [[0 for x in range(gridsize)] for y in range(gridsize)] 

tiles = 1024 / gridsize
tilewidth = tiles - 4

#0-> build mode, 1 -> pathfind mode
gamemode = 0
left_mouse_clicked = False
right_mouse_clicked = False

selected_block = 1

startplaced = False
startlocation = [-1,-1]
goalplaced = False
goallocation = [-1,-1]


#Image Loader
saveimg = pygame.transform.scale(pygame.image.load("save.png"), (64,64))
savebutton = Button(saveimg, 1024, 0)

loadimg = pygame.transform.scale(pygame.image.load("load.png"), (64,64))
loadbutton = Button(loadimg, 1024, 64)

goalimg = pygame.image.load("goal.png")
grid_goalimg = pygame.transform.scale(goalimg, (int(tilewidth),int(tilewidth)))
menu_goalimg = pygame.transform.scale(goalimg, (64,64))
goalbutton = Button(menu_goalimg, 1024, 960)

startimg = pygame.transform.scale(pygame.image.load("start.png"), (64,64))
startbutton = Button(startimg, 1024, 896)

wallimg = pygame.transform.scale(pygame.image.load("wall.png"), (64,64))
wallbutton = Button(wallimg, 1024, 832)

trashimg = pygame.transform.scale(pygame.image.load("trash.png"), (64,64))
trashbutton = Button(trashimg, 1024,128)


#TODO Laoding a saved 16x16 grid on a 32x32 grid crashes the game because the matrix is too small. Can be fixed by saving specific sizes
def save_current_level():
    pickle_out = open("matrix.pickle","wb")
    pickle.dump(matrix, pickle_out)
    pickle_out.close()

def load_saved_level():
    pickle_in = open("matrix.pickle", "rb")
    matrix = pickle.load(pickle_in)
    pickle_in.close()
    return matrix

def cleargrid():
    global startplaced, goalplaced, startlocation, goallocation
    for x in range(gridsize):
        for y in range(gridsize):
            matrix[x][y] = 0
    startplaced = False
    startlocation = [-1,-1]
    goalplaced = False
    goallocation = [-1,-1]
def addblock(selected_tile, selected_block):
    global startplaced, goalplaced, startlocation, goallocation
    if selected_block == 1:
        if selected_tile == startlocation:
            startplaced = False
            startlocation = [-1,-1]
        elif selected_tile == goallocation:
            goalplaced = False
            goallocation = [-1,-1]
        matrix[selected_tile[0]][selected_tile[1]] = selected_block

    elif selected_block == 2:
        if selected_tile == goallocation:
            goalplaced = False
            goallocation = [-1,-1]
        if startplaced:
            matrix[startlocation[0]][startlocation[1]] = 0
            matrix[selected_tile[0]][selected_tile[1]] = selected_block
            startlocation = selected_tile 
        else:
            startplaced = True
            matrix[selected_tile[0]][selected_tile[1]] = selected_block
            startlocation = selected_tile 

    elif selected_block == 3:
        if selected_tile == startlocation:
            startplaced = False
            startlocation = [-1,-1]
        if goalplaced:
            matrix[goallocation[0]][goallocation[1]] = 0
            matrix[selected_tile[0]][selected_tile[1]] = selected_block      
            goallocation = selected_tile
        else:
            goalplaced = True
            matrix[selected_tile[0]][selected_tile[1]] = selected_block
            goallocation = selected_tile

def removewall(selected_tile):
    global startplaced, goalplaced, startlocation, goallocation
    if selected_tile == startlocation:
        startplaced = False
        startlocation = [-1,-1]
    elif selected_tile == goallocation:
        goalplaced = False
        goallocation = [-1,-1]
    matrix[selected_tile[0]][selected_tile[1]] = 0

def draw():
    #Background
    screen.fill(bgcolor)
    
    if gamemode == 0:
        savebutton.draw(screen)
        loadbutton.draw(screen)
        goalbutton.draw(screen)
        startbutton.draw(screen)
        wallbutton.draw(screen)
        trashbutton.draw(screen)
    
    elif gamemode == 1:
        pass
    #pygame.draw.rect(screen, (109,162,255), (1024,0,4,1024))
    #pygame.draw.rect(screen, (109,162,255), (1088-4,0,4,1024))
    
    #Level
    for x in range(gridsize):
        for y in range(gridsize):
            
            #Empty
            if matrix[x][y] == 0:
                pygame.draw.rect(screen, (210,210,210), ((2 + tilewidth*x + 4*x),(2 + tilewidth*y + 4*y),tilewidth,tilewidth))	
                #pygame.draw.rect(screen, (0,255,0), ((10 + 100*x + 10*x),(10 + 100*y + 10*y),100,100))	


            #Wall
            elif matrix[x][y] == 1:
                pygame.draw.rect(screen, (161,77,58), ((2 + tilewidth*x + 4*x),(2 + tilewidth*y + 4*y),tilewidth,tilewidth))
            
            #Start
            elif matrix[x][y] == 2:
                pygame.draw.rect(screen, (82,138,174), ((2 + tilewidth*x + 4*x),(2 + tilewidth*y + 4*y),tilewidth,tilewidth))

            #Goal
            elif matrix[x][y] == 3:
                screen.blit(grid_goalimg, [(2 + tilewidth*x + 4*x),(2 + tilewidth*y + 4*y)])
                
                



go = True
while go:

    #Build mode
    if gamemode == 0:
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:	
                mousepos = event.pos
                mousebutton = event.button
                #mouse on grid
                if mousepos[0] < 1024 and mousepos[1] < 1024:
                
                    clicked_tile = (math.floor(mousepos[0]/tiles),math.floor(mousepos[1]/tiles))
                    
                    #left click
                    if mousebutton == 1:
                        left_mouse_clicked = True
                        #If mouse doesnt move while clicking, MOUSEMOTION isnt triggerd. Thats why the matrix needs to be adjusted here
                        addblock(clicked_tile, selected_block)
                    
                    elif mousebutton == 2:
                        matrix[clicked_tile[0]][clicked_tile[1]] = 3

                    elif mousebutton == 3:
                        right_mouse_clicked = True
                        removewall(clicked_tile)

                #mouse on sidebar
                else:
                    if savebutton.rect.collidepoint(event.pos):
                        save_current_level()
                    elif loadbutton.rect.collidepoint(event.pos):
                        matrix = load_saved_level()
                    elif wallbutton.rect.collidepoint(event.pos):
                        selected_block = 1
                    elif startbutton.rect.collidepoint(event.pos):
                        selected_block = 2
                    elif goalbutton.rect.collidepoint(event.pos):
                        selected_block = 3
                    elif trashbutton.rect.collidepoint(event.pos):
                        cleargrid()
            
            if event.type == pygame.MOUSEBUTTONUP:	
                mousebutton = event.button
                #left click
                if mousebutton == 1:
                    left_mouse_clicked = False
                    
                
                elif mousebutton == 3:
                    right_mouse_clicked = False

            if event.type == pygame.MOUSEMOTION:
                mousepos = event.pos
                if mousepos[0] < 1024 and mousepos[1] < 1024:
            
                    clicked_tile = (math.floor(mousepos[0]/tiles),math.floor(mousepos[1]/tiles))
                
                    if left_mouse_clicked and selected_block == 1:
                        addblock(clicked_tile,selected_block)  
                    elif right_mouse_clicked:
                        removewall(clicked_tile)  
                        
            
    
    draw()	
    pygame.display.update()
    clock.tick(120)