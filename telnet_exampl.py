import sys
import telnetlib

HOST1 = "sn3595.ddns.net"
HOST2 = "sn3604.ddns.net"
HOST3 = "sn3614.ddns.net"
HOST4 = "sn3615.ddns.net"

def GetSupplyVoltage():
    tn.read_until(b"login: ")

    tn.write(b"user" + b"\n")

    tn.read_until(b"Password: ")
    tn.write(b"civil001" + b"\n")
    tn.read_until(b"OK")
    tn.write(b"AT*POWERIN?" + b"\n")
    out = tn.read_until(b"OK", 5)
    #print(tn.read_all())
    b = str(out[18:23], encoding='utf-8')
    print(b)
    #print(out[18:23] + b" V\n")

try:
    tn = telnetlib.Telnet(HOST1, 2332, 10)
    print("Supply Voltage bridge sn3595:")
    GetSupplyVoltage()
    tn.close()
except:
    print("Bridge sn3595 off-line?\n")

try:
    tn = telnetlib.Telnet(HOST2, 2332, 10)
    print("Supply Voltage bridge sn3604:")
    GetSupplyVoltage()
    tn.close()
except:
    print("Bridge sn3604 off-line?\n")

try:
    tn = telnetlib.Telnet(HOST3, 2332, 10)
    print("Supply Voltage bridge sn3614:")
    GetSupplyVoltage()
    tn.close()
except:
    print("Bridge sn3614 off-line?\n")

try:
    tn = telnetlib.Telnet(HOST4, 2332, 10)
    print("Supply Voltage bridge sn3615:")
    GetSupplyVoltage()
    tn.close()
except:
    print("Bridge sn3615 off-line?\n")

