from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password  # 用户密码管理
from django.utils import timezone  # django带时区管理的时间类
from .models import dzTable, tsglyTable, smTable, tsTable, jsTable, BookReview # 引入数据库
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
        if not (xm and mm and mmqr):
            context['msg'] = "请填写完整的信息"
            return render(request, 'register.html', context=context)
        if mm != mmqr:
            context["msg"] = "两次密码输入不一致，请检查"
            return render(request, 'register.html', context=context)
        if len(mm) < 6:
            context["msg"] = "密码长度至少需要六位"
            return render(request, 'register.html', context=context)
        table = dzTable  # 默认只处理读者注册
        id_field = 'dzid'
        if table.objects.filter(xm=xm).exists():
            context["msg"] = "用户名已被使用，请选择其他用户名"
            return render(request, 'register.html', context=context)
        if table.objects.exists():
            id_value = int(getattr(table.objects.latest(id_field), id_field)) + 1
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

from django.db.models import Count, Window, F
from django.db.models.functions import Rank

def dz_index(request):
    if request.session.get('login_type', None) != 'dz':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm', None)
    context['id'] = request.session.get('id', None)
    all_borrows = jsTable.objects.filter(dzid_id=request.session.get('id'))
    current_borrows = all_borrows.filter(ghsj=None)

    # Calculate total number of users
    total_users = jsTable.objects.values('dzid_id').distinct().count()

    # Calculate the rank of the current user based on the total number of borrows
    user_ranks = jsTable.objects.values('dzid_id').annotate(total_borrows=Count('id')).annotate(rank=Window(expression=Rank(), order_by=F('total_borrows').desc()))
    current_user_rank = user_ranks.filter(dzid_id=request.session.get('id')).order_by('rank').first().get('rank')

    grzt = []
    for elem in all_borrows:
        if elem.tsid:
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
    context['current_borrow_count'] = len(current_borrows)
    context['historical_borrow_count'] = len(all_borrows)
    context['user_rank'] = current_user_rank
    context['total_users'] = total_users
    return render(request, 'dz_index.html', context=context)

def current_borrows_view(request):  # 当前借阅书籍
    if request.session.get('login_type', None) != 'dz':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm', None)
    context['id'] = request.session.get('id', None)
    current_borrows = jsTable.objects.filter(dzid_id=request.session.get('id')).filter(ghsj=None)
    grzt = []
    for elem in current_borrows:
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
    context['current_borrow_count'] = len(current_borrows)  # 当前借阅数量
    return render(request, 'current_borrows.html', context=context)

from django.shortcuts import render, get_object_or_404
from django.db.models import Avg

def book_details(request, isbn):
    # Fetch book information from tsTable
    books_info = tsTable.objects.filter(isbn=isbn)

    # Calculate the average score from bookReview
    average_score = BookReview.objects.filter(isbn=isbn).aggregate(Avg('score'))['score__avg'] or 0

    # Fetch all reviews for the book
    reviews = BookReview.objects.filter(isbn=isbn)

    context = {
        'xm': request.session.get('xm', None),
        'id': request.session.get('id', None),
        'books_info': books_info,
        'average_score': average_score,
        'reviews': reviews,
    }
    return render(request, 'book_details.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

# 读者书目状态查询
def dz_smztcx(request):
    if request.session.get('login_type', None) != 'dz':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm', None)
    context['id'] = request.session.get('id', None)
    
    # 检查是否是提交书评的POST请求
    if request.method == 'POST' and 'isbn' in request.POST and 'comment' in request.POST:
        # 处理书评提交
        isbn_code = request.POST.get('isbn')
        score = request.POST.get('score')
        comment = request.POST.get('comment')
        dzid = request.session.get('id', None)
        try:
            isbn_instance = smTable.objects.get(isbn=isbn_code)
            BookReview.objects.create(isbn=isbn_instance, score=score, comment=comment, dzid_id=dzid)
            return JsonResponse({'message': 'Review submitted successfully!'})
        except smTable.DoesNotExist:
            return JsonResponse({'message': 'ISBN code does not match any book.'}, status=404)
        
    elif request.method == 'GET':
        return render(request, 'dz_smztcx.html', context=context)
    else:  # POST
        context['sm'] = sm = request.POST.get('sm')  # 书名
        context['zz'] = zz = request.POST.get('zz')  # 作者
        context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
        context['cbs'] = cbs = request.POST.get('cbs')  # 出版社
        context['msg'] = "未知错误，请重试"
        result = smTable.objects.all()
        if not sm:  # 确保书名输入不为空
            context['msg'] = "请输入书名进行搜索！"
            return render(request, 'dz_smztcx.html', context=context)
        result = result.filter(sm__icontains=sm)  # 使用 __icontains 实现模糊搜索
        if zz:
            result = result.filter(zz__icontains=zz)
        if isbn:
            result = result.filter(isbn__startswith=isbn)
        if cbs:
            result = result.filter(cbs__icontains=cbs)
        smzt = []
        for elem in result:
            detail_url = reverse('book_details', kwargs={'isbn': elem.isbn})
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
                    'detail_url': detail_url,
                }
            )
        context['msg'] = ''
        context['smzt'] = smzt
        return render(request, 'dz_smztcx.html', context=context)

def check_review(request, isbn):
    dzid = request.session.get('id', None)
    hasReviewed = BookReview.objects.filter(isbn__isbn=isbn, dzid_id=dzid).exists()
    if hasReviewed:
        message = "You have already reviewed this book. To submit another review, please revoke your previous one first."
    else:
        message = ""
    return JsonResponse({'hasReviewed': hasReviewed, 'message': message})

@csrf_exempt
def submit_review(request):
    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        score = request.POST.get('score')
        comment = request.POST.get('comment')
        dzid = request.session.get('id', None)
        
        if not score:
            return JsonResponse({'message': 'Score is required.'}, status=400)
        
        try:
            isbn_instance = smTable.objects.get(isbn=isbn)
            # Removed the check for existing review here
            BookReview.objects.create(isbn=isbn_instance, score=score, comment=comment, dzid_id=dzid)
            return JsonResponse({'message': 'Review submitted successfully!'})
        except smTable.DoesNotExist:
            return JsonResponse({'message': 'No book matches the provided ISBN code.'}, status=404)
    return JsonResponse({'message': 'Invalid request'}, status=400)

def dz_js(request):  # 读者借书
    if request.session.get('login_type', None) != 'dz':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm')
    context['dzid'] = str(request.session.get('id', None))  # 将 id 转换为字符串类型
    if request.method == 'GET':
        return render(request, 'dz_js.html', context=context)
    else:
        context['isbn'] = isbn = request.POST.get('isbn')
        context['msg'] = "未知错误，请重试"
        dzid = context['dzid']  # 获取读者 id，直接从会话中获取
        if not isbn:
            context['msg'] = "请填写完整的ISBN号"
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
            yhsj=timezone.now() + timezone.timedelta(days=60)# 借书期限60天
        )
        item.save()  # 添加借书信息
        context['msg'] = "借阅成功！（图书id：" + str(result.tsid) + "）"
        return render(request, 'dz_js.html', context=context)

def dz_hs(request):  # 读者还书
    if request.session.get('login_type', None) != 'dz':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm')
    context['dzid'] = request.session.get('id', None)
    if request.method == 'GET':
        return render(request, 'dz_hs.html', context=context)
    else:
        dzid = context['dzid']  # 获取读者 id，直接从会话中获取
        context['tsid'] = tsid = request.POST.get('tsid')
        context['msg'] = "未知错误，请重试"
        if not tsid:
            context['msg'] = "请填写完整的图书id"
            return render(request, 'dz_hs.html', context=context)
        if not tsid.isdecimal():
            context['msg'] = "图书id必须是数字！"
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

# 读者评价列表
def my_reviews(request):
    dzid = request.session.get('id', None)
    context = dict()
    context['xm'] = request.session.get('xm')  # Assuming 'xm' is the user's name or similar
    context['dzid'] = dzid  # Get dzid from session
    if request.method == 'GET':
        # Fetch all reviews for the given dzid, including related book details
        reviews = BookReview.objects.filter(dzid=dzid).select_related('isbn').order_by('comment_time')
        
        # Set up pagination
        paginator = Paginator(reviews, 10)  # Show 10 reviews per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Calculate offset
        offset = (page_obj.number - 1) * paginator.per_page
        
        # Prepare reviews data for the template
        reviews_data = [{
            'id': review.id,
            'isbn': review.isbn.isbn,
            'sm': review.isbn.sm,
            'score': review.score,
            'comment': review.comment,
            'comment_time': review.comment_time,
            'index': i + 1 + offset  # Add an index key for each review
        } for i, review in enumerate(page_obj)]
        
        context['reviews'] = reviews_data
        context['current_page'] = page_obj.number
        context['total_pages'] = paginator.num_pages
        context['offset'] = offset  # Add offset to context
    
    return render(request, 'my_reviews.html', context=context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
def revoke_review(request):
    try:
        # Parse request body to get data
        data = json.loads(request.body)
        review_id = data.get('reviewId')
        # Attempt to retrieve and delete the review
        review = BookReview.objects.get(id=review_id)
        review.delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        
        return JsonResponse({'success': False, 'error': str(e)})

def ranking(request): # 展示评分最高的十本书及其评分，被借阅次数最多的十本书及其被借次数
    if request.session.get('login_type', None) != 'dz':
        return HttpResponseRedirect("/")
    
    context = dict()
    context['xm'] = request.session.get('xm', None)
    context['id'] = request.session.get('id', None)
    
    # 获取评分最高的十本书及其评分，确保书籍有评分
    top_rated_books = BookReview.objects.exclude(score__isnull=True).values('isbn__sm', 'isbn').annotate(average_score=Avg('score')).filter(average_score__gt=0).order_by('-average_score')[:10]
    
    # 获取被借阅次数最多的十本书及其被借次数，确保书籍被借阅过
    most_borrowed_books = jsTable.objects.exclude(tsid__isnull=True).values('tsid__isbn__sm', 'tsid__isbn').annotate(borrow_count=Count('tsid')).filter(borrow_count__gt=0).order_by('-borrow_count')[:10]
    
    context['top_rated_books'] = top_rated_books
    context['most_borrowed_books'] = most_borrowed_books
    
    return render(request, 'ranking.html', context=context)

# =====================管理员======================

def gly_index(request):  # 管理员首页
    if request.session.get('login_type', None) != 'gly':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm')
    context['glyid'] = request.session.get('id') 
    return render(request, 'gly_index.html', context=context) 

def book_details2(request, isbn): 
    # Fetch book information from tsTable
    books_info = tsTable.objects.filter(isbn=isbn)

    # Calculate the average score from bookReview
    average_score = BookReview.objects.filter(isbn=isbn).aggregate(Avg('score'))['score__avg'] or 0

    # Fetch all reviews for the book
    reviews = BookReview.objects.filter(isbn=isbn)

    context = {
        'xm': request.session.get('xm', None),
        'id': request.session.get('id', None),
        'books_info': books_info,
        'average_score': average_score,
        'reviews': reviews,
    }
    return render(request, 'book_details2.html', context)

# 读者书目状态查询
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
        if not sm:  # 确保书名输入不为空
            context['msg'] = "请输入书名进行搜索！"
            return render(request, 'gly_smztcx.html', context=context)
        result = smTable.objects.filter(sm__icontains=sm)  # 使用 __icontains 实现模糊搜索
        if zz:
            result = result.filter(zz__icontains=zz)
        if isbn:
            result = result.filter(isbn__startswith=isbn)
        if cbs:
            result = result.filter(cbs__icontains=cbs)
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

def borrowed_books(request):# 所有借阅信息
    if request.session.get('login_type', None) != 'gly':
        return HttpResponseRedirect("/")
    context = dict()
    context['xm'] = request.session.get('xm', None)
    context['glyid'] = request.session.get('id') 
    borrowed_books = jsTable.objects.select_related('dzid', 'tsid').filter(ghsj__isnull=True).order_by('dzid')
    context['borrowed_books'] = borrowed_books
    return render(request, 'borrowed_books.html', context=context)

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
                jsTable.objects.filter(tsid=elem).update(is_valid=False)
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
                jsTable.objects.filter(tsid=elem).update(is_valid=False)
                elem.delete()
            context['msg'] = "出库成功！"
            context['tsid'] = tsid
        
        sm = smTable.objects.get(isbn=isbn)
        remaining_books = tsTable.objects.filter(isbn=elem.isbn).count()
        if remaining_books == 0:
        # 如果没有剩余的书，从smTable和tsTable中删除
            sm.delete()
        else:
        # 更新smTable中的数量    
            sm.count = tsTable.objects.filter(isbn=elem.isbn).count()
            #sm.bwjcs = tsTable.objects.filter(isbn=elem.isbn, zt='不外借').count()
            #sm.wjccs = tsTable.objects.filter(isbn=elem.isbn, zt='未借出').count()
            #sm.yjccs = tsTable.objects.filter(isbn=elem.isbn, zt='已借出').count()
            sm.save()
        return render(request, 'gly_ck.html', context=context)
    
from django.db.models import Count

def book_count_view(request):
    # 使用annotate和Count来计算每本书的借阅次数，并使用filter排除借阅次数为0的记录
    book_counts = jsTable.objects.values('tsid__isbn__isbn', 'tsid__isbn__sm')\
        .annotate(total=Count('tsid'))\
        .filter(total__gt=0)\
        .order_by('-total')
    context = {
        'book_counts': book_counts,
        'glyid': request.session.get('id')
    }
    return render(request, 'book_count.html', context)

def reader_count_view(request):
    reader_counts = jsTable.objects.values('dzid__dzid', 'dzid__xm').annotate(total=Count('dzid')).order_by('-total')
    context = {
        'reader_counts': reader_counts,
        'glyid': request.session.get('id')
    }
    return render(request, 'reader_count.html', context)