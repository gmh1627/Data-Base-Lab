import os
import re
from flask import Flask, flash, session, g
from flask import redirect
from flask import request, make_response
from flask import render_template
from flask import url_for
from db import *

# 生成一个app
app = Flask(__name__, template_folder='templates', static_url_path='/static', static_folder='static')
app.secret_key = 'lab'

ROOT_PASSWORD = "0000"
now = 0

# 对app执行请求页面地址到函数的绑定
# 将所有对主页面的访问都跳转到首页
@app.route("/", methods=["GET", "POST"])
def init():
    session["user_type"] = ""
    session["user_id"] = ""
    session["password"] = ""
    session["id"] = ""
    return redirect(url_for('index', page = 0, search = "", status=0))

@app.route("/index", methods=["GET", "POST"])
def index():
    '''未登录时的首页'''
    page = int(request.args["page"])
    bookname = request.args["search"]
    status = int(request.args["status"])
    if request.method == "POST":
        # 客户端在 index 页面发起的POST请求
        if 'back' in request.form:
            return redirect(url_for('index', page = 0, search = "", status=0))
        elif 'login' in request.form:
            return redirect(url_for('index', page = page, search = bookname, status=0))
        elif 'search' in request.form:
            bookname = request.form["bookname"]
            #传入搜索到的图书的全部内容
            return redirect(url_for('index', page = 0, search = bookname, status=0))
        elif 'page+' in request.form:
            page = page + 1
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            books, page = db_search_books(db, page, bookname)
            db.close()
            return redirect(url_for('index', page = page, search = bookname, status=0))
        elif 'page-' in request.form:
            page = max(page - 1, 0)
            return redirect(url_for('index', page = page, search = bookname, status=0))
        elif 'book_detail' in request.form:
            book_id = request.form["index"]
            return redirect(url_for('book', id=book_id))
        elif 'forgot' in request.form:
            # 忘记密码
            return redirect(url_for('admin_num', status=-1))
        elif 'logging_in' in request.form:
            # 登录请求
            user_type = request.form["user_type"]
            user_id = request.form["user_id"]
            password = request.form["password"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            if user_type == "admin":
                if db_login_admin(db, user_id, password):
                    session["user_type"] = user_type
                    session["user_id"] = user_id
                    session["password"] = password
                    session["id"] = ""
                    db.close()
                    return redirect(url_for('admin_index', page = page, search = bookname, status=0))
                else:
                    db.close()
                    return redirect(url_for('index', page = page, search = bookname, status=-1))
            elif user_type == "reader":
                if db_login_reader(db, user_id, password):
                    session["user_type"] = user_type
                    session["user_id"] = user_id
                    session["password"] = password
                    session["id"] = ""
                    db.close()
                    return redirect(url_for('reader_index', page = page, search = bookname, status=0))
                else:
                    db.close()
                    return redirect(url_for('index', page = page, search = bookname, status=-1))
            elif user_type == "root":
                # root 只有一个账户
                if user_id == "root" and password == ROOT_PASSWORD:
                    session["user_type"] = user_type
                    session["user_id"] = user_id
                    session["password"] = password
                    db.close()
                    return redirect(url_for('root_index', status=0))
                else:
                    db.close()
                    return redirect(url_for('index', page = page, search = bookname, status=-1))
        elif 'register' in request.form:
            # 注册请求
            user_type = request.form["user_type"]
            name = request.form.get('username')
            sex = request.form.get('sex')
            phone = request.form.get('phone')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            # 判断电话号码是否符合规范
            if not re.match(r'^\d{11}$', phone):
                return redirect(url_for('index', page = page, search = bookname, status=-2))
            # 判断两次密码是否正确
            if password == confirm_password:
                if user_type == "reader":
                    db = db_login("root", "Archaeus_13", "localhost", "db_library")
                    # 判断用户名是否重复
                    flag = db_search_reader_name(db, name)
                    if flag == False:
                        db.close()
                        return redirect(url_for('index', page = page, search = bookname, status=-4))
                    ID = db_insert_reader(db, name, sex, phone, password)
                    session["user_type"] = user_type
                    session["user_id"] = ID
                    session["password"] = password
                    db.close()
                    return redirect(url_for('reader_index', page = page, search = bookname, status=1))
                if user_type == "admin":
                    db = db_login("root", "Archaeus_13", "localhost", "db_library")
                    # 判断管理员申请人的名称是否重复
                    flag1 = db_search_admin_name(db, name)
                    flag2 = db_search_applicant_name(db, name)
                    if flag1 == False or flag2 == False:
                        db.close()
                        return redirect(url_for('index', page = page, search = bookname, status=-4))
                    db_insert_applicant(db, name, sex, phone, password)
                    db.close()
                    return redirect(url_for('index', page = page, search = bookname, status=1))
            else:
                return redirect(url_for('index', page = page, search = bookname, status=-3))
    db = db_login("root", "Archaeus_13", "localhost", "db_library")
    books, page = db_search_books(db, page, bookname)
    db.close()
    return render_template("/index.html", books=books, page=page + 1, status=status)

@app.route("/admin_num")
def admin_num():
    '''管理员列表，列出所有管理员'''
    status = int(request.args["status"])
    db = db_login("root", "Archaeus_13", "localhost", "db_library")
    cursor = db.cursor()
    cursor.execute("select * from administrator")
    admins = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("/admin_num.html", status=status, admins=admins)

@app.route("/reader_index", methods=['POST', "GET"])
def reader_index():
    '''读者首页'''
    user_id = session['user_id']
    page = int(request.args["page"])
    bookname = request.args["search"]
    status = int(request.args["status"])
    if session["user_type"] != "reader":
        return render_template("404.html"), 404
    if request.method == "POST":
        # 客户端在 index 页面发起的POST请求
        if 'back' in request.form:
            return redirect(url_for('reader_index', page = 0, search = "", status=0))
        if 'log_out' in request.form:
            session["user_type"] = ""
            session["user_id"] = ""
            session["password"] = ""
            session["id"] = ""
            return redirect(url_for('index', page = 0, search = "", status=0))
        elif 'search' in request.form:
            bookname = request.form["bookname"]
            #传入搜索到的图书的全部内容
            return redirect(url_for('reader_index', page = 0, search = bookname, status=0))
        elif 'page+' in request.form:
            page = page + 1
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            books, page = db_search_books(db, page, bookname)
            db.close()
            return redirect(url_for('reader_index', page = page, search = bookname, status=0))
        elif 'page-' in request.form:
            page = max(page - 1, 0)
            return redirect(url_for('reader_index', page = page, search = bookname, status=0))
        elif 'name' in request.form:
            username = request.form.get('newname')
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            flag = db_search_reader_name(db, username)
            if flag == True:
                db_update_reader_name(db, username, user_id)
                db.close()
                return redirect(url_for('reader_index', page = page, search = bookname, status=2))
            db.close()
            return redirect(url_for('reader_index', page = page, search = bookname, status=-4))
        elif 'pwd' in request.form:
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            user = db_search_single_reader(db, user_id)
            old_password = request.form.get('old_pwd')
            if old_password == user[7]:
                password = request.form.get('new_pwd')
                confirm_password = request.form.get('confirm_pwd')
                if password == confirm_password:
                    db_update_reader_password(db, password, user_id)
                    session["password"] = password
                    db.close()
                    return redirect(url_for('reader_index', page = page, search = bookname, status=2))
                else:
                    db.close()
                    return redirect(url_for('reader_index', page = page, search = bookname, status=-3))
            db.close()
            return redirect(url_for('reader_index', page = page, search = bookname, status=-1))
        elif 'phone' in request.form:
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            phone = request.form.get('newphone')
            if not re.match(r'^\d{11}$', phone):
                db.close()
                return redirect(url_for('reader_index', page = page, search = bookname, status=-2))
            db_update_reader_phone(db, phone, user_id)
            db.close()
            return redirect(url_for('reader_index', page = page, search = bookname, status=2))
        elif 'borrow' in request.form:
            book_id = request.form["book"]
            session["id"] = book_id
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            user = db_search_single_reader(db, user_id)
            book = db_search_bookID(db, book_id)
            db.close()
            if book[9] == 0:
                return redirect(url_for('reader_index', page = page, search = bookname, status=-7))
            if user[4] == 2:
                return redirect(url_for('reader_index', page = page, search = bookname, status=-6))
            # want = 1 借阅
            return redirect(url_for('reader_br', want=1))
        elif 'reserve' in request.form:
            book_id = request.form["book"]
            session["id"] = book_id
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            user = db_search_single_reader(db, user_id)
            book = db_search_bookID(db, book_id)
            db.close()
            if book[9] != 0:
                return redirect(url_for('reader_index', page = page, search = bookname, status=-8))
            if user[4] != 0:
                return redirect(url_for('reader_index', page = page, search = bookname, status=-6))
            # want = 2 预约
            return redirect(url_for('reader_br', want=2))
        elif 're' in request.form:
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            borrow = db_search_single_borrow(db, user_id)
            reserve = db_search_single_reserve(db, user_id)
            db.close()
            if len(borrow) == 0 and len(reserve) == 0:
                return redirect(url_for('reader_index', page = page, search = bookname, status=-5))
            session["id"] = ""
            # want = 0 还书/续借
            return redirect(url_for('reader_br', want=0))
    db = db_login("root", "Archaeus_13", "localhost", "db_library")
    user = db_search_single_reader(db, user_id)
    borrow = db_search_single_borrow(db, user_id)
    reserve = db_search_single_reserve(db, user_id)
    books, page = db_search_books(db, page, bookname)
    db.close()
    return render_template("/reader_index.html", books=books, page=page + 1, status=status, user=user, borrow = len(borrow), reserve = len(reserve))

@app.route("/reader_br", methods=['POST', "GET"])
def reader_br():
    '''读者个人的借阅预约详情页'''
    user_id = session['user_id']
    book_id = session["id"]
    want = int(request.args["want"])
    if session['user_type'] != "reader":
        return render_template("404.html"), 404
    if request.method == 'POST':
        if 'back' in request.form:
            session["id"] = ""
            return redirect(url_for('reader_index', page = 0, search = "", status=0))
        elif 'borrow' in request.form:
            days = int(request.form["days"])
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            db_borrow_book(db, user_id, book_id, days, now)
            db.close()
            return redirect(url_for('reader_br', want=3))
        elif 'reserve' in request.form:
            days = int(request.form["days"])
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            db_reserve_book(db, user_id, book_id, days, now)
            db.close()
            return redirect(url_for('reader_br', want=4))
        elif 'renew' in request.form:
            days = int(request.form["days"])
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            user = db_search_single_reader(db, user_id)
            if user[4] != 0:
                db.close()
                return redirect(url_for('reader_index', page = 0, search = "", status=-6))
            db_renew_book(db, user_id, book_id, days, now)
            db.close()
            return redirect(url_for('reader_br', want=3))
        elif 'return' in request.form:
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            db_return_book(db, user_id, book_id, now)
            db.close()
            session["id"] = ""
            return redirect(url_for('reader_index', page = 0, search = "", status=3))
        elif 'not_reserve' in request.form:
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            db_not_reserve_book(db, user_id, book_id)
            db.close()
            session["id"] = ""
            return redirect(url_for('reader_index', page = 0, search = "", status=3))
        elif 'renew_or_return' in request.form:
            session["id"] = request.form["renew_or_return"]
            # want = 3 续借/还书
            return redirect(url_for('reader_br', want=3))
        elif 'see_or_not_reserve' in request.form:
            session["id"] = request.form["see_or_not_reserve"]
            # want = 4 取消预约
            return redirect(url_for('reader_br', want=4))
    db = db_login("root", "Archaeus_13", "localhost", "db_library")
    user = db_search_single_reader(db, user_id)
    borrows = db_search_single_borrow(db, user_id)
    reserves = db_search_single_reserve(db, user_id)
    info = [book_id]
    message = 0; real = want
    if want == 1 or want == 2:
        if db_check_borrow(db, user_id, book_id):
            message = -1; real = 3
        elif db_check_reserve(db, user_id, book_id):
            message = -2; real = 4
    if real == 2:
        info.append(db_find_nearest(db, now, book_id))
    elif real == 3:
        for borrow in borrows:
            if str(borrow[0]) == str(book_id):
                if db_find_nearest(db, borrow[3] + 1, book_id) != 0:
                    info.append(0)
                else: info.append(10)
                break
    info.append(0)
    db.close()
    if info[1] == -1:
        message = -3
    session["begin_date"] = info[1]
    return render_template("/reader_br.html", borrows=borrows, reserves=reserves, user=user, message=message, real=real, info=info)

@app.route("/admin_index", methods=['POST', "GET"])
def admin_index():
    '''管理员首页'''
    user_id = session['user_id']
    page = int(request.args["page"])
    bookname = request.args["search"]
    status = int(request.args["status"])
    if session["user_type"] != "admin":
        return render_template("404.html"), 404
    if request.method == "POST":
        # 客户端在 index 页面发起的POST请求
        if 'back' in request.form:
            return redirect(url_for('admin_index', page = 0, search = "", status=0))
        elif 'log_out' in request.form:
            session["user_type"] = ""
            session["user_id"] = ""
            session["password"] = ""
            session["id"] = ""
            return redirect(url_for('index', page = 0, search = "", status=0))
        elif 'search' in request.form:
            bookname = request.form["bookname"]
            #传入搜索到的图书的全部内容
            return redirect(url_for('admin_index', page = 0, search = bookname, status=0))
        elif 'page+' in request.form:
            page = page + 1
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            books, page = db_search_books(db, page, bookname)
            db.close()
            return redirect(url_for('admin_index', page = page, search = bookname, status=0))
        elif 'page-' in request.form:
            page = max(page - 1, 0)
            return redirect(url_for('admin_index', page = page, search = bookname, status=0))
        elif 'name' in request.form:
            username = request.form.get('newname')
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            flag = db_search_admin_name(db, username)
            if flag == True:
                db_update_admin_name(db, username, user_id)
                db.close()
                return redirect(url_for('admin_index', page = page, search = bookname, status=2))
            db.close()
            return redirect(url_for('admin_index', page = page, search = bookname, status=-4))
        elif 'pwd' in request.form:
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            user = db_search_single_administrator(db, user_id)
            old_password = request.form.get('old_pwd')
            if old_password == user[4]:
                password = request.form.get('new_pwd')
                confirm_password = request.form.get('confirm_pwd')
                if password == confirm_password:
                    db_update_admin_password(db, password, user_id)
                    session["password"] = password
                    db.close()
                    return redirect(url_for('admin_index', page = page, search = bookname, status=2))
                else:
                    db.close()
                    return redirect(url_for('admin_index', page = page, search = bookname, status=-3))
            db.close()
            return redirect(url_for('admin_index', page = page, search = bookname, status=-1))
        elif 'phone' in request.form:
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            phone = request.form.get('newphone')
            if not re.match(r'^\d{11}$', phone):
                db.close()
                return redirect(url_for('admin_index', page = page, search = bookname, status=-2))
            db_update_admin_phone(db, phone, user_id)
            db.close()
            return redirect(url_for('admin_index', page = page, search = bookname, status=2))
        elif 'modify' in request.form:
            session["id"] = request.form["book"]
            # status = 1 修改图书信息
            return redirect(url_for('admin_index', page=page, search=bookname, status=1))
        elif 'book_name' in request.form:
            book_id = session["id"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            name = request.form.get('newname')
            db_update_book_name(db, book_id, name)
            db.close()
            # status = 3 修改成功
            return redirect(url_for('admin_index', page=page, search=bookname, status=3))
        elif 'img' in request.form:
            book_id = session["id"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            img = request.files.get('newimg')
            img_name = img.filename
            img_path = os.path.join('static', img_name)
            img.save(img_path)
            db_update_book_img(db, book_id, '/static/'+img_name)
            db.close()
            return redirect(url_for('admin_index', page=page, search=bookname, status=3))
        elif 'author' in request.form:
            book_id = session["id"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            name = request.form.get('newauthor')
            db_update_book_author(db, book_id, name)
            db.close()
            return redirect(url_for('admin_index', page=page, search=bookname, status=3))
        elif 'price' in request.form:
            book_id = session["id"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            name = request.form.get('newprice')
            db_update_book_price(db, book_id, name)
            db.close()
            return redirect(url_for('admin_index', page=page, search=bookname, status=3))
        elif 'type' in request.form:
            book_id = session["id"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            db_update_book_type(db, book_id, name)
            db.close()
            return redirect(url_for('admin_index', page=page, search=bookname, status=3))
        elif 'biref' in request.form:
            book_id = session["id"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            name = request.form.get('newbrief')
            db_update_book_brief(db, book_id, name)
            db.close()
            return redirect(url_for('admin_index', page=page, search=bookname, status=3))
        elif 'pd' in request.form:
            book_id = session["id"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            name = request.form.get('newpd')
            db_update_book_pd(db, book_id, name)
            db.close()
            return redirect(url_for('admin_index', page=page, search=bookname, status=3))
        elif 'press' in request.form:
            book_id = session["id"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            name = request.form.get('newpress')
            db_update_book_press(db, book_id, name)
            db.close()
            return redirect(url_for('admin_index', page=page, search=bookname, status=3))
        elif 'store' in request.form:
            book_id = session["id"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            num = request.form.get('newstore')
            if db_update_book_store(db, book_id, num):
                db.close()
                return redirect(url_for('admin_index', page=page, search=bookname, status=3))
            else:
                db.close()
                return redirect(url_for('admin_index', page=page, search=bookname, status=-5))
        elif 'insert' in request.form:
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            newname = request.form["newname"]
            newimg = request.files.get("newimg")
            img_name = newimg.filename
            img_path = os.path.join('static', img_name)
            newimg.save(img_path)
            newauthor= request.form["newauthor"]
            newprice = request.form["newprice"]
            newtype = request.form["newtype"]
            newbrief = request.form["newbrief"]
            newpd = request.form["newpd"]
            newpress = request.form["newpress"]
            newnum = request.form["newstore"]
            book_id = db_insert_book(db, newname, newauthor, newprice, newtype, newbrief, newpd, newpress, newnum, '/static/' + img_name)
            db.close()
            if book_id == None:
                return redirect(url_for('admin_index', page=page, search=bookname, status=-6))
            return redirect(url_for('admin_index', page=page, search=bookname, status=4))
        elif 'goto_user' in request.form:
            return redirect(url_for('reader_num', search="", status=0))
    db = db_login("root", "Archaeus_13", "localhost", "db_library")
    user = db_search_single_administrator(db, user_id)
    books, page = db_search_books(db, page, bookname)
    if session["id"] != "":
        name = db_search_bookID(db, session["id"])
        if name == None:
            session["id"] = ""
            name = ""
        else: name = name[1]
    else:
        name = ""
    db.close()
    return render_template("/admin_index.html", books=books, page=page + 1, status=status, user=user, bookname=name)

@app.route("/reader_num", methods=['POST', "GET"])
def reader_num():
    '''用户管理，对所有读者的管理'''
    admin_id = session['user_id']
    readername = request.args["search"]
    status = int(request.args["status"])
    if request.method == "POST":
        if 'back' in request.form:
            return redirect(url_for('reader_num', search = "", status=0))
        elif 'log_out' in request.form:
            session["user_type"] = ""
            session["user_id"] = ""
            session["password"] = ""
            session["book_id"] = ""
            return redirect(url_for('index', page = 0, search = "", status=0))
        elif 'search' in request.form:
            readername = request.form["readername"]
            return redirect(url_for('reader_num', search=readername, status=0))
        elif 'detail' in request.form:
            session["id"] = request.form["reader"]
            # status = 1 用户详情
            return redirect(url_for('reader_num', search=readername, status=1))
        elif 'black' in request.form:
            reader_id = session["id"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            db_update_reader_permission(db, reader_id, 2)
            # status = 2 加入黑名单成功
            db.close()
            return redirect(url_for('reader_num', search="", status=2))
        elif 'goto_book' in request.form:
            return redirect(url_for('admin_index', page=0, search="", status=0))
    db = db_login("root", "Archaeus_13", "localhost", "db_library")
    user = db_search_single_administrator(db, admin_id)
    if session["id"] != "":
        reader_id = session["id"]
        borrow = db_search_single_borrow(db, reader_id)
        reserve = db_search_single_reserve(db, reader_id)
    else:
        reader_id = ""
        borrow = []
        reserve = []
    if readername == "":
        cursor = db.cursor()
        cursor.execute("select * from reader")
        readers = cursor.fetchall()
        cursor.close()
    else:
        readers = db_search_readername(db, readername)
    db.close()
    return render_template("/reader_num.html", readers=readers, user=user, status=status, borrows=borrow, reserves=reserve, reader_id=reader_id)
    
@app.route("/root_index", methods=['POST', "GET"])
def root_index():
    '''root首页'''
    global now
    status = int(request.args["status"])
    if session["user_type"] != "root":
        return render_template("404.html"), 404
    if request.method == 'POST':
        if 'log_out' in request.form:
            session["user_type"] = ""
            session["user_id"] = ""
            session["password"] = ""
            session["book_id"] = ""
            return redirect(url_for('index', page = 0, search = "", status=0))
        elif 'time+' in request.form:
            now += 1
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            db_time_plus(db, now)
            db.close()
            return redirect(url_for("root_index", status=0))
        elif 'approve' in request.form:
            id = request.form["approve"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            applicant = db_search_single_applicant(db, id)
            db_insert_administrator(db, applicant[1], applicant[2], applicant[3], applicant[4])
            db_delete_applicant(db, id)
            db.close()
            return redirect(url_for("root_index", status=1))
        elif 'reject' in request.form:
            id = request.form["reject"]
            db = db_login("root", "Archaeus_13", "localhost", "db_library")
            db_delete_applicant(db, id)
            db.close()
            return redirect(url_for("root_index", status=-1))
    db = db_login("root", "Archaeus_13", "localhost", "db_library")
    users = db_search_all_applicant(db)
    db.close()
    return render_template("/root_index.html", users=users, status=status, date=now)

#返回不存在页面的处理
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = "5000", debug=True)