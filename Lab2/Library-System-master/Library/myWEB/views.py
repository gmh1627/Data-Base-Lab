from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password  # 用户密码管理
from django.utils import timezone  # django带时区管理的时间类
from .models import dzTable, tsglyTable, smTable, tsTable, jsTable # 引入数据库、
from django.core.paginator import Paginator

def home(request):
    return render(request, 'home.html')

def login_view(request):  # 读者、管理员用户登录
    context = dict()
    if request.method == 'POST':
        context["username"] = username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")  # 新增的字段
        if not username:
            context["msg"] = "请输入用户名"
            return render(request, 'home.html', context=context)
        if not password:
            context["msg"] = "密码不能为空"
            return render(request, 'home.html', context=context)
        if user_type == 'admin':  # 管理员使用用户名登录
            result = tsglyTable.objects.filter(xm=username)
            if result.exists() and check_password(password, result[0].psw):  # 管理员登录成功
                request.session['login_type'] = 'gly'
                request.session['id'] = result[0].glyid
                request.session['xm'] = result[0].xm
                return redirect('/gly_index/')
            else:
                context["msg"] = "用户名或密码输入错误"
                return render(request, 'home.html', context=context)
        else:  # 读者使用用户名登录
            result = dzTable.objects.filter(xm=username)
            if result.exists() and check_password(password, result[0].psw):  # 读者登录成功
                request.session['login_type'] = 'dz'
                request.session['id'] = result[0].dzid
                request.session['xm'] = result[0].xm
                return redirect('/dz_index/')
            else:
                context["msg"] = "用户名或密码输入错误"
                return render(request, 'home.html', context=context)
    else:
        return render(request, 'home.html')

def register(request):  # 新用户注册账户
    context = dict()
    if request.method == 'GET':
        return render(request, 'register.html', context=context)
    elif request.method == 'POST':
        context["xm"] = xm = request.POST.get("xm")  # 姓名
        mm = request.POST.get("mm")  # 密码
        mmqr = request.POST.get("mmqr")  # 密码确认
        user_type = request.POST.get("user_type")  # 用户类型
        context["msg"] = "未知错误，请重试"
        if not (xm and mm and mmqr):
            context['msg'] = "请填写完整的信息"
            return render(request, 'register.html', context=context)
        if mm != mmqr:
            context["msg"] = "两次密码输入不一致，请检查"
            return render(request, 'register.html', context=context)
        if len(mm) < 6:
            context["msg"] = "密码长度至少需要六位"
            return render(request, 'register.html', context=context)
        if user_type == 'admin':
            table = tsglyTable
            id_field = 'glyid'
        else:
            table = dzTable
            id_field = 'dzid'
        if table.objects.filter(xm=xm).exists():
            context["msg"] = "用户名已被使用，请选择其他用户名"
            return render(request, 'register.html', context=context)
        if table.objects.exists():
            id_value = int(getattr(table.objects.latest(id_field), id_field)) + 1  # 修改这里，使 id_value 直接是数字
        else:
            id_value = 1
        item = table(xm=xm, **{id_field: id_value, 'psw': make_password(mm)})
        item.save()
        return redirect('login_view')
    else:
        return render(request, 'register.html', context=context)
        
def logout_view(request):  # 读者、管理员退出登录
    if request.session.get('login_type', None):
        request.session.flush()
    return HttpResponseRedirect("/")

"""
登录后的session:
request.session['login_type']: 读者'dz'  管理员'gly'
request.session['id']: 读者id  管理员工号 
request.session['xm']: 读者姓名 管理员姓名
"""

# =====================读者======================

def dz_index(request):  # 读者首页
    if request.session.get('login_type', None) != 'dz':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm', None)
    context['id'] = request.session.get('id', None)
    result = jsTable.objects.filter(dzid_id=request.session.get('id'))
    grzt = []
    for elem in result:
        grzt.append(
            {
                'tsid': elem.tsid.tsid,
                'sm': elem.tsid.isbn.sm,
                'jysj': elem.jysj,
                'yhsj': elem.yhsj,
                'ghsj': elem.ghsj
            }
        )
    paginator = Paginator(grzt, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    return render(request, 'dz_index.html', context=context)

def dz_smztcx(request):  # 读者书目状态查询
    if request.session.get('login_type', None) != 'dz':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm', None)
    if request.method == 'GET':
        return render(request, 'dz_smztcx.html', context=context)
    else:  # POST
        context['sm'] = sm = request.POST.get('sm')  # 书名
        context['zz'] = zz = request.POST.get('zz')  # 作者
        context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
        context['cbs'] = cbs = request.POST.get('cbs')  # 出版社
        context['msg'] = "未知错误，请重试"
        result = smTable.objects.all()
        if not sm and not zz and not isbn and not cbs:
            context['msg'] = "请输入有效筛选信息！"
            return render(request, 'dz_smztcx.html', context=context)
        if sm:
            result = result.filter(sm__contains=sm)
        if zz:
            result = result.filter(zz__contains=zz)
        if isbn:
            result = result.filter(isbn__startswith=isbn)
        if cbs:
            result = result.filter(cbs__contains=cbs)
        smzt = []
        for elem in result:
            smzt.append(
                {
                    'ISBN': elem.isbn,
                    'sm': elem.sm,
                    'zz': elem.zz,
                    'cbs': elem.cbs,
                    'cbny': elem.cbny,
                    'kccs': len(tsTable.objects.filter(isbn=elem.isbn)),
                    'bwjcs': len(tsTable.objects.filter(isbn=elem.isbn, zt='不外借')),
                    'wjccs': len(tsTable.objects.filter(isbn=elem.isbn, zt='未借出')),
                    'yjccs': len(tsTable.objects.filter(isbn=elem.isbn, zt='已借出')),
                    'yyycs': len(tsTable.objects.filter(isbn=elem.isbn, zt='已预约')),
                }
            )
        context['msg'] = ''
        context['smzt'] = smzt
        return render(request, 'dz_smztcx.html', context=context)

def dz_js(request):  # 读者借书
    if request.session.get('login_type', None) != 'dz':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm')
    context['dzid'] = dzid = request.session.get('dzid')  # Get reader id from session
    if request.method == 'GET':
        return render(request, 'dz_js.html', context=context)
    else:
        context['isbn'] = isbn = request.POST.get('isbn')
        context['msg'] = "未知错误，请重试"
        if not dzid or not isbn:
            context['msg'] = "请填写完整的读者id和ISBN号"
            return render(request, 'dz_js.html', context=context)
        if not dzid.isdecimal():
            context['msg'] = "读者id不存在！"
            return render(request, 'dz_js.html', context=context)
        result = dzTable.objects.filter(dzid=dzid)
        if not result.exists():
            context['msg'] = "读者id不存在！"
            return render(request, 'dz_js.html', context=context)
        result = smTable.objects.filter(isbn=isbn)
        if not result.exists():
            context['msg'] = "ISBN号填写错误，不存在该类书籍！"
            return render(request, 'dz_js.html', context=context)
        result = jsTable.objects.filter(dzid_id=dzid, ghsj=None)
        if len(result) >= 10:
            context['msg'] = "该读者借阅书籍数已经达到上限！"
            return render(request, 'dz_js.html', context=context)
        result = tsTable.objects.filter(isbn_id=isbn, zt='未借出')
        if not result.exists():
            context['msg'] = "该图书已全部被借出，无法借阅！"
            return render(request, 'dz_js.html', context=context)
        result = result[0]
        result.zt = '已借出'
        result.save()  # 修改图书状态
        item = jsTable(
            dzid_id=dzid,
            tsid=result,
            jysj=timezone.now(),
            yhsj=timezone.now() + timezone.timedelta(days=60)
        )
        item.save()  # 添加借书信息
        context['msg'] = "借阅成功！（图书id：" + str(result.tsid) + "）"
        return render(request, 'dz_js.html', context=context)

def dz_hs(request):  # 读者还书
    if request.session.get('login_type', None) != 'dz':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm')
    if request.method == 'GET':
        return render(request, 'dz_hs.html', context=context)
    else:
        context['dzid'] = dzid = request.POST.get('dzid')
        context['tsid'] = tsid = request.POST.get('tsid')
        context['msg'] = "未知错误，请重试"
        if not dzid or not tsid:
            context['msg'] = "请填写完整的读者id和ISBN号"
            return render(request, 'dz_hs.html', context=context)
        if not dzid.isdecimal() or not tsid.isdecimal():
            context['msg'] = "读者id和图书id必须是数字！"
            return render(request, 'dz_hs.html', context=context)
        result = dzTable.objects.filter(dzid=dzid)
        if not result.exists():
            context['msg'] = "读者id不存在！"
            return render(request, 'dz_hs.html', context=context)
        result = tsTable.objects.filter(tsid=tsid)
        if not result.exists():
            context['msg'] = "不存在该图书id！"
            return render(request, 'dz_hs.html', context=context)
        result = jsTable.objects.filter(dzid_id=dzid, tsid_id=tsid, ghsj=None)  # 未归还的借书记录
        if not result.exists():
            context['msg'] = "该读者未借阅该图书！"
            return render(request, 'dz_hs.html', context=context)
        result = result[0]
        if timezone.now() - result.yhsj > timezone.timedelta(days=0):  # 逾期未还
            context['msg'] = "图书逾期归还，应该缴纳费用" + str((timezone.now() - result.yhsj).days * 0.1) + "元"
        else:  # 期限内归还
            context['msg'] = "图书期限内归还"
        ts = tsTable.objects.get(tsid=tsid)
        ts.zt = '未借出'
        ts.save()
        result.ghsj = timezone.now()  # 归还此书
        result.save()
        return render(request, 'dz_hs.html', context=context)

# =====================管理员======================

def gly_index(request):  # 管理员首页
    if request.session.get('login_type', None) != 'gly':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm')
    context['glyid'] = request.session.get('id') 
    return render(request, 'gly_index.html', context=context) 

def gly_smztcx(request):  # 管理员书目状态查询
    if request.session.get('login_type', None) != 'gly':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm', None)
    context['glyid'] = request.session.get('id') 
    if request.method == 'GET':
        return render(request, 'gly_smztcx.html', context=context)
    else:
        context['sm'] = sm = request.POST.get('sm')  # 书名
        context['zz'] = zz = request.POST.get('zz')  # 作者
        context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
        context['cbs'] = cbs = request.POST.get('cbs')  # 出版社
        context['msg'] = "未知错误，请重试"
        result = smTable.objects.all()
        if sm:
            result = result.filter(sm__contains=sm)
        if zz:
            result = result.filter(zz__contains=zz)
        if isbn:
            result = result.filter(isbn__startswith=isbn)
        if cbs:
            result = result.filter(cbs__contains=cbs)
        smzt = []
        for elem in result:
            smzt.append(
                {
                    'ISBN': elem.isbn,
                    'sm': elem.sm,
                    'zz': elem.zz,
                    'cbs': elem.cbs,
                    'cbny': elem.cbny,
                    'kccs': len(tsTable.objects.filter(isbn=elem.isbn)),
                    'bwjcs': len(tsTable.objects.filter(isbn=elem.isbn, zt='不外借')),
                    'wjccs': len(tsTable.objects.filter(isbn=elem.isbn, zt='未借出')),
                    'yjccs': len(tsTable.objects.filter(isbn=elem.isbn, zt='已借出')),
                }
            )
        context['msg'] = ''
        context['smzt'] = smzt
        return render(request, 'gly_smztcx.html', context=context)

def smzt_all(request):  # 所有书目状态查询
    context = dict()
    context['glyid'] = request.session.get('id') 
    result = smTable.objects.all()
    smzt = []
    for elem in result:
        smzt.append(
            {
                'ISBN': elem.isbn,
                'sm': elem.sm,
                'zz': elem.zz,
                'cbs': elem.cbs,
                'cbny': elem.cbny,
                'kccs': len(tsTable.objects.filter(isbn=elem.isbn)),
                'bwjcs': len(tsTable.objects.filter(isbn=elem.isbn, zt='不外借')),
                'wjccs': len(tsTable.objects.filter(isbn=elem.isbn, zt='未借出')),
                'yjccs': len(tsTable.objects.filter(isbn=elem.isbn, zt='已借出')),
            }
        )
    paginator = Paginator(smzt, 10)  # 每页显示10个书目
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    context['all_books'] = smzt
    return render(request, 'smzt_all.html', context=context)

def gly_rk(request):  # 管理员入库
    if request.session.get('login_type', None) != 'gly':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm', None)
    context['glyid'] = request.session.get('id') 
    if request.method == 'GET':
        return render(request, 'gly_rk.html', context=context)
    else:
        context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
        context['rksl'] = rksl = request.POST.get('rksl')  # 入库数量
        context['rkhzt'] = rkhzt = request.POST.get('rkhzt')  # 入库后状态（流通室、阅览室）
        context['sm'] = sm = request.POST.get('sm')  # 书名（新书录入）
        context['zz'] = zz = request.POST.get('zz')  # 作者（新书录入）
        context['cbs'] = cbs = request.POST.get('cbs')  # 出版社（新书录入）
        context['cbny'] = cbny = request.POST.get('cbny')  # 出版年月（新书录入）
        context['msg'] = "未知错误，请重试"
        if not isbn or not rksl or not rkhzt:
            context['msg'] = "请填写ISBN号、入库数量和入库后状态"
            return render(request, 'gly_rk.html', context=context)
        if rkhzt != '流通室' and rkhzt != '阅览室':
            context['msg'] = "入库后状态必须为流通室或阅览室"
            return render(request, 'gly_rk.html', context=context)
        result = smTable.objects.filter(isbn=isbn)
        if result.exists():  # 旧书录入
            if sm:
                result = result.filter(sm__contains=sm)
                if not result.exists():
                    context['msg'] = "检测到旧书录入，且书名信息不匹配，请检查"
                    return render(request, 'gly_rk.html', context=context)
            if zz:
                result = result.filter(zz__contains=zz)
                if not result.exists():
                    context['msg'] = "检测到旧书录入，且作者信息不匹配，请检查"
                    return render(request, 'gly_rk.html', context=context)
            if cbs:
                result = result.filter(cbs__contains=cbs)
                if not result.exists():
                    context['msg'] = "检测到旧书录入，且出版社信息不匹配，请检查"
                    return render(request, 'gly_rk.html', context=context)
            if cbny:
                result = result.filter(cbny=cbny)
                if not result.exists():
                    context['msg'] = "检测到旧书录入，且出版年月不匹配，请检查"
                    return render(request, 'gly_rk.html', context=context)
            if rkhzt == '流通室':
                for _ in range(int(rksl)):
                    item = tsTable(
                        isbn_id=isbn,
                        cfwz='流通室',
                        zt='未借出',
                        jbr_id=request.session.get('id'),
                    )
                    item.save()
            else:  # 阅览室不外借
                for _ in range(int(rksl)):
                    item = tsTable(
                        isbn_id=result[0].isbn,
                        cfwz='阅览室',
                        zt='不外借',
                        jbr_id=request.session.get('id'),
                    )
                    item.save()
            context['msg'] = "旧书入库成功！"
            book = smTable.objects.get(isbn=isbn)
            book.count = tsTable.objects.filter(isbn=book).count()
            book.save()
        else:   # 新书录入
            if not (sm and zz and cbs and cbny):
                context['msg'] = "检测到新书录入，请完整填写信息"
                return render(request, 'gly_rk.html', context=context)
            item = smTable(
                isbn=isbn,
                sm=sm,
                zz=zz,
                cbs=cbs,
                cbny=cbny,
                jbr_id=request.session.get('id'),
            )
            item.save()
            if rkhzt == '流通室':
                for _ in range(int(rksl)):
                    item = tsTable(
                        isbn_id=isbn,
                        cfwz='流通室',
                        zt='未借出',
                        jbr_id=request.session.get('id'),
                    )
                    item.save()
            else:  # 阅览室不外借
                for _ in range(int(rksl)):
                    item = tsTable(
                        isbn_id=isbn,
                        cfwz='阅览室',
                        zt='不外借',
                        jbr_id=request.session.get('id'),
                    )
                    item.save()
            context['msg'] = "新书入库成功！"
            book = smTable.objects.get(isbn=isbn)
            book.count = tsTable.objects.filter(isbn=book).count()
            book.save()
        return render(request, 'gly_rk.html', context=context)

def gly_ck(request):  # 管理员出库
    if request.session.get('login_type', None) != 'gly':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm', None)
    context['glyid'] = request.session.get('id') 
    if request.method == 'GET':
        return render(request, 'gly_ck.html', context=context)
    else:
        context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
        context['cksl'] = cksl = request.POST.get('cksl')  # 出库数量
        context['ckyx'] = ckyx = request.POST.get('ckyx')  # 出库优先（未借出、不外借）
        context['msg'] = "未知错误，请重试"
        if not isbn or not cksl or not ckyx:
            context['msg'] = "请填写ISBN号、入出库数量和优先出库位置"
            return render(request, 'gly_ck.html', context=context)
        if ckyx != '流通室' and ckyx != '阅览室':
            context['msg'] = "优先出库位置必须为流通室或阅览室"
            return render(request, 'gly_ck.html', context=context)
        result = smTable.objects.filter(isbn=isbn)
        if not result.exists():
            context['msg'] = "ISBN录入有误，请检查"
            return render(request, 'gly_ck.html', context=context)
        wjc = tsTable.objects.filter(isbn_id=isbn, zt='未借出')  # 未借出图书数量
        bwj = tsTable.objects.filter(isbn_id=isbn, zt='不外借')  # 不外借图书数量
        ts = tsTable.objects.filter(isbn_id=isbn)  # 所有图书数量
        cksl = int(cksl)
        if len(ts) < cksl:
            context['msg'] = "出库数量超过藏书总数！请检查"
            return render(request, 'gly_ck.html', context=context)
        if len(wjc) + len(bwj) < cksl:
            context['msg'] = "由于部分书目已被借出，出库失败！"
            return render(request, 'gly_ck.html', context=context)
        tsid = ''
        ck = []
        if ckyx == '流通室':  # 未借出 > 不外借
            for elem in wjc:
                if cksl > 0:
                    tsid += str(elem.tsid) + ' '
                    ck.append(elem)
                    cksl -= 1
                else:
                    break
            for elem in bwj:
                if cksl > 0:
                    tsid += str(elem.tsid) + ' '
                    ck.append(elem)
                    cksl -= 1
                else:
                    break
            for elem in ck:
                elem.delete()
            context['msg'] = "出库成功！"
            context['tsid'] = tsid
        else:  # 不外借 > 未借出
            for elem in bwj:
                if cksl > 0:
                    tsid += str(elem.tsid) + ' '
                    ck.append(elem)
                    cksl -= 1
                else:
                    break
            for elem in wjc:
                if cksl > 0:
                    tsid += str(elem.tsid) + ' '
                    ck.append(elem)
                    cksl -= 1
                else:
                    break
            for elem in ck:
                elem.delete()
            context['msg'] = "出库成功！"
            context['tsid'] = tsid
        
        sm = smTable.objects.get(isbn=isbn)
        sm.kccs = tsTable.objects.filter(isbn=elem.isbn).count()
        sm.bwjcs = tsTable.objects.filter(isbn=elem.isbn, zt='不外借').count()
        sm.wjccs = tsTable.objects.filter(isbn=elem.isbn, zt='未借出').count()
        sm.yjccs = tsTable.objects.filter(isbn=elem.isbn, zt='已借出').count()
        sm.save()
        return render(request, 'gly_ck.html', context=context)