#-------------------------------------------------------------------------------
# Name:        manage_entries v1.0
# Purpose:     The client backend, managing local and cloud storage of entries
#
# Author:      Bodhi Connolly
#
# Created:     24/05/2014
# Copyright:   (c) Bodhi Connolly 2014
# Licence:     GNU General Public License, version 3 (GPL-3.0)
#-------------------------------------------------------------------------------

import dropbox
import plistlib
import os
import datetime
from time import time
from time import sleep
import threading
import uuid


#global settings
try:
    settings=eval(open('settings.txt','rU').read())
except IOError:
    print 'Invalid settings file'
sub_dir=settings['sub_dir']
dropbox_path=settings['dropbox_path']
db_code=settings['db_code']

class Entry(dict):
    """A class to store an Day One entry file"""
    def uuid(self):
        """Return entry UUID

        Entry.uuid() -> str
        """
        return self['UUID']

    def been_edited(self):
        """Set an entry as edited

        Entry.been_edited() -> None
        """
        self['edited']=True

    def is_edited(self):
        """Return whether entry has been edited

        Entry.is_edited() -> bool
        """
        try:
            return self['edited']
        except KeyError:
            return False
    def __lt__(self,other):
        """Set compare method to use entry creation date

        Entry.__lt__(Entry) -> bool
        """
        if self['Creation Date']<other['Creation Date']:
            return True
        else:
            return False

    def has_saved(self):
        """Remove edited flag from entry

        Entry.has_saved() -> None
        """
        self.pop('edited')


    def load_entry(self,uuid):
        """Load entry from file

        Entry.load_entry(str) -> dict
        """
        data=open(os.path.join(sub_dir, uuid)+'.doentry','rb')
        pl = plistlib.readPlist(data)
        return pl

    def save_entry(self):
        """Save entry to file

        Entry.save_entry() -> None
        """
        plistlib.writePlist(self,
        (os.path.join(sub_dir, self.uuid())+'.doentry'))

class EntryList(object):
    """A class to store a list of entries"""
    def __init__(self):
        """Initialise EntryList object with a blank list

        EntryList.__init__() -> None
        """
        self.filelist=[]

    def add_entry(self):
        """Add an empty Entry to list with current date

        EntryList.add_entry() -> None
        """
        self.blank=Entry({'Creation Date':(datetime.datetime.now()),
               'Creator': {'Device Agent': 'iPhone/iPhone5,2',
               'Generation Date': (datetime.datetime.now()),
               'Host Name': "BC's iPhone",
               'OS Agent': 'iOS/7.0.3',
               'Software Agent': 'Day One iOS/1.12'},
               'Entry Text': "",
               'Location': {'Administrative Area': '',
               'Country': '',
               'Latitude': '',
               'Locality': '',
               'Longitude': '',
               'Place Name': ''},
                'Starred': False,
                'Time Zone': 'Australia/Brisbane',
                'UUID': str(uuid.uuid4()).replace('-',''),
                'Weather': {'Celsius': '',
              'Description': '',
              'IconName': '',
              'Relative Humidity':'',}})

        self.filelist.append(self.blank)
        self.filelist=sorted(self.filelist,reverse=True)

    def load_entry(self,uuid):
        """Read entry from Day One entry file

        Returns None if invalid entry file.

        EntryList.load_entry(str) -> dict
        """
        try:
            data=open(os.path.join(sub_dir, uuid)+
                        '.doentry','rb')
            pl = plistlib.readPlist(data)
            return pl
        except TypeError:
            pass

    def load_list(self):
        """Iterate over directory attempting to load each file

        EntryList.load_list() -> None
        """
        for filename in os.listdir(sub_dir):
            filename=filename[:-8]
            try:
                entry=Entry(self.load_entry(filename))
                self.filelist.append(entry)
            except TypeError:
                pass

        self.filelist=sorted(self.filelist,reverse=True)
    def get_all(self):
        """Return all Entry files in list, sorted by date

        EntryList.get_all() -> list(Entry)
        """
        self.filelist=sorted(self.filelist,reverse=True)
        return self.filelist

    def save_list(self):
        """Save Entries in list to file

        EntryList.save_list() -> None
        """
        for entry in self.filelist:
            if entry.is_edited():
                entry['upload']=True
                entry.has_saved()
                plistlib.writePlist(entry,
                (os.path.join(sub_dir, entry.uuid())+'.doentry'))

    def __getitem__(self,key):
        """Set the getitem method to retrieve from sorted Entry files

        EntryList.__getitem__(int) -> Entry
        """
        return sorted(self.filelist,reverse=True)[key]


class Dbox(object):
    """An object for uloading and downloading files from Dropbox"""
    def __init__(self):
        """Create Dropbox connection with app code, app secret and auth code

        Dbox.__init__() -> None
        """
        code=db_code
        app_key = '705ow3ln28cjfqc'
        app_secret = '2cxlx1apfqx5xb0'
        self.client = dropbox.client.DropboxClient(code)

    def download_entry(self,filepath):
        """Download Entry file from Dropbox and write to subdirectory

        Dbox.download_entry(str) -> None
        """
        uuid=filepath[-40:-8]
        print 'downloading: '+dropbox_path+'/'+uuid+'.doentry'
        try:
            data=self.client.get_file(dropbox_path+'/'+uuid+'.doentry')
            pl = plistlib.readPlist(data)
            plistlib.writePlist(pl,(os.path.join(sub_dir, uuid)+'.doentry'))
        except dropbox.rest.ErrorResponse:
            pass


    def update_dir(self):
        """Ask Dropbox for list of files that need updating
        (using cursor value from previous request) and update them.
        Save request details to cursor file for next request.

        Dbox.update_dir() -> None
        """
        try:
            if open('cursor.txt','rU').read()=='':
                history=None
            else:
                history=open('cursor.txt','rU').read()
        except IOError:
            with open('cursor.txt','w') as cursorfile:
                cursorfile.write('')
            history=None
        changes=self.get_changes(history,dropbox_path)
        while changes['has_more']:
            changes=self.get_changes(changes['cursor'],dropbox_path)
        print str(len(changes['entries']))+' file/s to update...'
        for entry in changes['entries']:
            try:
                self.download_entry(entry[0])
            except TypeError as e:
                print 'typeerror on load: '+str(e)

        with open('cursor.txt','w') as cursorfile:
            cursorfile.write(changes['cursor'])

    def get_changes(self,cursor=None,path_prefix=None):
        """Ask Dropbox which files need updating

        Dbox.get_changes(str,str) -> dict
        """
        return self.client.delta(cursor,path_prefix)

    def upload_entry(self,filename,data):
        """Upload a local entry file to Dropbox

        Dbox.upload_entry(str,file) -> None
        """
        try:
            self.client.put_file(dropbox_path+'/'+filename,data,overwrite=True)
        except dropbox.rest.ErrorResponse as e:
            print filename+': '+str(e)

    def upload_changes(self):
        """Upload any modified files to Dropbox

        Note: uses multiple threads to increase speed

        Dbox.upload_changes() -> None
        """
        for filename in os.listdir(sub_dir):
            try:
                if Entry().load_entry(filename[:-8])['upload']:
                    entry=Entry().load_entry(filename[:-8])
                    entry.pop('upload')
                    plistlib.writePlist(entry,
                            (os.path.join(sub_dir, entry['UUID'])+'.doentry'))
                    data=open(
                        os.path.join(sub_dir, entry['UUID'])+'.doentry','rb')
                    while threading.activeCount()>5:
                        sleep(1)
                    threading.Thread(
                        target=self.upload_entry,args=(filename,data)).start()
            except KeyError:
                    pass
    def upload_changes_nothread(self):
        """Upload any modified files to Dropbox

        Note: does not use multiple threads

        Dbox.upload_changes_nothread() -> None
        """
        for filename in os.listdir(sub_dir):
            try:
                if Entry().load_entry(filename[:-8])['upload']:
                    entry=Entry().load_entry(filename[:-8])
                    entry.pop('upload')
                    plistlib.writePlist(entry,
                    (os.path.join(sub_dir, entry['UUID'])+'.doentry'))
                    data=open(
                        os.path.join(sub_dir, entry['UUID'])+'.doentry','rb')
                    self.upload_entry(filename,data)
            except KeyError:
                    pass

    def upload_photo(self,uuid,file,ext='.jpg'):
        """Upload an image to Dropbox

        Note: if unspecified, assumed filetype jpg.

        Dbox.upload_photo(str,file,str) -> None
        """
        self.client.put_file(dropbox_path[:-7]+
                            'photos/'+uuid+ext,file,overwrite=True)

def main():
    pass

if __name__ == '__main__':
    main()

