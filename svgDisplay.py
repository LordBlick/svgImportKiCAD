#!/usr/bin/python2
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-


from gtk import gdk, DrawingArea, CAN_FOCUS
from gobject import timeout_add as addTick, source_remove as unWatch
MB_Left = 1
MB_Midlle = 2
MB_Right = 3
from clDrawSVG import svgDraw, Pnt
class svgCairo(DrawingArea):
	# Draw in response to an expose-event
	__gsignals__ = {'expose-event': 'override'}
	def __init__(self, parent, x, y):
		DrawingArea.__init__(self)
		self.set_flags(self.flags() | CAN_FOCUS)
		self.set_events(self.get_events() | gdk.BUTTON_PRESS_MASK | gdk.BUTTON_RELEASE_MASK)
		#|gdk.POINTER_MOTION_MASK|gdk.POINTER_MOTION_HINT_MASK)
		self.init_drawer()
		self.connect("button-press-event", self._mouseButton)
		self.connect("button-release-event", self._mouseButton)
		self.connect("scroll-event", self._mouseScroll)
		parent.put(self, x, y)

	def init_drawer(self):
		self.drag_click = self.drag_call = None
		self.drawer = svgDraw()
		self.reset_drawer()

	def reset_drawer(self):
		self.min, self.max = self.drawer.bounds(updatePrims=True)
		self.drawer_area = self.max - self.min
		self.pos = -self.min
		self.zoomscale = 1.0

	def set_drag_call(self, callback):
		if callable(callback): self.drag_call = callback

	def pan(self, amt):
		cr = self.window.cairo_create()
		self._reset_ctm(cr)
		self.pos +=  Pnt(cr.device_to_user_distance(*amt))
		self.redraw()

	def _Drag(self):
		if not(self.drag_click):
			return False
		ptPos = Pnt(self.get_pointer())
		ptst = Pnt(self.drag_click[:-1])
		if ptPos!=ptst:
			MButt = self.drag_click[2]
			rel = ptPos - ptst
			if MButt==MB_Left:
				if self.drag_call:
					dpt = self.last_d+rel
					upt = dpt/self.scale
					ux, uy = upt//1
					if ux|uy:
						self.drag_call(*upt)
						if ux:
							self.last_d.x = 0.
						if uy:
							self.last_d.y = 0.
					else:
						self.last_d += rel
			elif MButt==MB_Midlle:
				self.pan(rel)
			self.drag_click = ptPos[0], ptPos[1], MButt
		return True

	def findClickSelection(self, pnt, state):
		cr = self.window.cairo_create()
		self._reset_ctm(cr)
		upt = Pnt(cr.device_to_user_distance(*pnt))
		upt -= self.pos
		if hasattr(self.drawer, 'clicked') and(callable(self.drawer.clicked)):
			self.drawer.clicked(upt, state)

	#http://www.pygtk.org/docs/pygtk/class-gdkevent.html
	def _mouseButton(self, widget, event):
		es = event.state
		lsState = (
			(gdk.CONTROL_MASK, 'Ctrl'),
			(gdk.MOD1_MASK, 'Alt'),
			(gdk.MOD2_MASK, 'Num'),
			(gdk.MOD3_MASK, 'Mod3'),
			(gdk.MOD4_MASK, 'Mod4'),
			(gdk.MOD5_MASK, 'AltGr'),
			(gdk.LOCK_MASK, 'Lock'),
			(gdk.META_MASK, 'Meta'),
			(gdk.SHIFT_MASK, 'Shift'),
			(gdk.SUPER_MASK, 'Super'),
			(gdk.SCROLL_MASK, 'Scroll'),
			(gdk.BUTTON1_MASK, 'MB1'),
			(gdk.BUTTON2_MASK, 'MB2'),
			(gdk.BUTTON3_MASK, 'MB3'),
			(gdk.BUTTON4_MASK, 'MB4'),
			(gdk.BUTTON5_MASK, 'MB5'),
			#look into ~/Devel/Python/TextViewEdit/keyPressLog
			)
		state = [nmModifier for Modifier, nmModifier in lsState if(Modifier&es)]
		if event.type == gdk.BUTTON_PRESS:
			if not self.drag_click and(event.button in (MB_Left, MB_Midlle)):
				self.drag_click = event.x, event.y, event.button
				self.tickID = addTick(100, self._Drag)
			if event.button == MB_Left:
				self.findClickSelection((event.x, event.y), state)
		elif event.type == gdk.BUTTON_RELEASE:
			if self.drag_click and(event.button == self.drag_click[2]):
				unWatch(self.tickID)
				self.drag_click = None
		elif event.type == gdk._2BUTTON_PRESS:
			print("Duo-Click")

	def zoom(self, zamt, center):
		cr = self.window.cairo_create()
		if zamt>1 and self.zoomscale<64 or zamt<1 and self.zoomscale>1/64.:
			self.zoomscale *= zamt
		#print("Zoom scale: %g" % self.zoomscale)
		self._reset_ctm(cr)
		old_pos = Pnt(cr.device_to_user(*center))
		self._rescale()
		self._reset_ctm(cr)
		new_pos = Pnt(cr.device_to_user(*center))
		self.pos += new_pos - old_pos
		self.redraw()

	def _mouseScroll(self, widget, event):
		zamt = 0.5 if (event.direction == gdk.SCROLL_DOWN) else 2
		self.zoom(zamt, (event.x, event.y))
		return True

	def _reshape(self):
		self.size = Pnt(self.window.get_size())
		self._rescale()
		self.pos = (self.size//self.scale-self.drawer_area)/2-self.min

	def _get_scale(self, src, dst):
		(sw, sh) = src
		(dw, dh) = dst
		return min(float(dw) / sw, float(dh) / sh)

	_rescale = lambda self: setattr(self, 'scale',  self._get_scale(self.drawer_area, self.size) * self.zoomscale)
	#def _rescale(self):
		#self.scale = self._get_scale(self.drawer_area, self.size) * self.zoomscale

	def _reset_ctm(self, cr):
		cr.identity_matrix()
		cr.scale(self.scale, self.scale)
		cr.translate(*self.pos)
		l = 6
		self.clickRadius = r = cr.device_to_user_distance(l, l)[0]
		self.drawer.selectRadius(r)

	def draw(self, x, y, w, h):
		cr = self.window.cairo_create()
		# Restrict Cairo to the exposed area; avoid extra work
		cr.rectangle(x, y, w, h)
		cr.clip()
		# Fill the background with black
		cr.set_source_rgb(0., 0., 0.)
		cr.rectangle(x, y, w, h)
		cr.fill()
		# Initialize coordinate transformations (panning, zooming)
		self._reset_ctm(cr)
		self.drawer.draw(cr)

	redraw = lambda self: self.draw(0, 0, *self.size)

	def do_expose_event(self, event):
		#if self.invalidData:
			#self.window.draw_rectangle(self.get_style().black_gc, True, 0, 0, *self.window.get_size())
			#return
		if self.window.get_size() != self.size:
			self._reshape()
		self.draw(event.area.x, event.area.y, event.area.width, event.area.height)

	def refresh(self):
		#self._reshape()
		self.queue_draw()
