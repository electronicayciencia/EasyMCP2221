# Stepper motor control
import EasyMCP2221
from time import sleep


fullstep = (
    (1,1,0,0),
    (0,1,1,0),
    (0,0,1,1),
    (1,0,0,1),
    )

wave = (
    (1,0,0,0),
    (0,1,0,0),
    (0,0,1,0),
    (0,0,0,1),
    )

halfstep = (
    (1,0,0,0),
    (1,1,0,0),
    (0,1,0,0),
    (0,1,1,0),
    (0,0,1,0),
    (0,0,1,1),
    (0,0,0,1),
    (1,0,0,1),
    )




def run(numsteps, mode = "full", delay = 0):
    if numsteps < 0:
        increment = -1
    else:
        increment = 1

    if mode == "full":
        phases = fullstep
    if mode == "wave":
        phases = wave
    if mode == "half":
        phases = halfstep

    nphases = len(phases)
    
    for _ in range(1, abs(numsteps)):
        run.step = run.step + increment
        p = phases[run.step % nphases]
        mcp.GPIO_write(p[0],p[1],p[2],p[3])
        sleep(delay)
        
    mcp.GPIO_write(0,0,0,0)



mcp = EasyMCP2221.Device()

mcp.set_pin_function(
    gp0 = "GPIO_OUT",
    gp1 = "GPIO_OUT",
    gp2 = "GPIO_OUT",
    gp3 = "GPIO_OUT")


run.step = 0

run(2048)

sleep(1)

run(-2048)

# run(randint(1*2048,3*2048))
