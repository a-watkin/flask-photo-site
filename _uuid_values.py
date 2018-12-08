import uuid
import datetime


filename = 'somefile.jpg'

temp = filename.split('.')
created = datetime.datetime.now()
identifier = str(uuid.uuid1()).split('-')[0]

print(identifier, type(uuid.uuid1()))


temp[0] = temp[0] + "_" + identifier

print('.'.join(temp))
