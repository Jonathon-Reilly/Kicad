import mysql.connector
import genpart_db

#capacitor prefered values
e3 = [10, 22, 47]
e6 = [10, 15, 22, 33, 47, 68]
e12 = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82]

#SMD capacitors suffix letters
# 1 - type          2 - size        3 - voltage    4 - type
# C Ceramic         A 01005/0402    A Reserved)    A C0G (NP0)
# E Electrolytic    B 0201/0603     B 2.5V         B X7R
# T Tantalum        C 0402/1005     C 4V           C X5R
# P Polyester       D 0603/1608     D 6.3V         D Y5V
# M Polymer         E 0805/2012     E 10V
# N Niobium         F 1008/2520     F 16V
#                   G 1206/3216     G 25V 
#                   H 1210/3225     H 35V  
#                   I 1218/3245     I 50V 
#                   J 1806/4516     J 100V
#                   K 1812/4532     K 150V
#                   L 2010/5025     L 200V
#                   M 2512/6332     M 250V
#                                   N 450V
#                                   O 500V
#                                   P 600V
#                                   R 630V
#                                   S 1kV
#                                   T 1.5kV
#                                   U 2kV
#                                   V 2.5kV
#                                   W 4kV
#                                   X 10kV

#sql config
sqlconfig = {
  'user': 'kicadpartman',
  'password': 'uBhC3PDBm7dS2aqP',
  'host': 'home.jahodovi.cz',
  'database': 'kicadpartman',
  'raise_on_warnings': True,
}

#resistor config
capconfig = {
  'e': e6,
  'p': "CEIB",          # Ceramic, 0603, 50V, X7R
  'pnp' : '08055C',     # part number prefix
  'pns' : 'KAT2A',      # part number suffix
  'min' : 3,
  'max' : 5,
  'maxval' : 47
}

#part config
partdata = {
  'category' : '31',
  'partname' : '',
  'partlabel' : '',
  'component' : 'C',
  'footprint' : 'smd_passive::CAPC2013X90N',
  'value' : '',
  'tolerance' : '10%',
  'rohs' : '1',
  'smd' : '1',
  'generic' : '1',
  'description' : 'Ceramic capacitor; X7R; 50V; SMD; 0805; -55÷125°C'
}

#spare config
sparedata = {
  'mfg' : '1',
  'partnumber' : '',
  'supplier' : '1',
  'datasheet' : 'AVX/X7R.pdf'
}

#functions

# MAIN

# Connect to the database
cnx = mysql.connector.connect(**sqlconfig)

# Build part data
for multiple in range(capconfig['min'], capconfig['max']+1):
  for v in capconfig['e']:
    value = v * 10**multiple
    #if (value>=10000000000):
    #  suffix = "m"
    #  value = value / 100000
    if (value>=10000000):
      suffix = "u"
      value = value / 1000000
    elif (value>=10000):
      suffix = "n"
      value = value / 1000
    else:
      suffix = "p"

    x = int(value / 10)
    y = int(value % 10)
    if (y%10 == 0):
      y = int(y/10)
    if (y == 0):
      valstr = str(int(x))+suffix
    else:
      valstr = str(int(x))+"."+str(y)+suffix
    
    if multiple==0:
      sparestr = str(x) + 'R' + str(y)
    else:
      sparestr = str(v) + str(multiple-1)
    partnumber=capconfig['pnp']+sparestr+capconfig['pns']
    
    partvalue = valstr
    partname = valstr + " " + capconfig['p']
    print(partname + "  /  " + partnumber)
    
    #add part to database
    partid = genpart_db.db_check_part(cnx, partname)
    if partid == 0:
      partdata['partname'] = partname
      partdata['partlabel'] = partname
      partdata['value'] = partvalue
      partid = genpart_db.db_insert(cnx, 'parts', partdata)
      print("Part ID="+str(partid))
    else:
      print("Part exists as ID="+str(partid))
      
    #add spare with partnumber to database
    if partid > 0:
      spareid = genpart_db.db_check_spare(cnx, partnumber)
      if spareid == 0:
        sparedata['partid'] = str(partid)
        sparedata['partnumber'] = partnumber
        spareid = genpart_db.db_insert(cnx, 'spare', sparedata)
        print("Spare ID="+str(spareid))
      else:
        print("Spare exists as ID="+str(spareid))
      
    print("-----------")
    if (multiple == capconfig['max']) & (v == capconfig['maxval']):
      break

# Close connection                              
cnx.close()
