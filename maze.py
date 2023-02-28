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
#Any number > 341 crashes the programm because the goalimg is being scaled to fit a tile. When the gridsize is bigger than 256, the tilewidth becomes negative, because its tiles-4
#The image gets scaled with the int value of tilewidth, so everything up to -0.99 gets rounded up to 0. At 342, the tile width is smaller than -1, so it rounds up to -1 and crashes.
gridsize = 32

matrix = [[0 for x in range(gridsize)] for y in range(gridsize)] 
#Blockids: 0->nothing, 1-> wall, 2-> start, 3-> goal

#width and height of a single tile, including the 2px border on each side
tiles = 1024 / gridsize
#width and height of a single tile, minus the 2px border on each side. 2 sides, so 2px + 2px = 4px
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
savebutton = Button(saveimg, 1024, 64)

loadimg = pygame.transform.scale(pygame.image.load("load.png"), (64,64))
loadbutton = Button(loadimg, 1024, 128)

goalimg = pygame.image.load("goal.png")
grid_goalimg = pygame.transform.scale(goalimg, (int(tilewidth),int(tilewidth)))
menu_goalimg = pygame.transform.scale(goalimg, (64,64))
goalbutton = Button(menu_goalimg, 1024, 960)

startimg = pygame.transform.scale(pygame.image.load("start.png"), (64,64))
startbutton = Button(startimg, 1024, 896)

wallimg = pygame.transform.scale(pygame.image.load("wall.png"), (64,64))
wallbutton = Button(wallimg, 1024, 832)

trashimg = pygame.transform.scale(pygame.image.load("trash.png"), (64,64))
trashbutton = Button(trashimg, 1024,192)

playimg = pygame.transform.scale(pygame.image.load("play.png"), (64,64))
playbutton = Button(playimg, 1024, 64)

playmodeimg = pygame.transform.scale(pygame.image.load("playmode.png"), (64,64))
playmodebutton = Button(playmodeimg,1024, 0)

editmodeimg = pygame.transform.scale(pygame.image.load("editmode.png"), (64,64))
editmodebutton = Button(editmodeimg,1024, 0)

def get_neighbors(s):
    #will never happen, since start and goal dont fit in one tile
    if gridsize == 1:
        return []

    #left edge
    elif s[0] == 0:
        #left upper corner
        if s[1] == 0:
            return [(1,0),(0,1)]
        #left lower corner
        elif s[1] == (gridsize - 1):
            return [(0,gridsize-2), (1,gridsize-1)]
        #left edge
        else:
            return [(0,s[1]-1),(1,s[1]),(0,s[1]+1)]
    
    #right edge
    elif s[0] == (gridsize -1):
        #right upper corner
        if s[1] == 0:
            return [(gridsize-1,1),(gridsize-2,0)]
        #right lower corner
        elif s[1] == (gridsize - 1):
            return [(gridsize-1,gridsize-2), (gridsize-2,gridsize-1)]
        #right edge
        else:
            return [(gridsize-1,s[1]-1),(gridsize-1,s[1]+1),(gridsize-2,s[1])]

    #upper edge (corner already covered)
    elif s[1] == 0:
        return [(s[0]+1,0),(s[0],1),(s[0]-1,0)]

    #lower edge
    elif s[1] == (gridsize -1):
        return [(s[0], gridsize -2),(s[0]+1,gridsize-1),(s[0]-1,gridsize-1)]
    
    #middle tile
    else:
        return [(s[0],s[1]-1),(s[0]+1,s[1]),(s[0],s[1]+1),(s[0]-1,s[1])]

def dfs(visited_tiles,s,g,path):
    #s = (x,y)
    
    visited_tiles.append(s)
    if s == g:
        path.append(s)
        return
    
    #linker rand
    if s[0] == 0:
        #linke obere ecke
        if s[1] == 0:
            pass


    



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

def removestart():
    global startplaced, startlocation
    startplaced = False
    startlocation = [-1,-1]

def removegoal():
    global goalplaced, goallocation
    goalplaced = False
    goallocation = [-1,-1]

def cleargrid():
    global startplaced, goalplaced, startlocation, goallocation
    for x in range(gridsize):
        for y in range(gridsize):
            matrix[x][y] = 0
    removestart()
    removegoal()

def addblock(selected_tile, selected_block):
    global startplaced, goalplaced, startlocation, goallocation
    if selected_block == 1:
        if selected_tile == startlocation:
            removestart()
        elif selected_tile == goallocation:
            removegoal()
        matrix[selected_tile[0]][selected_tile[1]] = selected_block

    elif selected_block == 2:
        if selected_tile == goallocation:
            removegoal()
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
            removestart()
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
        removestart()
    elif selected_tile == goallocation:
        removegoal()
    matrix[selected_tile[0]][selected_tile[1]] = 0

def draw():
    #Background
    screen.fill(bgcolor)
    
    if gamemode == 0:
        playmodebutton.draw(screen)
        savebutton.draw(screen)
        loadbutton.draw(screen)
        goalbutton.draw(screen)
        startbutton.draw(screen)
        wallbutton.draw(screen)
        trashbutton.draw(screen)
    
    elif gamemode == 1:
        editmodebutton.draw(screen)
        playbutton.draw(screen)
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
                        pass

                    elif mousebutton == 3:
                        right_mouse_clicked = True
                        removewall(clicked_tile)

                #mouse on sidebar
                else:
                    if playmodebutton.rect.collidepoint(event.pos):
                        gamemode = 1

                    elif savebutton.rect.collidepoint(event.pos):
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


    #Algo mopde                    
    elif gamemode == 1:        
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
                        neighbors = get_neighbors(clicked_tile)
                        #If mouse doesnt move while clicking, MOUSEMOTION isnt triggerd. Thats why the matrix needs to be adjusted here
                        for neighbor in neighbors:
                            addblock(neighbor, 1)
                    
                #mouse on sidebar
                else:
                    if editmodebutton.rect.collidepoint(event.pos):
                        gamemode = 0

                    elif playbutton.rect.collidepoint(event.pos):
                        if startplaced and goalplaced:
                            print("OK")
                        else:
                            print("NO")
                  
    draw()	
    pygame.display.update()
    clock.tick(120)