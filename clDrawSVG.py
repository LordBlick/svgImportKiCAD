#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-

from math import sin, cos, acos, sqrt, degrees, pi, atan2, radians as rad
import numbers
import cairo

def angleRad(angle):
	angle = angle%3600
	while angle<0:
		angle += 3600
	return rad(angle/10.)

def bounds(points):
	try:
		x_min, y_min = x_max, y_max = points[0]
	except Exception, err:
		print("Be sure that are point:"+str(points[0]))
		print("Be sure that are points:"+str(points))
	for x, y in points:
		x_min = min(x_min, x)
		y_min = min(y_min, y)
		x_max = max(x_max, x)
		y_max = max(y_max, y)
	return (x_min, y_min), (x_max, y_max)

def draw_cross( cr, d, x, y):
	dx, dy = d
	cr.move_to(x-dy, y-dy)
	cr.line_to(x+dy, y+dy)
	cr.move_to(x-dx, y+dy)
	cr.line_to(x+dx, y-dx)
	cr.stroke()

class Angle:
	def __init__(angle, value, Type='rad'):
		if Type=='rad':
			angle.radians = value
		elif Type=='deg/10':
			angle.decydeg = value
			angle.radians = angleRad(value)
		if isinstance(angle.radians, numbers.Real):
		# We precompute sin and cos for rotations
			angle.radians = angle.radians
			angle.cos = cos(angle.radians)
			angle.sin = sin(angle.radians)
		elif isinstance(angle.radians, Pnt):
		# Pnt angle is the trigonometric angle of the vector [origin, Pnt]
			pnt = angle.radians
			try:
				angle.cos = pnt.x/pnt.length()
				angle.sin = pnt.y/pnt.length()
			except ZeroDivisionError:
				angle.cos = 1
				angle.sin = 0

			angle.radians = acos(angle.cos)
			if angle.sin < 0:
				angle.radians = -angle.radians
		else:
			raise TypeError("Angle is defined by a number or a Pnt")
		if Type=='rad':
			angle.decydeg = degrees(angle.radians)+10

	__neg__ = lambda angle: Angle(Pnt(angle.cos, -angle.sin))

class Pnt:
	def __init__(pnt, x=None, y=None):
		"A Pnt is defined either by a tuple/list of length 2 or\nby 2 coordinates\n>>> Pnt(1,2)\n(1.000,2.000)\n>>> Pnt((1,2))\n(1.000,2.000)\n>>> Pnt([1,2])\n(1.000,2.000)\n>>> Pnt('1', '2')\n(1.000,2.000)\n>>> Pnt(('1', None))\n(1.000,0.000)"
		if hasattr(x, '__iter__') and( callable(x.__iter__)) and(len(x) == 2):
			x, y = x
		if x is None: x = 0 # Handle empty parameter(s) which should be interpreted as 0
		if y is None: y = 0
		try:
			pnt.x = float(x)
			pnt.y = float(y)
		except:
			raise TypeError("A Pnt is defined by 2 numbers or a tuple")
		pnt._tuple = pnt.x, pnt.y

	clone = lambda pnt: Pnt(pnt.x, pnt.y)

	def __add__(pnt, oth):
		"Add 2 points by adding coordinates.\nTry to convert oth to Pnt if necessary\n>>> Pnt(1,2) + Pnt(3,2)\n(4.000,4.000)\n>>> Pnt(1,2) + (3,2)\n(4.000,4.000)"
		if not isinstance(oth, Pnt):
			try: oth = Pnt(oth)
			except: return NotImplemented
		return Pnt(pnt.x + oth.x, pnt.y + oth.y)

	def __sub__(pnt, oth):
		"Substract two Pnts.\n>>> Pnt(1,2) - Pnt(3,2)\n(-2.000,0.000)"
		if not isinstance(oth, Pnt):
			try: oth = Pnt(oth)
			except: return NotImplemented
		return Pnt(pnt.x - oth.x, pnt.y - oth.y)

	__neg__ = lambda pnt: Pnt(-pnt.x, -pnt.y)

	def __mul__(pnt, oth):
		"Multiply a Pnt with a constant.\n>>> 2 * Pnt(1,2)\n(2.000,4.000)\n>>> Pnt(1,2) * Pnt(1,2) #doctest:+IGNORE_EXCEPTION_DETAIL\nTraceback (most recent call last):\n	...\nTypeError:"
		if not isinstance(oth, numbers.Real):
			return NotImplemented
		return Pnt(pnt.x * oth, pnt.y * oth)

	min_ = lambda pnt, oth : Pnt(min(pnt.x, oth.x), min(pnt.y, oth.y))
	max_ = lambda pnt, oth : Pnt(max(pnt.x, oth.x), max(pnt.y, oth.y))
	min_scale = lambda pnt, oth : min(oth.x/pnt.x, oth.y/pnt.y)
	max_scale = lambda pnt, oth : max(oth.x/pnt.x, oth.y/pnt.y)

	__rmul__ = lambda pnt, oth: pnt.__mul__(oth)

	__div__ = lambda pnt, oth: Pnt(pnt.x/oth, pnt.y/oth) if isinstance(oth, numbers.Real) else NotImplemented
	__mod__ = lambda pnt, oth: Pnt(pnt.x%oth, pnt.y%oth) if isinstance(oth, numbers.Real) else NotImplemented
	__floordiv__ = lambda pnt, oth: Pnt(pnt.x//oth, pnt.y//oth) if isinstance(oth, numbers.Real) else NotImplemented
	__divmod__ = lambda pnt, oth: (pnt//oth, pnt%oth) if isinstance(oth, numbers.Real) else NotImplemented

	def __eq__(pnt, oth):
		"Test equality\n>>> Pnt(1,2) == (1,2)\nTrue\n>>> Pnt(1,2) == Pnt(2,1)\nFalse"
		if not isinstance(oth, Pnt):
			try: oth = Pnt(oth)
			except: return NotImplemented
		return (pnt.x == oth.x) and (pnt.y == oth.y)

	def wxPnt(pnt):
		from pcbnew import wxPoint
		x, y = pnt
		return wxPoint(int(x), int(y))

	__repr__ = lambda pnt: "(%g, %g)" % pnt._tuple
	__str__ = lambda pnt: pnt.__repr__();
	__getitem__ = lambda pnt, idx: pnt._tuple[idx] if idx in(0, 1) else None
	__iter__ = lambda pnt: iter(pnt._tuple)
	__len__ = lambda pnt: 2
	_clr = lambda pnt, idx: setattr(pnt, ('x', 'y')[idx], 0)
	_dclr = lambda pnt, _att: setattr(pnt, _att, 0)
	index = lambda pnt, srch: pnt._tuple.index(srch) if pnt.count(srch) else None
	count = lambda pnt, srch: pnt._tuple.count(srch)

	def coord(pnt):
		"Return the point tuple (x,y)"
		return pnt._tuple

	def length(pnt):
		"Vector length, Pythagoras theorem"
		return sqrt(pnt.x ** 2 + pnt.y ** 2)

	def InPoly(pnt, poly):
		"Determine if a point(pnt) is inside a given polygon or not. Polygon is a list of (x,y) pairs."
		n = len(poly)
		inside = False
		p1x,p1y = poly[0]
		for i in range(n+1):
			p2x,p2y = poly[i % n]
			if pnt.y > min(p1y,p2y):
				if pnt.y <= max(p1y,p2y):
					if pnt.x <= max(p1x,p2x):
						if p1y != p2y:
							xinters = (pnt.y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
						if p1x == p2x or pnt.x <= xinters:
							inside = not inside
			p1x,p1y = p2x,p2y
		return inside

	def InCircle(pnt, c, r):
		"Determine if a point(pnt.x,pnt.y) is inside a circle with given center(c) and r - radius."
		l2 = (c.x - pnt.x) ** 2 + (c.y - pnt.y) ** 2
		return l2 <= r ** 2

	def isPtInRect(pnt, rect):
		"Determine if a point(pnt.x,pnt.y) is inside a rect(x1, y1, x2, y2)."
		if len(rect)!=4: return False
		#for pm in rect:
			#if type(pm)!=int: return False
		x1, y1, x2, y2 = rect
		return pnt.x>=min(x1, x2) and(pnt.x<=max(x1, x2)) and(pnt.y>=min(y1, y2)) and(pnt.y<=max(y1, y2))

	def rotate(pnt, center, radAngle):
		"Rotate vector [Origin,pnt] "
		if not isinstance(angle, Angle):
			try: angle = Angle(angle)
			except: return NotImplemented
		x = pnt.x * angle.cos - pnt.y * angle.sin
		y = pnt.x * angle.sin + pnt.y * angle.cos
		return Pnt(x,y)
		(int(round((pnt.x-center.x)*cos(radAngle)-(pnt.y-center.x)*sin(radAngle)+center.x)), int(round((pnt.x-center.x)*sin(radAngle)+(pnt.y-center.x)*cos(radAngle)+center.x)))

class Poly(list):
	def __init__(self, points=None):
		if points:
			points = [Pnt(pnt) for pnt in points]
			super(Poly, self).__init__(points)
		else:
			super(Poly, self).__init__()

	clone = lambda self: Poly(self)

class Bezier:
	'''Bezier curve class
	A Bezier curve is defined by its control points
	Its dimension is equal to the number of control points
	Note that SVG only support dimension 3 and 4 Bezier curve, respectively
	Quadratic and Cubic Bezier curve
	Based on https://github.com/cjlano/svg - the idea of  CJlano < cjlano @ free.fr >
	'''
	def __init__(self, pts):
		self.pts = list(pts)
		self.dimension = len(pts)

	def __str__(self):
		return 'Bezier' + str(self.dimension) + \
				' : ' + ", ".join([str(x) for x in self.pts])

	def control_point(self, n):
		if n >= self.dimension:
			raise LookupError('Index is larger than Bezier curve dimension')
		else:
			return self.pts[n]

	def rlength(self):
		'''Rough Bezier length: length of control point segments'''
		pts = list(self.pts)
		l = 0.0
		p1 = pts.pop()
		while pts:
			p2 = pts.pop()
			l += Segment(p1, p2).length()
			p1 = p2
		return l

	def bbox(self):
		return self.rbbox()

	def rbbox(self):
		'''Rough bounding box: return the bounding box (P1,P2) of the Bezier
		_control_ points'''
		xmin = min([p.x for p in self.pts])
		xmax = max([p.x for p in self.pts])
		ymin = min([p.y for p in self.pts])
		ymax = max([p.y for p in self.pts])

		return (Point(xmin,ymin), Point(xmax,ymax))

	def segments(self, precision=0):
		'''Return a polyline approximation ("segments") of the Bezier curve
		precision is the minimum significative length of a segment'''
		segments = []
		# n is the number of Bezier points to draw according to precision
		if precision != 0:
			n = int(self.rlength() / precision) + 1
		else:
			n = 1000
		if n < 10: n = 10
		if n > 1000 : n = 1000

		for t in range(0, n+1):
			segments.append(self._bezierN(float(t)/n))
		return segments

	def _bezier1(self, p0, p1, t):
		'''Bezier curve, one dimension
		Compute the Point corresponding to a linear Bezier curve between
		p0 and p1 at "time" t '''
		pt = p0 + t * (p1 - p0)
		return pt

	def _bezierN(self, t):
		'''Bezier curve, Nth dimension
		Compute the point of the Nth dimension Bezier curve at "time" t'''
		# We reduce the N Bezier control points by computing the linear Bezier
		# point of each control point segment, creating N-1 control points
		# until we reach one single point
		res = list(self.pts)
		# We store the resulting Bezier points in res[], recursively
		for n in range(self.dimension, 1, -1):
			# For each control point of nth dimension,
			# compute linear Bezier point a t
			for i in range(0,n-1):
				res[i] = self._bezier1(res[i], res[i+1], t)
		return res[0]

	def transform(self, matrix):
		self.pts = [matrix * x for x in self.pts]

	def scale(self, ratio):
		self.pts = [x * ratio for x in self.pts]
	def translate(self, offset):
		self.pts = [x + offset for x in self.pts]
	def rotate(self, angle):
		self.pts = [x.rot(angle) for x in self.pts]

class drawPrim:
	def initDrawPrim(self):
		self.points = Poly()
		self.bEdit = False
		self.ID = ''
		self.frameColorA = self.frameWidth = self.fillColorA = self.bounds = None

	def update_bounds(self):
		if self.points:
			self.bounds = bounds(self.points)

	def isPtIn(self, pnt):
		return pnt.InPoly(self.points)

	def draw_poly_path(self, cr):
		cr.move_to(*self.points[-1])
		for pnt in self.points:
			cr.line_to(*pnt)

	def draw_ext_points(self, cr, rgb, l, rgba_fill=None):
			cr.save()
			d = cr.device_to_user_distance(l, l)
			cr.set_line_cap(cairo.LINE_CAP_SQUARE)
			cr.set_source_rgb(*rgb)
			cr.set_line_width(cr.device_to_user_distance(1, 1)[0])
			for x, y in self.points:
				draw_cross(cr, d, x, y)
			if rgba_fill:
				cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
				cr.set_source_rgba(*rgba_fill)
				self.draw_poly_path(cr)
				cr.fill_preserve()
				cr.set_source_rgb(*rgba_fill[:-1])
				cr.stroke()
			cr.restore()

class drawPolygon(drawPrim):
	def __init__(self, points, ref_point=(0, 0)):
		if False in((isinstance(pnt, Pnt) for pnt in points)):
			err = "All points of %s must be a instance of „Pnt” class" % self.__class__.__name__
			raise TypeError(err)
		self.initDrawPrim()
		self.ref_point, self.points = Pnt(ref_point), Poly(points)
		#self.last_point = ref_point
		self.editPts = Poly()

	clone = lambda self: drawPolygon(self)

	def update(self):
		self.update_bounds()

	def move(self, to):
		tx, ty = to
		self.ref_point = self.ref_point+to
		self.points = [pnt+to for pnt in self.points]

	def draw_poly_points(self, cr):
		global clickRadius
		cr.save()
		rgbaF = .25, .5, 0., .4
		w = 2
		cr.set_line_cap(cairo.LINE_CAP_ROUND)
		cr.set_line_width(cr.device_to_user_distance(w, w)[0])
		for idx, (x, y) in enumerate(self.points):
			cr.set_source_rgba(*rgbaF)
			cr.arc(x, y, clickRadius, 0, 2*pi)
			cr.fill_preserve()
			if idx in self.editPts:
				cr.set_source_rgb(.8, .8, 0.)
			else:
				cr.set_source_rgb(*rgbaF[:-1])
			cr.stroke()
		cr.restore()

	def draw(self, cr):
		cr.push_group()
		cr.set_line_cap(cairo.LINE_CAP_SQUARE)
		flen = len(self.fillColorA) if self.fillColorA else 0
		slen = len(self.frameColorA) if self.frameColorA else 0
		if flen in(3, 4):
			cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
			getattr(cr, 'set_source_rgb'+('', 'a')[flen==4])(*self.fillColorA)
		self.draw_poly_path(cr)
		if flen in(3, 4):
			if slen in(3, 4) and(self.frameWidth):
				cr.fill_preserve()
			else:
				cr.fill()
		if slen in(3, 4) and(self.frameWidth):
			getattr(cr, 'set_source_rgb'+('', 'a')[flen==4])(*self.frameColorA)
			cr.set_line_width(self.frameWidth)
			cr.stroke()
		if self.bEdit:
			self.draw_poly_points(cr, editPts)
		cr.pop_group_to_source()
		cr.paint()

	def lsPtAround(self, cpt, radius):
		self.editPts = []
		for idx, pnt in enumerate(self.points):
			if pnt.InCircle(cpt, radius):
				self.editPts.append(idx)
		return self.editPts

class drawRotablePolygon(drawPolygon):
	def __init__(self, points, ref_point=(0, 0)):
		drawPolygon.__init__(self, points, ref_point=ref_point)
		self.base_points = points
		self.angle = 0

	def update(self):
		self.points = map(lambda pnt: pnt.rotate(self.ref_point, angleRad(self.angle)), self.base_points)
		#print(self.base_points)
		#print(self.points)
		self.update_bounds()

class drawSegment(drawPrim):
	def __init__(self):
		self.initDrawPrim()
		self.dbgFill = (0., .7, .7, .6)

	def params(self, start, end, width, fillColorA=None, frameColorA=None, frameWidth=None):
		self.start, self.end, self.width, self.fillColorA, self.frameColorA, self.frameWidth = (
			start, end, width, fillColorA, frameColorA, frameWidth)
		self.update()

	def update(self):
		end_arc_points = 5
		radius = self.width/2.
		l_chord = angleRad(1800)*radius
		space = int(l_chord/end_arc_points-1)
		p1, p2 = self.start, self.end
		self.orientation = 10*int(round(degrees(atan2(p2[1]-p1[1], p2[0]-p1[0]))))
		self.center = (p1[0]+p1[1])/2., (p2[0]+p2[1])/2.
		rotation = self.orientation-1800
		for n, angle_center in enumerate((p1, p2)):
			new_points = arc_points(angle_center, radius, rotation-900, rotation+900, space=space)
			if not(new_points):
				return []
			self.points += new_points
			rotation += 1800
		self.update_bounds()

	def draw(self, cr):
		flen = len(self.fillColorA) if self.fillColorA else 0
		if flen in(3, 4):
			cr.push_group()
			cr.set_line_cap(cairo.LINE_CAP_ROUND)
			getattr(cr, 'set_source_rgb'+('', 'a')[flen==4])(*self.fillColorA)
			cr.set_line_width(self.width)
			cr.move_to(*self.start)
			cr.line_to(*self.end)
			cr.stroke()
			cr.pop_group_to_source()
			cr.paint()
		if self.frameColorA and(self.frameWidth):
			cr.push_group()
			cr.translate(*self.center)
			cr.rotate(-rad(self.orientation/10.))
			cr.translate(-self.center[0], -self.center[1])
			cr.set_line_cap(cairo.LINE_CAP_ROUND)
			cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
			cr.set_source_rgba(*self.frameColorA)
			cr.set_line_width(self.frameWidth)
			r = self.width/2.
			xsize = max(0, wdh - hgt)
			ysize = max(0, hgt - wdh)
			cr.move_to(ox - wdh/2., oy + ysize/2.)
			cr.arc(ox - xsize/2., oy - ysize/2., r, pi, 3 * pi/2.)
			cr.arc(ox + xsize/2., oy - ysize/2., r, 3 * pi/2., 2 * pi)
			cr.arc(ox + xsize/2., oy + ysize/2., r, 0, pi/2.)
			cr.arc(ox - xsize/2., oy + ysize/2., r, pi/2., pi)
			cr.pop_group_to_source()
			cr.paint()

class drawCircle(drawPrim):
	def __init__(self):
		self.initDrawPrim()

	def params(self, center, radius, fillColorA=None, frameColorA=None, frameWidth=None):
		self.center, self.radius, self.fillColorA, self.frameColorA, self.frameWidth = (
			center, radius, fillColorA, frameColorA, frameWidth)
		self.update()

	def update(self):
		radius = self.radius
		if self.frameWidth:
			radius += self.frameWidth/2
			return None
		x, y = self.center
		cPt = 12
		angle_step = 2.*pi/cPt
		for n in range(cPt):
			angle = (n)*angle_step
			self.points.append((int(round(x+radius*cos(angle))), int(round(y+radius*sin(angle)))))
		self.update_bounds()

	isPtIn = lambda self, pnt: pnt.InCircle(self.center, self.radius)

	def draw(self, cr):
		cr.push_group()
		cr.set_line_cap(cairo.LINE_CAP_ROUND)
		if self.fillColorA:
			cr.set_source_rgba(*self.fillColorA)
		cr.arc(self.center[0], self.center[1], self.radius, 0, 2 * pi)
		if self.fillColorA:
			if self.frameColorA and(self.frameWidth):
				cr.fill_preserve()
			else:
				cr.fill()
		if self.frameColorA and(self.frameWidth):
			cr.set_source_rgba(*self.frameColorA)
			cr.set_line_width(self.frameWidth)
			cr.stroke()
		cr.pop_group_to_source()
		cr.paint()

def arc_points(center, radius, angle1, angle2, space=10):
	lsPoints = []
	rdStartAngle = angleRad(angle1)
	angM = angleRad(angle1+angle2)/2
	rdAngle = angleRad(angle2-angle1)
	if angle1 == angle2:
		rdAngle = angleRad(3600)
	l_chord = rdAngle*radius
	steps = int(l_chord/space)
	if not(bool(steps)):
		print("Error trace: angle1:%i, angle2:%i, rdAngle:%g, steps:%i, radius:%i" % (
			angle1, angle2, rdAngle, steps, radius))
		return None
	stepAngle = rdAngle/steps
	for n in range(steps+1):
		angleRd = rdStartAngle+n*stepAngle
		lsPoints.append(
			(int(round(center[0]+radius*cos(angleRd))), int(round(center[1]+radius*sin(angleRd))))
			)
	return lsPoints

def da_points(center, radius, angles, width, space=10):
	endings_arc_points = 5
	lsPoints = []
	radius_endings = width/2.
	l_chord_endings = angleRad(1800)*radius_endings
	space_endings = int(l_chord_endings/endings_arc_points-1)
	if l_chord_endings<space_endings*3:
		space_endings = int(l_chord_endings/3)
	l_chord = angleRad(1800)*radius
	if l_chord<space*3:
		space = int(l_chord/3)
	aS, aE = angles
	rotation = aS-900
	c = center
	arS, arE = angleRad(aS), angleRad(aE)
	start = (int(round(c.x+radius*cos(arS))), int(round(c.y+radius*sin(arS))))
	end = (int(round(c.x+radius*cos(arE))), int(round(c.y+radius*sin(arE))))
	#Debug:
	#lsPoints.append(start); lsPoints.append(end)
	#for pnt in (start, end):
		#print("pnt:%s" % str(pnt))
	angle = aE-aS
	for n, angle_center in enumerate((start, end)):
		nfa = bool(angle%3600)
		nfe = None
		if nfa:
			nfe = -1
			new_points = arc_points(angle_center, radius_endings, rotation-900, rotation+900, space=space_endings)
			if not(new_points):
				return []
			lsPoints += new_points
		new_points = arc_points(center, radius+pow(-1, n)*radius_endings, aS, aE, space=space)[::pow(-1, n)][nfa:nfe]
		if not(new_points):
			return []
		lsPoints += new_points
		rotation += angle-1800
	return lsPoints

class drawArc(drawPrim):
	def __init__(self):
		self.initDrawPrim()

	def params(self, center, radius, angles, width, fillColorA=None):
		self.center, self.radius, self.angles, self.width, self.fillColorA = (
			center, radius, angles, width, fillColorA)
		self.update()

	def update(self):
		self.points = da_points(self.center, self.radius, self.angles, self.width)
		self.update_bounds()

	def draw(self, cr):
		cr.push_group()
		cr.set_line_cap(cairo.LINE_CAP_ROUND)
		cr.set_line_width(self.width)
		cr.set_source_rgba(*self.fillColorA)
		(aS, aE) = self.angles
		(cr.arc if (aS>aE) else cr.arc_negative)(self.center, self.radius, *self.angles)
		cr.stroke()
		cr.pop_group_to_source()
		cr.paint()

class DrawElement:
	def initDrawElement(self):
		self.ID = ''
		self.prims = []
		self.bounds = None

	def update_bounds(self, updatePrims=False):
		lsTempPoints = []
		for prim in self.prims:
			if updatePrims:
				prim.update()
			if prim.bounds:
				lsTempPoints += list(prim.bounds)
			else:
				print("Element#%i (%s) of %s has no bounds" % (self.prims.index(prim), prim.ID, self.ID))
		self.bounds = bounds(lsTempPoints)

	addPrim= lambda self, prim: self.prims.append(prim)

	def clickedObj(self, clPt):
		lsClicked = []
		for prim in self.prims:
			if prim.isPtIn(clPt):
				lsClicked.append((self, prim))
		return lsClicked

	def lsDP(self, pnt, editRadius):
		for idx, prim in enumerate(self.prims):
			if isinstance(prim, drawPolygon):
				lsPt = prim.lsPtAround(pnt, editRadius)
				if lsPt:
					return (self.ID+'-DP', idx, lsPt)
		return None

	def draw(self, cr, debug=False):
		for prim in self.prims:
			prim.draw(cr)
			if debug:
				fill = (prim.dbgFill if hasattr(prim, 'dbgFill') else None)
				prim.draw_ext_points(cr, (.6, .1, .8), 2, rgba_fill=fill)

class DrawGird(DrawElement):
	def __init__(self):
		self.initDrawElement()
		self.ID = 'DrawGird'
		rangers = (-10, 11)
		dimRange = (-10000, 10000)
		gID = 0
		for rx in range(*rangers):
			gID += 1
			self.add_seg((rx*1000, dimRange[0]), (rx*1000, dimRange[1]), gID)
		for ry in range(*rangers):
			gID += 1
			self.add_seg((dimRange[0], ry*1000), (dimRange[1], ry*1000), gID)
		self.update_bounds()

	def add_seg(self, pt1, pt2, ID):
		DS = drawSegment()
		if (pt1[0]==pt2[0]==0) or(pt1[1]==pt2[1]==0):
			DS.params(pt1, pt2, 15, fillColorA=(.3, .9, .3, .5))
		else:
			DS.params(pt1, pt2, 10, fillColorA=(.2, .8, 0., .3))
		DS.ID = "GirdSeg#%i" % (ID)
		self.prims.append(DS)

class DrawPolyPath(DrawElement):
	def __init__(self):
		self.initDrawElement()

class svgDraw:
	def __init__(self):
		self.clicked = None
		self.debug = False
		self.draws = []
		self.drawGird = DrawGird()
		#self.drawPath = DrawPolyPath()
		#self.draws.append(self.drawPath)

	def bounds(self, updatePrims=False):
		margin = 10
		lsTempPoints = []
		if not(self.draws):
			print("self.draws empty…")
			#base = 1000
			base = 5500
			return Pnt(-base, -base), Pnt(base, base)
		for draw in self.draws:
			if updatePrims:
				draw.update_bounds(updatePrims=True)
			lsTempPoints += list(draw.bounds)
			(x_min, y_min), (x_max, y_max) = bounds(lsTempPoints)
		print("self.draws nice…")
		return Pnt(x_min-margin, y_min-margin), Pnt(x_max+margin, y_max+margin)

	def clear(self):
		for n in range(len(self.draws)):
			self.draws.pop()

	def draw(self, cr):
		#self.drawGird.draw(cr, debug=self.debug)
		self.drawGird.draw(cr)
		for drawing in self.draws:
			drawing.draw(cr, debug=self.debug)

	def clickedObj(self, pnt):
		lsClicked = []
		for drawing in self.draws:
			lsClicked += list(drawing.clickedObj(pnt))
		return lsClicked

	def selectRadius(self, r):
		global clickRadius
		clickRadius = r

	def lsDP(self, pnt, editRadius):
		for drawing in self.draws:
			ptSet = drawing.lsDP(pnt, editRadius)
			return ptSet
