import pymysql

def get_db():
    try:
        db = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="1234567890", db="test", charset = "utf8")
    except:
        db = None
        print("database connect fail")

    return db


def user_login(studentId, password):
    db = get_db()
    cursor = db.cursor()
    sql = "SELECT name FROM STUDENT WHERE studentId = '%s' && password = '%s'"% \
       (studentId, password)
    try:
   # 执行sql语句
        cursor.execute(sql)
        name = cursor.fetchall()
        
        # 执行sql语句
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    cursor.close()

    return name


def get_grade(studentId):
    db = get_db()
    cursor = db.cursor()
    sql = "select course.name, grade from student, course, sc where student.studentId = sc.studentId && sc.courseId = course.courseId && student.studentId = '%s' " % \
        (studentId);
  
    try:
   # 执行sql语句
        print(sql)
        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)
        # 执行sql语句
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    cursor.close()

    return results

def db_close():
    db = get_db()
    if db is not None:
        db.close()

if __name__ == "__main__":
    db_close()