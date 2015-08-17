import time
import numpy.random as rand
import sys
import numpy
import math

from mpi4py import MPI
from mpi4py.MPI import ANY_SOURCE

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

in_end_pos = False
params = { 'screenSize':480, 'screenSizeY':640, 'plankSize':120, 'ballSize':10, 'timeStep':0.5 }
contraints = { 'xMin' : params['plankSize']/2, 'xMax' : params['screenSize'] - params['plankSize']/2, 
    'yMin' : params['ballSize']/2, 'yMax' : params['screenSize'] - params['ballSize']/2,
    'vMax' : 120, 'vMin': 80, 'angleMax': 0, 'angleMin': 0 }

state = { 'diff':0, 'xPlank': 240, 'xBall': 240, 'yBall': 0, 'v':0, 'angle':0 }
old_state = state.copy()
last_outcomes = [0]

def newState():
    global state, old_state

    rads = state['angle']*math.pi/180
    newY = state['yBall'] + state['v'] * math.cos(rads) * params['timeStep']
    newX = state['xBall'] + state['v'] * math.sin(rads) * params['timeStep']
    state['yBall'] = newY
    state['xBall'] = newX
    state['diff'] = state['xBall'] - state['xPlank']

def moveLeft():
    state['xPlank'] += 30

def moveLeftLong():
    state['xPlank'] += 50

def stay():
    pass

def moveRight():
    state['xPlank'] -= 30

def moveRightLong():
    state['xPlank'] -= 50

actionsAvailable = [moveLeftLong, moveLeft, stay, moveRight, moveRightLong]

def checkValid():
    global state
    if state['xPlank'] < contraints['xMin']:
        state['xPlank'] = contraints['xMin']
    if state['xPlank'] > contraints['xMax']:
        state['xPlank'] = contraints['xMax']

    if state['xBall'] < contraints['yMin']:
        state['xBall'] = contraints['yMin']
    if state['xBall'] > contraints['yMax']:
        state['xBall'] = contraints['yMax']

def randomBeam():
    global state, old_state
    print "BEAM!!"

    xPlank = rand.randint(contraints['xMin'], contraints['xMax'])
    xBall = rand.randint(contraints['yMin'], contraints['yMax'])
    v = rand.randint(contraints['vMin'], contraints['vMax'])
    #angle = rand.randint(contraints['angleMin'], contraints['angleMax'])

    state['xPlank'] = xPlank
    state['xBall'] = xBall
    state['v'] = v
    state['yBall'] = 0
    #state['angle'] = angle
    state['diff'] = state['xBall'] - state['xPlank'] # so if ball is left from plank it will be negative

    state = comm.bcast(state, root=0)

global iteration
iteration = 0

def move(action): 
    global in_end_pos, iteration, state, old_state
    old_state = state.copy()
    action()  
    checkValid()
    newState()
    outcome = calculateOutcome()
    in_end_pos = False
    if(checkEnd()):
        #print 'isend'
        print state
        in_end_pos = True
        outcome *= 1.5
        iteration += 1
    return [state, outcome, in_end_pos]

def calculateOutcome():
    global state, old_state

    diffStates = (abs(old_state['xBall'] - old_state['xPlank']))-(abs(state['xBall'] - state['xPlank'])) #will be positive for a right moves (relative distance getting smaller) or negative for opposite case
    if(diffStates == 0 and abs(state['xBall'] - state['xPlank']) < params['plankSize']/2): #stays on right place
        return 50
    elif (diffStates == 0): # stays on a wrong place
        return -30
    else:
        return diffStates

def checkEnd():
    #print 'end'
    return state['yBall'] > params['screenSizeY'] - 10

def getState():
    return state

def init_new_trial():

    randomBeam()
    outcome = 0
    in_end_pos = False
    return [outcome, in_end_pos]

def print_world_file():
    pass
    



