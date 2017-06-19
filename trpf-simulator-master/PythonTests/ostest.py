import os

a = "directoryname"
b = os.path.realpath(__file__)
c = os.path.dirname(os.path.realpath(__file__))
print(b)
print(c)
d = os.path.join(c,'..','netlistspls')
print(d)
e = "hamburger"
print(e.split('b')[1])
