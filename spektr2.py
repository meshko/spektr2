#!/usr/bin/env python3
import wx
import sys
import math

class Settings:
    def __init__(self):
        self.rect_width = 20
        self.rect_height = 80
        self.rect_color = wx.RED
        self.background_color = wx.Colour(200,200,200)
        self.line_color = wx.BLUE
        self.line_width = 4
        self.line_angle = 45


class SettingsDialog(wx.Dialog):

    def __init__(self, parent, *args, **kw):
        super(SettingsDialog, self).__init__(parent, *args, **kw)
        self.parent = parent                
        self.InitUI()
        #self.SetSize((250, 200))
        self.Fit()
        self.SetTitle("Настройки")


    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        #sb = wx.StaticBox(pnl, label='Colors')
        #sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        sbs = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.StaticText(pnl, label="Background color"), flag=wx.ALIGN_RIGHT) 
        bgPicker = wx.ColourPickerCtrl(pnl, name='Background color', colour=self.parent.settings.background_color)
        hbox.Add(bgPicker, flag=wx.ALIGN_RIGHT)
        hbox.SetSizeHints(self)
        sbs.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.StaticText(pnl, label="Rectangle color")) 
        recPicker = wx.ColourPickerCtrl(pnl, name='Background color', colour=self.parent.settings.rect_color)
        hbox.Add(recPicker, 0, wx.ALIGN_RIGHT, 0)
        hbox.SetSizeHints(self)
        sbs.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.StaticText(pnl, label="Line color")) 
        linePicker = wx.ColourPickerCtrl(pnl, name='Background color', colour=self.parent.settings.line_color)
        hbox.Add(linePicker, 0, wx.ALIGN_RIGHT, 0)
        hbox.SetSizeHints(self)
        sbs.Add(hbox)

        #hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        #hbox1.Add(wx.RadioButton(pnl, label='Custom'))
        #hbox1.Add(wx.TextCtrl(pnl), flag=wx.LEFT, border=5)
        #sbs.Add(hbox1)

        # line
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.Slider(pnl, value=self.parent.settings.line_width, minValue=1, maxValue=10, style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL | wx.SL_LABELS))
        sbs.Add(hbox)
        # angle
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.Slider(pnl, value=self.parent.settings.line_angle, minValue=10, maxValue=80, style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL | wx.SL_LABELS))
        sbs.Add(hbox)
        # rectangle height
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.Slider(pnl, value=self.parent.settings.rect_height, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL | wx.SL_LABELS))
        sbs.Add(hbox)
        # rectangle width
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.Slider(pnl, value=self.parent.settings.rect_width, minValue=0, maxValue=30, style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL | wx.SL_LABELS))
        sbs.Add(hbox)

        pnl.SetSizer(sbs)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, id=wx.ID_OK, label='OK')
        cancelButton = wx.Button(self, id=wx.ID_CANCEL, label='Cancel')
        hbox2.Add(okButton)
        hbox2.Add(cancelButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)


class View(wx.Panel):
    def __init__(self, parent, settings):
        super(View, self).__init__(parent)
        self.settings = settings
        self.results = []
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        button = wx.Button(self, label = "Настройки", pos = (10,10), size=(120, 20))
        button.Bind(wx.EVT_BUTTON, self.on_settings)
        button = wx.Button(self, label = "Результаты", pos = (10,40), size=(120, 20))
        button.Bind(wx.EVT_BUTTON, self.on_results)
        button = wx.Button(self, label = "Помощь", pos = (10,70), size=(120, 20))
        button.Bind(wx.EVT_BUTTON, self.on_help)
        button = wx.Button(self, label = "Выход", pos = (10,100), size=(120, 20))
        button.Bind(wx.EVT_BUTTON, self.on_exit)

        self.line_pos = 0

    def on_size(self, event):
        event.Skip()
        w = event.Size.Width
        h = event.Size.Height
        #print("resize: %s" % event)
        self.rect_width = w * self.settings.rect_width / 100.0 
        self.rect_height = h * self.settings.rect_height / 100.0 
        self.rect_x = w / 2 - self.rect_width/2
        self.line_start_x = self.rect_x / 2
        self.line_x_len = (self.rect_x / 2 ) # remove rect_width
        self.line_y_len = self.line_x_len * math.tan(math.radians(self.settings.line_angle))
        self.line2_start_x = self.line_start_x + self.rect_x / 2 + self.rect_width

        self.Refresh()

    def on_paint(self, event):
        w, h = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.settings.background_color))
        dc.Clear()        
        dc.SetBrush(wx.Brush(self.settings.rect_color))
        dc.SetPen(wx.Pen(self.settings.rect_color))
        dc.DrawRectangle(self.rect_x, h - self.rect_height, self.rect_width, self.rect_height)
        dc.SetPen(wx.Pen(self.settings.line_color, width=self.settings.line_width))
        dc.DrawLine(self.line_start_x, h, self.line_start_x + self.line_x_len, h - self.line_y_len)
        dc.DrawLine(self.line2_start_x, h - self.line_pos, self.line2_start_x + self.line_x_len, h - self.line_y_len - self.line_pos)

    def on_key_down(self, event):
        keycode = event.GetKeyCode()    
        _, h = self.GetClientSize()      
        if keycode == wx.WXK_UP:                
            if self.line_pos < h: self.line_pos += 1
            self.Refresh()
        elif keycode == wx.WXK_DOWN:
            if self.line_pos > 0: self.line_pos -= 1
            self.Refresh()
        elif keycode == wx.WXK_ESCAPE:            
            sys.exit(0)
        elif keycode == wx.WXK_RETURN:        
            self.results += [int(self.line_y_len - self.line_pos)]            
            self.line_pos = 0
            self.Refresh()
    
    def on_settings(self, event):
        cdDialog = SettingsDialog(self)
        if cdDialog.ShowModal() == wx.ID_OK:
            print("oked")
        else:
            print("cancelled")
        cdDialog.Destroy()
    def on_results(self, event):
        print("butt")
    def on_help(self, event):
        print("help")
    def on_exit(self, event):
        sys.exit(0)


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('Спектр 2')
        self.SetClientSize((800, 600))
        self.Center()
        self.view = View(self, Settings())


def main():
    app = wx.App(False)
    frame = Frame()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
