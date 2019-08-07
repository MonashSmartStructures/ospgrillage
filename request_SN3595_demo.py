import requests

r = requests.get("http://sn3595.ddns.net/#/FileBrowser;component/FileBrowserPage.dyn.xaml")

print(r.text)


#with open('Testing.txt','wb') as f:
 #   f.write(r.content)