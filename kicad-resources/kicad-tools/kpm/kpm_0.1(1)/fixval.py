import mysql.connector
#import token
import re

#sql config
sqlconfig = {
  'user': 'kicadpartman',
  'password': 'uBhC3PDBm7dS2aqP',
  'host': 'home.jahodovi.cz',
  'database': 'kicadpartman',
  'raise_on_warnings': True,
}
#functions

def elvalue(text):
  tokenized_input = []
  for token in re.split(r'(\d+(?:\.\d+)?)', text):
    token = token.strip()
    if re.match(r'\d+\.\d+', token):
      tokenized_input.append(float(token))
    elif token.isdigit():
      tokenized_input.append(int(token))
    elif token:
      tokenized_input.append(token)
  value = tokenized_input[0]
  if len(tokenized_input)>1:
    if tokenized_input[1]=='k':
      value *= 1000
    elif tokenized_input[1]=='M':
      value *= 1000000
    elif tokenized_input[1]=='p':
      value *= 1e-12
    elif tokenized_input[1]=='n':
      value *= 1e-9
    elif tokenized_input[1]=='u':
      value *= 1e-6
    elif tokenized_input[1]=='m':
      value *= 1e-3
    
  return value



# MAIN

# Connect to the database
cnx = mysql.connector.connect(**sqlconfig)

cursor = cnx.cursor()

query = "SELECT id,value FROM parts"
cursor.execute(query)
result = 0
rows = cursor.fetchall()
cursor.close()

for row in rows:
  print(row)
  elval = elvalue(row[1])
  cursor = cnx.cursor()
  query = "UPDATE parts SET value2='"+str(elval)+"' WHERE id="+str(row[0])
  print(query)
  cursor.execute(query)
  cursor.close()

cnx.commit()
  

# Close connection                              
cnx.close()
