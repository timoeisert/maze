import pygame
import sys
import math


#General setup
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption("MAZE")
#1088 x 1024
screen =  pygame.display.set_mode([1024+64,1024])

#Level setup
bgcolor = (163,163,163)

#Height and width of the grid (Needs to be 2^x)
gridsize = 16
matrix = [[0 for x in range(gridsize)] for y in range(gridsize)] 

tiles = 1024 / gridsize
tilewidth = tiles - 4

print(matrix)




def draw():
    #Background
    screen.fill(bgcolor)
    pygame.draw.rect(screen, (109,162,255), (1024,0,4,1024))
    pygame.draw.rect(screen, (109,162,255), (1088-4,0,4,1024))
    
    #Level
    for x in range(gridsize):
        for y in range(gridsize):
            if matrix[x][y] == 0:
                pygame.draw.rect(screen, (210,210,210), ((2 + tilewidth*x + 4*x),(2 + tilewidth*y + 4*y),tilewidth,tilewidth))	
                #pygame.draw.rect(screen, (0,255,0), ((10 + 100*x + 10*x),(10 + 100*y + 10*y),100,100))	
        
            if matrix[x][y] == 1:
                pygame.draw.rect(screen, (255,0,0), ((2 + tilewidth*x + 4*x),(2 + tilewidth*y + 4*y),tilewidth,tilewidth))	


go = True
while go:	
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
                    matrix[clicked_tile[0]][clicked_tile[1]] = 1
                
                elif mousebutton == 3:
                    matrix[clicked_tile[0]][clicked_tile[1]] = 0

            #mouse on sidebar
            else:
                print("sidebar")
        
    draw()	
    pygame.display.update()
    clock.tick(120)