import sys
import time
import buworld

Buffer=[]

def Flush():
  Data="".join(Buffer)
  sys.stdout.write(Data)
  sys.stdout.flush()
  Buffer[:]=[]

def Write(What):
  Buffer.append(What)

def Print(What):
  global CX
  Free=79-CX
  Len=len(What)
  if Len>Free:
    What=What[:Free]
    Len=Free
  if Len>0:
    Write(What)
    CX+=Len

def IssueCommand(Command, Count):
  if Count==0:
    return
  if Count==1:
    CountStr=""
  else:
    CountStr=str(Count)
  Write("\x1B["+CountStr+Command)

def GoUp(Count):
  global CY
  if Count>CY:
    Count=CY
  IssueCommand("A", Count)
  CY-=Count

def GoDown(Count):
  global CY
  if Count>39-CY:
    Count=39-CY
  IssueCommand("B", Count)
  CY+=Count

def GoToLine(Line):
  if Line>CY:
    GoDown(Line-CY)
  elif Line<CY:
    GoUp(CY-Line)

def GoLeft(Count):
  global CX
  if Count>CX:
    Count=CX
  IssueCommand("D", Count)
  CX-=Count

def GoRight(Count):
  global CX
  if Count>79-CX:
    Count=79-CX
  IssueCommand("C", Count)
  CX+=Count

def GoToColumn(Column):
  global CX
  if Column==0 and CX!=0:
    Write("\r")
    CX=0
  elif Column>CX:
    GoRight(Column-CX)
  elif Column<CX:
    GoLeft(CX-Column)

def GotoXY(X,Y):
  GoToLine(Y)
  GoToColumn(X)

def NewLine():
  global CX,CY
  if CY==39:
    GoToColumn(0)
  else:
    Write("\n")
    CX=0
    CY+=1

def InitializeScreen():
  global CX,CY,Attr
  Write("\n"*39)
  Flush()
  CX=0
  CY=39
  Attr=7

def SetAttr(NewAttr):
  global Attr
  Colors="04261537"
  List=[]
  OldBg=Attr/16
  OldFg=Attr%16
  NewBg=NewAttr/16
  NewFg=NewAttr%16
  if NewFg in (7,15) or OldFg>7 and NewFg<8:
    List.append("")
    OldFg=7
    OldBg=0
  if OldFg<8 and NewFg>7:
    List.append("1")
  OldFg&=7
  NewFg&=7
  if OldBg!=NewBg:
    List.append("4"+Colors[NewBg])
  if OldFg!=NewFg:
    List.append("3"+Colors[NewFg])
  if len(List)>0:
    Command="\x1B["+";".join(List)+"m"
    Write(Command)
  Attr=NewAttr

def ClearScreen():
  global CX,CY
  SetAttr(7)
  GotoXY(0,0)
  for i in range(40):
    Write("\x1B[K")
    NewLine()
  GotoXY(0,0)
  Flush()
  CX=None
  CY=None

def MakeLines():
  GotoXY(0,0)
  for i in range(40):
    Print("Line %d"%i)
    NewLine()

def ShowColors():
  for i in range(8):
    GotoXY(10, i+5)
    for j in range(16):
      SetAttr(i*16+j)
      Print("XX")
  SetAttr(7)
  GotoXY(39,78)

def DebugScreen():
  for i in range(30):
    for j in range(4):
      DisplayedMap[i][j]=None
  for i in range(8):
    for j in range(16):
      DisplayedMap[i+5][j+5]=None
  MakeLines()
  ShowColors()
  Flush()

def SynchronizeOrigin():
  global Origin
  OX,OZ=Origin
  if OX is None:
    OX=16384
    OY=16384
  PX,PY,PZ=Player
  if PX is None:
    PX,PY,PZ=FirstMapPos
  if PX is not None:
    if OX+10>PX or OX+30<PX or  OZ+5>PZ or OZ+25<PZ:
      Origin=(PX-20,PZ-20)

def GetPlayerPosition():
  global Player
  def ParseCoord(Coord):
    Index=Coord.find(".")
    if Index>0:
      Coord=Coord[:Index]
    Coord=int(Coord)
    Coord+=309120
    Coord/=800
    return Coord
  try:
    InF=open(WorldBase+"/players/singleplayer")
  except (IOError,OSError):
    Player=(None,None,None)
    return
  while True:
    Line=InF.readline()
    if Line=="" or Line.startswith("position"):
      break
  InF.close()
  Player=None
  if Line!="":
    Start=Line.index("(")
    Stop=Line.index(")")
    Line=Line[Start+1:Stop]
    Line=Line.split(",")
    X=ParseCoord(Line[0])
    Y=ParseCoord(Line[1])
    Z=ParseCoord(Line[2])
    if X==772 and Y==772 and Z==772:
      X=None
      Y=None
      Z=None
    Player=(X,Y,Z)
    SynchronizeOrigin()

def UnpackChunkPos(Pos):
  Z=Pos%1024
  Pos/=1024
  Y=Pos%1024
  X=Pos/1024
  return X,Y,Z

class TMapItem(object):
  def __init__(s):
    s.Coords={}
    s.Min=1024
    s.Max=-1
  def Add(s,Y):
    s.Coords[Y]=True
    if Y>s.Max:
      s.Max=Y
    if Y<s.Min:
      s.Min=Y

def GenerateImage():
  Result=[]
  for i in range(30):
    Result.append([(7,"  ")]*40)
  return Result

def ClearMap():
  global Origin,Map,MapPos,FirstMapPos
  Origin=(None,None)
  Map={0:[]}
  MapPos=0
  FirstMapPos=(None,None,None)

def UpdateMap():
  global MapPos,FirstMapPos
  Last=Map[0]
  try:
    InF=open(WorldBase+"/mapgen.log")
  except (IOError,OSError):
    ClearMap()
    return
  InF.seek(MapPos)
  while True:
    Line=InF.readline()
    if Line=="":
      break
    Line=int(Line)
    if len(Last)==10:
      Last[0:1]=[]
    Last.append(Line)
    Pos=UnpackChunkPos(Line)
    X,Y,Z=Pos
    if MapPos==0:
      FirstMapPos=Pos
      MapPos=1
    Pos=(X,Z)
    if Pos in Map:
      Item=Map[Pos]
    else:
      Item=TMapItem()
      Map[Pos]=Item
    Item.Add(Y)
  MapPos=InF.tell()
  InF.close()

def ToChar(Value):
  if Value<372:
    Result="<"
  elif Value>372+26:
    Result=">"
  else:
    Result=chr(0x40+Value-371)
  return Result

def DrawMap():
  global DrawnPos
  OldX=CX
  OldY=CY
  X,Z=Origin
  GotoXY(20,33)
  Print("OX="+str(X)+" "*4)
  GotoXY(29,33)
  Print("OZ="+str(Z)+" "*4)
  X,Y,Z=Player
  GotoXY(20,35)
  Print("PX="+str(X)+" "*4)
  GotoXY(29,35)
  Print("PY="+str(Y)+" "*4)
  GotoXY(38,35)
  Print("PZ="+str(Z)+" "*4)
  if DrawnPos!=MapPos:
    Last=Map[0]
    Len=len(Last)
    for Index in range(10):
      GotoXY(0,Index+30)
      if Index<Len:
        Item=str(Last[Index])
      else:
        Item=" "*10
      Print(Item)
    DrawnPos=MapPos
  if Origin[0] is None:
    CurrentMap=GenerateImage()
  else:
    CurrentMap=[]
    OX,OZ=Origin
    for i in range(30):
      Line=[]
      CurrentMap.append(Line)
      for j in range(40):
        X=OX+j
        Z=OZ+29-i
        Pos=(X,Z)
        if Pos in Map:
          Item=Map[Pos]
          Attr=14
          Down=ToChar(Item.Min)
          Up=ToChar(Item.Max)
          Expected=Item.Max-Item.Min+1
          if Expected!=len(Item.Coords):
            Attr=12
          if X==Player[0] and Z==Player[2]:
            Attr+=16*4
          else:
            Attr+=16*1
          Piece=(Attr,Down+Up)
        else:
          Piece=(7,"  ")
        Line.append(Piece)
  for i in range(30):
    for j in range(40):
      Orig=DisplayedMap[i][j]
      New=CurrentMap[i][j]
      if New!=Orig:
        Attr,Text=New
        GotoXY(j*2,i)
        SetAttr(Attr)
        Print(Text)
        DisplayedMap[i][j]=New
  SetAttr(7)
  GotoXY(OldX, OldY)

def RunLoop():
  DebugScreen()
  while True:
    GetPlayerPosition()
    UpdateMap()
    DrawMap()
    Flush()
    time.sleep(0.1)

def Main():
  global WorldBase,DrawnPos,DisplayedMap
  DisplayedMap=GenerateImage()
  WorldName=sys.argv[1]
  WorldBase=buworld.GetWorldBase(WorldName)
  DrawnPos=0
  ClearMap()
  UpdateMap()
  InitializeScreen()
  try:
    RunLoop()
  finally:
    ClearScreen()
