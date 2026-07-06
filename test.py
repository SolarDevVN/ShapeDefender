import turtle
import random

screen = turtle.Screen()
screen.setup(900, 600)
screen.bgcolor("#08111f")
screen.title("Turtle Artwork")
screen.tracer(0)

artist = turtle.Turtle()
artist.hideturtle()
artist.speed(0)
artist.pensize(2)


def draw_star(x, y, size, color):
    artist.penup()
    artist.goto(x, y)
    artist.color(color)
    artist.begin_fill()
    artist.setheading(90)
    for _ in range(5):
        artist.forward(size)
        artist.right(144)
    artist.end_fill()


# Draw stars
for _ in range(70):
    x = random.randint(-430, 430)
    y = random.randint(120, 280)
    size = random.randint(3, 7)
    draw_star(x, y, size, "white")

# Draw moon
artist.penup()
artist.goto(220, 180)
artist.color("#f7f3b2")
artist.begin_fill()
artist.circle(55)
artist.end_fill()

# Add moon glow
artist.penup()
artist.goto(210, 190)
artist.color("#dfe2b8")
artist.begin_fill()
artist.circle(40)
artist.end_fill()

# Draw mountains
artist.penup()
artist.goto(-450, -120)
artist.color("#3f4f6d")
artist.begin_fill()
artist.goto(-220, 80)
artist.goto(-90, -120)
artist.goto(40, 60)
artist.goto(220, -120)
artist.goto(450, 40)
artist.goto(450, -300)
artist.goto(-450, -300)
artist.goto(-450, -120)
artist.end_fill()

# Draw foreground hill
artist.penup()
artist.goto(-450, -180)
artist.color("#2f3b4e")
artist.begin_fill()
artist.goto(-250, -40)
artist.goto(-120, -180)
artist.goto(0, -70)
artist.goto(180, -180)
artist.goto(450, -80)
artist.goto(450, -300)
artist.goto(-450, -300)
artist.goto(-450, -180)
artist.end_fill()

# Draw a simple lake
artist.penup()
artist.goto(-150, -140)
artist.color("#2f6f7a")
artist.begin_fill()
artist.goto(150, -140)
artist.goto(120, -220)
artist.goto(-140, -220)
artist.goto(-150, -140)
artist.end_fill()

# Draw trees
for x in [-300, -180, 320]:
    artist.penup()
    artist.goto(x, -120)
    artist.color("#4b3220")
    artist.begin_fill()
    artist.goto(x + 20, -80)
    artist.goto(x + 40, -120)
    artist.goto(x, -120)
    artist.end_fill()

    artist.penup()
    artist.goto(x + 20, -70)
    artist.color("#2f7d3a")
    artist.begin_fill()
    artist.circle(25)
    artist.end_fill()

    artist.penup()
    artist.goto(x + 20, -20)
    artist.color("#2f7d3a")
    artist.begin_fill()
    artist.circle(20)
    artist.end_fill()

# Draw a small cabin
artist.penup()
artist.goto(-20, -110)
artist.color("#8a4b2a")
artist.begin_fill()
artist.goto(70, -110)
artist.goto(70, -40)
artist.goto(-20, -40)
artist.goto(-20, -110)
artist.end_fill()

artist.penup()
artist.goto(-10, -40)
artist.color("#c89b68")
artist.begin_fill()
artist.goto(60, -40)
artist.goto(25, 20)
artist.goto(-10, -40)
artist.end_fill()

artist.penup()
artist.goto(-10, -90)
artist.color("#5c3b1e")
artist.pendown()
artist.goto(20, -90)
artist.goto(20, -60)
artist.goto(40, -60)
artist.goto(40, -90)
artist.goto(70, -90)
artist.penup()

screen.update()
turtle.done()
