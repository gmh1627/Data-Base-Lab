drop table if exists borrow;
drop table if exists reserve;
drop table if exists reader;
drop table if exists administrator;
drop table if exists applicant;
drop table if exists book;
/*
drop procedure if exists borrowBook;
drop procedure if exists returnBook;
drop procedure if exists reserveBook;
drop procedure if exists renewBook;
*/
create table book(
 ID int primary key not NULl,	-- 0
 name varchar(20) not NULL,		-- 1
 author varchar(20),	-- 2
 price float,		-- 3
 type varchar(20), -- 图书类型 4
 brief varchar(800), -- 简介 5
 publish_Date date,	-- 出版日期 6
 press varchar(20), -- 出版社 7
 store int not NULL,	-- 总数量 8
 num int, -- 库存数量 9
 borrow_times int default 0, -- 借阅次数 10
 image text	-- 图书封面 11
);

create table administrator(
 ID int primary key not NULL,
 name varchar(20) not NULL,
 sex char(2) not null,
 check(sex='男' or sex='女' or sex='？'),
 phone decimal(11),
 password char(20)	-- 密码
);

create table applicant(
 ID int primary key not NULL,
 name varchar(20) not NULL,
 sex char(2) not null,
 check(sex='男' or sex='女' or sex='？'),
 phone decimal(11),
 password char(20)	-- 密码
);

create table reader(
 ID int primary key not NULL,
 name varchar(20) not NULL,
 sex char(2) not null,
 check(sex='男' or sex='女' or sex='？'),
 phone decimal(11), -- 联系电话
 permission INT default 0, -- 权限，0 可借阅/预约/续借，1 可借 不可预约/续借，2 不可借阅/预约/续借
 penalty float default 0, -- 违约金总额
 paid float default 0, -- 已支付金额
 password char(20)
);

create table borrow(
 book_ID int,
 reader_ID int,
 borrow_Date int, -- 借阅时间
 repay_Date int, -- 应还时间
 renew int default 0,	-- 续借次数
 constraint PK_Borrow primary key(book_ID,reader_ID,borrow_Date),
 constraint FK_Borrow_book_ID foreign key(book_ID) references Book(ID),
 constraint FK_Borrow_reader_ID foreign key(reader_ID) references Reader(ID)
);

create table reserve(
 book_ID int,
 reader_ID int,
 reserve_Date int,	-- 预计取书
 late_Date int,	-- 预计还书
 constraint PK_Reserve primary key(book_ID,reader_ID,reserve_Date),
 constraint FK_Reserve_book_ID foreign key(book_ID) references Book(ID),
 constraint FK_Reserve_reader_ID foreign key(reader_ID) references Reader(ID),
 constraint RBcheck check(late_Date > reserve_Date)
);

Delimiter //
#drop trigger if exists update_booknum;
create trigger update_afborrow after insert on borrow for each row
begin
	declare cnt int;
	select count(*) from reserve where book_ID = new.book_ID and reader_ID = new.reader_ID into cnt;
    if cnt >0 then update reserve set take_Date = new.borrow_Date where book_ID = new.book_ID and reader_ID = new.reader_ID;end if;
	update book set borrow_times=borrow_times+1 where ID=new.book_ID;
end //

/*
Delimiter //
drop trigger if exists update_booknum;
create trigger update_booknum before insert on book for each row
begin
	update book set num=new.store where ID=new.ID;
end //
*/
/* 存储过程borrowBook，当读者借书时调用该存储过程完成借书处理
   flag=-1 输入错误，flag=-2 违规借阅，flag=-3 图书无库存，flag=-4 无权限
Delimiter //
create procedure borrowBook(in bid char(8), in rid char(8), out flag int)
begin
    declare rcnt int; declare bcnt int;
    declare pm int;
    declare bt int;
    declare bn int;
    declare ab int;
    declare rr int;
    declare ord int;
    declare reserve_cnt int;
	declare continue handler for sqlexception set flag=0; -- 当错误代码为sqlexception时将变量flag设为0，继续执行当前任务
    start transaction;
	select count(*) from reader where ID=rid into rcnt;
    select count(*) from book where ID=bid into bcnt;
	if rcnt=0 or bcnt=0 then set flag=-1;    -- 找不到读者或图书ID
	else
		select permission from reader where ID=rid into pm;
		if pm<>2 then	-- 读者有借阅权限
			select count(*) from borrow where reader_ID=rid into bt;	-- 读者已经借阅了3本图书且均未归还
            select count(*) from borrow where reader_ID=rid and book_ID=bid into ab;	-- 读者已借阅同一本读书且未归还
			if bt=3 or ab>0 then set flag=-2;
			else
				select num from book where ID=bid into bn;
				if bn=0 then set flag=-3;		-- 无库存
				else	-- 有库存
					select count(*) from reserve where book_ID=bid into reserve_cnt;
                    if reserve_cnt<bn then set flag=0;	-- 有多余未被预约的书，可直接借阅
                    else
						select count(*) from reserve where book_ID=bid and reader_ID=rid into rr;
						if rr=1 then 	-- 该图书存在预约记录，且当前借阅者已预约，查看预约位次
							select count(*) from(
								select book_ID, reader_ID from reserve where book_ID=bid 
                                order by reserve_Date asc limit bn)table_ar 
							where reader_ID=rid into ord;
							if ord>0 then set flag=1;	-- 预约位次小于库存数量，可预约
                            else set flag=-3;	-- 预约位次大于库存数，不可预约
                            end if;
						else set flag=-3;	-- 借阅者未预约
						end if;
                    end if;
                end if;
			end if;
		else set flag=-4;	-- 无权限
		end if;
	end if;
    if flag=0 or flag=1 then
        insert into borrow value(bid, rid, curdate(), 0);
		update book set num=num-1, borrow_times=borrow_times+1 where ID=bid;
        if flag=1 then delete from reserve where book_ID=bid and reader_ID=rid; end if;
		commit;
	else rollback;
	end if;
end //

存储过程returnBook，当读者还书时调用该存储过程完成还书处理
   flag=-1 输入错误，flag=-2 违规归还
Delimiter //
create procedure returnBook(in bid char(8), in rid char(8), out flag int)
begin
    declare rcnt int;
    declare bcnt int;
    declare ab int;
	declare continue handler for sqlexception set flag=0; -- 当错误代码为sqlexception时将变量flag设为0，继续执行当前任务
    start transaction;
	select count(*) from reader where ID=rid into rcnt;
    select count(*) from book where ID=bid into bcnt;
	if rcnt=0 or bcnt=0 then set flag=-1;    -- 找不到读者或图书ID
	else
		select count(*) from borrow where reader_ID=rid and book_ID=bid into ab;
		if ab=0 then set flag=-2;		-- 没有借过该图书或借过但已归还
		else set flag=0;
		end if;
	end if;
    if flag=0 then
		delete from borrow where book_ID=bid and reader_ID=rid;
		update book set num=num+1 where ID=bid;
        select borrow_Date from borrow where book_ID=bid and reader_ID=rid into bcnt;
        select renew from borrow where book_ID=bid and reader_ID=rid into rcnt;
        set bcnt=curdate()-borrow-renew*30;	  -- 计算超出预定日期的天数
        if bcnt>30 and bcnt<150 then	-- 每超出一天罚款0.2元
			update reader set penalty=penalty+0.2*bcnt where ID=rid; 
		end if;
        if bcnt>=150 then	-- 设置违约金上限为30元
			update reader set penalty=penalty+30 where ID=rid; 
		end if;
        select reader_ID from reserve where book_ID=bid and take_Date is null order by reserve_Date asc limit 1 into ab;
		if ab is not null then	-- 该书存在预约，则更新预约表
			update reserve set take_Date=curdate()+10 where reader_ID=ab and book_ID=bid; 
		end if;
		commit;
	else rollback;
	end if;
end //

存储过程reserveBook，当读者预约时调用该存储过程预约处理
   flag=-1 输入错误，flag=-2 违规预约，flag=-3 库存充足 不允许预约，flag=-4 无权限
Delimiter //
create procedure reserveBook(in bid char(8), in rid char(8), out flag int)
begin
    declare rcnt int; declare bcnt int;
    declare br int; declare rr int;
    declare pm int;
    declare bt int; declare rt int;
    declare bn int; declare rn int;
    declare already_borrow int;
    declare already_reserve int;
    declare reader_reserve int;
	declare continue handler for sqlexception set flag=0; -- 当错误代码为sqlexception时将变量flag设为0，继续执行当前任务
    start transaction;
	select count(*) from reader where ID=rid into rcnt;
    select count(*) from book where ID=bid into bcnt;
	if rcnt=0 or bcnt=0 then set flag=-1;    -- 找不到读者或图书ID
	else
		select permission from reader where ID=rid into pm;
		if pm=0 then	-- 有预约权限
			select count(*) from borrow where reader_ID=rid and bt;
			select count(*) from reserve where reader_ID=rid into rt;
			if bt+rt=5 then set flag=-2; -- 读者借阅且预约的书籍已经有5本
			else
				select count(*) from reserve where reader_ID=rid and book_ID=bid into rr;
				select count(*) from book where reader_ID=rid and book_ID=bid into br;
				if br>0 or rr>0 then set flag=-2;	-- 该书已被该读者借阅或预约且未还书
				else
					select num from book where ID=bid into bn;
                    select count(*) from reserve where book_ID=bid into rn;
					if rn>=bn then set flag=0;	-- 该图书已被借阅完或已预约数不少于库存数，此时可以预约
					else set flag=-3;	-- 该书库存充足，无需预约
					end if;
				end if;
			end if;
		else set flag=-4;	-- 无权限
		end if;
	end if;
    if flag=0 then
        insert into reserve value(bid, rid, curtime(), NULL);
		commit;
	else rollback;
	end if;
end //

存储过程renewBook，当读者续借时调用该存储过程完成续借处理
   flag=-1 输入错误，flag=-2 违规续借，flag=-3 已被预约或续借次数已达上限，flag=-4 无权限
Delimiter //
create procedure renewBook(in bid char(8), in rid char(8), out flag int)
begin
    declare rcnt int; declare bcnt int;
    declare pm int;
    declare bt int;
    declare br int;
    declare bn int;
    declare ab int;
    declare rr int;
    declare ord int;
    declare reserve_cnt int;
	declare continue handler for sqlexception set flag=0; -- 当错误代码为sqlexception时将变量flag设为0，继续执行当前任务
    start transaction;
	select count(*) from reader where ID=rid into rcnt;
    select count(*) from book where ID=bid into bcnt;
	if rcnt=0 or bcnt=0 then set flag=-1;    -- 找不到读者或图书ID
	else
		select permission from reader where ID=rid into pm;
		if pm=0 then	-- 读者有续借权限
			select count(*) from borrow where reader_ID=rid into bt;	-- 读者已经借阅了3本图书且均未归还
            select count(*) from borrow where reader_ID=rid and book_ID=bid into ab;	-- 没有借过该图书或借过但已归还
			if bt=3 or ab=0 then set flag=-2;
			else
				select renew from borrow where reader_ID=rid and book_ID=bid into br;	-- 查看续借次数
                select count(*) from reserve where book_ID=bid into reserve_cnt;	-- 查看预约人数
				select num from book where ID=bid into bn;
                if br=3 or reserve_cnt>bn then set flag=-3;		-- 已被预约或续借次数已达上限
				else set flag=0;
                end if;
			end if;
		else set flag=-4;	-- 无权限
		end if;
	end if;
    if flag=0 then
        update borrow set renew=renew+1 where book_ID=bid and reader_ID=rid;
		commit;
	else rollback;
	end if;
end //
*/