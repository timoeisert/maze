import pygame
import sys
import math
import pickle
import copy
from collections import deque
import tkinter as tk
from tkinter import filedialog
import os
import heapq

from ctypes import windll
#0: window gets stretched on 1440p to be same size as 1080p
#1: window gets set to right 1440p size but doesnt change on 1080p, thus making it blurry there
#2: window is crisp on both 1440p and 1080p, which makes it relatively small on 1440p
windll.shcore.SetProcessDpiAwareness(2)


class Button:
	def __init__(self, image, xpos, ypos):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = xpos
		self.rect.y = ypos
	def set_pos(self,xpos,ypos):
		self.rect.x = xpos
		self.rect.y = ypos
	def draw(self,screen):
		screen.blit(self.image, self.rect)

	
class StateButton(Button):
	def __init__(self, image, xpos, ypos, state):
		super().__init__(image, xpos, ypos)
		#Pauseplaybutton states: 0 -> play, 1 -> pause, 2 -> replay
		#Speedbutton states:1
		#Pathlinebutton states: 0 -> no line, 1 -> line
		self.state = state
	def set_image(self, image):
		self.image = image	
	def set_state(self, state):
		self.state = state
	def get_state(self):
		return self.state


class Popup:
	def __init__(self,xpos,ypos,length,height,crossimg,active,displaytext,popid):
		self.rect = pygame.Rect(xpos,ypos,length,height)
		self.quitbutton = Button(crossimg,(xpos+length-32-2),(ypos+2))
		self.active = active
		self.topbox = pygame.Rect(self.rect.x,self.rect.y,self.rect.width,36)
		self.moving = False
		self.displaytext = displaytext
		self.popid = popid
	
	def activate(self):
		global any_popup_active
		
		self.active = True
		any_popup_active = True
	def deactivate(self):
		global any_popup_active
	
		self.active = False
		any_popup_active = False
	def get_rect(self):
		return self.rect
	def get_active(self):
		return self.active
	def get_quitbutton(self):
		return self.quitbutton
	def get_topbox(self):
		return self.topbox
	def get_popid(self):
		return self.popid
	def reset(self):
		self.rect.center = (512,512)
		self.quitbutton.set_pos((self.rect.x + self.rect.width - 34),(self.rect.y + 2))
		self.topbox.x =self.rect.x
		self.topbox.y = self.rect.y
	def set_moving(self,moving):
		self.moving = moving
	def get_moving(self):
		return self.moving
	def get_displaytext(self):
		return self.displaytext
	def update(self,xpos,ypos):
		
		self.rect.x+= xpos
		self.rect.y+= ypos
		
		if (self.rect.x > (1088 -10) or self.rect.y > (1024 - 10) or
			self.rect.x < (10-self.rect.width) or self.rect.y < (10- self.rect.height)):
			self.rect.center = (512,512)
			self.moving = False
			
		self.quitbutton.set_pos((self.rect.x + self.rect.width - 34),(self.rect.y + 2))
		self.topbox.x =self.rect.x
		self.topbox.y = self.rect.y
	def draw(self,screen):
		pygame.draw.rect(screen,(136,195,232),self.rect)
		pygame.draw.rect(screen,(82,138,174),self.topbox)
		self.quitbutton.draw(screen)
		
class PopupOneButton(Popup):
	def __init__(self,xpos,ypos,length,height,crossimg,active,displaytext,popid,okimg):
		super().__init__(xpos,ypos,length,height,crossimg,active,displaytext,popid)
		self.okbutton = Button(okimg,(xpos+length-110),(ypos+height-90))
		#padding: 2px on right border, 100px button1

	def get_okbutton(self):
		return self.okbutton	
	def reset(self):
		super().reset()
		
		self.okbutton.set_pos((self.rect.x+self.rect.width-110),(self.rect.y+self.rect.height-90))
		
	def update(self,xpos,ypos):
		super().update(xpos,ypos)
		
		self.okbutton.set_pos((self.rect.x+self.rect.width-110),(self.rect.y+self.rect.height-90))
		
	def draw(self,screen):
		super().draw(screen)
		self.okbutton.draw(screen)
	
class PopupButton(Popup):
	def __init__(self,xpos,ypos,length,height,crossimg,active,displaytext,popid,confirmimg,cancelimg):
		super().__init__(xpos,ypos,length,height,crossimg,active,displaytext,popid)	
		self.confirmbutton = Button(confirmimg,(xpos+length-162),(ypos+height-90))
		#padding: 2px on right border, 160px button1, 2px padding inbetween, 160px button2 ->324
		self.cancelbutton = Button(cancelimg,(xpos+length-324),(ypos+height-90))

	def get_confirmbutton(self):
		return self.confirmbutton
	def get_cancelbutton(self):
		return self.cancelbutton	
	def reset(self):
		super().reset()
		self.confirmbutton.set_pos((self.rect.x+self.rect.width-170),(self.rect.y+self.rect.height-90))
		self.cancelbutton.set_pos((self.rect.x+self.rect.width-340),(self.rect.y+self.rect.height-90))
		
	def update(self,xpos,ypos):
		super().update(xpos,ypos)
		self.confirmbutton.set_pos((self.rect.x+self.rect.width-170),(self.rect.y+self.rect.height-90))
		self.cancelbutton.set_pos((self.rect.x+self.rect.width-340),(self.rect.y+self.rect.height-90))
			
	def draw(self,screen):
		super().draw(screen)
		self.confirmbutton.draw(screen)
		self.cancelbutton.draw(screen)

class PopupGridSize(PopupButton):
	def __init__(self,xpos,ypos,length,height,crossimg,active,displaytext,popid,confirmimg,cancelimg,font_big):
		PopupButton.__init__(self,xpos,ypos,length,height,crossimg,active,displaytext,popid,confirmimg,cancelimg)	
		self.input_rect = pygame.Rect(self.rect.centerx - 60,ypos + 300,120,60)
		self.text_box_color = (100,0,0)
		self.text_surface = font_big.render(str(user_text),True,(255,255,255))
		self.text_box_active = False

	def reset(self): 
		PopupButton.reset(self)
		self.input_rect.x = self.rect.centerx - 60
		self.input_rect.y = self.rect.y + 300
	def update(self,xpos,ypos):
		PopupButton.update(self,xpos,ypos)
		self.input_rect.x = self.rect.centerx - 60
		self.input_rect.y = self.rect.y + 300

	def change_text(self, newtext):
		self.text_surface = font_big.render(str(newtext),True,(255,255,255))
		
	def draw(self,screen):
		PopupButton.draw(self,screen)
		pygame.draw.rect(screen,self.text_box_color,self.input_rect,2)
		screen.blit(self.text_surface,self.input_rect)

	def set_textboxcolor(self,color):
		self.text_box_color = color

	def get_text_box_active(self):
		return self.text_box_active
	
	def set_text_box_active(self,state):
		self.text_box_active = state
		
	def get_input_rect(self):
		return self.input_rect
	
	def deactivate(self):
		global user_text
		super().deactivate()
		self.change_text(user_text)	
	def activate(self):
		global user_text
		super().activate()
		
		self.change_text(user_text)	

class Node:
	def __init__(self,coordinates,parent):
		self.coordinates = coordinates
		self.parent = parent
	def get_parent(self):
		return self.parent
	def get_coords(self):
		return self.coordinates

class Timer:
	def __init__(self,intervaltime):
		self.intervaltime = intervaltime
		self.time = intervaltime
	def set_time(self,time):
		self.time = time
	def get_time(self):
		return self.time
	def subtract_time(self):
		self.time = self.time -1
	def set_intervaltime(self, intervaltime):
		self.intervaltime = intervaltime
	def get_intervaltime(self):
		return self.intervaltime



root = tk.Tk()
root.withdraw()
#dir_path = os.path.dirname(os.path.realpath(__file__))
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)



#print(application_path)
#General setup
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption("MAZE")
#1088 x 1024
screen =  pygame.display.set_mode([1024+64,1024])


#Level setup
bgcolor = (163,163,163)

#Height and width of the grid (Needs to be 2^x). Reccomended max:64 Working max:128
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
selected_algorithm = 0
left_mouse_clicked = False
right_mouse_clicked = False
middle_mouse_clicked = False

selected_block = 1

startplaced = False
startlocation = [-1,-1]
goalplaced = False
goallocation = [-1,-1]

goalpath = []
backupmatrix = [[0 for x in range(gridsize)] for y in range(gridsize)] 

#Line drawing variables
linestartcoords = None
lineendcoords = None
linecoords = []

#Grid size change text
user_text = str(gridsize)


#Text Renderer
text_font = pygame.font.SysFont("Arial",24)
font_big = pygame.font.SysFont("Arial",46)
text_cache = {}

def get_textmsg(msg, colour):
	if not msg in text_cache:
		text_cache[msg] = text_font.render(msg, True, colour)
	return text_cache[msg]

def draw_text(img, x, y):
	screen.blit(img, (x,y))


def blit_text(screen, text, popuprect, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    #plus padding of 10 on both sides
    x = popuprect[0] + 10
    y = popuprect[1] + 60
    #x coordinate + width of popup
    max_width = popuprect[2] + popuprect[0] - 10
    #max_height = surface.get_size()
   
    for line in words:
        for word in line:
            word_surface = font.render(word, 1, color)
            word_width, word_height = word_surface.get_size()
            word_height  += 10
            if x + word_width >= max_width:
                x = popuprect[0] +10  # Reset the x.
                y += word_height  # Start on new row.
            screen.blit(word_surface, (x, y))
            x += word_width + space
        x = popuprect[0] +10 # Reset the x.
        y += word_height  # Start on new row.

text = "This is a really long sentence with a couple of breaks.\nSometimes it will break even if there isn't a break " \
       "in the sentence, but that's because the text is too long to fit the screen.\nIt can look strange sometimes.\n" \
       "This function doesn't check if the text is too high to fit on the height of the surface though, so sometimes " \
       "text will disappear underneath the surface"






#Image Loader
playmodeimg = pygame.image.load("graphics/playmodev2.png")
playmodebutton = Button(playmodeimg,1024, 0)

helpimg = pygame.image.load("graphics/help.png")
buildhelpbutton = Button(helpimg, 1024,(1*64))
algohelpbutton = Button(helpimg,1024,(1*64))

saveimg = pygame.image.load("graphics/savev2.png")
savebutton = Button(saveimg, 1024, (3*64))

loadimg = pygame.image.load("graphics/load.png")
loadbutton = Button(loadimg, 1024, (4*64))

trashimg = pygame.image.load("graphics/trash.png")
trashbutton = Button(trashimg, 1024, (5*64))

sizeimg = pygame.image.load("graphics/changesize.png")
sizebutton = Button(sizeimg, 1024, (6*64))

wallimg = pygame.transform.scale(pygame.image.load("graphics/wall.png"), (64,64))
wallbutton = Button(wallimg, 1024, 832)

startimg = pygame.transform.scale(pygame.image.load("graphics/start.png"), (64,64))
startbutton = Button(startimg, 1024, 896)

goalimg = pygame.image.load("graphics/goal.png")
grid_goalimg = pygame.transform.scale(goalimg, (int(tilewidth),int(tilewidth)))
menu_goalimg = pygame.transform.scale(goalimg, (64,64))
goalbutton = Button(menu_goalimg, 1024, 960)

editmodeimg = pygame.transform.scale(pygame.image.load("graphics/editmode.png"), (64,64))
editmodebutton = Button(editmodeimg,1024, 0)

crossimg = pygame.transform.scale(pygame.image.load("graphics/cross.png"),(32,32))
confirmimg = pygame.image.load("graphics/continue.png")
cancelimg = pygame.image.load("graphics/cancel.png")
okimg = pygame.image.load("graphics/ok.png")
clear_matrix_popup = PopupButton(512,128,500,300,crossimg,False,"clear_grid","clear_matrix_popup",confirmimg,cancelimg)
clear_matrix_popup.reset()
build_help_popup = PopupOneButton(512,128,600,700,crossimg,False,"build_help","build_help_popup",okimg)
build_help_popup.reset()
algo_help_popup = PopupOneButton(512,128,600,700,crossimg,False,"algo_help","algo_help_popup",okimg)
algo_help_popup.reset()
start_goal_placed_popup = PopupOneButton(512,128,500,300,crossimg,False,"startgoal_placed","start_goal_placed_popup",okimg)
start_goal_placed_popup.reset()
matrix_wrong_size_popup = PopupButton(512,128,600,500,crossimg,False,"wrong_size","wrong_size_popup",confirmimg,cancelimg)
matrix_wrong_size_popup.reset()
change_gridsize_popup = PopupGridSize(512,128,600,500,crossimg,False,"change_size","change_size_popup",confirmimg,cancelimg,font_big)
change_gridsize_popup.reset()

popuplist = [build_help_popup,algo_help_popup,clear_matrix_popup,start_goal_placed_popup,matrix_wrong_size_popup,change_gridsize_popup]







skipimg = pygame.image.load("graphics/skip.png")
skipbutton = Button(skipimg,1024,(4*64))
goimg = pygame.image.load("graphics/go.png")
pauseimg = pygame.image.load("graphics/pause.png")
resetimg = pygame.image.load("graphics/reset.png")
gopausebutton = StateButton(goimg, 1024,(6*64),0)

stopimg = pygame.image.load("graphics/stop.png")
stopbutton = Button(stopimg,1024,(7*64))

goalpathlineonimg = pygame.image.load("graphics/goalpathlineon.png")
goalpathlineoffimg = pygame.image.load("graphics/goalpathlineoff.png")
goalpathlinebutton  = StateButton(goalpathlineonimg,1024,(7*64),1)

speed0img = pygame.image.load("graphics/speed0.png")
speed1img = pygame.image.load("graphics/speed1.png")
speed2img = pygame.image.load("graphics/speed2.png")
speed3img = pygame.image.load("graphics/speed3.png")
speedimgs = [speed0img,speed1img,speed2img,speed3img]
speedbutton = StateButton(speed1img,1024,(5*64),1)

dfsimg = pygame.image.load("graphics/dfs.png")
dfsbutton = Button(dfsimg, 1024,(12*64))

bfsimg = pygame.image.load("graphics/bfs.png")
bfsbutton = Button(bfsimg,1024,(13*64))

dijkstraimg = pygame.image.load("graphics/dijkstra.png")
dijkstrabutton = Button(dijkstraimg,1024,(14*64))

linetempimg = pygame.image.load("graphics/linetemp.png").convert_alpha()
grid_linetemp = pygame.transform.scale(linetempimg, (int(tilewidth),int(tilewidth)))
speedtimes = [80,30,5,1]
algotimer = Timer(speedtimes[1])

loaded_matrix = None
stack_global = []
queue_global = deque()
visited_tiles_global = {}
goal_found = False
visited_matrix_global = [[False for x in range(gridsize)] for y in range(gridsize)] 
drawgoalpathline = True

#Dijkstra/A*
#[Cost (Uses one million instead of inf just because),Distance from goal (Heuristic, hast to be calculated)]
dijkastarmatrix = [[[1000000,0] for x in range(gridsize)] for y in range(gridsize)] 
dijkastarheap = []
heapq.heapify(dijkastarheap)

all_text = {
	"clear_grid":"Do you really want to \nclear the grid?\nThis action cannot be undone!",
	"build_help":"Hier steht irgendwann mal eine Anleitung zum Programm. Bleibt gespannt!!!!!",
	"algo_help":"Hier steht irgendwann mal eine Anleitung zum Algostuff. Bleibt gespannt!!!!!",
	"startgoal_placed":"You need to place the start tile and the goal tile before you can switch into algo-mode!",
	"wrong_size":"The level you loaded doesn't match the size of the grid. Parts of the level might be cropped out. Do you want to continue?",
	"change_size":"Change size placeholder"
}







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
	
	tileneighbors = get_neighbors(s)
	#print(tileneighbors)
	for neighbor in tileneighbors:
		if matrix[neighbor[0]][neighbor[1]] != 1 and neighbor not in visited_tiles:
			if g not in path:
				dfs(visited_tiles,neighbor,g,path)

		if neighbor in path:
			path.append(s)
			return visited_tiles    

	
def iterative_dfs2(s,g):
	stack = []
	visited_tiles = {}

	stack.append((s,None))

	while stack:
		v = stack.pop(-1)
		visited_tiles[v[0]] = v[1]

		if v[0] == g:
			
			return visited_tiles, True
		
		#List of tuples (x,y) of coordinates
		tileneighbors = get_neighbors(v[0])
		tileneighbors.reverse()
		#Iterates through each neighbor
		for neighbor in tileneighbors:
			if matrix[neighbor[0]][neighbor[1]] != 1:
				if not neighbor in visited_tiles.keys():
					stack.append((neighbor,v[0]))
	
	return visited_tiles, False

def iterative_dfs(visited_tiles,s,g):
	stack = []

	stack.append(Node(s,None))
	
	while stack:
		
		v = stack.pop(-1)
		visited_tiles.append(v)

		if v.get_coords() == g:
			
			return visited_tiles, True
		
		tileneighbors = get_neighbors(v.get_coords())
		tileneighbors.reverse()
		for neighbor in tileneighbors:
			if matrix[neighbor[0]][neighbor[1]] != 1:
				if not neighbor in list(tiles.get_coords() for tiles in visited_tiles):
					stack.append(Node(neighbor,v))
	
	
	return visited_tiles, False
	"""
	print("before",stack)

	v = stack.pop(-1)
	print("after",stack)
	visited_tiles.append(v)
	tileneighbors = get_neighbors(v[0])
	print(tileneighbors)
	for neighbor in tileneighbors:
		if matrix[neighbor[0]][neighbor[1]] != 1:
			if not neighbor in list(tiles[0] for tiles in visited_tiles):
				stack.append([neighbor,v[0]])
	
	print("stack",stack)

	v = stack.pop(-1)
	print("after",stack)
	visited_tiles.append(v)
	tileneighbors = get_neighbors(v[0])
	print(tileneighbors)
	for neighbor in tileneighbors:
		if matrix[neighbor[0]][neighbor[1]] != 1:
			if not neighbor in list(tiles[0] for tiles in visited_tiles):
				stack.append([neighbor,v[0]])

	print("stackend",stack)      
	return visited_tiles
	"""
	"""
	while stack:
		print(stack)
		v = stack.pop(-1)
		visited_tiles.append(v)

		#if goal is found, return visited_tiles
		if v[0] == g:
			return visited_tiles
		
		#iterates through all neighbors who arent a wall and arent visited yet
		tileneighbors = get_neighbors(v[0])
		for neighbor in tileneighbors:
			if matrix[neighbor[0]][neighbor[1]] != 1:
				if not any(neighbor in tiles[0] for tiles in visited_tiles):
					stack.append([neighbor,v[0]])
					
			"""


def dfs_step(stack,visited_tiles,visited_matrix,g):
	#return: stacl, visited_tiles, visited_matrix, algo_finished, goal found, new_visited, new_stack 
	new_on_stack = []
	if stack:
		
		#Takes nodes off the stack until an unvisited node is found. Without this, the porgram sometimes appears to do nothing,
		#Because the node on top of stack has already been visited (loop) and the program needs to wait until the next step to try again
		while True:
			if stack:
				v = stack.pop(-1)
	
				if not (visited_matrix[v[0][0]][v[0][1]]):
					break
			else:
				return stack, visited_tiles,visited_matrix, True,False, None, []
		
		
		#If vertex has not been visited yet (vertecies can be added to stack more than once)
		
		#Adding to visited_tiles should only be O(1)
		visited_tiles[v[0]] = v[1]
		visited_matrix[v[0][0]][v[0][1]] = True
		if v[0] == g:
		
			return stack, visited_tiles,visited_matrix, True,True, v[0], new_on_stack
		#List of tuples (x,y) of coordinates
		tileneighbors = get_neighbors(v[0])
		tileneighbors.reverse()
		#Iterates through each neighbor
		for neighbor in tileneighbors:
			if matrix[neighbor[0]][neighbor[1]] != 1:
				if not visited_matrix[neighbor[0]][neighbor[1]]:
					new_on_stack.append(neighbor)
					stack.append((neighbor,v[0]))

		return stack, visited_tiles, visited_matrix, False,False, v[0], new_on_stack
	else:
		return stack, visited_tiles, visited_matrix, True,False, None, []
	
def bfs_step(queue,visited_tiles,visited_matrix,g):
	#return: queue, visited_tiles, visited_matrix, algo_finished, goal found, new_visited, new_queue 
	new_on_queue = []
	if queue:
		while True:
			if queue:
				v = queue.popleft()
				
				if not (visited_matrix[v[0][0]][v[0][1]]):
					break
			else:
				return queue, visited_tiles, visited_matrix, True, False, None, []
		visited_tiles[v[0]] = v[1]
		visited_matrix[v[0][0]][v[0][1]] = True
		if v[0] == g:
			return queue, visited_tiles, visited_matrix, True, True, v[0], new_on_queue
		
		tileneighbors = get_neighbors(v[0])
		#No need to reverse because in queue the first object is retrieved first aswell
		for neighbor in tileneighbors:
			if matrix[neighbor[0]][neighbor[1]] != 1:
				if not visited_matrix[neighbor[0]][neighbor[1]]:
					new_on_queue.append(neighbor)
					queue.append((neighbor,v[0]))
					
		return queue, visited_tiles, visited_matrix, False, False, v[0], new_on_queue
	else:
		return queue, visited_tiles, visited_matrix, True, False, None, []

def dijkstra_step(g):
	#return algofinished, new_queue, new_visited, goalfound
	global dijkastarheap, dijkastarmatrix, visited_matrix_global, visited_tiles_global
	if dijkastarheap:
		new_on_queue = []
		#A tile is added to queue. Later, a better path to tile is found. The first path doesn't get removed,
		#so the tile is in queue twice now. The better path gets popped first, so the second one can be dropped.
		while True:
			if dijkastarheap:
				smallestentry = heapq.heappop(dijkastarheap)
		
				currentcost , v = smallestentry
		
				#If this node has already been updated
				if not visited_matrix_global[v[0]][v[1]]:
					break
			else:
				return False, [], None, False
		visited_matrix_global[v[0]][v[1]] = True
		#If current node is end node
		if v == g:
			return True, [], None, True
		tileneighbors = get_neighbors(v)
		
		for neighbor in tileneighbors:
			if matrix[neighbor[0]][neighbor[1]] != 1:
				if not visited_matrix_global[neighbor[0]][neighbor[1]]:
					newcost = currentcost + 1
					if newcost < dijkastarmatrix[neighbor[0]][neighbor[1]][0]:
						dijkastarmatrix[neighbor[0]][neighbor[1]][0] = newcost
						heapq.heappush(dijkastarheap, (newcost,neighbor))
						new_on_queue.append(neighbor)
						#parent of new found tile is v
						visited_tiles_global[neighbor] = v
		
		
		return False, new_on_queue, v, False
				
	else:
		return True, [], None, False
		

		

#bfs and dfs
def algorunfs(algo_started, algo_finished, selected_algorithm,visited_tiles,visited_matrix,startlocation,goallocation):
	global queue_global, stack_global, goal_found
	if selected_algorithm == 0:
		
		if not algo_finished:
			if algo_started == False:
				stack_global.append((startlocation,None))
				algo_started = True
			stack_global, visited_tiles,visited_matrix, algo_finished,goal_found, new_visited, new_stack = dfs_step(stack_global,visited_tiles,visited_matrix,goallocation)

			if new_stack:
				for stacktile in new_stack:
					addblock(stacktile,5)
					
				#addblock(new_stack[-1],6)
				

			if new_visited:
				addblock(new_visited, 4)
			
	elif selected_algorithm == 1:
		
		if not algo_finished:
			if algo_started == False:
				queue_global.append((startlocation,None))
				algo_started = True
			queue_global, visited_tiles, visited_matrix, algo_finished, goal_found, new_visited, new_queue = bfs_step(queue_global,visited_tiles,visited_matrix,goallocation)
			
			if new_queue:
				for queuetile in new_queue:
					addblock(queuetile,5)
				#Colouring the tile that will be visited next is not straigthforward, because already visited tiles might be in the queue.
				#This might be a problem in dfs alwell so i wont colour them at all for now. Only possibility is in O(n)
				#addblock(queue_global[0][0],6)
			
			if new_visited:
				addblock(new_visited, 4)
		#print(goal_found)				
	return algo_started, algo_finished, visited_tiles, visited_matrix

#dijkstra and a*
def algorunda(algo_started, algo_finished, goallocation):
	
	global dijkastarheap, goal_found
	if selected_algorithm == 2:
		if not algo_finished:
			if algo_started == False:
				heapq.heappush(dijkastarheap,(0,startlocation))
				algo_started = True
			algo_finished, new_queue, new_visited, goal_found = dijkstra_step(goallocation)
			if new_queue:
				for stacktile in new_queue:
					addblock(stacktile,5)

			if new_visited:
				addblock(new_visited, 4)
						
	elif selected_algorithm == 3:
		pass

	return algo_started, algo_finished

def draw_algo_path(g,visited_tiles):
	global goalpath
	goalpath = []
	#Tuple of coordinates(x,y)
	currentnode = g
	while True:
		if visited_tiles.get(currentnode) == None:
			goalpath.append(currentnode)
			break
		
		goalpath.append(currentnode)
		currentnode = visited_tiles.get(currentnode)

	for tile in goalpath:
		addblock(tile,6)





#TODO Laoding a saved 16x16 grid on a 32x32 grid crashes the game because the matrix is too small. Can be fixed by saving specific sizes
def save_current_level():
	file_path = None
	file_path = filedialog.asksaveasfilename(filetypes=[('level',".pickle")],defaultextension=".pickle")
	if file_path:
		pickle_out = open(file_path,"wb")
		pickle.dump(matrix, pickle_out)
		pickle_out.close()

def load_saved_level():
	#Old implementation
	"""
	pickle_in = open("matrix.pickle", "rb")
	matrix = pickle.load(pickle_in)
	pickle_in.close()
	return matrix
	"""
	
	file_path = None
	file_path = filedialog.askopenfilename(initialdir=f"{application_path}\level",
				filetypes=[("level",".pickle")])

	if file_path:
	
		pickle_in = open(file_path, "rb")
		matrix = pickle.load(pickle_in)
		pickle_in.close()
		return matrix, len(matrix[0])	
	else:
		return None, None
def wrong_size_matrix(new_matrix):
	global matrix, gridsize
	
	removestart()
	removegoal()
	gridsize = len(new_matrix[0])
	matrix = copy.deepcopy(new_matrix)
	#If loaded matrix is smaller than set gridsize

	find_goal_start()

def change_matrix_size(oldgridsize):
	global matrix
	
	oldmatrix = copy.deepcopy(matrix)
	matrix = [[0 for x in range(gridsize)] for y in range(gridsize)] 
	
	removestart()
	removegoal()
			

	if gridsize < oldgridsize:
		for x in range(gridsize):
			for y in range(gridsize):
				matrix[x][y] = oldmatrix[x][y]
	
	elif gridsize > oldgridsize:
		for x in range(oldgridsize):
			for y in range(oldgridsize):
				matrix[x][y] = oldmatrix[x][y]
	
	find_goal_start()

def update_gridstuff():
	global tiles, tilewidth, gridsize, grid_goalimg, goalimg, visited_matrix_global, dijkastarmatrix, grid_linetemp, linetempimg,user_text
		#width and height of a single tile, including the 2px border on each side
	tiles = 1024 / gridsize
	#width and height of a single tile, minus the 2px border on each side. 2 sides, so 2px + 2px = 4px
	tilewidth = tiles - 4
	visited_matrix_global = [[False for x in range(gridsize)] for y in range(gridsize)] 
	dijkastarmatrix = [[[1000000,0] for x in range(gridsize)] for y in range(gridsize)] 
	grid_goalimg = pygame.transform.scale(goalimg, (int(tilewidth),int(tilewidth)))
	grid_linetemp = pygame.transform.scale(linetempimg, (int(tilewidth),int(tilewidth)))
	user_text = str(gridsize)
def find_goal_start():
	global startplaced, startlocation, goalplaced, goallocation 			
	for x in range(gridsize):
		for y in range(gridsize):
			if matrix[x][y] == 2:
				startplaced = True
				startlocation = (x,y)
			elif matrix[x][y] == 3:
				goalplaced = True
				goallocation = (x,y)
					
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

	elif selected_block == 4:
		if not (selected_tile == goallocation) and not (selected_tile == startlocation):
			matrix[selected_tile[0]][selected_tile[1]] = selected_block

	elif selected_block == 5:
		if not (selected_tile == goallocation) and not (selected_tile == startlocation):
			matrix[selected_tile[0]][selected_tile[1]] = selected_block        

	elif selected_block == 6:
		if not (selected_tile == goallocation) and not (selected_tile == startlocation):
			matrix[selected_tile[0]][selected_tile[1]] = selected_block        

def removewall(selected_tile):
	global startplaced, goalplaced, startlocation, goallocation
	if selected_tile == startlocation:
		removestart()
	elif selected_tile == goallocation:
		removegoal()
	matrix[selected_tile[0]][selected_tile[1]] = 0





def drawselectionbox(selected):
#This function draws a selction box around the currently selected building block/ algorithm
#The param selected is an integer that indicates how many squares the box has to go up from the bottom
#selected = 1 -> Box around lowest button, 2 -> Box around second lowest button...
	#Upper bar
	pygame.draw.rect(screen, (210,210,210), (1024,1024-(selected*64),64,3))
	#Lower bar
	pygame.draw.rect(screen, (210,210,210), (1024,1024-((selected-1)*64)-3,64,3))
	#Left bar
	pygame.draw.rect(screen, (210,210,210), (1024,1024-(selected*64),3,64))

	pygame.draw.rect(screen, (210,210,210), (1085,1024-(selected*64),3,64))


def naiveline(point1,point2):
	plottedcoords = []
	#calculate linear function, line between point 1 and 2
	#y = mx + b, m = (y2-y1)/(x2-x1)
	x1, y1 = point1
	x2, y2 = point2
	rise = y2 - y1
	run = x2 - x1
	
	#x doesnt change -> slope infinite, vertical line
	if run == 0:
		#Make sure that y2 is larger than y1
		if y2 < y1:
			y1, y2 = (y2, y1)
		for y in range(y1, y2+1):
			plottedcoords.append((x1,y))
	else:
		#calculate slope
		m = rise / run	
		#calculate b (y1 = mx1 +b -> y1 - mx1 = b) y intercept
		b = y1 - m * x1
		#line more horizontal than vertical m=0 included
		if (m<=1 and m >= -1):
			if x2 < x1:
				x1, x2 = (x2, x1)
			for x in range(x1, x2 + 1):
				#y = m*x+b
				y = int(round(m * x + b))
				plottedcoords.append((x, y))
		#line more vertical than horizontal
		else:
			if y2 < y1:
				y1, y2 = (y2, y1)
			for y in range(y1, y2 +1):
				#x = (y-b)/m
				x = int(round((y-b)/m))
				plottedcoords.append((x,y))

	return plottedcoords		

#DRAW FUNTION
def reset_algo(visited_tiles,stack,visited_matrix_global,algostarted,algopaused,algofinished):
	global queue_global, goal_found, dijkastarmatrix, dijkastarheap
	goal_found = False
	queue_global = deque()
	visited_tiles = {}
	stack = []
	visited_matrix_global = [[False for x in range(gridsize)] for y in range(gridsize)] 
	dijkastarmatrix = [[[1000000,0] for x in range(gridsize)] for y in range(gridsize)] 
	dijkastarmatrix[startlocation[0]][startlocation[1]][0] = 0
	#This shouldn't be needed since the heuristic is never changed
	"""							
	for i in range(gridsize):
		for j in range(gridsize):
			x1, y1 = goallocation
			x2, y2 = i, j
			distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 )
			dijkastarmatrix[i][j][1] = distance
			
	"""
	dijkastarheap = []
	algostarted = False
	algopaused = False
	algofinished = False
	algotimer.set_time(algotimer.get_intervaltime())
	return visited_tiles,stack,visited_matrix_global,algostarted,algopaused,algofinished

def reset_playmode():
	gopausebutton.set_state(0)
	gopausebutton.set_image(goimg)
	
	currentspeed = 1
	speedbutton.set_state(currentspeed)
	speedbutton.set_image(speedimgs[currentspeed])
	algotimer.set_intervaltime(speedtimes[currentspeed])

def reset_line():
	global linecoords,linestartcoords,lineendcoords, middle_mouse_clicked
	linecoords = []
	linestartcoords = None
	lineendcoords = None
	middle_mouse_clicked = False
	
def draw():
	#Background
	screen.fill(bgcolor)
	
	if gamemode == 0:
		playmodebutton.draw(screen)
		buildhelpbutton.draw(screen)
		savebutton.draw(screen)
		loadbutton.draw(screen)
		goalbutton.draw(screen)
		startbutton.draw(screen)
		wallbutton.draw(screen)
		trashbutton.draw(screen)
		sizebutton.draw(screen)
		#
		drawselectionbox(4-selected_block)
		
		
	elif gamemode == 1:
		editmodebutton.draw(screen)
		algohelpbutton.draw(screen)
		speedbutton.draw(screen)
		gopausebutton.draw(screen)
		if not algo_finished:
			skipbutton.draw(screen)
		if algo_started:
			stopbutton.draw(screen)
		else:

			if goal_found:
				goalpathlinebutton.draw(screen)			

			dfsbutton.draw(screen)
			bfsbutton.draw(screen)
			dijkstrabutton.draw(screen)
			
			drawselectionbox(4-selected_algorithm)
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
			
			elif matrix[x][y] == 4:
				pygame.draw.rect(screen, (0,100,0), ((2 + tilewidth*x + 4*x),(2 + tilewidth*y + 4*y),tilewidth,tilewidth))
			
			elif matrix[x][y] == 5:
				pygame.draw.rect(screen, (0,200,0), ((2 + tilewidth*x + 4*x),(2 + tilewidth*y + 4*y),tilewidth,tilewidth))
			
			elif matrix[x][y] == 6:
				pygame.draw.rect(screen, (255,216,0), ((2 + tilewidth*x + 4*x),(2 + tilewidth*y + 4*y),tilewidth,tilewidth))
	#drawing preview line:
	if middle_mouse_clicked:
		for coords in linecoords:
			x, y = coords
			
			screen.blit(grid_linetemp, [(2 + tilewidth*x + 4*x),(2 + tilewidth*y + 4*y)])	

	#textimg = get_textmsg("This is the help bar\nSo is this",(100,0,0))
	#print(textimg.get_rect())
	#draw_text(textimg,500,500)	
	if goal_found and drawgoalpathline:
		for i in range(len(goalpath)-1):
			starttile = goalpath[i]
			endtile = goalpath[i+1]
			spos = [int(starttile[0]*tiles + (tiles / 2)), int(starttile[1] * tiles + (tiles / 2))]
			epos = [int(endtile[0]*tiles + (tiles / 2)), int(endtile[1] * tiles + (tiles / 2))]
			pygame.draw.line(screen,(0,0,0),spos,epos,4)
	
	for popup in popuplist:
		if popup.get_active():
			popup.draw(screen)
			popuptext = all_text[popup.get_displaytext()]
			blit_text(screen, popuptext, popup.get_rect(), font_big)
	
		












okbuttonlist = ["start_goal_placed_popup","build_help_popup","algo_help_popup"]
any_popup_active = False
currently_selected_popup = None
moving = False
algo_started = False
algo_finished = False
algo_paused = False
#GAME LOOP

go = True
while go:
	
	if any_popup_active:
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			
			if event.type == pygame.MOUSEBUTTONDOWN:	
				mousepos = event.pos
				mousebutton = event.button
				
				if mousebutton == 1:
					for popup in popuplist:
						if popup.get_active():
							selectedpopupid = popup.get_popid()
							#Bonus actions for ButtonPopup
							if selectedpopupid == "clear_matrix_popup":
								if popup.get_confirmbutton().rect.collidepoint(event.pos):
									cleargrid()
									popup.deactivate()
									popup.reset()
								elif popup.get_cancelbutton().rect.collidepoint(event.pos):
									popup.deactivate()
									popup.reset()
							if selectedpopupid == "wrong_size_popup":
								if popup.get_confirmbutton().rect.collidepoint(event.pos):
									wrong_size_matrix(loaded_matrix)
									update_gridstuff()
									popup.deactivate()
									popup.reset()
								elif popup.get_cancelbutton().rect.collidepoint(event.pos):
									popup.deactivate()
									popup.reset()	
									
							if selectedpopupid == "change_size_popup":
								if popup.get_confirmbutton().rect.collidepoint(event.pos):
									#if new gridsize is valid:
									#Not empty
									if user_text:
										#Working number
										if int(user_text) > 0 and int(user_text) <= 300:
											#old gridsize:
											oldgridsize = gridsize
											gridsize = int(user_text)
											change_matrix_size(oldgridsize)
											update_gridstuff()
											popup.deactivate()
											popup.reset()

									#else:
								
								elif popup.get_cancelbutton().rect.collidepoint(event.pos):
									user_text = str(gridsize)
									popup.deactivate()
									popup.reset()		
								
								elif popup.get_quitbutton().rect.collidepoint(event.pos):
									user_text = str(gridsize)
									popup.deactivate()
									popup.reset()
									
								if popup.get_input_rect().collidepoint(event.pos):
									popup.set_text_box_active(True)
									popup.set_textboxcolor((255,0,0))
								else:
									popup.set_text_box_active(False)
									popup.set_textboxcolor((0,255,0))
									
							if selectedpopupid in okbuttonlist:
								if popup.get_okbutton().rect.collidepoint(event.pos):
									popup.deactivate()
									popup.reset()
							if popup.get_quitbutton().rect.collidepoint(event.pos):
								
								popup.deactivate()
								popup.reset()
								
								
							
							elif popup.get_topbox().collidepoint(event.pos):
								
								popup.set_moving(True)
								moving = True
								currently_selected_popup = popup
								
							"""
							elif popup.rect.collidepoint(event.pos):

								cleargrid()
								popup.deactivate()
								popup.reset()
							"""
			if event.type == pygame.MOUSEBUTTONUP and moving:
				currently_selected_popup.set_moving(False)
				moving = False
			
			if event.type == pygame.MOUSEMOTION and moving:
				
				currently_selected_popup.update(event.rel[0],event.rel[1])
			
			if event.type == pygame.KEYDOWN and change_gridsize_popup.get_active():
				if change_gridsize_popup.get_text_box_active():
					if event.key == pygame.K_BACKSPACE:
						user_text = user_text[:-1]
					else:
						if len(user_text) < 3 and event.unicode.isnumeric():
		
							user_text += event.unicode
							
					change_gridsize_popup.change_text(user_text)	
	else:					
		#Build mode

		if gamemode == 0:
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				
				if event.type == pygame.MOUSEBUTTONDOWN:	
					mousepos = event.pos
					mousebutton = event.button

					#Wenn popup nicht aktiv:
				
						#mouse on grid
					if mousepos[0] < 1024 and mousepos[1] < 1024:
					
						clicked_tile = (math.floor(mousepos[0]/tiles),math.floor(mousepos[1]/tiles))
						
						#left click
						if mousebutton == 1:
						
							
							left_mouse_clicked = True
							#If mouse doesnt move while clicking, MOUSEMOTION isnt triggerd. Thats why the matrix needs to be adjusted here
							addblock(clicked_tile, selected_block)
							
						elif mousebutton == 2:
							middle_mouse_clicked = True
							linestartcoords = clicked_tile
							lineendcoords = clicked_tile
							linecoords = naiveline(linestartcoords,lineendcoords)

						elif mousebutton == 3:
							right_mouse_clicked = True
							removewall(clicked_tile)

					#mouse on sidebar
					else:
						if mousebutton == 1:
							if playmodebutton.rect.collidepoint(event.pos):
								reset_line()
								if goalplaced and startplaced:
									
									backupmatrix = copy.deepcopy(matrix)
									gamemode = 1
									#initialize dijkstra and a* matrix:
									
									dijkastarmatrix[startlocation[0]][startlocation[1]][0] = 0
									
									for i in range(gridsize):
										for j in range(gridsize):
											x1, y1 = goallocation
											x2, y2 = i, j
											distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 )
											dijkastarmatrix[i][j][1] = distance
									
								else:
									start_goal_placed_popup.activate()

							elif buildhelpbutton.rect.collidepoint(event.pos):
								reset_line()
								build_help_popup.activate()
								
							elif savebutton.rect.collidepoint(event.pos):
								reset_line()
								save_current_level()
							elif loadbutton.rect.collidepoint(event.pos):
								reset_line()
								
								
								
								loaded_matrix, matrixsize = load_saved_level()
								if loaded_matrix:
									if matrixsize != gridsize:
										matrix_wrong_size_popup.activate()
									
									else:
										matrix = loaded_matrix
										find_goal_start()
								
							elif wallbutton.rect.collidepoint(event.pos):
								reset_line()
								selected_block = 1
							elif startbutton.rect.collidepoint(event.pos):
								reset_line()
								selected_block = 2
							elif goalbutton.rect.collidepoint(event.pos):
								reset_line()
								selected_block = 3
							elif trashbutton.rect.collidepoint(event.pos):#
								reset_line()
								clear_matrix_popup.activate()

							elif sizebutton.rect.collidepoint(event.pos):
								reset_line()
								change_gridsize_popup.activate()
							
				
					
				elif event.type == pygame.MOUSEBUTTONUP:	
					mousebutton = event.button
					clicked_tile = (math.floor(mousepos[0]/tiles),math.floor(mousepos[1]/tiles))
					#left click
					if mousebutton == 1:
						left_mouse_clicked = False
					
					elif mousebutton == 2 and middle_mouse_clicked:
						if mousepos[0] < 1024 and mousepos[1] < 1024:
							middle_mouse_clicked = False
							lineendcoords = clicked_tile
							linecoords = naiveline(linestartcoords,lineendcoords)
							for coords in linecoords:
								addblock(coords,1)
							linecoords = []
							linestartcoords = None
							lineendcoords = None					
						else:
							middle_mouse_clicked = False
							linecoords = []
							linestartcoords = None
							lineendcoords = None
					elif mousebutton == 3:
						right_mouse_clicked = False

				if event.type == pygame.MOUSEMOTION:
					mousepos = event.pos
					if mousepos[0] < 1024 and mousepos[1] < 1024:
				
						clicked_tile = (math.floor(mousepos[0]/tiles),math.floor(mousepos[1]/tiles))
					
						if left_mouse_clicked and selected_block == 1:
							addblock(clicked_tile,selected_block)  
						elif middle_mouse_clicked:
							#if mouse is not still on same end coords for line
							if not lineendcoords == clicked_tile:
								lineendcoords = clicked_tile
								linecoords = naiveline(linestartcoords,lineendcoords)
								
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
							pass
							"""
							Displays all neighboring tiles of clicked tile
							
							neighbors = get_neighbors(clicked_tile)
							#If mouse doesnt move while clicking, MOUSEMOTION isnt triggerd. Thats why the matrix needs to be adjusted here
							for neighbor in neighbors:
								addblock(neighbor, 1)
							"""
						
					#mouse on sidebar
					else:
						
						if mousebutton == 1:
							if editmodebutton.rect.collidepoint(event.pos):
								reset_playmode()
								visited_tiles_global,stack_global,visited_matrix_global,algo_started,algo_paused,algo_finished = reset_algo(
									visited_tiles_global,stack_global,visited_matrix_global,algo_started,algo_paused,algo_finished)
								matrix = copy.deepcopy(backupmatrix)
								gamemode = 0
								
							elif algohelpbutton.rect.collidepoint(event.pos):	
								algo_help_popup.activate()
								
							elif skipbutton.rect.collidepoint(event.pos) and not algo_finished:
								if not algo_started:
									if selected_algorithm == 0 or selected_algorithm == 1:
										algo_started, algo_finished, visited_tiles_global, visited_matrix_global = algorunfs(
												False,False,selected_algorithm,visited_tiles_global,visited_matrix_global,startlocation,goallocation)
									elif selected_algorithm == 2 or selected_algorithm == 3:
										algo_started, algo_finished = algorunda(False, False, goallocation)
								while not algo_finished:
									if selected_algorithm == 0 or selected_algorithm == 1:
										algo_started, algo_finished, visited_tiles_global, visited_matrix_global = algorunfs(
										algo_started,algo_finished,selected_algorithm,visited_tiles_global, visited_matrix_global, startlocation,goallocation)	
									elif selected_algorithm == 2 or selected_algorithm == 3:
										algo_started, algo_finished = algorunda(algo_started, algo_finished, goallocation)
								
							elif speedbutton.rect.collidepoint(event.pos):
								currentspeed = speedbutton.get_state()
								if currentspeed < 3:
									speedbutton.set_state(currentspeed + 1)
									speedbutton.set_image(speedimgs[currentspeed + 1])
									algotimer.set_intervaltime(speedtimes[currentspeed+1])
								else:
									currentspeed = 0
									speedbutton.set_state(currentspeed)
									speedbutton.set_image(speedimgs[currentspeed])
									algotimer.set_intervaltime(speedtimes[currentspeed])
									
							elif gopausebutton.rect.collidepoint(event.pos):
								if gopausebutton.get_state() == 0:
									gopausebutton.set_state(1)
									gopausebutton.set_image(pauseimg)
									#If algo is already running, but has been paused
									if algo_paused:
										algo_paused = False
									#If algo is being started for the first time
									else:
										algotimer.set_time(algotimer.get_intervaltime())
										if selected_algorithm == 0 or selected_algorithm == 1:
											algo_started, algo_finished, visited_tiles_global, visited_matrix_global = algorunfs(
												False,False,selected_algorithm,visited_tiles_global,visited_matrix_global,startlocation,goallocation)
										elif selected_algorithm == 2 or selected_algorithm == 3:
											algo_started, algo_finished = algorunda(False, False, goallocation)


								elif gopausebutton.get_state() == 1:
									gopausebutton.set_state(0)
									gopausebutton.set_image(goimg)
									algo_paused = True
									
								elif gopausebutton.get_state() == 2:
									visited_tiles_global,stack_global,visited_matrix_global,algo_started,algo_paused,algo_finished = reset_algo(
										visited_tiles_global,stack_global,visited_matrix_global,algo_started,algo_paused,algo_finished)
									matrix = copy.deepcopy(backupmatrix)
									gopausebutton.set_state(0)
									gopausebutton.set_image(goimg)
									
							elif stopbutton.rect.collidepoint(event.pos) and algo_started:
							
								visited_tiles_global,stack_global,visited_matrix_global,algo_started,algo_paused,algo_finished = reset_algo(
									visited_tiles_global,stack_global,visited_matrix_global,algo_started,algo_paused,algo_finished)
								matrix = copy.deepcopy(backupmatrix)
								gopausebutton.set_state(0)
								gopausebutton.set_image(goimg)			

							elif goalpathlinebutton.rect.collidepoint(event.pos) and not algo_started and goal_found:
								if goalpathlinebutton.get_state() == 0:
									goalpathlinebutton.set_state(1)
									goalpathlinebutton.set_image(goalpathlineonimg)
									drawgoalpathline = True
								
								elif goalpathlinebutton.get_state() == 1:
									goalpathlinebutton.set_state(0)
									goalpathlinebutton.set_image(goalpathlineoffimg)
									drawgoalpathline = False
							

							elif dfsbutton.rect.collidepoint(event.pos) and not algo_started:
								selected_algorithm = 0
							
							elif bfsbutton.rect.collidepoint(event.pos) and not algo_started:
								selected_algorithm = 1

							elif dijkstrabutton.rect.collidepoint(event.pos) and not algo_started:
								selected_algorithm = 2

							"""
							elif playbutton.rect.collidepoint(event.pos):
								if startplaced and goalplaced:
									if selected_algorithm == 0:
										path = []
										
										pathfound = False
										visited_tiles, pathfound =iterative_dfs2(startlocation,goallocation)
										if pathfound:
											#Tuple of coordinates(x,y)
											currentnode = goallocation
											while True:
												if visited_tiles.get(currentnode) == None:
													path.append(currentnode)
													break
												
												path.append(currentnode)
												currentnode = visited_tiles.get(currentnode)
											
										for visitedtile in visited_tiles.keys():
											addblock(visitedtile, 4)
										
										for foundtile in path:
											addblock(foundtile, 5)

									elif selected_algorithm == 1:
											
										visited_tiles = []
										foundpath = []
										visited_tiles = dfs(visited_tiles,startlocation,goallocation,foundpath)
										print(foundpath)
										print(visited_tiles)
										for visitedtile in visited_tiles:
											addblock(visitedtile, 4)
										for foundtile in foundpath:
											addblock(foundtile, 5)

									elif selected_algorithm == 2:
											
										path = []
										visited_tiles = []
										pathfound = False
										visited_tiles, pathfound = iterative_dfs(visited_tiles,startlocation,goallocation)
										if pathfound:
											currentnode = visited_tiles[-1]
											while True:
												if currentnode.get_parent() == None:
													path.append(currentnode.get_coords())
													break
												path.append(currentnode.get_coords())
												currentnode = currentnode.get_parent()

												

										
										
										for visitedtile in visited_tiles:
											addblock(visitedtile.get_coords(), 4)
										

										for foundtile in path:
											addblock(foundtile, 5)
									
									elif selected_algorithm == 3:
										if not finished:
											if algo_started == False:
												stack_global.append((startlocation,None))
												algo_started = True
												stack_global, visited_tiles_global, finished = dfs_step(stack_global,visited_tiles_global,goallocation)

											else:
												stack_global, visited_tiles_global, finished = dfs_step(stack_global,visited_tiles_global,goallocation)

											for visitedtile in visited_tiles_global.keys():
												addblock(visitedtile, 4)
										
								else:
									print("NO")
								"""	
			
			if algo_started and not algo_paused:
				if not algo_finished:
					intervaltime = algotimer.get_intervaltime()
					currenttime = algotimer.get_time()
					if currenttime == 0:
						
						if selected_algorithm == 0 or selected_algorithm == 1:
							algo_started, algo_finished, visited_tiles_global, visited_matrix_global = algorunfs(
								algo_started,algo_finished,selected_algorithm,visited_tiles_global, visited_matrix_global, startlocation,goallocation)	
						elif selected_algorithm == 2 or selected_algorithm == 3:
							algo_started, algo_finished = algorunda(algo_started, algo_finished, goallocation)
							
					#If timer > 0 subtract 1
					if currenttime > 0:
						algotimer.set_time(currenttime-1)
					
					#If timer is 0, reset to intervaltime
					else:
						algotimer.set_time(intervaltime)

				else:
					#If goal has been found:
					if goal_found:
						draw_algo_path(goallocation,visited_tiles_global)
					
					#If algo finished without finding goal	
					else:
						pass
					algo_started = False
					gopausebutton.set_state(2)
					gopausebutton.set_image(resetimg)
					#print(stack_global)
					#print(visited_tiles_global)
					stack_global = []
					visited_tiles_global = []
					visited_matrix_global = []
				
								
	draw()	
	
	pygame.display.update()
	clock.tick(120)