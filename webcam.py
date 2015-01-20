#-------------------------------------------------------------------------------
# Name:        webcam v1.0
# Purpose:     Create a window to take a photo with the webcam
#
# Author:      Bodhi Connolly
#
# Created:     24/05/2014
# Copyright:   (c) Bodhi Connolly 2014
# Licence:     GNU General Public License, version 3 (GPL-3.0)
#-------------------------------------------------------------------------------

import os
import wx
import manage_entries

try:
    from VideoCapture import Device
    webcam_available=True
except ImportError:
    print 'Webcam module not available...'
    webcam_available=False



class WebcamFrame(wx.Frame):
    """A frame that hosts a panel showing a webcam feed"""
    def __init__(self,*args,**kw):
        """Initialise the frame with a WebcamPanel and buttons

        WebcamFrame.__init__(*args,**kw) -> None
        """
        super(WebcamFrame,self).__init__(*args,title='Add Photo',
                                        size=(950,850),**kw)
        self.panel = WebcamPanel(self,-1,size=(950,700))
        self.MakeModal(True)
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
        bSizer2.Add(self.panel,1,wx.EXPAND,5)

        #buttons
        self.button_take = wx.Button(self, wx.ID_ANY, "Take Photo",
                                    (350,750), wx.DefaultSize, 0 )
        self.button_take.Bind(wx.EVT_BUTTON, self.panel.TakePhoto)
        self.button_cancel = wx.Button(self, wx.ID_ANY, "Cancel",
                                        (500,750), wx.DefaultSize, 0 )
        self.button_cancel.Bind(wx.EVT_BUTTON, self.leave)

        bSizer1.Add( bSizer2, 1, wx.ALL|wx.EXPAND, 5 )

        self.exitCheck = wx.PyTimer(self.to_exit)
        self.exitCheck.Start(40)

        self.Bind(wx.EVT_CLOSE,self.leave)

    def to_exit(self):
        """Exit if picture has been taken

        WebcamFrame.to_exit() -> None
        """
        if self.panel.picturetaken:
            self.leave()

    def leave(self,evt=None):
        """Close frame

        WebcamFrame.leave() -> None
        """
        self.MakeModal(False)
        self.Destroy()



class WebcamPanel(wx.Panel):
    """A panel that displays a feed from the webcam"""
    def __init__(self,*args,**kw):
        """Initialise panel with constantly refreshing feed

        WebcamPanel.__init__(*args,**kw) -> None
        """
        super(WebcamPanel,self).__init__(*args,**kw)

        self.cam = Device()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.refreshTimer = wx.PyTimer(lambda :self.Refresh(False))
        self.refreshTimer.Start(50)

        self.calcTimer = wx.PyTimer(self.CalcPic)
        self.calcTimer.Start(40)
        self.CalcPic()
        self.takepicture=False
        self.picturetaken=False
        self.uuid='no_uuid'

    def TakePhoto(self,evt=None):
        """Set takepicture variable to True, telling the OnPaint function to
        take a photo on next refresh

        WebcamPanel.TakePhoto(event) -> None
        """
        self.takepicture=True

    def CalcPic(self):
        """Get frame from webcam ready for display

        WebcamPanel.CalcPic() -> None
        """
        pilImage = self.cam.getImage()
        self.pilImage = pilImage

    def setUUID(self,uuid):
        """Set UUID to associated entry

        WebcamPanel.setUUID(str) -> None
        """
        self.uuid=uuid

    def OnPaint(self, evt=None):
        """Display latest webcam frame, and take photo if
        takepicture is set

        WebcamPanel.OnPaint(event) -> None
        """
        dc = wx.PaintDC(self)
        pilImage = self.pilImage
        w, h = pilImage.size[0], pilImage.size[1]
        image = wx.EmptyImage(w, h)
        image.SetData(pilImage.convert("RGB").tostring())
        image = image.Mirror()
        dc.DrawBitmap(wx.BitmapFromImage(image),0,0, True)
        if self.takepicture:
            self.cam.saveSnapshot(os.path.join('photos', self.uuid)+'.jpg')
            self.takepicture=False
            self.picturetaken=True
            self.db=manage_entries.Dbox()
            self.db.upload_photo(self.uuid,open(os.path.join(
                                'photos', self.uuid)+'.jpg','rb'))


def main():
    a = wx.App(0)
    f = WebcamFrame(None,-1,style=wx.DEFAULT_FRAME_STYLE
                & (~wx.RESIZE_BORDER)&(~wx.MAXIMIZE_BOX))
    f.Show()
    a.MainLoop()


if __name__ == '__main__':
    main()
