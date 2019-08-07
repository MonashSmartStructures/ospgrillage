import pysftp as sftp
import ftplib



myHostname = "sn3595.ddns.net"
myUsername = "admin"
myPassword = "civil"

#s = ftplib.FTP(myHostname,myUsername,myPassword)
#s.login(myUsername,myPassword)

#s.cwd("/U/SN3595")


cnopts = sftp.CnOpts()
cnopts.hostkeys = None

def sftpExample():
    try:
        s = sftp.Connection(host=myHostname, username=myUsername, password=myPassword,cnopts=cnopts)
        print("Connection successfully established ... ")

        # Define the file that you want to download from the remote directory
        #remoteFilePath = '/var/U/SN3595/SN3595107-26-1902-39-23-PM.tdms'
        remoteFilePath = '/media/sdb1/SN3595/SN3595104-04-1911-43-06-AM.tdms'
        localFilePath = 'F:\Python_Project\SN3595104-04-1911-43-06-AM.tdms'
        # Define the local path where the file will be saved
        # or absolute "C:\Users\sdkca\Desktop\TUTORIAL.txt"

        s.get(remoteFilePath, localFilePath)
        s.close()
    except:
        print("not working")

# connection closes automatically at the end of method
sftpExample()
