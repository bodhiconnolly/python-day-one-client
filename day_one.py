#-------------------------------------------------------------------------------
# Name:        day_one v1.0
# Purpose:     The main interface and logic of the Day One Python Client
#
# Author:      Bodhi Connolly
#
# Created:     24/05/2014
# Copyright:   (c) Bodhi Connolly 2014
# Licence:     GNU General Public License, version 3 (GPL-3.0)
#-------------------------------------------------------------------------------

import manage_entries
import webcam
import location
import wx
import wx.xrc
import wx.calendar
import threading
import datetime
import time


class MainPanel ( wx.Panel ):
    """The main GUI of the Day One program"""
    def __init__( self, parent ):
        """Initialise the main Day One panel

        MainPanel.__init__(Parent) -> None"""
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY,
                            pos = wx.DefaultPosition, size = wx.Size(800,610),
                            style = wx.TAB_TRAVERSAL )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.button_new = wx.Button( self, wx.ID_ANY, u"New Entry",
                                    wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.button_new, 1, wx.ALL, 5 )
        self.button_new.Bind(wx.EVT_BUTTON,self.new_entry)
        self.button_new.SetToolTipString("Create a new entry with current date")

        self.button_settings = wx.Button( self, wx.ID_ANY, u"Settings",
                                        wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.button_settings, 1, wx.ALL, 5 )
        self.button_settings.Enable(False)

        self.button_photo = wx.Button( self, wx.ID_ANY, u"Photo",
                                        wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.button_photo, 1, wx.ALL, 5 )
        self.button_photo.Bind(wx.EVT_BUTTON,self.open_webcam)
        self.button_photo.SetToolTipString("Add a photo from webcam")

        self.dpc = wx.GenericDatePickerCtrl(self, size=(120,-1),
                                       style = wx.TAB_TRAVERSAL
                                       | wx.DP_DROPDOWN
                                       | wx.DP_SHOWCENTURY
                                       | wx.DP_ALLOWNONE )
        self.Bind(wx.EVT_DATE_CHANGED, self.date_change, self.dpc)
        bSizer2.Add(self.dpc,0 , wx.ALL, 5)
        self.dpc.SetToolTipString("Change entry date")
        self.dpc.SetRange(wx.calendar._pydate2wxdate(datetime.date(year=1900,
                            month=01,day=01)),wx.calendar._pydate2wxdate(
                            datetime.datetime.now().date()))

        self.button_location = wx.Button( self, wx.ID_ANY, u"Location",
                                    wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.button_location, 1, wx.ALL, 5 )
        self.button_location.Bind(wx.EVT_BUTTON,self.get_location)
        self.button_location.SetToolTipString(
                                        "Attach a location and weather data")

        self.button_star = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap(
                                        "star.tiff", wx.BITMAP_TYPE_ANY ),
                                        wx.DefaultPosition,
                                        wx.DefaultSize, wx.BU_AUTODRAW )
        bSizer2.Add( self.button_star, 0, wx.TOP|wx.LEFT|wx.RIGHT, 5 )
        self.button_star.SetMaxSize( wx.Size( 30,30 ) )
        self.button_star.Bind(wx.EVT_BUTTON,self.make_starred)
        self.button_star.SetToolTipString("Star entry (toggle)")

        bSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )
        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

        self.entry_listbox = wx.ListBox( self, wx.ID_ANY,
                                    wx.DefaultPosition, wx.DefaultSize, [], 0 )
        bSizer3.Add( self.entry_listbox, 1, wx.ALL|wx.EXPAND, 10 )
        self.entry_listbox.SetMaxSize( wx.Size( 250,-1 ) )
        self.Bind(wx.EVT_LISTBOX, self.selection, self.entry_listbox)

        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        self.text_display = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,
                                wx.DefaultPosition, wx.DefaultSize,
                                wx.TE_MULTILINE)
        bSizer4.Add( self.text_display, 1, wx.EXPAND|wx.RIGHT|wx.TOP, 10 )
        self.Bind(wx.EVT_TEXT, self.edited, self.text_display)

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        self.wordCount = wx.StaticText( self, wx.ID_ANY,
                        u"Word Count:", wx.DefaultPosition,
                        wx.DefaultSize, 0 )
        self.wordCount.Wrap( -1 )
        bSizer5.Add( self.wordCount, 1, wx.ALL, 5 )
        bSizer5.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        self.location = wx.StaticText( self, wx.ID_ANY,
                            u"Location:", wx.DefaultPosition,
                            wx.DefaultSize, 0 )
        self.location.Wrap( -1 )
        bSizer5.Add( self.location, 1, wx.ALL, 5 )
        bSizer5.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        self.weather = wx.StaticText( self, wx.ID_ANY, u"Weather:",
                                    wx.DefaultPosition, wx.DefaultSize, 0 )
        self.weather.Wrap( -1 )
        bSizer5.Add( self.weather, 1, wx.ALL, 5 )

        bSizer4.Add( bSizer5, 0, wx.EXPAND, 5 )
        bSizer3.Add( bSizer4, 1, wx.EXPAND, 5 )
        bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )
        self.SetSizer( bSizer1 )
        self.Layout()
        self.Centre( wx.BOTH )

        self.firstTime=True
        self.display_list()
        self.entry_listbox.SetSelection(0)
        self.selection()

        self.leave=False
        self.save_thread=threading.Thread(target=self.bg_saving)
        self.save_thread.daemon=True
        self.save_thread.start()

    def display_list(self):
        """Displays the sorted list of entries in a listbox

        MainPanel.display_list() -> None
        """
        if not self.firstTime:
            selections = list(self.entry_listbox.GetStrings())
            index=len(selections)
            while index >0:
                self.entry_listbox.Delete(index-1)
                index-=1
            self.text_display.ChangeValue('')

        if self.firstTime:
            self.allEntries=manage_entries.EntryList()
            self.allEntries.load_list()
            self.entry_selected=0

        for x in self.allEntries.get_all():
            self.append_entry(x)
        if not (self.firstTime or self.entry_selected==-1):
            self.entry_listbox.SetSelection(self.entry_selected)



    def append_entry(self,entry):
        """Appends entry to listbox, displaying time and first 30 characters
            of entry text

        MainPanel.append_entry(Entry(dict)) -> None
        """
        try:
            ap_string=((entry['Creation Date']).strftime('%d')+'th '
                       +(entry['Creation Date']).strftime('%B')[:3]+' '
                       +(entry['Creation Date']).strftime('%Y')
                       +': '+str(entry['Entry Text'])[:30])
        except (KeyError,UnicodeEncodeError):
            try:
                ap_string=((entry['Creation Date']).strftime('%d')+'th '
                       +(entry['Creation Date']).strftime('%B')[:3]+' '
                       +(entry['Creation Date']).strftime('%Y'))+': '
                entry['Entry Text']=''
            except (KeyError,UnicodeEncodeError):
                ap_string='Invalid'

        if entry['Starred']:
            self.entry_listbox.Append('**'+ap_string)
        else:
            self.entry_listbox.Append(ap_string)

    def update_entry(self,pos1,pos2):
        """Updates the listbox display of the given index

        MainPanel.update_entry(int,int) -> None
        """
        if not pos1==-1:
            entry=self.allEntries.get_all()[pos1]
            self.entry_listbox.GetSelections()[0]
            self.entry_listbox.Delete(pos1)
            ap_string=((entry['Creation Date']).strftime('%d')+'th '
                           +(entry['Creation Date']).strftime('%B')[:3]+' '
                           +(entry['Creation Date']).strftime('%Y')
                           +': '+str(entry['Entry Text'])[:30])
            if entry['Starred']:
                self.entry_listbox.Insert('**'+ap_string,pos1)
            else:
                self.entry_listbox.Insert(ap_string,pos1)
            self.entry_listbox.SetSelection(pos2)

    def selection(self,evt=None):
        """Saves open file and updates main text from new selection

            MainPanel.selection(event) -> None
            """
        if not (self.entry_selected==-1 or self.firstTime):
            self.allEntries[self.entry_selected]['Entry Text']=(
                                    self.text_display.GetRange(
                                    0,self.text_display.GetLastPosition()))
        try:
            self.text_display.ChangeValue(str(self.allEntries.get_all()
            [self.entry_listbox.GetSelections()[0]]['Entry Text']))
            if not self.entry_selected==-1:
                self.update_entry(self.entry_selected,
                                self.entry_listbox.GetSelections()[0])
            self.entry_selected=self.entry_listbox.GetSelections()[0]
        except IndexError:
            self.text_display.ChangeValue('')
        self.update_date()
        self.update_wordcount()
        self.update_location_weather()
        self.firstTime=False

    def edited(self,evt=None):
        """Updates word count, markes entry as edited, and saves entry text

        MainPanel.edited(event) -> None
        """
        try:
            self.entry_listbox.GetSelections()[0]
        except IndexError:
            return
        self.allEntries[self.entry_selected].been_edited()
        self.update_wordcount()
        self.allEntries[self.entry_selected]['Entry Text']=(
                                    self.text_display.GetRange
                                    (0,self.text_display.GetLastPosition()))
        self.update_entry(self.entry_listbox.GetSelections()
                            [0],self.entry_listbox.GetSelections()[0])

    def new_entry(self,evt=None):
        """Saves old entry, adds new entry at current date,
        deselects all entries

        MainPanel.new_entry(event) -> None
        """
        self.entry_listbox.DeselectAll()
        self.selection()
        self.entry_selected=-1
        self.allEntries.add_entry()
        self.display_list()
        new_date=wx.calendar._pydate2wxdate(datetime.datetime.now().date())
        self.dpc.SetValue(new_date)

    def open_webcam(self,evt=None):
        """Opens webcam window and associates it with the open entry.
        If not webcam available, display dialog.

        MainPanel.open_webcam(event) -> None
        """
        if webcam.webcam_available:
            if not self.entry_selected==-1:
                 webcam_window = webcam.WebcamFrame(None,-1,
                                                    style=wx.DEFAULT_FRAME_STYLE
                                                    &(~wx.RESIZE_BORDER)&
                                                    (~wx.MAXIMIZE_BOX))
                 webcam_window.Show()
                 webcam_window.panel.setUUID(self.allEntries.get_all()
                                [self.entry_listbox.GetSelections()[0]]['UUID'])
            else:
                err=wx.MessageDialog(self,
                        'Error: No entry selected.',style=wx.ICON_ERROR|wx.OK)
                err.ShowModal()
        else:
            err=wx.MessageDialog(self,
                    'Error: VideoCapture module needed for webcam feature.'+
                    'Windows only.',style=wx.ICON_ERROR|wx.OK)
            err.ShowModal()

    def set_open_key(self,key,value):
        """Updates a key in the currently displayed entry

        MainPanel.set_open_key(str,str) -> None
        """
        try:
            self.entry_listbox.GetSelections()[0]
        except IndexError:
            return
        self.allEntries[self.entry_selected].been_edited()
        self.allEntries[self.entry_selected][key]=value

    def set_open_key_key(self,key1,key2,value):
        """Updates a key within a dict in the currently displayed entry

        MainPanel.set_open_key_key(str,str,str) -> None
        """
        try:
            self.entry_listbox.GetSelections()[0]
        except IndexError:
            return
        self.allEntries[self.entry_selected].been_edited()
        self.allEntries[self.entry_selected][key1][key2]=value

    def get_location(self,evt=None):
        """Gets the users location and weather by opening up a window with an
        entry box attached to Google Maps and openWeatherMap

        MainPanel.get_location(event) -> None
        """
        if not self.entry_selected==-1:
            self.location_window = location.Location(self)
            self.location_window.ShowModal()
            if self.location_window.searched:
                    self.set_open_key_key('Weather','Celsius',
                                        str(self.location_window.celcius))
                    self.set_open_key_key('Weather','Description',
                                        str(self.location_window.description))
                    self.set_open_key_key('Weather','Relative Humidity',
                                        str(self.location_window.humidity))
                    self.set_open_key_key('Weather','IconName',
                                        str(self.location_window.icon)+'.png')
                    try:
                        self.set_open_key_key('Location','Country',
                                        str(self.location_window.country))
                    except UnicodeEncodeError:
                        self.set_open_key_key('Location','Country','')
                    try:
                        self.set_open_key_key('Location','Place Name',
                                        str(self.location_window.placename))
                    except UnicodeEncodeError:
                        self.set_open_key_key('Location','Place Name','')
                    self.set_open_key_key('Location','Administrative Area',
                                        str(self.location_window.adminarea))
                    try:
                        self.set_open_key_key('Location','Locality',
                                            str(self.location_window.locality))
                    except UnicodeEncodeError:
                        self.set_open_key_key('Location','Locality','')
            self.update_location_weather()
        else:
            err=wx.MessageDialog(self,
                    'Error: No entry selected.',style=wx.ICON_ERROR|wx.OK)
            err.ShowModal()

    def word_count(self,text):
        """Returns a rudimentary count of the number of words in a string

        MainPanel.word_count(str) -> int
        """
        text=text.split()
        return str(len(text))

    def date_change(self, evt=None):
        """Updates selected entry with date from wxDatePickerCtrl

        MainPanel.date_change(event) -> None
        """
        if not self.entry_selected==-1:
            try:
                new_date=wx.calendar._wxdate2pydate(evt.GetDate())
                new_date=datetime.datetime.combine(
                                        new_date,datetime.datetime.min.time())
                self.set_open_key('Creation Date',new_date)
                self.display_list()
                self.entry_selected=-1
                self.entry_listbox.DeselectAll()
                self.selection()
            except TypeError:
                pass

    def update_wordcount(self):
        """Updates the word count label with the current word count

        MainPanel.update_wordcount() -> None
        """
        if not self.entry_selected==-1:
            self.wordCount.SetLabel('Word Count: '+
                                    self.word_count(self.text_display.GetRange
                                    (0,self.text_display.GetLastPosition())))
        else:
             self.wordCount.SetLabel('Word Count: ')

    def update_date(self):
        """Updates the date control with the current entry date

        MainPanel.update_date() -> None
        """
        new_date=wx.calendar._pydate2wxdate(self.allEntries
                                        [self.entry_selected]
                                        ['Creation Date'].date())
        self.dpc.SetValue(new_date)

    def update_location_weather(self):
        """Updates the location and weather label with the current location
        and weather

        MainPanel.update_location_weather() -> None
        """
        if not self.entry_selected==-1:
            try:
                if (self.allEntries[self.entry_selected]
                                                    ['Weather']['Celsius']==''):
                    self.weather.SetLabel('No weather')
                else:
                    self.weather.SetLabel(
                                    self.allEntries[self.entry_selected]
                                    ['Weather']['Celsius']+u'\N{DEGREE SIGN}'+
                                    ', '+self.allEntries[self.entry_selected]
                                    ['Weather']['Description'])
            except (KeyError,TypeError):
                self.weather.SetLabel('No weather')

            try:
                if (self.allEntries[self.entry_selected]
                            ['Location']['Place Name']==''
                and self.allEntries[self.entry_selected]
                            ['Location']['Locality']==''):
                    self.location.SetLabel('No location')
                else:
                    self.location.SetLabel(self.allEntries[self.entry_selected]
                                    ['Location']['Place Name']+' '+
                                    self.allEntries[self.entry_selected]
                                    ['Location']['Locality'])
            except (KeyError,TypeError):
                self.location.SetLabel('No location')
        else:
            self.weather.SetLabel('No weather')
            self.location.SetLabel('No location')


    def make_starred(self,evt=None):
        """Toggles the star flag in the open entry

        MainPanel.make_starred(event) -> None
        """
        if  self.allEntries[self.entry_selected]['Starred']:
            self.set_open_key('Starred',False)
        else:
            self.set_open_key('Starred',True)
        self.selection()

    def on_close(self,evt=None):
        """Saves the text from the open entry and uploads all un-uploaded
        changes to Dropbox

        MainPanel.update_wordcount() -> None
        """
        self.leave=True
        if not self.entry_selected==-1:
                self.allEntries[self.entry_selected]['Entry Text']=(
                                                    self.text_display.GetRange
                                                    (0,self.text_display
                                                    .GetLastPosition()))
        self.save_upload(self.allEntries)

    def bg_saving(self):
        """Uploads changed files to dropbox if time since last upload is
        more than 15 seconds

        MainPanel.bg_saving() -> None
        """
        time_dif=datetime.timedelta(seconds=15)
        old_time=datetime.datetime.now()
        try:
            while not self.leave:
                time.sleep(0.1)
                if datetime.datetime.now()-old_time>time_dif:
                    self.save_upload(self.allEntries)
                    old_time=datetime.datetime.now()
        except wx.PyDeadObjectError:
            pass

    def save_upload(self,entries):
        """Saves changes and uploads modified entries to Dropbox

        MainPanel.save_upload(EntryList) -> None
        """
        db=manage_entries.Dbox()
        entries.save_list()
        db.upload_changes()

    def save_upload_nothread(self,entries):
        """Saves changes and uploads modified entries to Dropbox without using
        a multithreaded upload process

        MainPanel.save_upload(EntryList) -> None
        """
        db=manage_entries.Dbox()
        entries.save_list()
        db.upload_changes_nothread()


class MainWindow ( wx.Frame ):
    """A frame to host the main GUI in MainPanel"""
    def __init__( self, parent ):
        """Initialises the frame with a MainPanel

        MainWindow.__init__(Parent) -> None
        """
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
                            title='Day One Python Client',
                            pos = wx.DefaultPosition, size=wx.Size( 810,650 ),
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.Show(True)
        self.SetSizeHintsSz( wx.Size( 800,600 ), wx.DefaultSize )
        self.main=MainPanel(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)
    def on_close(self,evt=None):
        """Actives the panel close procedure and then closes the frame

        MainWindow.on_close(event) -> None
        """
        self.main.on_close()
        self.Destroy()

class SplashScreen(wx.SplashScreen):
    """
    A splashscreen that updates files from dropbox before opening main window
    """
    def __init__(self, parent=None):
        """Initialises the splashscreen

        SplashScreen.__init__(Parent) -> None
        """
        try:
            aBitmap = wx.Image(name = "splashscreen.png").ConvertToBitmap()
        except wx.PyAssertionError:
            aBitmap = wx.EmptyBitmap(1,1)
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splashDuration = 1000 #milliseconds
        wx.SplashScreen.__init__(self, aBitmap, splashStyle,
                                 splashDuration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.db=manage_entries.Dbox()
        self.db.update_dir()
        wx.Yield()

    def OnExit(self, evt=None):
        evt.Skip()


class DayOneApp(wx.App):
    """A custon app class that opens a splash screen and then a MainWindow"""
    def __init__(self):
        """Initialises the app and opens the splash screen

        MainWindow.__init__() -> None
        """
        wx.App.__init__(self)
        a=SplashScreen(None)
        time.sleep(1)
        frame=MainWindow(None)
        favicon = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO, 16, 16)
        wx.Frame.SetIcon(frame, favicon)

def main():
    app = DayOneApp()
    app.MainLoop()

if __name__ == '__main__':
    main()
