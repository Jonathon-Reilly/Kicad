import mysql.connector

#resistor prefered values
e3 = [100, 220, 470]
e6 = [100, 150, 220, 330, 470, 680]
e12 = [100, 120, 150, 180, 220, 270, 330, 390, 470, 560, 680, 820]
e24 = [100, 110, 120, 130, 150, 160, 180, 200, 220, 240, 270, 300, 330, 360, 390, 430, 470, 510, 560, 620, 680, 750, 820, 910]
e48 = [100, 102, 110, 115, 121, 127, 133, 140, 147, 154, 162, 169, 187, 196, 205, 215, 226, 237, 243, 249, 261, 274, 287, 301, 316, 332, 348, 365, 383, 402, 422, 442, 464, 487, 511, 536, 562, 590, 619, 649, 681, 715, 750, 787, 825, 866, 909, 953]
e96 = [100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130, 133, 137, 140, 143, 147, 150, 154, 158, 162, 165, 169, 174, 178, 182, 187, 191, 196, 200, 205, 210, 215, 221, 226, 232, 237, 243, 249, 255, 261, 267, 274, 280, 287, 294, 301, 309, 316, 324, 332, 340, 348, 357, 365, 374, 383, 392, 402, 412, 422, 432, 442, 453, 464, 475, 487, 499, 511, 523, 536, 549, 562, 576, 590, 604, 619, 634, 649, 665, 681, 698, 715, 732, 750, 768, 787, 806, 825, 845, 866, 887, 909, 931, 953, 976]

#SMD resistor suffix letters
# 1 - type          2 - size        3 - tolerance
# F Film            A 01005/0402    A 50%
# C Carbon          B 0201/0603     B 20%
# M Melf            C 0402/1005     C 10%
#                   D 0603/1608     D 5%
#                   E 0805/2012     E 2%
#                   F 1008/2520     F 1%
#                   G 1206/3216     G 0.5%
#                   H 1210/3225     H 0.25%
#                   I 1218/3245     I 0.1%
#                   J 1806/4516
#                   K 1812/4532
#                   L 2010/5025
#                   M 2512/6332

#sql config
sqlconfig = {
  'user': 'kicadpartman',
  'password': 'uBhC3PDBm7dS2aqP',
  'host': 'home.jahodovi.cz',
  'database': 'kicadpartman',
  'raise_on_warnings': True,
}

#resistor config
resconfig = {
  'e': e24,
#  'p': "FDF", #Film, 0603, 1%
  'p': "FEF", #Film, 0805, 1%
}

#part config
partdata = {
  'category' : '21',
  'partname' : '',
  'partlabel' : '',
  'component' : 'R',
  'footprint' : 'smd_passive::RESC2012X45N',
  'value' : '',
  'tolerance' : '1%',
  'rohs' : '1',
  'smd' : '1',
  'generic' : '1',
  'description' : 'Thick film resistor; SMD; 0603; 100mW; ±1%; -55÷155°C'
}

#spare config
sparedata = {
  'mfg' : '11',
  'partnumber' : '',
  'supplier' : '1',
  'datasheet' : 'Vishay/CRCW.pdf'
}

partnumber_prefix = 'CRCW0805'
partnumber_suffix = 'FKTA'

#functions

def check_part(cnx, partname):
  # Check part label is in the database
  cursor = cnx.cursor()

  query = "SELECT id FROM parts WHERE partname='" + partname + "'"
  cursor.execute(query)
  result = 0
  for row in cursor:
    result = int(row[0])
  cursor.close()

  return result

def check_spare(cnx, partnumber):
  # Check part label is in the database
  cursor = cnx.cursor()

  query = "SELECT id FROM spare WHERE partnumber='" + partnumber + "'"
  cursor.execute(query)
  result = 0
  for row in cursor:
    result = int(row[0])
  cursor.close()

  return result

def insert_db(cnx, table, data):
  # Insert part to database
  cursor = cnx.cursor()
  names = "("
  values = "("
  first = 1
  for key in data:
    if first == 0:
      names += ", "
      values += ", "
    first = 0
    names += "`"+key+"`"
    values += "'"+data[key]+"'"
  names += ")"
  values += ")"
  
  query = "INSERT INTO "+table+" "+names+" VALUES "+values+";"
  #print(query)
  cursor.execute(query)
  rowid = cursor.lastrowid
  cursor.close()
  cnx.commit()

  return rowid
  

# MAIN

# Connect to the database
cnx = mysql.connector.connect(**sqlconfig)

# Build part data
last = 8
for multiple in range(0, last):
  for v in resconfig['e']:
    value = v * 10**multiple
    if (value>=100000000):
      suffix = "M"
      suffix2= suffix
      value = value / 1000000
    elif (value>=100000):
      suffix = "k"
      suffix2= suffix
      value = value / 1000
    else:
      suffix = ""
      suffix2 = "R"
    x = int(value / 100)
    y = int(value % 100)
    if (y%10 == 0):
      y = int(y/10)
    if (y == 0):
      valstr = str(int(x))+suffix
      sparestr = str(int(x))+suffix2
    else:
      valstr = str(int(x))+"."+str(y)+suffix
      sparestr = str(int(x))+suffix2+str(y)
    while len(sparestr)<4:
      sparestr += '0'
    partvalue = valstr
    partname = valstr + " " + resconfig['p']
    print(partname)
    
    #add part to database
    partid = check_part(cnx, partname)
    if partid == 0:
      partdata['partname'] = partname
      partdata['partlabel'] = partname
      partdata['value'] = partvalue
      partid = insert_db(cnx, 'parts', partdata)
      print("Part ID="+str(partid))
    else:
      print("Part exists as ID="+str(partid))
      
    #add spare with partnumber to database
    if partid > 0:
      partnumber=partnumber_prefix+sparestr.upper()+partnumber_suffix
      spareid = check_spare(cnx, partnumber)
      if spareid == 0:
        sparedata['partid'] = str(partid)
        sparedata['partnumber'] = partnumber
        print(partnumber)
        spareid = insert_db(cnx, 'spare', sparedata)
        print("Spare ID="+str(spareid))
      else:
        print("Spare exists as ID="+str(spareid))
      
    print("-----------")
    if (multiple == last-1):
      break

# Close connection                              
cnx.close()
