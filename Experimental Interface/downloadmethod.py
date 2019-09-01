import paramiko

#myUsername = "admin"
#myPassword = "civil"
#day= '30'
#month = '8'
#year = '19'
#bridgeno = '3595'
#myHostname = "sn{bridgeno}.ddns.net".format(bridgeno = bridgeno)

#rawcommand = 'SN{bridgeno}1{month}-{day}-{year}'
#filedate = rawcommand.format(bridgeno = bridgeno,month = month.zfill(2), day = day, year = year)
#print(filedate)

#rawremotepath = '/media/sdb1/SN{bridgeno}'
#remotepath = rawremotepath.format(bridgeno = bridgeno)
#print(remotepath)
#localpath = 'F:/Python_Project'
def downloadSSH(username,password,myHostname,filedate,remotepath,localpath):
    # ------------------------- Establish SSH connection ------------------------------------------------------
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=myHostname,port=22,username=username,password=password)
    s = ssh_client.open_sftp()
    rfile = s.listdir(remotepath)
    print(rfile)

    for files in rfile:
        fileday = files[0:15]  # get substring of file date
        if fileday == filedate:
            print('downloading: = ', files)
            s.get(remotepath + '/' + files, localpath + '/' + files)
            print('Download complete for: = ', files)

    ssh_client.close()
# ------------------------- Establish SSH connection ------------------------------------------------------
# - - create file list of the selected date

#downloadSSH(myUsername,myPassword,myHostname,filedate,localpath)

