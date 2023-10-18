import mysql.connector

host = 'localhost'
user = 'root'
passwd = 'rootbar'
database = 'mydatabase'

def add_patient(name, mail, company, phone_number, age):
    if name == "" or age == "" or company == "" or mail == "" or phone_number == "":
        return 0
    else:
        con = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)
        mycursor = con.cursor()
        query = "SELECT * FROM patients WHERE id = %s"
        value = (company,)
        mycursor.execute(query, value)
        row = mycursor.fetchone()
        if row is not None:
            mycursor.execute("SELECT * FROM patients")
            myresult = mycursor.fetchall()
            for x in myresult:
                print(x)
            return 2
        else:
            mycursor.execute("INSERT INTO patients(name, id, mail, device, age, sex) VALUES(%s, %s, %s, %s, %s, %s)",
                             (name, company, mail, device, age, sex))
        mycursor.execute("SELECT * FROM patients")
        myresult = mycursor.fetchall()
        for x in myresult:
            print(x)
        con.commit()
        con.close()
        return 3

def update_device_patient(dev, company):
    con = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)
    mycursor = con.cursor()
    mycursor.execute("INSERT INTO device(did, aid) VALUES(%s, %s)", (dev, company))
    con.commit()
    con.close()

def device_readings(dev, heart, temp, dt, spo):
    con = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)
    mycursor = con.cursor()
    mycursor.execute("UPDATE dataArd SET heart = %d WHERE did = %s", (heart, dev))
    mycursor.execute("UPDATE dataArd SET spo = %d WHERE did = %s", (spo, dev))
    mycursor.execute("UPDATE dataArd SET temp = %d WHERE did = %s", (temp, dev))
    con.commit()
    con.close()

def patient_det(company):
    con = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)
    mycursor = con.cursor()
    query = "SELECT * FROM patients WHERE id = %s"
    value = (company,)
    mycursor.execute(query, value)
    row = mycursor.fetchone()
    mycursor.close()
    con.close()
    return row

def remove_pat(company):
    con = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)
    mycursor = con.cursor()
    query = "DELETE FROM patients WHERE id = %s"
    value = (company,)
    mycursor.execute(query, value)
    con.commit()
    mycursor.execute("SELECT * FROM patients")
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)
    mycursor.close()
    con.close()

def get_all():
    con = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)
    mycursor = con.cursor()
    con.commit()
    mycursor.execute("SELECT * FROM patients")
    myresult = mycursor.fetchall()
    mycursor.close()
    con.close()
    if myresult:
        return myresult
    else:
        return 0

def search(name):
    con = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)
    mycursor = con.cursor()
    query = "SELECT * FROM patients WHERE name = %s"
    value = (name,)
    mycursor.execute(query, value)
    row = mycursor.fetchall()
    mycursor.close()
    con.close()
    print(row)
    if row:
        return row
    else:
        return 0
