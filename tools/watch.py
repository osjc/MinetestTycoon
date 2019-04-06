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

def UnpackChunkPos(Pos):
  Z=Pos%1024
  Pos/=1024
  Y=Pos%1024
  X=Pos/1024
  return X,Y,Z

def GetPlayerPosition():
  global Player
  if PlayerPos is None:
    Player=(None,None,None)
  else:
    Player=UnpackChunkPos(PlayerPos)
    SynchronizeOrigin()

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
  global Origin,Map,MapPos,FirstMapPos,PlayerPos,Score
  Origin=(None,None)
  Map={0:[]}
  MapPos=0
  FirstMapPos=(None,None,None)
  PlayerPos=None
  Score=0

Deltas=[]
for x in range(-1,2):
  for y in range(-1,2):
    for z in range(-1,2):
      if x!=0 or y!=0 or z!=0:
        Deltas.append(x*1048576 + y*1024 + z)

def UpdateMap():
  global MapPos,FirstMapPos,PlayerPos,Score
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
    Line=Line.split()
    Index=Line[0]
    if Index[0]=="P":
      if Index[1]=="a":
        PlayerPos=int(Index[2:])
      else:
        Code=int(Index[1:])
        PlayerPos+=Deltas[Code]
      GetPlayerPosition()
    if Index[0] not in "0123456789":
      continue
    Line=int(Index)
    if PlayerPos is None:
      PlayerPos=Line
      GetPlayerPosition()
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
    Score+=1
  MapPos=InF.tell()
  InF.close()

def ToChar(Value):
  if Value<372:
    Result="<"
  elif Value>372+26:
    Result=">"
  else:
    Result=39+Value-371
    if Result>0x39:
      Result+=39
    elif Result<0x30:
      Result+=43
    Result=chr(Result)
  return Result

def DrawMap():
  global DrawnPos
  OldX=CX
  OldY=CY
  GotoXY(20,31)
  Print("Discovery score: "+str(Score)+" "*6)
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
          if (X+Z)&1:
            Attr=11
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
