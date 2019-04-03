import sys
import os
import stat
import sqlite
from cStringIO import StringIO
import reader
import parsebin
import dump

def CreateDirectories(Dir):
  List=Dir.split("/")
  Current=""
  if List[0]=="":
    List[0:1]=[]
    List[0]="/"+List[0]
  for Item in List:
    if len(Current)>0:
      Current+="/"
    Current+=Item
    try:
      Stat=os.stat(Current)
      if stat.S_ISDIR(Stat.st_mode):
        continue
    except (OSError,IOError):
      pass
    os.mkdir(Current)

def InterpretWorldBase(Cwd):
  Splitted=Cwd.split("/")
  Result=[]
  for Item in Splitted:
    if Item=="..":
      if len(Result)>0:
        Result.pop()
    elif Item!=".":
      Result.append(Item)
  return "/".join(Result)

def ParseCoord(Coord):
  Coord-=2048
  Coord+=1932
  Coord/=5
  return Coord

def GetChunkIndex(X,Y,Z):
  X=ParseCoord(X)
  Y=ParseCoord(Y)
  Z=ParseCoord(Z)
  return X*1048576+Y*1024+Z

class TMapWriter(object):
  def __init__(s,Volatile,MapgenMap):
    s.Volatile=Volatile
    s.MapgenMap=MapgenMap
  def SetCount(s,Count):
    s.Count=Count
    s.Current=0
  def WriteBlock(s,Position,Data):
    s.Current+=1
    Position=parsebin.DecodePosition(Position)
    X,Y,Z=Position
    Pos="[%d,%d,%d]"%(X-2048,Y-2048,Z-2048)
    Skip=False
    if s.MapgenMap is not None:
      Index=GetChunkIndex(X,Y,Z)
      Pos+=" {"+str(Index)+"}"
      Skip=Index not in s.MapgenMap
    if Skip:
      print "Skipping",
    else:
      print "Saving",
    print "block",s.Current,"of",s.Count,"at",Pos
    if Skip:
      return
    InF=StringIO(Data)
    InF=reader.TFileReader(InF)
    Block=parsebin.ParseBinaryBlock(InF)
    Dir=MapBase+"/%03X/%03X"%(Y,X)
    Name="%03X"%Z
    CreateDirectories(Dir)
    OutF=open(Dir+"/"+Name,"w")
    dump.EmitBlock(OutF,Block,s.Volatile)
    OutF.close()

def DumpMap(Volatile,MapgenMap):
  Writer=TMapWriter(Volatile,MapgenMap)
  sqlite.ExtractMap(WorldBase,Writer)

def GetWorldBase(WorldName):
  Cwd=os.getcwd()
  Cwd+="/"+sys.argv[0]+"/../../../../worlds/"+WorldName
  WorldBase=InterpretWorldBase(Cwd)
  return WorldBase

def ReadMapgenLog():
  try:
    InF=open(WorldBase+"/mapgen.log")
  except (IOError,OSError):
    print "No mapgen log, will save everything"
    return
  MapgenMap={}
  while True:
    Line=InF.readline()
    if Line=="":
      break
    if Line[0] not in "0123456789":
      continue
    Line=int(Line)
    MapgenMap[Line]=True
  InF.close()
  return MapgenMap

def Main():
  global WorldBase,MapBase
  WorldName=None
  Volatile=False
  OnlyGenerated=False
  Invalid=None
  for Arg in sys.argv[1:]:
    if Arg=="-h":
      Invalid=Ellipsis
      break
    elif Arg=="-v":
      if Volatile:
        Invalid="Too many -v options"
        break
      Volatile=True
    elif Arg=="-g":
      if OnlyGenerated:
        Invalid="Too many -g options"
        break
      OnlyGenerated=True
    else:
      if WorldName is not None:
        Invalid="Too many world names"
        break
      WorldName=Arg
  if WorldName is None:
    Invalid="Missing world name"
  if Invalid is not None:
    if Invalid is not Ellipsis:
      print Invalid
      print
    print "Usage: buworld.py [-v] [-g] worldname"
    print
    print "-v\tSave volatile data into the backup"
    print "-g\tSave only generated mapchunks"
    return
  WorldBase=GetWorldBase(WorldName)
  BackupBase=WorldName
  MapBase=BackupBase+"/map"
  MapgenMap=None
  if OnlyGenerated:
    MapgenMap=ReadMapgenLog()
  DumpMap(Volatile,MapgenMap)
