
import ConfigParser
import os
import wx
from configtool.data import BSIZESMALL, offsetTcLabel

INIFILE = "configtool.ini"
DEFAULT_INIFILE = "configtool.default.ini"

ARDUINODIR = 0
CFLAGS = 1
LDFLAGS = 2
OBJCOPYFLAGS= 3
PROGRAMMER = 4
PORT = 5
UPLOADSPEED = 6
NUMTEMPS = 7
MINADC = 8
MAXADC = 9
T0 = 10
R1 = 11


class Settings:
  def __init__(self, app, folder):
    self.app = app
    self.cmdfolder = folder
    self.inifile = os.path.join(folder, INIFILE)
    self.section = "configtool"

    self.arduinodir = ""
    self.cflags = ""
    self.ldflags = ""
    self.objcopyflags = ""
    self.programmer = "wiring"
    self.port = "/dev/ttyACM0"
    self.uploadspeed = 38400

    self.t0 = 25;
    self.r1 = 0;
    self.numTemps = 25
    self.maxAdc = 1023
    self.minAdc = 1

    self.cfg = ConfigParser.ConfigParser()
    self.cfg.optionxform = str

    if not self.cfg.read(self.inifile):
      if not self.cfg.read(os.path.join(folder, DEFAULT_INIFILE)):
        print ("Neither of settings files %s or %s exist. Using default values."
               % (INIFILE, DEFAULT_INIFILE))
        return

    if self.cfg.has_section(self.section):
      for opt, value in self.cfg.items(self.section):
        value = value.replace('\n', ' ')
        if opt == "arduinodir":
          self.arduinodir = value
        elif opt == "cflags":
          self.cflags = value
        elif opt == "ldflags":
          self.ldflags = value
        elif opt == "programmer":
          self.programmer = value
        elif opt == "port":
          self.port = value
        elif opt == "objcopyflags":
          self.objcopyflags = value
        elif opt == "t0":
          self.t0 = value
        elif opt == "r1":
          self.r1 = value
        elif opt == "numtemps":
          self.numTemps = value
        elif opt == "maxadc":
          self.maxAdc = value
        elif opt == "minadc":
          self.minAdc = value
        elif opt == "uploadspeed":
          self.uploadspeed = value
        else:
          print "Unknown %s option: %s - ignoring." % (self.section, opt)
    else:
      print "Missing %s section - assuming defaults." % self.section

  def saveSettings(self):
    self.section = "configtool"
    try:
      self.cfg.add_section(self.section)
    except ConfigParser.DuplicateSectionError:
      pass

    self.cfg.set(self.section, "arduinodir", str(self.arduinodir))
    self.cfg.set(self.section, "cflags", str(self.cflags))
    self.cfg.set(self.section, "ldflags", str(self.ldflags))
    self.cfg.set(self.section, "objcopyflags", str(self.objcopyflags))
    self.cfg.set(self.section, "programmer", str(self.programmer))
    self.cfg.set(self.section, "port", str(self.port))
    self.cfg.set(self.section, "t0", str(self.t0))
    self.cfg.set(self.section, "r1", str(self.r1))
    self.cfg.set(self.section, "numtemps", str(self.numTemps))
    self.cfg.set(self.section, "maxadc", str(self.maxAdc))
    self.cfg.set(self.section, "minadc", str(self.minAdc))
    self.cfg.set(self.section, "uploadspeed", str(self.uploadspeed))

    try:
      cfp = open(self.inifile, 'wb')
    except:
      print "Unable to open settings file %s for writing." % self.inifile
      return
    self.cfg.write(cfp)
    cfp.close()


class SettingsDlg(wx.Dialog):
  def __init__(self, parent, settings):
    wx.Dialog.__init__(self, parent, wx.ID_ANY, "Modify settings",
                       size = (500, 300))
    self.SetFont(settings.font)
    self.settings = settings

    self.modified = False

    self.Bind(wx.EVT_CLOSE, self.onExit)

    htArdDir = "Where to find the arduino tools (avr-gcc, avrdude, etc). " \
               "This is only used for windows. For linux it is assumed that " \
               "the tools are available through the normal PATH."
    htCFlags = "Flags passed into the avr-gcc compiler. These flags can " \
               "have 3 different variables embedded within them:" \
               "\n\n  %F_CPU%   will be replaced by the value of the CPU " \
               "Clock Rate." \
               "\n\n  %CPU%     will be replaced by the value of the CPU. " \
               "\n\n  %ALNAME%  is the name of the source file being " \
               "compiled with the .c extension replaced by .al.\n\n" \
               "Note: the flag -save-temps=obj does not appear to be a " \
               "valid flag for win32. Omit the \"=obj\", or omit it entirely."
    htLDFlags = "Flags passed to avr-gcc to be passed on to the linker."
    htObjCopy = "Flags passed to avr-objcopy."
    htProgrammer = "The programmer type - passed to avrdude."
    htPort = "The port through which the firmware will be uploaded - " \
             "passed to avrdude."
    htSpeed = "The baud rate with which to communicate with the bootloader."
    htNumTemps = "The number of entries generated for the thermistor tables. " \
                 "Higher numbers slightly increase temperature reading " \
                 "accuracy, but also cost binary size. Default is 25."
    htMinAdc = "The minimum ADC value returned by the thermistor. Typically 0."
    htMaxAdc = "The maximum ADC value returned by the thermistor. " \
               "Typically 1023 (maximum of 10-bit ADCs)."
    htT0 = "The T0 value used for thermistor table calculation. Typically 25."
    htR1 = "The R1 value used for thermistor table calculation. Typically 0."

    # This table MUST be in the same order as the constants defined at
    # the top of this file.
    self.fields = [["Arduino Directory", settings.arduinodir, htArdDir],
                   ["C Compiler Flags", settings.cflags, htCFlags],
                   ["LD Flags", settings.ldflags, htLDFlags],
                   ["Object Copy Flags", settings.objcopyflags, htObjCopy],
                   ["AVR Programmer", settings.programmer, htProgrammer],
                   ["Port", settings.port, htPort],
                   ["Upload Speed", settings.uploadspeed, htSpeed],
                   ["Number of Temps", settings.numTemps, htNumTemps],
                   ["Minimum ADC value", settings.minAdc, htMinAdc],
                   ["Maximum ADC value", settings.maxAdc, htMaxAdc],
                   ["T0", settings.t0, htT0],
                   ["R1", settings.r1, htR1]]

    self.teList = []

    hsz = wx.BoxSizer(wx.HORIZONTAL)
    hsz.AddSpacer((10, 10))

    sz = wx.BoxSizer(wx.VERTICAL)
    sz.AddSpacer((10, 10))

    labelWidth = 140
    for f in self.fields:
      lsz = wx.BoxSizer(wx.HORIZONTAL)
      t = wx.StaticText(self, wx.ID_ANY, f[0], size = (labelWidth, -1),
                        style = wx.ALIGN_RIGHT)
      t.SetFont(settings.font)
      lsz.Add(t, 1, wx.TOP, offsetTcLabel)

      lsz.AddSpacer((8, 8))

      te = wx.TextCtrl(self, wx.ID_ANY, f[1], size = (600, -1))
      te.Bind(wx.EVT_TEXT, self.onTextCtrl)
      te.SetToolTipString(f[2])
      lsz.Add(te)
      self.teList.append(te)

      sz.Add(lsz)
      sz.AddSpacer((10, 10))

    sz.AddSpacer((20, 20))

    bsz = wx.BoxSizer(wx.HORIZONTAL)
    b = wx.Button(self, wx.ID_ANY, "Save", size = BSIZESMALL)
    b.SetFont(settings.font)
    self.Bind(wx.EVT_BUTTON, self.onSave, b)
    bsz.Add(b)
    self.bSave = b
    bsz.AddSpacer((5, 5))

    b = wx.Button(self, wx.ID_ANY, "Exit", size = BSIZESMALL)
    b.SetFont(settings.font)
    self.Bind(wx.EVT_BUTTON, self.onExit, b)
    bsz.Add(b)
    self.bExit = b

    sz.Add(bsz, 1, wx.ALIGN_CENTER_HORIZONTAL)
    sz.AddSpacer((10, 10))

    hsz.Add(sz)
    hsz.AddSpacer((10, 10))

    self.SetSizer(hsz)
    self.setModified(False)

    self.Fit()

  def setModified(self, flag):
    self.modified = flag
    if flag:
      self.bSave.Enable(True)
      self.bExit.SetLabel("Cancel")
    else:
      self.bSave.Enable(False)
      self.bExit.SetLabel("Exit")

  def onTextCtrl(self, evt):
    self.setModified(True)
    evt.Skip()

  def onSave(self, evt):
    self.saveValues()
    self.EndModal(wx.ID_OK)

  def saveValues(self):
    self.settings.arduinodir = self.teList[ARDUINODIR].GetValue()
    self.settings.cflags = self.teList[CFLAGS].GetValue()
    self.settings.ldflags = self.teList[LDFLAGS].GetValue()
    self.settings.objcopyflags = self.teList[OBJCOPYFLAGS].GetValue()
    self.settings.programmer = self.teList[PROGRAMMER].GetValue()
    self.settings.port = self.teList[PORT].GetValue()
    self.settings.uploadspeed = self.teList[UPLOADSPEED].GetValue()
    self.settings.numTemps = self.teList[NUMTEMPS].GetValue()
    self.settings.minAdc = self.teList[MINADC].GetValue()
    self.settings.maxAdc = self.teList[MAXADC].GetValue()
    self.settings.t0 = self.teList[T0].GetValue()
    self.settings.r1 = self.teList[R1].GetValue()

    self.settings.saveSettings()

  def onExit(self, evt):
    if not self.confirmLoseChanges("exit"):
      return
    self.EndModal(wx.ID_EXIT)

  def confirmLoseChanges(self, msg):
    if not self.modified:
      return True

    dlg = wx.MessageDialog(self, "Are you sure you want to " + msg + "?\n"
                                 "There are changes to your settings that "
                                 "will be lost.",
                           "Changes pending",
                           wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
    rc = dlg.ShowModal()
    dlg.Destroy()

    if rc != wx.ID_YES:
      return False

    return True