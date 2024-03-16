import turtle

c = turtle.Turtle()

def draw_square():
    c.right(90)
    c.forward(100)
    c.left(90)
    c.forward(100)
    c.left(90)
    c.forward(100)
    c.left(90)
    c.forward(100)
  
# draw_square()  
def draw_square():
    for i in range(4):
        c.forward(100)
        c.right(90)
# draw_square()

name = turtle.Turtle()
def square():
    for sides in range(4):
        name.forward(100)
        name.left(90)
# square()

a = turtle.Turtle()

def drawsq (sideleng , col):
    print(5)
    for sides in range(4):
        a.color(col)
        a.forward(sideleng)
        a.right(90)
    
print(drawsq(200 , "cyan"))

turtle.done()    
    
    