from django.db import models

class dzTable(models.Model):  # Reader information
    dzid = models.AutoField(primary_key=True)  # Reader ID
    psw = models.CharField(max_length=256)  # Reader password
    xm = models.CharField(max_length=10)  # Name
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(dzTable, self).save(force_insert, force_update, using, update_fields)
     
from django.contrib.auth.hashers import make_password

class tsglyTable(models.Model):
    glyid = models.CharField(max_length=10, primary_key=True)  # Work number
    psw = models.CharField(max_length=256)  # Administrator password
    xm = models.CharField(max_length=10)  # Name

    def save(self, *args, **kwargs):
        self.psw = make_password(self.psw)  # Encrypt the password before saving
        super(tsglyTable, self).save(*args, **kwargs)

class smTable(models.Model):  # Bibliographic information
    isbn = models.CharField(max_length=50, primary_key=True)  # ISBN number
    sm = models.CharField(max_length=50)  # Book title
    zz = models.CharField(max_length=50)  # Author
    cbs = models.CharField(max_length=50)  # Publisher
    cbny = models.DateTimeField()  # Publication year and month
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

from django.core.validators import MinValueValidator, MaxValueValidator

class BookReview(models.Model):  # Book review
    dzid = models.ForeignKey(dzTable, on_delete=models.CASCADE)
    isbn = models.ForeignKey(smTable, on_delete=models.CASCADE)
    score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    comment = models.TextField(blank=True, null=True, max_length=300)
    comment_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("dzid", "isbn", "comment_time")
        
class jsTable(models.Model):  # Borrowing information
    dzid = models.ForeignKey(dzTable, on_delete=models.PROTECT)  # Reader ID
    tsid = models.ForeignKey(tsTable, on_delete=models.SET_NULL, null=True)  # Book ID
    jysj = models.DateTimeField()  # Borrowing time
    yhsj = models.DateTimeField()  # Due time
    ghsj = models.DateTimeField(blank=True, null=True)  # Return time
    is_valid = models.BooleanField(default=True)  # Validity of the record

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        assert self.jysj < self.yhsj, 'The return time should be after the borrowing time'
        super(jsTable, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        unique_together = ("dzid", "tsid", "jysj")