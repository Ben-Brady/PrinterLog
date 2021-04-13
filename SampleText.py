from Modules import printer

import datetime
import json

with open('Text.json','r') as fObj:
    Text = json.load(fObj)

Channel = printer.Queue('General',Testing=True)
Start = datetime.datetime.now()
for x in Text:
    Offset = datetime.timedelta(seconds=x[0])
    Channel.Add(x[2],Start+Offset,x[1])