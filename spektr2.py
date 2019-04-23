#!/usr/bin/env python3
import wx
import sys
import math
import json
from copy import copy


class Settings:
    def __init__(self):
        self.rect_width = 20
        self.rect_height = 80
        self.rect_color = wx.RED
        self.background_color = wx.Colour(200, 200, 200)
        self.line_color = wx.BLUE
        self.line_width = 4
        self.line_angle = 45

    def to_json(self):
        return json.dumps({'rect_width': self.rect_width,
                           'rect_height': self.rect_height,
                           'rect_color': self.rect_color.GetAsString(wx.C2S_HTML_SYNTAX),
                           'bg_color': self.background_color.GetAsString(wx.C2S_HTML_SYNTAX),
                           'line_color': self.line_color.GetAsString(wx.C2S_HTML_SYNTAX),
                           'line_width': self.line_width,
                           'line_angle': self.line_angle})

    def from_json(self, json_str):
        js = json.loads(json_str)
        self.rect_width = js['rect_width']
        self.rect_height = js['rect_height']
        self.line_width = js['line_width']
        self.line_angle = js['line_angle']
        self.rect_color = wx.Colour(js['rect_color'])
        self.background_color = wx.Colour(js['bg_color'])
        self.line_color = wx.Colour(js['line_color'])


class ResultsDialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        super(ResultsDialog, self).__init__(parent, *args, **kw)
        self.parent = parent
        self.SetTitle("Результаты")
        self.result_str = "\n".join(map(str, parent.results))
        self.result_str += "\n"
        self.result_str += 'Среднее: ' + str(sum(parent.results) / len(parent.results))
        text_ctrl = wx.TextCtrl(self, size=(150,200), value=self.result_str, style=wx.TE_READONLY | wx.TE_CENTER | wx.TE_MULTILINE)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        cbButton = wx.Button(self, id=wx.ID_OK, label='Скопировать')
        cbButton.Bind(wx.EVT_BUTTON, self.on_clipboard)
        cbButton.SetDefault()
        cancelButton = wx.Button(self, id=wx.ID_CANCEL, label='Закрыть')
        clearButton = wx.Button(self, label="Очистить")
        hbox2.Add(cbButton)
        hbox2.Add(cancelButton, flag=wx.LEFT, border=5)
        hbox2.Add(clearButton, flag=wx.LEFT, border=5)
        clearButton.Bind(wx.EVT_BUTTON, self.on_clear)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(text_ctrl, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        self.SetSizer(vbox)
        self.Fit()

    def on_clipboard(self, e):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.result_str))
            wx.TheClipboard.Close()
        self.Close()

    def on_clear(self, e):
        self.parent.results = []
        self.Close()


class SettingsDialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        super(SettingsDialog, self).__init__(parent, *args, **kw)
        self.parent = parent
        self.InitUI()
        # self.SetSize((250, 200))
        self.Fit()
        self.SetTitle("Настройки")

    def create_color_picker(self, parent, text, name, color):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.StaticText(parent, label=text), flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        picker = wx.ColourPickerCtrl(parent, name=name, colour=color)
        hbox.Add(picker, proportion=1, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        picker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_color_picked)
        return hbox

    def on_color_picked(self, e):
        color_picker = e.GetEventObject()
        if color_picker.GetName() == "Background":
            self.parent.settings.background_color = color_picker.GetColour()
        elif color_picker.GetName() == "Rectangle":
            self.parent.settings.rect_color = color_picker.GetColour()
        elif color_picker.GetName() == "Line":
            self.parent.settings.line_color = color_picker.GetColour()
        self.parent.Refresh()

    def create_slider(self, parent, text, name, val, min_val, max_val):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.StaticText(parent, label=text), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        slider = wx.Slider(parent, name=name, value=val, minValue=min_val, maxValue=max_val,
                           style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL | wx.SL_LABELS)
        hbox.Add(slider)
        # slider.Bind(wx.EVT_SCROLL_CHANGED, self.on_slider)
        slider.Bind(wx.EVT_SCROLL, self.on_slider)
        return hbox

    def on_slider(self, e):
        slider = e.GetEventObject()
        if slider.GetName() == "line_width":
            self.parent.settings.line_width = e.GetPosition()
        elif slider.GetName() == "line_angle":
            self.parent.settings.line_angle = e.GetPosition()
        elif slider.GetName() == "rect_width":
            self.parent.settings.rect_width = e.GetPosition()
        elif slider.GetName() == "rect_height":
            self.parent.settings.rect_height = e.GetPosition()
        self.parent.force_recalc()
        self.parent.Refresh()

    def InitUI(self):
        pnl = wx.Panel(self)

        sbs = wx.BoxSizer(wx.VERTICAL)
        sbs.Add(self.create_color_picker(pnl, "Цвет фона", "Background", self.parent.settings.background_color), proportion=1, flag=wx.ALIGN_CENTER)
        sbs.Add(self.create_color_picker(pnl, "Цвет прямоугольника", "Rectangle", self.parent.settings.rect_color), proportion=1, flag=wx.ALIGN_CENTER)
        sbs.Add(self.create_color_picker(pnl, "Цвет линии", "Line", self.parent.settings.line_color), proportion=1, flag=wx.ALIGN_CENTER)

        sbs.Add(self.create_slider(pnl, "Толщина линии", "line_width", self.parent.settings.line_width, 1, 10), proportion=1, flag=wx.ALIGN_RIGHT)
        sbs.Add(self.create_slider(pnl, "Угол линии", "line_angle", self.parent.settings.line_angle, 10, 80), proportion=1, flag=wx.ALIGN_RIGHT)
        sbs.Add(self.create_slider(pnl, "Ширина прямоугольника", "rect_width", self.parent.settings.rect_width, 0, 50), proportion=1, flag=wx.ALIGN_RIGHT)
        sbs.Add(self.create_slider(pnl, "Высота прямоугольника", "rect_height", self.parent.settings.rect_height, 0, 100), proportion=1, flag=wx.ALIGN_RIGHT)

        pnl.SetSizer(sbs)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, id=wx.ID_OK, label='OK')
        okButton.SetDefault()
        cancelButton = wx.Button(self, id=wx.ID_CANCEL, label='Cancel')
        hbox2.Add(okButton)
        hbox2.Add(cancelButton, flag=wx.LEFT, border=5)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(pnl, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)

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

        button = wx.Button(self, label="Настройки", pos=(10, 10), size=(120, 20))
        button.Bind(wx.EVT_BUTTON, self.on_settings)
        button = wx.Button(self, label="Результаты", pos=(10, 40), size=(120, 20))
        button.Bind(wx.EVT_BUTTON, self.on_results)
        button = wx.Button(self, label="Помощь", pos=(10, 70), size=(120, 20))
        button.Bind(wx.EVT_BUTTON, self.on_help)
        button = wx.Button(self, label="Выход", pos=(10, 100), size=(120, 20))
        button.Bind(wx.EVT_BUTTON, self.on_exit)

        try:
            with open('spektr2.json', 'r') as config_file:
                self.settings.from_json("\n".join(config_file.readlines()))
        except Exception as ex:
            print(ex)
        self.line_pos = 0

    def on_size(self, event):
        event.Skip()
        w = event.Size.Width
        h = event.Size.Height
        self.calc_sizes(w, h)
        self.Refresh()

    def force_recalc(self):
        w, h = self.GetClientSize()
        self.calc_sizes(w, h)

    def calc_sizes(self, w, h):
        self.rect_width = w * self.settings.rect_width / 100.0
        self.rect_height = h * self.settings.rect_height / 100.0
        self.rect_x = w / 2 - self.rect_width / 2
        self.line_start_x = self.rect_x / 2
        self.line_x_len = (self.rect_x / 2)  # remove rect_width
        self.line_y_len = self.line_x_len * math.tan(math.radians(self.settings.line_angle))
        self.line2_start_x = self.line_start_x + self.rect_x / 2 + self.rect_width


    def on_paint(self, event):
        w, h = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.settings.background_color))
        dc.Clear()

        dc.SetPen(wx.Pen(self.settings.line_color, width=self.settings.line_width))
        dc.DrawLine(self.line_start_x, h, self.line_start_x + self.line_x_len, h - self.line_y_len)
        dc.DrawLine(self.line2_start_x, h - self.line_pos, self.line2_start_x + self.line_x_len,
                    h - self.line_y_len - self.line_pos)

        dc.SetBrush(wx.Brush(self.settings.rect_color))
        dc.SetPen(wx.Pen(self.settings.rect_color))
        dc.DrawRectangle(self.rect_x, h - self.rect_height, self.rect_width, self.rect_height + 1)

    def on_key_down(self, event):
        keycode = event.GetKeyCode()
        _, h = self.GetClientSize()
        if keycode == wx.WXK_UP:
            if self.line_pos < self.rect_height: self.line_pos += 1
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
        old_settings = copy(self.settings)
        cdDialog = SettingsDialog(self)
        if cdDialog.ShowModal() != wx.ID_OK:
            self.settings = old_settings
            self.force_recalc()
            self.Refresh()
        else:
            try:
                json_str = self.settings.to_json()
                with open('spektr2.json', 'w') as config_file:
                    config_file.write(json_str)
            except Exception as ex:
                print(ex)
        cdDialog.Destroy()

    def on_results(self, event):
        if self.results:
            res = ResultsDialog(self)
            res.ShowModal()
            res.Destroy()

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
