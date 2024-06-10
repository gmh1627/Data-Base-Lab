from django.db import models

class dzTable(models.Model):  # Reader information
    dzid = models.AutoField(primary_key=True)  # Reader ID
    psw = models.CharField(max_length=256)  # Reader password
    xm = models.CharField(max_length=10)  # Name
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(dzTable, self).save(force_insert, force_update, using, update_fields)
        
class tsglyTable(models.Model):  # Library administrator information
    glyid = models.CharField(max_length=10, primary_key=True)  # Work number
    psw = models.CharField(max_length=256)  # Administrator password
    xm = models.CharField(max_length=10)  # Name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(tsglyTable, self).save(force_insert, force_update, using, update_fields)

class smTable(models.Model):  # Bibliographic information
    isbn = models.CharField(max_length=50, primary_key=True)  # ISBN number
    sm = models.CharField(max_length=50)  # Book title
    zz = models.CharField(max_length=50)  # Author
    cbs = models.CharField(max_length=50)  # Publisher
    cbny = models.DateTimeField()  # Publication year and month
    jbr = models.ForeignKey(tsglyTable, on_delete=models.CASCADE)  # Handler
    count = models.IntegerField(default=0)  # Count of books

class tsTable(models.Model):  # Book information
    tsid = models.AutoField(primary_key=True)  # Book id
    isbn = models.ForeignKey(smTable, on_delete=models.CASCADE)  # ISBN number
    cfwz = models.CharField(max_length=20)  # Storage location (Circulation room, Reading room)
    zt = models.CharField(max_length=20)  # Status (Not borrowed, Borrowed, Not for loan, Reserved)
    jbr = models.ForeignKey(tsglyTable, on_delete=models.CASCADE)  # Handler

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        assert self.cfwz in ('流通室', '阅览室'), 'The storage location must be the circulation room or the reading room'
        assert self.zt in ('未借出', '已借出', '不外借'), 'The book status must be Not borrowed, Borrowed, Not for loan, Reserved'
        super(tsTable, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):  # Outbound trigger
        assert self.zt != '已借出', 'Borrowed books are not allowed to be out of the library'
        super(tsTable, self).delete(using, keep_parents)


class jsTable(models.Model):  # Borrowing information
    dzid = models.ForeignKey(dzTable, on_delete=models.PROTECT)  # Reader ID
    tsid = models.ForeignKey(tsTable, on_delete=models.PROTECT)  # Book ID
    jysj = models.DateTimeField()  # Borrowing time
    yhsj = models.DateTimeField()  # Due time
    ghsj = models.DateTimeField(blank=True, null=True)  # Return time

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        assert self.jysj < self.yhsj, 'The return time should be after the borrowing time'
        super(jsTable, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        unique_together = ("dzid", "tsid", "jysj")
'''
class yyTable(models.Model):  # 预约信息
    dzid = models.ForeignKey(dzTable, on_delete=models.CASCADE)  # 读者ID
    isbn = models.ForeignKey(smTable, on_delete=models.CASCADE)  # ISBN号
    tsid = models.ForeignKey(tsTable, blank=True, null=True, on_delete=models.CASCADE)  # 图书ID
    yysj = models.DateTimeField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):  # 创建预约触发器
        super(yyTable, self).save(force_insert, force_update, using, update_fields)
        if not self.tsid:  # 新建预约没有图书id
            mail(
                "预约成功通知函",
                "您已成功预约一本书, 书名为《" + str(self.isbn.sm) +
                "》。预约时间：" + str(timezone.now()),
                self.dzid.email
            )
        else:  # 预约更新添加图书id
            mail(
                "预约借书通知",
                "您预约的图书《" + str(self.isbn.sm) + "》已经为您库存，请及时借阅！",
                self.dzid.email
            )

    class Meta:
        unique_together = ("dzid", "isbn", "yysj")
'''
