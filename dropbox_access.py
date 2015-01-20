# Include the Dropbox SDK
import dropbox

app_key = '705ow3ln28cjfqc'
app_secret = '2cxlx1apfqx5xb0'

#app auth url
flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

authorize_url = flow.start()
print '1. Go to: ' + authorize_url
print '2. Click "Allow" (you might have to log in first)'
print '3. Copy the authorization code.'

code = raw_input("Enter the authorization code here: ").strip()

#generate access token
access_token, user_id = flow.finish(code)

#open settings file
settings=eval(open('settings.txt','rU').read())

#add code to settings
settings['db_code']=access_token

#save settings
with open ('settings.txt', 'w') as fp:
    first=True
    fp.write('{')    
    for p in settings.items():
        if not first:
            fp.write(',')
        if first:
            first=False
        fp.write("'%s':'%s'" % p)
    fp.write('}')

print 'Settings.txt has been updated with your access code :)'
leave = raw_input("Press return to exit...")
