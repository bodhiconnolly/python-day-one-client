#-------------------------------------------------------------------------------
# Name:        location v1.0
# Purpose:     get location input from user and find relevant weather
#
# Author:      Bodhi Connolly
#
# Created:     24/05/2014
# Copyright:   (c) Bodhi Connolly 2014
# Licence:     GNU General Public License, version 3 (GPL-3.0)
#-------------------------------------------------------------------------------

from pygeocoder import Geocoder,GeocoderError
import urllib2
import json
import wx
from cStringIO import StringIO

class Location ( wx.Dialog ):
    """A dialog to get user location and local weather via Google Maps and
    OpenWeatherMap"""
    def __init__( self, parent ):
        """Initialises the items in the dialog

        Location.__init__(Parent) -> None
        """
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY,
                            title = 'Entry Location',
                            pos = wx.DefaultPosition, size = wx.Size( -1,-1),
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.input_location = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,
                                            wx.DefaultPosition,
                                            wx.Size( 200,-1 ),
                                            wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER,self.button_click,self.input_location)
        bSizer2.Add( self.input_location, 0, wx.ALL, 5 )

        self.button_search = wx.Button( self, wx.ID_ANY, u"Search",
                                        wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.button_search, 0, wx.ALL, 5 )
        self.button_search.Bind(wx.EVT_BUTTON,self.button_click)

        self.button_submit = wx.Button( self, wx.ID_OK, u"OK",
                                        wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.button_submit, 0, wx.ALL, 5 )
        self.button_submit.Bind(wx.EVT_BUTTON,self.submit)

        self.cancel = wx.Button(self, wx.ID_CANCEL,size=(1,1))

        bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )

        self.bitmap = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap,
                                     wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.bitmap, 1, wx.ALL|wx.EXPAND, 5 )

        self.location_text = wx.StaticText( self, wx.ID_ANY,
                                             u"Location:", wx.DefaultPosition,
                                             wx.DefaultSize, 0 )
        self.location_text.Wrap( -1 )
        bSizer1.Add( self.location_text, 0, wx.ALL, 5 )

        self.weather_text = wx.StaticText( self, wx.ID_ANY,
                                            u"Weather:", wx.DefaultPosition,
                                            wx.DefaultSize, 0 )
        self.weather_text.Wrap( -1 )
        bSizer1.Add( self.weather_text, 0, wx.ALL, 5 )

        self.weathernames={'Clear':'Clear','Clouds':'cloudy'}

        self.SetSizer( bSizer1 )
        self.Layout()
        self.Centre( wx.BOTH )

        self.searched=False

    def button_click(self,evt=None):
        """Finds the coordinates from the user entry text and gets the weather
        from these coordinates

        Location.button_click(event) -> None
        """
        self.get_weather(self.get_coordinates())
        self.searched=True

    def get_coordinates(self):
        """Searches Google Maps for the location entered and returns the results

        Note: returns None if cannot find location

        Location.get_coordinates() -> pygeolib.GeocoderResult
        """
        try:
            self.results=Geocoder.geocode(self.input_location.GetRange(0,
                                        self.input_location.GetLastPosition()))
        except GeocoderError:
            return None
        try:
            self.location_text.SetLabel(str(self.results))
        except UnicodeDecodeError:
            return None
        return self.results

    def get_weather(self,coordinates):
        """Searches OpenWeatherMap for the weather at specified coordinates
        and sets variables based on this result for adding to entry. Also loads
        image of coordinates from Google Maps Static Image API.

        Location.get_weather() -> None
        """
        if coordinates==None:
            self.location_text.SetLabel('Invalid Location')
            self.weather_text.SetLabel('No Weather')
        else:
            coordinates=coordinates.coordinates
            request = urllib2.urlopen(
                        'http://api.openweathermap.org/data/2.5/weather?lat='
                        +str(coordinates[0])+'&lon='
                        +str(coordinates[1])+'&units=metric')
            response = request.read()
            self.weather_json = json.loads(response)
            self.weather_text.SetLabel("Weather is %s with a temperature of %d"
                            % (self.weather_json['weather'][0]['main'].lower(),
                            self.weather_json['main']['temp']))
            request.close()

            img_source = urllib2.urlopen(
                            'http://maps.googleapis.com/maps/api/staticmap?'+
                            '&zoom=11&size=600x200&sensor=false&markers='
                            +str(coordinates[0])+','+str(coordinates[1]))
            data = img_source.read()
            img_source.close()
            img = wx.ImageFromStream(StringIO(data))
            bm = wx.BitmapFromImage((img))
            self.bitmap.SetBitmap(bm)
            w, h = self.GetClientSize()
            self.SetSize((w+50,h+50))

            try:
                self.celcius=int(self.weather_json['main']['temp'])
            except KeyError:
                pass
            try:
                self.icon=(self.weathernames[self.weather_json
                                            ['weather'][0]['main']])
            except KeyError:
                self.icon='Clear'
            try:
                self.description=self.weather_json['weather'][0]['main']
            except KeyError:
                pass
            try:
                self.humidity=self.weather_json['main']['humidity']
            except KeyError:
                pass
            try:
                self.country=self.results.country
            except KeyError:
                pass
            try:
                self.placename=(str(self.results.street_number)
                                +' '+self.results.route)
            except (TypeError,KeyError):
                self.placename=''
            try:
                self.adminarea=self.results.administrative_area_level_1
            except KeyError:
                pass
            try:
                self.locality=self.results.locality
            except KeyError:
                pass

    def submit(self,evt=None):
        """Closes the dialog if user has already searched, else search and then
        close the dialog.

        Location.submit() -> None
        """
        if self.searched:
            self.Close()
        else:
            self.button_click()
            self.Close()


def main():
    a = wx.App(0)
    f = Location(None)
    f.Show()
    a.MainLoop()

if __name__ == '__main__':
    main()
