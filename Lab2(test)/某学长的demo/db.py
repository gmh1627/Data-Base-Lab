import MySQLdb
from MySQLdb._exceptions import OperationalError
import numpy as np

def db_login(user, passwd, host, dbname):
    try:
        db = MySQLdb.connect(host, user, passwd, dbname)
    except OperationalError:
        db = None

    return db

def db_close(db):
    if db is not None:
        db.close()

def db_showtable(db):
    cursor = db.cursor()
    cursor.execute("show tables")
    # fetchall() 一次性获取所有数据
    tabs = cursor.fetchall()    
    res = list()
    for tab in tabs:
        cursor.execute("select count(*) from " + tab[0])
        # fetchone() 一次性获取一条数据
        row_cnt = cursor.fetchone() 

        res.append((tab[0], row_cnt[0]))
    
    cursor.close()
    return res

def db_login_admin(db, ID, password):
    """管理员登录查询, 返回true or false"""
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM administrator WHERE ID = '%s' and password = '%s'" %(ID, password)
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    cursor.close()
    if count == 0:
        return False
    else:
        return True
    
def db_login_reader(db, ID, password):
    """读者登录查询, 返回true or false"""
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM reader WHERE ID = '%s' and password = '%s'" %(ID, password)
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    cursor.close()
    if count == 0:
        return False
    else:
        return True

def db_get_reader_num(db):
    '''获取读者总人数'''
    cursor = db.cursor()
    cursor.execute("select count(*) from reader")
    tab = cursor.fetchone()[0]
    cursor.close()
    return tab

def db_get_administrator_num(db):
    '''获取管理员总人数'''
    cursor = db.cursor()
    cursor.execute("select count(*) from administrator")
    tab = cursor.fetchone()[0]
    cursor.close()
    return tab

def db_get_applicant_num(db):
    '''获取管理员申请人总人数'''
    cursor = db.cursor()
    cursor.execute("select count(*) from applicant")
    tab = cursor.fetchone()[0]
    cursor.close()
    return tab

def db_search_allbook(db):
    '''获取所有书籍'''
    cursor = db.cursor()
    cursor.execute("select * from book")
    tabs = cursor.fetchall()
    cursor.close()
    return tabs

def db_search_allborrow(db, book_id):
    '''获取某本书的所有借阅情况'''
    cursor = db.cursor()
    sql = "select * from borrow where book_ID = '%s'" %(book_id)
    cursor.execute(sql)
    tabs = cursor.fetchall()
    cursor.close()
    return tabs

def db_search_allreserve(db, book_id):
    '''获取某本书的所有预约情况'''
    cursor = db.cursor()
    sql = "select * from reserve where book_ID = '%s'" %(book_id)
    cursor.execute(sql)
    tabs = cursor.fetchall()
    cursor.close()
    return tabs

def db_insert_borrow(db, book_id, reader_id, borrow_Date, repay_Date):
    '''增加借书，如果该书曾被该读者预约过，会自动修改预约记录(实际取书时间)'''
    cursor = db.cursor()
    try:
        sql = "insert into borrow(book_ID, reader_ID, borrow_Date, repay_Date) values('%s', '%s', '%s', '%s')" %\
                (book_id, reader_id, borrow_Date, repay_Date)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_insert_reserve(db, book_id, reader_id, reserve_Date, late_Date):
    '''增加预约'''
    cursor = db.cursor()
    try:
        sql = "insert into reserve(book_ID, reader_ID, reserve_Date, late_Date) values('%s', '%s', '%s', '%s')" %\
                (book_id, reader_id, reserve_Date, late_Date)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_insert_reader(db, name, sex, phone, password):
    '''增加读者'''
    cursor = db.cursor()
    ID = db_get_reader_num(db) + 1
    try:
        sql = "insert into reader(ID, name, sex, phone, password) values('%s', '%s', '%s', '%s', '%s')" %\
                (ID, name, sex, phone, password)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()
    return ID

def db_insert_administrator(db, name, sex, phone, password):
    '''增加管理员'''
    cursor = db.cursor()
    ID = db_get_administrator_num(db) + 1
    try:
        sql = "insert into administrator values('%s', '%s', '%s', '%s', '%s')" %\
                (ID, name, sex, phone, password)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()
    return ID

def db_insert_applicant(db, name, sex, phone, password):
    '''增加管理员申请者'''
    cursor = db.cursor()
    ID = db_get_applicant_num(db) + 1
    try:
        sql = "insert into applicant values('%s', '%s', '%s', '%s', '%s')" %\
                (ID, name, sex, phone, password)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()
    return ID

def db_insert_book(db, name, author, price, type, brief, pd, press, store, img_path):
    '''增加新书'''
    cursor = db.cursor()
    cursor.execute("select max(ID) from book")
    ID = cursor.fetchone()[0] + 1
    if int(store) <= 0: return None
    try:
        sql = "insert into book(ID, name, author, price, type, brief, publish_Date, press, store, num, image) values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %\
                (ID, name, author, price, type, brief, pd, press, store, store, img_path)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        return None
    cursor.close()
    return ID

def db_delete_applicant(db, id):
    '''删除管理员申请人'''
    cursor = db.cursor()
    try:
        sql = "delete from applicant where ID = '%s'" % (id)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_returnbook(db, book_id, reader_id, return_date):
    '''还书，修改借书记录'''
    cursor = db.cursor()
    try:
        sql = "update from borrow set return_date = '%s' where book_ID = '%s' and reader_ID = '%s'" % (return_date, book_id, reader_id)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_delete_book(db, ID):
    '''删除图书'''
    cursor = db.cursor()
    try:
        sql = "delete from borrow where book_ID = '%s'" % (ID)
        cursor.execute(sql)
        sql = "delete from reserve where book_ID = '%s'" % (ID)
        cursor.execute(sql)
        sql = "delete from book where ID = '%s'" % (ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        return False
    cursor.close()
    return True

def db_update_book_name(db, ID, name):
    '''修改图书名'''
    cursor = db.cursor()
    try:
        sql = "update book set name = '%s' where ID='%s'" % (name, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_renew(db, book_id, reader_id):
    '''续借'''
    cursor = db.cursor()
    sql = "select renew from borrow where book_ID = '%s' and reader_ID = '%s'" % (book_id, reader_id)
    cursor.execute(sql)
    cnt = cursor.fetchone()[0] + 1
    try:
        sql = "update borrow set renew = '%s' where book_ID='%s' and reader_ID='%s'" % (cnt, book_id, reader_id)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_book_author(db, ID, name):
    '''修改图书作者'''
    cursor = db.cursor()
    try:
        sql = "update book set author = '%s' where ID='%s'" % (name, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_book_price(db, ID, name):
    '''修改图书价格'''
    cursor = db.cursor()
    try:
        sql = "update book set price = '%s' where ID='%s'" % (name, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_book_price(db, ID, name):
    '''修改图书价格'''
    cursor = db.cursor()
    try:
        sql = "update book set price = '%s' where ID='%s'" % (name, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_book_type(db, ID, name):
    '''修改图书类型'''
    cursor = db.cursor()
    try:
        sql = "update book set type = '%s' where ID='%s'" % (name, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_book_brief(db, ID, name):
    '''修改图书简介'''
    cursor = db.cursor()
    try:
        sql = "update book set brief = '%s' where ID='%s'" % (name, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_book_pd(db, ID, name):
    '''修改图书出版日期'''
    cursor = db.cursor()
    try:
        sql = "update book set publish_Date = '%s' where ID='%s'" % (name, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_book_press(db, ID, name):
    '''修改图书出版社'''
    cursor = db.cursor()
    try:
        sql = "update book set press = '%s' where ID='%s'" % (name, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_book_store(db, ID, num):
    '''修改图书总数'''
    cursor = db.cursor()
    sql = "select store from book where ID='%s'" % (ID)
    cursor.execute(sql)
    cnt = cursor.fetchone()[0]
    sql = "select num from book where ID='%s'" % (ID)
    cursor.execute(sql)
    cnt2 = cursor.fetchone()[0]
    try:
        sum = cnt + int(num)
        sum2 = cnt2 + int(num)
    except ValueError:
        return False
    if sum2 < 0: return False
    if sum == 0: return db_delete_book(db, ID)
    try:
        sql = "update book set store = '%s' where ID='%s'" % (sum, ID)
        cursor.execute(sql)
        sql = "update book set num = '%s' where ID='%s'" % (sum2, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        return False
    cursor.close()
    return True

def db_update_book_img(db, ID, img_path):
    '''修改图书图片'''
    cursor = db.cursor()
    try:
        sql = "update book set image = '%s' where ID='%s'" % (img_path, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_reader_password(db, password, ID):
    '''读者修改个人密码'''
    cursor = db.cursor()
    try:
        sql = "update reader set password = '%s' where ID='%s'" % (password, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_admin_password(db, password, ID):
    '''管理员修改个人密码'''
    cursor = db.cursor()
    try:
        sql = "update administrator set password = '%s' where ID='%s'" % (password, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_reader_name(db, name, ID):
    '''读者修改个人用户名'''
    cursor = db.cursor()
    try:
        sql = "update reader set name = '%s' where ID='%s'" % (name, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_admin_name(db, name, ID):
    '''管理员修改个人用户名'''
    cursor = db.cursor()
    try:
        sql = "update administrator set name = '%s' where ID='%s'" % (name, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_reader_phone(db, phone, ID):
    '''读者修改个人电话号码'''
    cursor = db.cursor()
    try:
        sql = "update reader set phone = '%s' where ID='%s'" % (phone, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_admin_phone(db, phone, ID):
    '''管理员修改个人电话号码'''
    cursor = db.cursor()
    try:
        sql = "update administrator set phone = '%s' where ID='%s'" % (phone, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_reader(db, ID, name, sex, phone, permission, penalty, paid, password):
    '''修改读者信息'''
    cursor = db.cursor()
    try:
        sql = "update reader set name = '%s', sex = '%s', phone = '%s', permission = '%s', penalty = '%s', paid='%s', password='%s' where ID = '%s'"\
            % (name, sex, phone, permission, penalty, paid, password, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_update_reader_permission(db, ID, permission):
    '''修改读者权限'''
    cursor = db.cursor()
    try:
        sql = "select permission from reader where ID = '%s'" % (ID)
        cursor.execute(sql)
        permission = max(cursor.fetchone()[0], permission)
        sql = "update reader set permission = '%s' where ID = '%s'" % (permission, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_add_reader_penalty(db, ID, penalty):
    '''增加违约金'''
    cursor = db.cursor()
    try:
        sql = "select penalty from reader where ID = '%s'" % (ID)
        cursor.execute(sql)
        penalty += cursor.fetchone()[0]
        sql = "update reader set penalty = '%s' where ID = '%s'" % (penalty, ID)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()

def db_search_reader(db):
    """
    查询全体读者
    @res: list 返回 ID, name, sex 性别(char), phone(str), permission , penalty, paid
    """
    cursor = db.cursor()
    cursor.execute("select * from reader")
    tabs = cursor.fetchall()
    res = list()
    
    for tab in tabs:
        ID = tab[0]
        name = tab[1]
        sex = tab[2]
        phone = tab[3]
        permission = tab[4]
        penalty = tab[5]
        paid = tab[6]
        res.append((ID, name, sex, phone, permission, penalty, paid))

    cursor.close()
    return res

def db_search_administrator(db):
    """
    查询全体管理员
    @res: list 返回 ID, name, sex 性别(char), phone(str)
    """
    cursor = db.cursor()
    cursor.execute("select * from administrator")
    tabs = cursor.fetchall()
    res = list()
    
    for tab in tabs:
        ID = tab[0]
        name = tab[1]
        sex = tab[2]
        phone = tab[3]
        res.append((ID, name, sex, phone))

    cursor.close()
    return res

def db_search_reader_name(db, name):
    '''查询读者用户名是否重复，重复返回False'''
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM reader WHERE name = '%s'" %(name)
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    cursor.close()
    if count == 0:
        return True
    else:
        return False
    
def db_search_admin_name(db, name):
    '''查询管理员用户名是否重复'''
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM administrator WHERE name = '%s'" %(name)
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    cursor.close()
    if count == 0:
        return True
    else:
        return False
    
def db_search_applicant_name(db, name):
    '''查询管理员申请人用户名是否重复'''
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM applicant WHERE name = '%s'" %(name)
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    cursor.close()
    if count == 0:
        return True
    else:
        return False
    
def db_search_single_applicant(db, id):
    '''查询单个管理员申请人'''
    cursor = db.cursor()
    sql = "SELECT * FROM applicant WHERE ID = '%s'" %(id)
    cursor.execute(sql)
    tabs = cursor.fetchone()
    return tabs

def db_search_all_applicant(db):
    '''查询所有申请人'''
    cursor = db.cursor()
    sql = "SELECT * FROM applicant"
    cursor.execute(sql)
    tabs = cursor.fetchall()
    cursor.close()
    return tabs

def db_search_single_reader(db, ID):
    """查询单个读者"""
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM reader WHERE ID = '%s'" %(ID)
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.close()
        return []
    sql = "SELECT * FROM reader WHERE ID = '%s'" %(ID)
    cursor.execute(sql)
    tabs = cursor.fetchone()
    cursor.close()
    return tabs

def db_search_single_administrator(db, ID):
    """查询单个管理员"""
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM administrator WHERE ID = '%s'" %(ID)
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.close()
        return []
    sql = "SELECT * FROM administrator WHERE ID = '%s'" %(ID)
    cursor.execute(sql)
    tabs = cursor.fetchone()
    cursor.close()
    return tabs

def db_search_readername(db, name):
    """根据用户名(可以不是全称)查询读者"""
    cursor = db.cursor()
    cursor.execute("select * from reader where name like %s", ('%'+name+'%',))
    tabs = cursor.fetchall()
    cursor.close()
    return tabs

def db_search_bookID(db, ID):
    """查询某本图书详情"""
    cursor = db.cursor()
    sql = "select * from book where ID = '%s'" %(ID)
    cursor.execute(sql)
    tabs = cursor.fetchone()
    cursor.close()
    return tabs

def db_search_single_borrow(db, ID):
    """
    查询某个读者的借阅情况
    @res: list 返回 book_ID, book_name, borrow_Date, return_Date, renew 续借次数
    """
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM reader WHERE ID = '%s'" %(ID)
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.close()
        return []
    sql = "SELECT * FROM borrow WHERE reader_ID = '%s'" %(ID)
    cursor.execute(sql)
    tabs = cursor.fetchall()
    res = list()
    
    for tab in tabs:
        book_ID = tab[0]
        sql = "SELECT name FROM book WHERE ID = '%s'" %(book_ID)
        cursor.execute(sql)
        book_name = cursor.fetchone()[0]
        borrow_Date = tab[2]
        repay_Date = tab[3]
        renew = tab[4]
        res.append((book_ID, book_name, borrow_Date, repay_Date, renew))

    cursor.close()
    return res

def db_search_single_reserve(db, ID):
    """
    查询某个读者的预约情况
    @res: list 返回 book_ID, book_name, reserve_Date, take_Date(可能为NULL)
    """
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM reader WHERE ID = '%s'" %(ID)
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.close()
        return []
    sql = "SELECT * FROM reserve WHERE reader_ID = '%s'" %(ID)
    cursor.execute(sql)
    tabs = cursor.fetchall()
    res = list()
    
    for tab in tabs:
        book_ID = tab[0]
        sql = "SELECT name FROM book WHERE ID = '%s'" %(book_ID)
        cursor.execute(sql)
        book_name = cursor.fetchone()[0]
        reserve_Date = tab[2]
        late_Date = tab[3]
        res.append((book_ID, book_name, reserve_Date, late_Date))

    cursor.close()
    return res

def db_search_books(db, page, name = ""):
    """
    # 查询借阅量最高的书籍 或 根据书名查书
    @res: list 返回 name, author, price, type, brief, publish_Date, press, store, num ,borrow_times, img_str
    """
    cursor = db.cursor()
    if name == "":
        cursor.execute("select * from book order by borrow_times desc")
    else:
        cursor.execute("select * from book where name like %s", ('%'+name+'%',)) 
    tabs = cursor.fetchall()
    cursor.close()
    L = len(tabs)
    if 5 * page + 5 <= L:
        return tabs[5 * page: 5 * page + 5], page
    else:
        return tabs[-5:], (L - 1) // 5

def db_check_borrow(db, user_id, book_id):
    """
    检查是否借阅
    """
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM borrow WHERE reader_ID = '%s' and book_ID = '%s'" %(user_id, book_id)
    cursor.execute(sql)
    tab = cursor.fetchone()[0]
    db.commit()
    if tab > 0: return True
    return False

def db_check_reserve(db, user_id, book_id):
    """
    检查是否预约
    """
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM reserve WHERE reader_ID = '%s' and book_ID = '%s'" %(user_id, book_id)
    cursor.execute(sql)
    tab = cursor.fetchone()[0]
    db.commit()
    if tab > 0: return True
    return False

def db_find_nearest(db, time, book_id):
    bs = db_search_allborrow(db, book_id)
    rs = db_search_allreserve(db, book_id)
    book = db_search_bookID(db, book_id)
    empty = book[8] * np.ones(100, np.int32)
    for b in bs:
        start = max(b[2] - time, 0)
        end = min(max(b[3] - time + 1, 0), 100)
        empty[start:end] = empty[start:end] - 1
    for r in rs:
        start = max(r[2] - time, 0)
        end = min(max(r[3] - time + 1, 0), 100)
        empty[start:end] = empty[start:end] - 1
    for i in range(100):
        if empty[i] > 0:
            return i
    return -1

def db_borrow_book(db, user_id, book_id, days, now):
    try:
        cursor = db.cursor()
        sql = "insert into borrow(book_ID, reader_ID, borrow_Date, repay_Date) values('%s', '%s', '%s', '%s')" % (book_id, user_id, now, now + days)
        cursor.execute(sql)
        sql = "select borrow_times from book where id = '%s'" % (book_id)
        cursor.execute(sql)
        br_times = int(cursor.fetchone()[0]) + 1
        sql = "update book set borrow_times = '%s' where id = '%s'" % (br_times, book_id)
        cursor.execute(sql)
        sql = "select num from book where id = '%s'" % (book_id)
        cursor.execute(sql)
        num = int(cursor.fetchone()[0]) - 1
        sql = "update book set num = '%s' where id = '%s'" % (num, book_id)
        cursor.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def db_reserve_book(db, user_id, book_id, days, now):
    now = db_find_nearest(db, now, book_id)
    try:
        cursor = db.cursor()
        sql = "insert into reserve(book_ID, reader_ID, reserve_Date, late_Date) values('%s', '%s', '%s', '%s')" % (book_id, user_id, now, now + days)
        cursor.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def db_renew_book(db, user_id, book_id, days, now):
    try:
        cursor = db.cursor()
        sql = "SELECT * FROM borrow WHERE reader_ID = '%s' and book_ID = '%s'" %(user_id, book_id)
        cursor.execute(sql)
        borrow = cursor.fetchone()
        repay_date = borrow[3] + days
        sql = "update borrow set repay_Date = '%s' where reader_ID = '%s' and book_ID = '%s'" %(repay_date, user_id, book_id)
        cursor.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False


def db_return_book(db, user_id, book_id, now):
    try:
        cursor = db.cursor()
        sql = "delete FROM borrow WHERE reader_ID = '%s' and book_ID = '%s'" %(user_id, book_id)
        cursor.execute(sql)
        sql = "select num from book where id = '%s'" % (book_id)
        cursor.execute(sql)
        num = cursor.fetchone()[0] + 1
        sql = "update book set num = '%s' where id = '%s'" % (num, book_id)
        cursor.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def db_not_reserve_book(db, user_id, book_id):
    try:
        cursor = db.cursor()
        sql = "delete FROM reserve WHERE reader_ID = '%s' and book_ID = '%s'" %(user_id, book_id)
        cursor.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def db_time_plus(db, now):
    """
    增加一天，并刷新
    @now date -- 当前时间
    """
    cursor = db.cursor()
    cursor.execute("select * from borrow")
    tabs = cursor.fetchall()
    for tab in tabs:
        repay_date = tab[3]
        reader_id = tab[1]
        if repay_date < now:
            db_add_reader_penalty(db, reader_id, 1.5)
            db_update_reader_permission(db, reader_id, 1)

    # 增加天数时，将超过预计取书时间的预约变为借阅，预计归还变为还书时间，直到库存书用完
    # 可以直接调用 db_not_reserve_book 与 db_borrow_book
    cursor.execute("select * from book")
    tabs = cursor.fetchall()
    for tab in tabs:
        book_id = tab[0]
        num = tab[9]
        sql = "select count(*) from reserve where book_ID = '%s' and reserve_Date <= '%s' " %(book_id, now)
        cursor.execute(sql)
        count = cursor.fetchone()[0]
        while(count > 0 and num > 0):
            sql = "select * from reserve where book_ID= '%s' and reserve_Date <= '%s' order by reserve_Date asc limit 1" %(book_id, now)
            cursor.execute(sql)
            reserve = cursor.fetchone()
            reader_id = reserve[1]
            days = reserve[3] - reserve[2]
            db_not_reserve_book(db, reader_id, book_id)
            db_borrow_book(db, reader_id, book_id, days, now)
            count = count - 1
    
    cursor.close()


if __name__ == "__main__":
    db = db_login("root", "Archaeus_13", "localhost", "db_library")
    tabs = db_showtable(db)
    db_close(db)