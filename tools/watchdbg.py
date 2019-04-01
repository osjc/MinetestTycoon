import buworld
def GetWorldBase(World):
  return "/home/jozef/work/ostara/minetest/minetest/worlds/"+World
buworld.GetWorldBase=GetWorldBase

import watch
OutF=open("/dev/pts/8","w")
def Write(What):
  OutF.write(What)
  OutF.flush()
def Nop():
  pass
def Break():
  pass
watch.Break=Break
watch.Write=Write
watch.Flush=Nop
watch.Main()

#########

import watch
def Nop():
  pass
watch.Break=Nop
