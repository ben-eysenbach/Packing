import math
import Tkinter
import random
import time

class Square:

    def __init__(self, x, y, theta):
        '''Creates a centered at (x,y) with side length of 2. We assume that when theta=0 the corners point in cadinal directions'''
        self.x = x
        self.y = y
        self.theta = theta


    def getCorners(self):
        # right
        x1 = self.x + math.sqrt(2) * math.cos(self.theta)
        y1 = self.y + math.sqrt(2) * math.sin(self.theta)

        # top
        x2 = self.x + math.sqrt(2) * math.cos(self.theta + math.pi / 2)
        y2 = self.y + math.sqrt(2) * math.sin(self.theta + math.pi / 2)

        # left
        x3 = self.x + math.sqrt(2) * math.cos(self.theta + math.pi)
        y3 = self.y + math.sqrt(2) * math.sin(self.theta + math.pi)

        # bottom
        x4 = self.x + math.sqrt(2) * math.cos(self.theta + math.pi * 3 / 2)
        y4 = self.y + math.sqrt(2) * math.sin(self.theta + math.pi * 3 / 2)

        return [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

    def getOverlapCircle(self, r):
        '''Returns the area of the region outside the circle'''
        maxDelta = 0
        exteriorPt = None
        for (x, y) in self.getCorners():
            delta = math.sqrt(x**2 + y**2) - r
            if delta > maxDelta:
                maxDelta = delta
                exteriorPt = (x, y)
        return (maxDelta, exteriorPt)

    def getPotentialCircle(self, r, alpha=2.0, beta=0.1):
        (delta, exteriorPt) = self.getOverlapCircle(r)
        if delta == 0:
            return (0, 0, 0)
        norm = math.sqrt(self.x**2 + self.y**2)
        dx = alpha * delta * (-self.x) / norm
        dy = alpha * delta * (-self.y) / norm
        dist = getPtLineDist((0, 0), (self.x, self.y), exteriorPt)
        theta = math.asin(dist / math.sqrt(2))
        if theta > 0:
            dtheta = beta * delta * (math.pi / 4 - theta)
        else:
            dtheta = beta * delta * (-math.pi / 4 - theta)

        # print (dx, dy)
        print 'Theta:', dtheta*180/math.pi
        return (dx, dy, dtheta)

    def getOverlapSquare(self, sq2):
        '''Returns the area of the region overlapping with another square'''
        [pt1, pt2, pt3, pt4] = self.getCorners()
        maxArea = 0
        interiorPt = None
        # Include middle in case the squares are on top of each other but rotated such that no corners fall within the square
        for pt in sq2.getCorners() + [(sq2.x, sq2.y)]:
            a1 = getTriangleArea(pt1, pt2, pt)
            a2 = getTriangleArea(pt2, pt3, pt)
            a3 = getTriangleArea(pt3, pt4, pt)
            a4 = getTriangleArea(pt4, pt1, pt)
            if eq(sum([a1, a2, a3, a4]), 4):
                # pt inside or on an edge

                if not (eq(a1, 0) or eq(a2, 2) or eq(a3, 0) or eq(a4, 0)):
                    # pt inside
                    area = min([a1, a2, a3, a4])
                    if area > maxArea:
                        maxArea = area
                        interiorPt = pt
        return maxArea, interiorPt

    def getPotentialSquare(self, sq2, alpha=1.0, beta=0.1):
        '''Force extered on this square by sq2'''
        (overlap, interiorPt) = self.getOverlapSquare(sq2)
        if overlap == 0:
            return (0, 0, 0)
        dx = alpha * overlap * (self.x - sq2.x)
        dy = alpha * overlap * (self.y - sq2.y)
        dist = getPtLineDist((sq2.x, sq2.y), (self.x, self.y), interiorPt)
        theta = math.asin(dist / math.sqrt(2))
        if theta > 0:
            dtheta = beta * (math.pi / 4 - theta)
        else:
            dtheta = beta * (-math.pi / 4 - theta)
        return (dx, dy, dtheta)

    def __repr__(self):
        return '<Square: x=%.3f, y=%.3f, theta=%.3f>' % (self.x, self.y, self.theta)

class Packing:
    '''Class whether we can fit n saures of radius 2 into a circle of radius r'''

    def __init__(self, n, r):
        self.n = n
        self.r = r
        self.squares = self.getSquares()
        self.step = 1
        self.stepMax = 2000
        self.alphaBase = 1.0
        self.alpha = self.alphaBase
        self.alphaRate = 0.98 # decay per step
        self.alphaReset = 350 # reset to alphaRestRate after this many steps
        self.alphaResetRate = 0.9

        self.timeStep = 1
        self.canvasSize = 300
        self.scale = 10
        self.root = Tkinter.Tk()
        self.canvas = Tkinter.Canvas(self.root, width=self.canvasSize, height=self.canvasSize)
        self.canvas.pack()

    def getSquares(self):
        squares = []
        for k in range(self.n):
            x = 0.5 * self.r * (2 * random.random() - 1)
            y = 0.5 * self.r * (2 * random.random() - 1)
            theta = 2 * math.pi * random.random()
            squares.append(Square(x, y, theta))
        return squares

    def isPackable(self):
        print 'Step:', self.step
        done = True
        for sq in self.squares:
            (dx, dy, dtheta) = sq.getPotentialCircle(self.r, self.alpha, beta=self.alpha*10)
            if not (eq(dx, 0) and eq(dy, 0)):
                done = False
                sq.x += dx
                sq.y += dy
                sq.theta += dtheta
            for sq2 in self.squares:
                if sq != sq2:
                    (dx, dy, dtheta) = sq.getPotentialSquare(sq2, alpha=self.alpha, beta=self.alpha*10)
                    # print (dx, dy, dtheta)
                    if not(eq(dx, 0) and eq(dy, 0)):
                        done = False
                        sq.x += dx
                        sq.y += dy
                        sq.theta += dtheta

            sq.x += self.alpha * (2 * random.random() - 1)
            sq.y += self.alpha * (2 * random.random() - 1)
            sq.theta += self.alpha * (2 * random.random() - 1)
        # print self.squares
        self.updateCanvas()
        self.alpha *= self.alphaRate
        if done:
            print 'Done!'
            return True
        if self.step > self.stepMax:
            print 'Failed'
            return False
        if self.step % self.alphaReset == 0:
            self.alphaBase *= self.alphaResetRate
            self.alpha = self.alphaBase
        self.step += 1
        self.root.after(self.timeStep, self.isPackable)

    def drawSquare(self, sq):
        offset = self.canvasSize / 2
        corners = []
        for (x, y) in sq.getCorners():
            xInt = (int(self.scale*x+offset))
            yInt = (int(self.scale*y+offset))
            corners.append((xInt, yInt))
        self.canvas.create_polygon(*corners, outline='black', fill='red')

    def drawCircle(self,):
        r = self.r * self.scale
        offset = self.canvasSize / 2
        self.canvas.create_oval(offset - r, offset - r, offset + r, offset + r)

    def updateCanvas(self):
        self.canvas.delete(Tkinter.ALL)
        for sq in self.squares:
            self.drawSquare(sq)
        self.drawCircle()

    def show(self):
        self.root.after(self.timeStep, self.isPackable)
        self.root.mainloop()

def eq(x1, x2):
    return abs(x1 - x2) < 10e-14

def det((x1, y1), (x2, y2), (x3, y3)):
    '''Returns the determinant of the following matrix:
        x1, y1, 1
        x2, y2, 1
        x3, y3, 1

    Alternatively, this is the signed area of a triangle'''
    return x1*y2 + x2*y3 + x3*y1 - x2*y1 - x3*y2 - x1*y3

def getTriangleArea(pt1, pt2, pt3):
    return 0.5 * abs(det(pt1, pt2, pt3))

def getPtLineDist(pt1, pt2, pt3):
    '''Returns the signed distance between pt3 and the line between pt1 and pt2. If the pt lies to the right of the line, the sign is negative'''
    (x1, y1) = pt1
    (x2, y2) = pt2
    norm = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    return det(pt1, pt2, pt3) / norm


if __name__ == '__main__':
    p = Packing(10, 4.2)
    p.show()
