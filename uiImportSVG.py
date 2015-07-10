#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-

from os import chdir as cd, path as ph
from sys import path as ptSys

from gtk import Fixed
from gobject import TYPE_STRING as goStr, TYPE_BOOLEAN as goBool, TYPE_INT as goInt, TYPE_PYOBJECT as goPyObj


from pcbnew import FromMils, FromMM, ToMils, ToMM

class rasterMetricMils(Fixed):
	def __init__(fixed, txtLabel, parentFixed, apw, x, y, wtype=None, rangeMM=None, rangeMils=None, step=None, fontDesc=None):
		def getTxtPixelWidth(widget, txt, fontDesc=None):
			pangoLayout = widget.create_pango_layout(txt)
			if fontDesc:
				pangoLayout.set_font_description(fontDesc)
			pangoTxtSpc = pangoLayout.get_pixel_size()[0]
			del(pangoLayout)
			return pangoTxtSpc
		def inTest(in_):
			if hasattr(in_, '__getitem__') and(hasattr(in_, '__iter__'))\
				and(hasattr(in_, '__len__')) and(len(in_)==2):
					try:
						coerce(*in_)
					except Exception:
						return False
					return True
			return False
		def partDigits(val_):
			val_txt = "%g" % val_
			if not('.' in val_txt):
				return 0
			return len(val_txt.split('.')[1])
		if inTest(step):
			stMM, stMils = step
		else:
			stMM = 0.01
			stMils = 0.5
		if inTest(rangeMM):
			bNoRangeMM = False
			minMM, maxMM = rangeMM
			minMils, maxMils = ToMils(FromMM(minMM)), ToMils(FromMM(maxMM))
		else:
			bNoRangeMM = True
			minMM, maxMM = 0, 500
		if inTest(rangeMils):
			minMils, maxMils = rangeMils
			if bNoRangeMM:
				minMM, maxMM = ToMM(FromMils(minMils)), ToMM(FromMils(maxMils))
		else:
			minMils, maxMils = 0, 19685.039
		pdMM = max(map(partDigits, (stMM, minMM, maxMM)))
		pdMils = max(map(partDigits, (stMils, minMils, maxMils)))
		super(Fixed, fixed).__init__()
		if wtype=='butt':
			fixed.Butt = apw.Butt(txtLabel, fixed, 0, 0, 40)
			cw = getTxtPixelWidth(fixed.Butt, txtLabel, fontDesc=fontDesc)+8
			fixed.Butt.set_size_request(cw, apw.Height)
			fixed.clicked_action = lambda callback: fixed.Butt.connect("clicked", lambda xargs: callback())
		elif wtype=='chck':
			fixed.Check = apw.Check(txtLabel, fixed, 0, 0, 40)
			cw = getTxtPixelWidth(fixed.Check, txtLabel, fontDesc=fontDesc)+15
			fixed.Check.set_size_request(cw, apw.Height)
		else:
			fixed.Label = apw.Label(txtLabel, fixed, 0, 0, 40)
			cw = getTxtPixelWidth(fixed.Label, txtLabel, fontDesc=fontDesc)+8
			fixed.Label.set_size_request(cw, apw.Height)
		fixed.MM = apw.Num((0, minMM, maxMM, stMM), fixed, cw, 0, 70, partDigits=pdMM)
		apw.Label("mm=", fixed, cw+72, 0, 23)
		fixed.Mils = apw.Num((0, minMils, maxMils, stMils), fixed, cw+95, 0, 70, partDigits=pdMils)
		apw.Label("mils", fixed, cw+165, 0, 20)
		parentFixed.put(fixed, x, y)
		fixed.MM.connect("value-changed", fixed.units)
		fixed.Mils.connect("value-changed", fixed.units)
		fixed.set_value(0)
		if wtype=='chck':
			def toggled(widget):
				bCheck = widget.get_active()
				fixed.Mils.set_sensitive(bCheck)
				fixed.MM.set_sensitive(bCheck)
			fixed.Check.connect("toggled", fixed.toggled)
			def set_checked(bCheck):
				fixed.Check.set_active(bCheck)
				fixed.Mils.set_sensitive(bCheck)
				fixed.MM.set_sensitive(bCheck)
			fixed.set_checked = set_checked
			fixed.get_checked = lambda: fixed.Check.get_active()
		fixed.wtype = wtype

	def units(fixed, intOrWidget):
		if intOrWidget==fixed.MM:
			fixed.value = FromMM(intOrWidget.get_value())
			testVal =  FromMils(fixed.Mils.get_value())
			if fixed.value != testVal:
				setV = ToMils(fixed.value)
				fixed.Mils.set_value(setV)
				if hasattr(fixed, 'logView'):
					fixed.logView.insert_end("%gmils\n" % setV)
		elif intOrWidget==fixed.Mils:
			fixed.value = FromMils(intOrWidget.get_value())
			testVal =  FromMM(fixed.MM.get_value())
			if fixed.value != testVal:
				setV = ToMM(fixed.value)
				fixed.MM.set_value(setV)
				if hasattr(fixed, 'logView'):
					fixed.logView.insert_end("%gmm\n" % setV)
		elif type(intOrWidget)==int:
			fixed.value = intOrWidget
			fixed.MM.set_value(ToMM(intOrWidget))
			fixed.Mils.set_value(ToMils(intOrWidget))

	set_logtextview = lambda fixed, logview: setattr(fixed, 'logView', logview)

	set_value = lambda fixed, value: fixed.units(value)
	get_value = lambda fixed: fixed.value

class uiSvgImport(object):
	def __init__(ui):
		rundir = ph.expanduser('~/Devel/Python')
		ptSys.append(rundir)
		import appWidgets
		ui.apw = appWidgets.apw()
		apw = ui.apw
		gtk = apw.gtk
		pango = apw.pango
		ui.fontDesc = pango.FontDescription('Univers Condensed 8')
		ui.fontSmall = pango.FontDescription('Univers Condensed 7')
		ui.fontFixedDesc = pango.FontDescription('Terminus Bold 7')
		apw.descFontTvEntry = ui.fontDesc
		apw.BGcolor = gtk.gdk.Color('#383430')
		apw.FGcolor = gtk.gdk.Color('#FFF')
		apw.BGcolorEntry = gtk.gdk.Color('#201810')
		apw.Height = 25
		ui.uiInit()
		if __name__ == "__main__":
			ui.mainWindow.connect("destroy", lambda w: ui.uiExit())
			ui.buttonExit.connect("clicked", lambda w: ui.uiExit())
			ui.uiEnter()

	uiEnter = lambda ui: ui.apw.gtk.main()
	uiExit = lambda ui: ui.apw.gtk.main_quit()

	def uiInit(ui):
		from gobject import TYPE_STRING as goStr, TYPE_INT as goInt, TYPE_PYOBJECT as goPyObj
		ui.cfg = {}
		apw = ui.apw
		gtk = apw.gtk
		apw.rcGet(use_common_rc=True)
		ui.version = .3
		ui.title = "PCBnew python module based svg Import v.%0.2f. For BZR>5200" % ui.version
		ui.mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
		ui.wdhMain, ui.hgtMain = 600, 500
		ui.mainWindow.set_geometry_hints(min_width=ui.wdhMain, min_height=ui.hgtMain)
		#ui.mainWindow.resize(980, 750)
		ui.mainWindow.set_title(ui.title)
		ui.mainWindow.set_border_width(5)
		ui.accGroup = gtk.AccelGroup()
		ui.mainWindow.add_accel_group(ui.accGroup)
		
		ui.mainWindow.modify_bg(gtk.STATE_NORMAL, apw.BGcolor)
		# # # # # # # # # # # # # # # # # # # # # # # # #
		mainFrame = ui.mainFrame = gtk.Fixed()
		from svgDisplay import svgCairo
		ui.Display = svgCairo(mainFrame, 10, 10)
		ui.logView = apw.TextView(mainFrame, 0, 0, 0, 0, bEditable=False, fontDesc=ui.fontFixedDesc)

		ui.FitW = rasterMetricMils("Fit Width To:", mainFrame, apw, 0, 0, step=(0.05, 2))
		ui.FitH = rasterMetricMils("Fit Height To:", mainFrame, apw, 0, 0, step=(0.05, 2))

		ui.logoBigPixbuf = gtk.gdk.pixbuf_new_from_file(ph.realpath(ph.expanduser("img/svg-pcb.svg")))
		gtk.window_set_default_icon_list(ui.logoBigPixbuf, )
		ui.imageLogo = gtk.Image()
		ui.imageLogo.set_from_pixbuf(ui.logoBigPixbuf)
		mainFrame.put(ui.imageLogo, 0, 0)

		ui.labFilenameSVG = apw.Label("SVG File:", mainFrame, 0, 0, 50)
		if __name__ == "__main__":
			ui.txtFilenameSVG = apw.Butt('Test', mainFrame, 0, 0, 0)
		else:
			ui.txtFilenameSVG = apw.Label(u'Drag file to log view or use „Open” button →',
				mainFrame, 0, 0, 0, xalign=0., selectable=True)

		ui.buttonOpen = ui.apw.Butt(None, mainFrame, 0, 0, 30, stockID=gtk.STOCK_OPEN)
		ui.buttonOpen.set_tooltip_text('Open')
		ui.buttonReOpen = ui.apw.Butt(None, mainFrame, 0, 0, 30, stockID=gtk.STOCK_REFRESH)
		ui.buttonReOpen.set_tooltip_text('Reload')

		ui.labFilenamePCB = apw.Label("PCB File:", mainFrame, 0, 0, 50)
		if __name__ == "__main__":
			ui.txtFilenamePCB = apw.Butt('Test', mainFrame, 0, 0, 0)
		else:
			ui.txtFilenamePCB = apw.Label(u'Drag file to log view or use „Open” button →',
				mainFrame, 0, 0, 0, xalign=0., selectable=True)

		ui.buttonFileToSave = ui.apw.Butt('…', mainFrame, 0, 0, 30)
		ui.buttonFileToSave.set_tooltip_text('Open')
		ui.buttonSave = ui.apw.Butt(None, mainFrame, 0, 0, 30, stockID=gtk.STOCK_SAVE)
		ui.buttonSave.set_tooltip_text('Save')
		ui.buttonRestore = ui.apw.Butt(None, mainFrame, 0, 0, 30, stockID=gtk.STOCK_REVERT_TO_SAVED)
		ui.buttonRestore.set_tooltip_text('Restore from Backup')

		ui.checkDebugDraw = apw.Check("Debug Draw", mainFrame, 0, 0, 80)
		ui.buttonTest = ui.apw.Butt(None, mainFrame, 0, 0, 30, stockID=gtk.STOCK_PRINT_REPORT)
		ui.buttonTest.set_tooltip_text('Test')
		ui.buttonClear = apw.Butt("Clear Log", mainFrame, 0, 0, 55)
		ui.buttonExit = apw.Butt("Exit (Ctrl+Q)", mainFrame, 0, 0, 80)
		ui.buttonExit.add_accelerator( "clicked", ui.accGroup,
			ord('Q'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
		ui.mainWindow.add(mainFrame)
		ui.mainWindow.show_all()
		ui.mainWindow.set_keep_above(True)
		ui.lastWinSize = None
		ui.mainWindow.connect("configure-event", ui.uiSize)
		ui.dialogPath()

	def uiSize(ui, window, event):
		if event.type==ui.apw.gtk.gdk.CONFIGURE:
			w, h = event.width, event.height
			if ui.lastWinSize==(w, h):
				return True
			stdH = ui.apw.Height
			ui.lastWinSize = w, h
			mf = ui.mainFrame
			w0 = w-30
			dy = stdH+5
			buttH = dy*4+25
			dsplMargin = 10
			dsplH = (h-buttH)*3/4
			ui.Display.set_size_request(w0, dsplH)
			logH = h-dsplH-buttH-2*dsplMargin
			mf.move(ui.logView.parent, 10, dsplH+2*dsplMargin)
			ui.logView.set_size_request(w0, logH)
			y1 = dsplH+logH+2*dsplMargin+10
			mf.move(ui.FitW, 10, y1)
			mf.move(ui.FitH, 280, y1)
			x2 = 130
			y2 = y1+dy
			mf.move(ui.imageLogo, 0, y2)
			mf.move(ui.labFilenameSVG, 50, y2)
			mf.move(ui.txtFilenameSVG, 100, y2)
			ui.txtFilenameSVG.set_size_request(w-190, stdH)
			mf.move(ui.buttonOpen, w-85, y2)
			mf.move(ui.buttonReOpen, w-50, y2)
			y3 = y2+dy
			mf.move(ui.labFilenamePCB, 50, y3)
			mf.move(ui.txtFilenamePCB, 100, y3)
			ui.txtFilenamePCB.set_size_request(w-225, stdH)
			mf.move(ui.buttonFileToSave, w-120, y3)
			mf.move(ui.buttonSave, w-85, y3)
			mf.move(ui.buttonRestore, w-50, y3)
			y4 = y3+dy
			mf.move(ui.checkDebugDraw, 10, y4)
			mf.move(ui.buttonTest, 100, y4)
			mf.move(ui.buttonClear, w-160, y4)
			mf.move(ui.buttonExit, w-100, y4)
			#print("Event:  w:%i, h:%i" % (w, h))
		return True

	def dialogPath(ui):
		apw = ui.apw
		gtk = apw.gtk
		dlgMain = ui.dlgPath = gtk.Window(gtk.WINDOW_TOPLEVEL)
		dlgMain.set_geometry_hints(min_width=310, min_height=400,
			width_inc=0,
			#max_width=360, max_height=400
			)
		dcWgt = dlgMain.dcWgt = {}
		dcWgt['Name'] = 'dlgPath'
		dlgMain.add_accel_group(ui.accGroup)
		dlgMain.set_border_width(5)
		dlgMain.set_resizable(True)
		dlgMain.set_title('Draw Polygon Properities')
		dlgMain.set_transient_for(ui.mainWindow)
		dlgMain.set_destroy_with_parent(True)
		dlgMain.set_deletable(False)
		dlgMain.set_skip_taskbar_hint(False)
		dlgMain.modify_bg(gtk.STATE_NORMAL, ui.apw.BGcolor)
		# # # # # # # # # # # # # # # # # # # # # # # # #
		dlgFrame = dcWgt['dlgMainFrame'] = gtk.Fixed()
		tempWgtHeight = apw.Height
		apw.Height = 20

		lsPtSetDP = dcWgt['mdlPointsetDP'] = gtk.ListStore(goStr, goStr, goInt)
		tvPointsetDP = dcWgt['PointsetDP'] = gtk.TreeView(lsPtSetDP)
		tvSel = tvPointsetDP.get_selection()
		tvSel.set_mode(gtk.SELECTION_MULTIPLE)
		#Column #1 - Value
		lsProps = (
			('cell-background-gdk', gtk.gdk.Color('#5A0')),
			('editable', False))
		tvcPointsDP, crtxtPointsDP = apw.TreeTxtColumn('Points', 100, (0,), lsProps, fontDesc=ui.fontSmall)
		tvPointsetDP.append_column(tvcPointsDP)
		tvPointsetDP.set_tooltip_column(1, )
		tvPointsetDP.set_reorderable(True)
		tvPointsetDP.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color('#131'))
		apw.putScroll(dlgFrame, tvPointsetDP, 0, 0, 10, 10)

		dcWgt['FrameSel'] = apw.Frame('Selection', dlgFrame, 0, 0, 10, 10)
		tmpFx = dcWgt['SelFx'] = gtk.Fixed()
		xf, yf = 0, 0
		dcWgt['CommX'] = apw.Num((0, -1000000, 1000000, 1), tmpFx, xf+5, yf, 70)
		dcWgt['SetX'] = apw.Butt("Set X", tmpFx, xf+78, yf, 40)
		dcWgt['SetX'].set_tooltip_text("Set Common X for selection")
		yf += 25
		dcWgt['CommY'] = apw.Num((0, -1000000, 1000000, 1), tmpFx, xf+125, yf, 70)
		dcWgt['SetY'] = apw.Butt("Set Y", tmpFx, xf+198, yf, 40)
		dcWgt['SetY'].set_tooltip_text("Set Common Y for selection")
		yf += 25
		dcWgt['ArrLoX'] = apw.Butt("⇤", tmpFx, xf+5, yf, 20)
		dcWgt['ArrLoX'].set_tooltip_text("Arrange To Lowest X from selection")
		dcWgt['ArrHiX'] = apw.Butt("⇥", tmpFx,xf+ 30, yf, 20)
		dcWgt['ArrHiX'].set_tooltip_text("Arrange To Highest X from selection")
		dcWgt['ArrLoY'] = apw.Butt("⤒", tmpFx, xf+55, yf, 20)
		dcWgt['ArrLoY'].set_tooltip_text("Arrange To Lowest Y from selection")
		dcWgt['ArrHiY'] = apw.Butt("⤓", tmpFx, xf+80, yf, 20)
		dcWgt['ArrHiY'].set_tooltip_text("Arrange To Highest Y from selection")
		dcWgt['Split'] = apw.Butt("Split", tmpFx, xf+105, yf, 40)
		ls45deg = gtk.ListStore(goStr,)
		for way in('↗', '↘', '↙', '↖'):
			ls45deg.append((way, ))
		dcWgt['lb45deg'] = apw.ComboBox(ls45deg, tmpFx, xf+152, yf-1, 40, wrap=2)
		dcWgt['lb45deg'].set_active(0)
		dcWgt['Round45deg'] = apw.Butt("45°", tmpFx, xf+195, yf, 30)
		dcWgt['DelPts'] = apw.Butt("Delete", tmpFx, xf+250, yf, 50)
		dcWgt['FrameSel'].add(tmpFx)

		dcWgt['Apply'] = apw.Butt("Apply", dlgFrame, 0, 0, 40)
		dcWgt['OK'] = apw.Butt("OK", dlgFrame, 0, 0, 40)

		dlgMain.add(dlgFrame)
		dlgMain.show_all()
		dcWgt['lastWinSize'] = None
		def Size(dlgMain, event):
			dcWgt = dlgMain.dcWgt
			if event.type==gtk.gdk.CONFIGURE:
				w, h = event.width, event.height
				if dcWgt['lastWinSize']==(w, h):
					return True
				dlgFrame = dcWgt['dlgMainFrame']
				#print("Resize: (%i, %i)" % (w, h ))
				dcWgt['lastWinSize'] = w, h
				y = h-135
				dcWgt['PointsetDP'].parent.set_size_request(w-10, y)
				fSel = dcWgt['FrameSel']
				fSel.set_size_request(w-10, 90)
				dlgFrame.move(fSel, 0, y)
				dcWgt['SelFx'].move(dcWgt['DelPts'], w-67, 50)
				y += 100
				dlgFrame.move(dcWgt['Apply'], w-95, y)
				dlgFrame.move(dcWgt['OK'], w-50, y)

		dlgMain.connect("configure-event", Size)
		apw.setFrameFont(dlgFrame, ui.fontSmall)
		apw.Height = tempWgtHeight

	def uiHideDlg(ui, dlgUI, bStore=True):
		dcWgt = dlgUI.dcWgt
		if dlgUI.get_property("visible"):
			if bStore:
				store = ui.cfg[dcWgt['Name']+'Pos'] = "%i,%i" % dlgUI.get_position()
				#print("Store: %sPos=%s" % (dcWgt['Name'], store))
			dlgUI.hide()

	def uiDlgSetPos(ui, dlgUI, bUpper=False):
		dcWgt = dlgUI.dcWgt
		if dcWgt.get('Name'):
			if hasattr(ui, 'cfg'):
				nKey = dcWgt['Name']+'Pos'
				posTxt = ui.cfg.get(nKey)
				if posTxt:
					pos = tuple(map(int, posTxt.split(',')))
					#print("Load: %sPos=%i,%i" % ((dcWgt['Name'],) + pos))
					dlgUI.move(*pos)
				else:
					dw, dh = dlgUI.get_size()
					w, h = tuple(dlgUI.window.get_frame_extents())[2:]
					print("Dialog: %s, w:%i, h:%i, dw:%i, dh:%i" % (dlgUI.get_title(), w, h, dw, dh))
					ui = ui
					#mx, my = ui.mainWindow.get_position()
					mx, my = tuple(ui.mainWindow.window.get_frame_extents())[:2]
					if bUpper:
						dlgUI.move(mx, my-h)
					else:
						dlgUI.move(mx-w, my)

	def uiShowDlg(ui, dlgUI, bUpper=False):
		dlgUI.present()
		ui.uiDlgSetPos(dlgUI, bUpper=bUpper)
		dlgUI.set_keep_above(True)

	def storeGeometry(ui):
		for dlgTxt in('Path', ):
			ui.uiHideDlg(getattr(ui, 'dlg'+dlgTxt))
		lsGeo = map(lambda i: "%i" % i, tuple(ui.mainWindow.window.get_frame_extents()))
		ui.cfg['MainWindowGeometry'] = ','.join(lsGeo)
		print("Storing Main Window Geometry: %s" % ', '.join(lsGeo))

	def restoreGeometry(ui):
		if hasattr(ui, 'cfg'):
			txtGeo = ui.cfg.get('MainWindowGeometry')
			if txtGeo:
				x, y, w, h = tuple(map(int, txtGeo.split(',')))
				print("Main Window: %s,\n\tx:%i, y:%i, w:%i, h:%i" % (ui.mainWindow.get_title(), x, y, w, h))
				ui.mainWindow.set_size_request(w, h)
				#ui.mainWindow.resize(w, h)
				#ui.mainWindow.show_all()
				ui.mainWindow.move(x, y)
				ui.mainWindow.set_default_size(w, h)
		else:
			print("No UI cfg…")

if __name__ == "__main__":
	uiSvgImport()
