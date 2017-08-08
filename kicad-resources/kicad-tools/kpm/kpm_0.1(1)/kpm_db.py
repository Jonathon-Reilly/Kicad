import mysql.connector

class Kpm_Db():
  def __init__(self, config):
    self.config = config
    self.cnx = mysql.connector.connect(**config)
    self.categories = []

  def __dev__(self):
    cnx.close()

  def GetCategories(self, parent):
    cursor = self.cnx.cursor()
    query = "SELECT id, parent, shortname, value1, value2, value3 FROM categories"
    if parent >= 0:
      query += " WHERE parent='" + parent + "'"
    query += " ORDER BY parent, shortname ASC"
    cursor.execute(query)
    self.categories = cursor.fetchall()
    cursor.close()
    return self.categories
  
  def GetCategory(self, id):
    cursor = self.cnx.cursor()
    query = "SELECT parent, shortname, fullname, value1, value2, value3, description FROM categories WHERE id='"+str(id)+"'"
    cursor.execute(query)
    self.category = cursor.fetchone()
    cursor.close()
    return self.category

  def GetParts(self, category):
    cursor = self.cnx.cursor()

    query = "SELECT id, partname FROM parts WHERE category='" + str(category) + "'"
    query += " ORDER BY value1"
    cursor.execute(query)
    self.parts = cursor.fetchall()
    cursor.close()
    return self.parts

  def GetSpares(self, partid, fields):
    cursor = self.cnx.cursor()
    fn = ''
    first = 1
    for f in fields:
      if first == 0:
        fn += ", "
      first = 0
      fn += f
    query = "SELECT "+fn+" FROM spares s INNER JOIN mfgs m ON s.mfg=m.id INNER JOIN suppliers f ON s.supplier=f.id WHERE s.partid='" + str(partid) + "'"
    #print(query)
    cursor.execute(query)
    columns = cursor.description
    self.spares = cursor.fetchall()
    #columns = cursor.description
    #print(self.spares)
    cursor.close()
    return self.spares

  def GetSpare(self, spareid, fields):
    cursor = self.cnx.cursor()
    fn = ''
    first = 1
    for f in fields:
      if first == 0:
        fn += ", "
      first = 0
      fn += f
    query = "SELECT "+fn+" FROM spares s INNER JOIN mfgs m ON s.mfg=m.id INNER JOIN suppliers f ON s.supplier=f.id WHERE s.id='" + str(spareid) + "'"
    #print(query)
    cursor.execute(query)
    columns = cursor.description
    self.spare = cursor.fetchone()
    #columns = cursor.description
    #print(self.spares)
    cursor.close()
    return self.spare

  def GetManufacturer(self, name):
    cursor = self.cnx.cursor()
    query = "SELECT id FROM mfgs WHERE shortname LIKE '"+name+"'"
    cursor.execute(query)
    rows = cursor.fetchall()
    if cursor.rowcount == 1:
      mfgid = rows[0][0]
    else:
      mfgid = 0
    cursor.close()
    return mfgid

  def GetSupplier(self, name):
    cursor = self.cnx.cursor()
    query = "SELECT id FROM suppliers WHERE shortname LIKE '"+name+"'"
    cursor.execute(query)
    rows = cursor.fetchall()
    if cursor.rowcount == 1:
      sid = rows[0][0]
    else:
      sid = 0
    cursor.close()
    return sid

  def Stock(self, partid, count, price=0, currency="", bom=0, description=""):
    cursor = self.cnx.cursor()

    query = "UPDATE stock SET count=count+'"+str(count)+"'"
    if price!=0:
      query +=", price='"+str(price)+"', currency='"+currency+"'"
    query += "WHERE id='"+str(partid)+"';"
    #print(query)
    cursor.execute(query)
    if cursor.rowcount == 0:
      query = "INSERT INTO stock (id, count, price, currency) VALUES ('"+str(partid)+"', '"+str(count)+"', '"+str(price)+"', '"+currency+"');"
      #print(query)
      cursor.execute(query)

    query = "INSERT INTO flow (part, count, bom, price, currency, description) VALUES ('"+str(partid)+"', '"+str(count)+"', '"+str(bom)+"', '"+str(price)+"', '"+currency+"', '"+description+"');"
    #print(query)
    cursor.execute(query)
    
    cursor.close()
    self.cnx.commit()

  def GetStockFlow(self, fields, where):
    cursor = self.cnx.cursor()
    fn = ''
    first = 1
    for f in fields:
      if first == 0:
        fn += ", "
      first = 0
      fn += f
    query = "SELECT "+fn+" FROM flow f INNER JOIN parts p ON f.part=p.id WHERE " + where
    #print(query)
    cursor.execute(query)
    rows = cursor.fetchall()
    #columns = cursor.description
    #print(self.spares)
    cursor.close()
    return rows


  # Select from database
  def Select(self, table, fields, where=None, sort=None):
    cursor = self.cnx.cursor()
    names = ""
    for key in fields:
      if names != "":
        names += ", "
      names += "`"+key+"`"

    query = "SELECT "+names+" FROM "+table;
    if where != None:
      w = ""
      for key in where:
        if w != "":
          w += " AND "
        if type(where[key]) in [str, unicode]:
          w += unicode(key)+" LIKE '"+unicode(where[key])+"'"
        else:
          w += unicode(key)+"='"+unicode(where[key])+"'"
      query += " WHERE "+w;
    if sort != None:
      query += " ORDER BY "+sort
    #print(query)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()

    return rows
   
  def Insert(self, table, data):
    # Insert to database
    cursor = self.cnx.cursor()
    names = "("
    values = "("
    first = 1
    for key in data:
      if first == 0:
        names += ", "
        values += ", "
      first = 0
      names += "`"+unicode(key)+"`"
      values += "'"+unicode(data[key])+"'"
    names += ")"
    values += ")"

    query = "INSERT INTO "+table+" "+names+" VALUES "+values+";"
    #print(query)
    #rowid = 88888
    cursor.execute(query)
    rowid = cursor.lastrowid
    self.cnx.commit()
    cursor.close()

    return rowid
   
  def Update(self, table, data, where):
    # Insert to database
    cursor = self.cnx.cursor()
    values = ""
    for key in data:
      if values != "":
        values += ", "
      first = 0
      values += unicode(key)+"='"+unicode(data[key])+"'"

    w = ""
    for key in where:
      if w != "":
        w += " AND "
      first = 0
      w += unicode(key)+"='"+unicode(where[key])+"'"

    query = "UPDATE "+table+" SET "+values+" WHERE "+w+";"
    #print(query)
    cursor.execute(query)
    self.cnx.commit()
    cursor.close()

    return 0
   
  def Delete(self, table, where):
    # Insert to database
    cursor = self.cnx.cursor()

    w = ""
    for key in where:
      if w != "":
        w += " AND "
      first = 0
      if type(where[key]) in [str, unicode]:
        w += unicode(key)+" LIKE '"+unicode(where[key])+"'"
      else:
        w += unicode(key)+"='"+unicode(where[key])+"'"

    query = "DELETE FROM "+table+" WHERE "+w+";"
    print(query)
    cursor.execute(query)
    self.cnx.commit()
    cursor.close()

    return 0
   