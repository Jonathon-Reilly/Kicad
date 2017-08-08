import mysql.connector

#functions
def db_check_part(cnx, partname):
  # Check part label is in the database
  cursor = cnx.cursor()

  query = "SELECT id FROM parts WHERE partname='" + partname + "'"
  cursor.execute(query)
  result = 0
  for row in cursor:
    result = int(row[0])
  cursor.close()

  return result

def db_check_spare(cnx, partnumber):
  # Check part label is in the database
  cursor = cnx.cursor()

  query = "SELECT id FROM spare WHERE partnumber='" + partnumber + "'"
  cursor.execute(query)
  result = 0
  for row in cursor:
    result = int(row[0])
  cursor.close()

  return result

def db_insert(cnx, table, data):
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
  print(query)
  rowid = 88888
  #cursor.execute(query)
  #rowid = cursor.lastrowid
  cursor.close()
  cnx.commit()

  return rowid
