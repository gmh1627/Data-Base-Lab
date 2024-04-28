create schema s_t_c_s;  
create table student  
	(SNO char(11) primary key,  
     NAME varchar(4),  
     GENDER varchar(6),  
     BIRTHDAY datetime,  
     DEPART int  
	);  
  
insert into student (SNO, NAME, GENDER, BIRTHDAY, DEPART)  
values
('PB210000001', 'YH', 'male', '2002-03-29 00:00:00', 229),
('PB210000002', 'ZY', 'male', '2001-09-12 00:00:00', 11),
('PB210000003', 'FWJ', 'male', '2001-04-29 00:00:00', 12),
('PB210000004', 'JTY', 'male', '2002-03-15 00:00:00', 11),
('PB210000005', 'YY', 'female', '2002-08-12 00:00:00', 12),
('PB210000006', 'HCC', 'male', '2002-06-25 00:00:00', 229),
('PB210000007', 'RZJ', 'male', '2002-06-14 00:00:00', 11),
('PB210000008', 'WCS', 'male', '2002-08-23 00:00:00', 13),
('PB210000009', 'ZMS', 'female', '2002-06-23 00:00:00', 12),
('PB210000010', 'WD', 'male', '2003-02-24 00:00:00', 13),
('PB210000011', 'BL', 'female', '2002-05-08 00:00:00', 14),
('PB210000012', 'ADN', 'male', '2004-06-26 00:00:00', 10),
('PB210000013', 'HD', 'male', '2003-11-17 00:00:00', 14),
('PB210000014', 'GNJ', 'male', '2001-01-28 00:00:00', 11),
('PB210000015', 'XB', 'female', '2002-10-09 00:00:00', 12),
('PB210000016', 'LC', 'female', '2003-11-30 00:00:00', 11),
('PB210000017', 'TX', 'male', '2002-05-16 00:00:00', 12),
('PB210000018', 'MY', 'male', '2003-12-02 00:00:00', 14),
('PB210000019', 'MT', 'female', '2002-02-13 00:00:00', 10),
('PB210000020', 'XY', 'female', '2001-02-14 00:00:00', 229),
('PB210000021', 'LYH', 'male', '2002-09-30 00:00:00', 229),
('PB210000022', 'MSW', 'male', '2003-06-17 00:00:00', 11),
('PB210000023', 'HXY', 'male', '2003-02-18 00:00:00', 12),
('PB210000024', 'YHS', 'female', '2003-04-01 00:00:00', 229),
('PB210000025', 'YWB', 'male', '2003-08-12 00:00:00', 229);

create table teacher  
	(TNO char(7) primary key,  
	 NAME varchar(4),  
     GENDER varchar(6),  
     BIRTHDAY datetime,  
     POSITION varchar(30),  
     DEPART int  
	);  
  
insert into teacher (TNO, NAME, GENDER, BIRTHDAY, POSITION, DEPART)  
values
('TA90021', 'HMZ', 'male', '1994/12/23 00:00:00', 'Instructor', 11),
('TA90022', 'HB', 'female', '1978/4/9 00:00:00', 'Associate Professor', 10),
('TA90023', 'ZDH', 'male', '1986/11/17 00:00:00', 'Instructor', 229),
('TA90024', 'HS', 'male', '1977/4/10 00:00:00', 'Associate Professor', 6),
('TA90025', 'HTZ', 'female', '1969/7/28 00:00:00', 'Professor', 11),
('TA90026', 'TJY', 'male', '1973/10/3 00:00:00', 'Associate Professor', 12),
('TA90027', 'XR', 'male', '1970/5/16 00:00:00', 'Associate Professor', 11),
('TA90028', 'ZXY', 'male', '1986/7/16 00:00:00', 'Instructor', 229),
('TA90029', 'ZR', 'male', '1975/9/24 00:00:00', 'Associate Professor', 11),
('TA90030', 'SY', 'male', '1972/11/6 00:00:00', 'Professor', 229),
('TA90031', 'LQA', 'female', '1986/11/17 00:00:00', 'Associate Professor', 10),
('TA90032', 'GHJ', 'male', '1976/10/1 00:00:00', 'Associate Professor', 18);

create table course  
	(CNO char(8) primary key,   
	 NAME varchar(50),   
     TYPE int,   
	 TNO char(7),  
     foreign key(TNO) references teacher(TNO)  
    );  
    
insert into course (CNO, NAME, TYPE, TNO)
values
('20230400', 'Linear_Algebra', '1', 'TA90022'),
('20230402', 'DB_Design', '1', 'TA90021'),
('20230404', 'Machine_Learning', '1', 'TA90023'),
('20230406', 'Operating_System', '1', 'TA90025'),
('20230408', 'Natural_Language_Processing', '0', 'TA90027'),
('20230410', 'Artificial_Intelligence', '1', 'TA90025'),
('20230412', 'Data_Mining', '1', 'TA90025'),
('20230414', 'Signal_Control', '1', 'TA90024'),
('20230416', 'Computer_Network', '1', 'TA90029'),
('20230418', 'Pattern_Recognition', '1', 'TA90023'),
('20230420', 'Deep_Learning', '0', 'TA90030');

create table score (  
    SNO char(11),  
    CNO char(8),  
    DEGREE int,  
    primary key (SNO, CNO),  
    foreign key (SNO) references student(SNO),  
    foreign key (CNO) references course(CNO)  
);


insert into score (SNO, CNO, DEGREE)
values
('PB210000001', '20230402', 89),
('PB210000002', '20230402', 94),
('PB210000003', '20230402', 90),
('PB210000004', '20230402', 95),
('PB210000005', '20230402', 93),
('PB210000006', '20230402', 75),
('PB210000007', '20230402', 78),
('PB210000008', '20230402', 81),
('PB210000001', '20230404', 73),
('PB210000002', '20230404', 82),
('PB210000003', '20230404', 92),
('PB210000004', '20230404', 68),
('PB210000005', '20230404', 72),
('PB210000006', '20230404', 93),
('PB210000007', '20230400', 77),
('PB210000008', '20230400', 92),
('PB210000009', '20230400', 82),
('PB210000010', '20230400', 91),
('PB210000008', '20230418', 69),
('PB210000001', '20230418', 92),
('PB210000002', '20230418', 95),
('PB210000003', '20230418', 82),
('PB210000010', '20230406', 83),
('PB210000011', '20230406', 84),
('PB210000012', '20230406', 78),
('PB210000013', '20230406', 89),
('PB210000017', '20230408', 81),
('PB210000015', '20230408', 74),
('PB210000018', '20230408', 95),
('PB210000019', '20230408', 91),
('PB210000020', '20230408', 89),
('PB210000014', '20230410', 82),
('PB210000016', '20230410', 72),
('PB210000011', '20230410', 75),
('PB210000018', '20230412', 85),
('PB210000020', '20230412', 83),
('PB210000008', '20230412', 77),
('PB210000005', '20230412', 74),
('PB210000015', '20230412', 98),
('PB210000001', '20230412', 80),
('PB210000019', '20230412', 81),
('PB210000019', '20230416', 75),
('PB210000020', '20230416', 89),
('PB210000001', '20230416', 49),
('PB210000002', '20230416', 87),
('PB210000003', '20230416', 97),
('PB210000004', '20230416', 86),
('PB210000005', '20230416', 89),
('PB210000006', '20230418', 90),
('PB210000020', '20230418', 85),
('PB210000021', '20230418', 83),
('PB210000001', '20230420', 95),
('PB210000006', '20230420', 89),
('PB210000020', '20230420', 85),
('PB210000021', '20230420', 83),
('PB210000024', '20230420', 80),
('PB210000025', '20230420', 87);

select * from student;  
select * from teacher;  
select * from course;  
select * from score;  

-- 修改基本表
-- 1
alter table student add AGE int;  

-- 2
set sql_safe_updates = 0;  
update student set AGE = YEAR(CURDATE()) - YEAR(BIRTHDAY);  
select AGE from student;  

-- 3
update student set AGE = AGE + 2;  
select AGE from student;  
  
alter table student modify column AGE CHAR(2);

-- 4
alter table student drop column AGE;  
select * from student;

-- 5
create table teacher_course  
	(TNO char(7) primary key,  
     NUM_COURSE int,  
     foreign key(TNO) references Teacher(TNO)  
    );  

-- 6
insert into teacher_course (TNO, NUM_COURSE)  
select   
    teacher.TNO,   
    CASE   
        WHEN COUNT(course.CNO) > 0 THEN COUNT(course.CNO)  
        ELSE NULL   
    END AS NUM_COURSE  
from teacher  
left join course on teacher.TNO = course.TNO  
group by teacher.TNO;  
  
select * from teacher_course;  

-- 7
delete from teacher_course  
where NUM_COURSE is NULL;  
  
select * from teacher_course;  

-- 8
drop table teacher_course;

-- 9
-- 删除外键约束
alter table score drop foreign key score_ibfk_1;  
  
-- 修改列的数据类型  
alter table student modify column Sno VARCHAR(11);  

-- 重新创建外键约束  
alter table score add foreign key (SNO) references Student(Sno);  
  
insert into student (SNO, NAME, GENDER, BIRTHDAY, DEPART)  
values   
('PB22061161', 'GMH', 'male', '2004-07-25 00:00:00', 229),  
('PB22081558', 'LYX', 'female', '2004-7-7 00:00:00', 229),  
('PB22061177', 'WYB', 'male', '2003-12-29 00:00:00', 11); 
 
select * from student;  

-- 删除外键约束  
alter table score drop foreign key score_ibfk_3;  
  
-- 修改列的数据类型  
alter table score modify column Sno VARCHAR(11);  
  
-- 重新创建外键约束  
alter table score add foreign key (SNO) references Student(Sno);  
  
insert into score (SNO, CNO, DEGREE)  
values  
('PB22061161', '20230402', 96),  
('PB22061161', '20230410', 97),  
('PB22061161', '20230412', 99);  

select * from score;  

-- 10
select min(DEGREE) into @minDegree    
from score    
where SNO='PB22061161';  
  
delete from score    
where SNO='PB22061161' and DEGREE=@minDegree;  
  
select * from score where SNO='PB22061161';

-- 索引
-- 11
create index NAME_INDEX on course(name);
show index from course;

-- 12
create unique index TNO_INDEX on teacher(tno);
show index from teacher;

-- 13
create index RECORD_INDEX on score (sno desc, degree);

-- 14
show index from score;

-- 15
drop index TNO_INDEX on teacher;
show index from teacher;

-- 查询
-- 16
select Sno,NAME
from student
where DEPART='229';

-- 17
select Sno,NAME
from student
where DEPART='229' and NAME!='GMH';

-- 18
select Sno,NAME
from student
where DEPART='11';

-- 19
select Sno,NAME
from student
where DEPART!='11' and DEPART!='229';

-- 20
select teacher.Tno,teacher.NAME
from score,course,teacher
where course.CNO=score.CNO and course.TNO=teacher.TNO and score.SNO='PB22061161';

-- 21
select count(TNO)
from teacher 
where DEPART='11' or DEPART='229';

-- 22
select SNO,NAME,YEAR(CURDATE()) - YEAR(BIRTHDAY) as Maxage
from student
where DEPART='229' 
and YEAR(CURDATE()) - YEAR(BIRTHDAY) = (
	select max(YEAR(CURDATE()) - YEAR(BIRTHDAY))
    from student
    where DEPART='229');

-- 23
select SNO,NAME,YEAR(CURDATE()) - YEAR(BIRTHDAY) as Minage
from student
where DEPART='229' 
and YEAR(CURDATE()) - YEAR(BIRTHDAY) = (
	select min(YEAR(CURDATE()) - YEAR(BIRTHDAY))
    from student
    where DEPART='229');

-- 24
select student.SNO, student.NAME, score.DEGREE
from score, student, course
where student.SNO=score.SNO and score.CNO=course.CNO and course.NAME='DB_Design' and score.DEGREE<75;

-- 25
select distinct student.SNO, student.NAME
from student, course, teacher, score
where student.SNO=score.SNO and score.CNO=course.CNO and course.TNO=teacher.TNO 
	and teacher.NAME='ZDH';
    
-- 26 
select score.SNO, score.DEGREE
from score, course
where score.CNO=course.CNO and course.NAME='Linear_Algebra'
order by score.DEGREE desc;

-- 27
select distinct score.CNO, course.NAME, avg(score.DEGREE) as ave_degree
from score, course
where score.CNO=course.CNO
group by score.CNO;

-- 28
select distinct score.CNO, course.NAME, avg(score.DEGREE) as ave_degree
from score, course
where score.CNO=course.CNO and course.TYPE=1
group by score.CNO, course.NAME;

-- 29
select distinct student.SNO, student.NAME
from student
where not exists
	(select *
	 from course
     where course.TNO='TA90023' and not exists
			(select *
            from score
            where student.SNO=score.SNO and score.CNO=course.CNO));

-- 30
select course.CNO, course.NAME, max(score.DEGREE), min(score.DEGREE), max(score.DEGREE)-min(score.DEGREE) as score_diffence
from score, course
where score.CNO=course.CNO
group by course.CNO;

-- 31
select CNO, count(CNO) as num
from score
where DEGREE<75
group by CNO;

-- 32
select distinct teacher.TNO, teacher.NAME
from teacher, score, course
where teacher.TNO=course.TNO
	and exists(
    select * 
    from score
    where course.CNO=score.CNO and score.DEGREE<75);

-- 33
select student.SNO, student.NAME
from student, score
where student.SNO=score.SNO 
group by score.SNO
having count(score.SNO)<2;

-- 34
select distinct student.SNO, student.NAME
from student
where not exists
	(select *
	 from score score1
     where score1.SNO='PB210000001' and not exists
			(select *
            from score score2
            where student.SNO=score2.SNO and score1.CNO=score2.CNO));
            
select *
from score score1, score score2
where score1.SNO='PB210000001'  and score1.CNO=score2.CNO;
     
select *
from score score1
where score1.SNO='PB210000025';

-- 35
select distinct course.NAME, avg(score.DEGREE) as ave_degree
from score
left join course on score.CNO=course.CNO
group by score.CNO;

-- 36
select student.DEPART, count(distinct student.SNO) as num_student,
  avg(case when score.DEGREE is not null then score.DEGREE else null end) as avg_score
from student 
left join score
on student.SNO=score.SNO
group by student.DEPART;

-- 37
select distinct student.NAME
from student, score, course
where student.SNO=score.SNO and score.CNO=course.CNO and course.NAME!='DB_Design' and course.NAME!='Data_Mining';

-- 38
select course.NAME, min(year(current_date())-year(student.BITHDAY)) as Minage,  max(year(current_date())-year(student.BITHDAY)) as Maxage, avg(year(current_date())-year(student.BITHDAY)) as aveage
from score
left join student
on score.SNO=student.SNO
left join course 
on course.CNO=score.CNO
group by course.NAME;

-- 38(2)
select course.NAME, min(year(current_date())-year(student.BITHDAY)) as Minage,  max(year(current_date())-year(student.BITHDAY)) as Maxage, avg(year(current_date())-year(student.BITHDAY)) as aveage
from score, student, course 
where score.SNO=student.SNO and course.CNO=score.CNO
group by course.NAME;

-- 39
select student.SNO, student.NAME
from score, student, course 
where score.SNO=student.SNO and course.CNO=score.CNO and course.NAME like 'Computer%';

-- 40
select score1.*
from score score1
where abs((select avg(DEGREE) from score where CNO=score1.CNO) - score1.DEGREE) <= 12;

-- 41
create view db_229_student as
select *
from student
where DEPART=229
with check option;

select *
from db_229_student;

-- 42
update db_229_student
set NAME='G'
where SNO='PB210000020';

select *
from db_229_student;

-- 43
select SNO, NAME
from db_229_student
where year(current_date())-year(BIRTHDAY) < 22;

-- 44、
insert into student (SNO, NAME, GENDER, BIRTHDAY, DEPART)  
values   
('SA210110021', 'QXY', 'female', '2007-07-27', '229');

select *
from db_229_student;

-- 45
insert into db_229_student (SNO, NAME, GENDER, BIRTHDAY, DEPART)  
values   
('SA210110023', 'DPC', '男', '1997-04-27', '11');

-- 46 
drop view db_229_student;

-- 47
create table teacher_sal
	(TNO char(7) primary key,  
	 SAL float,
     foreign key(TNO) references teacher(TNO)
	);  
select * from teacher_sal;

-- 48
DELIMITER //
create trigger insert_sal
before insert on teacher_sal
for each row
begin
	declare TNO_num char(7);
	select count(*) into TNO_num
    from teacher
    where TNO = new.TNO;
    
    if TNO_num = 0 then
		signal sqlstate '45000'
        set message_text = '工号必须存在于teacher表中';
	end if;
end;
//
DELIMITER ;

DELIMITER //
create trigger update_sal
before update on teacher_sal
for each row
begin
	declare TNO_num char(7);
	select count(*) into TNO_num
    from teacher
    where TNO = new.TNO;
    
    if TNO_num = 0 then
		signal sqlstate '45000'
        set message_text = '工号必须存在于teacher表中';
	end if;
end;
//
DELIMITER ;

-- 49
DELIMITER //
create trigger insert2_sal
before insert on teacher_sal
for each row
begin
	declare pos varchar(30);
    select POSITION into pos
    from teacher;
 
	if new.SAL < 4000 and pos = 'Instructor' then
		set new.SAL = 4000;
	elseif new.sal < 7000 and position_salary = 'Associate professor' then
        set new.sal = 7000;
    elseif new.sal < 10000 and position_salary = 'Professor' then
        set new.sal = 10000;
    elseif new.sal > 7000 and position_salary = 'Instructor' then
        set new.sal = 7000;
    elseif new.sal > 10000 and position_salary = 'Associate professor' then
        set new.sal = 10000;
    elseif new.sal > 13000 and position_salary = 'Professor' then
        set new.sal = 1300;
    end if;
end;
//
DELIMITER ;

DELIMITER //
create trigger update2_sal
before update on teacher_sal
for each row
begin
	declare pos varchar(30);
    select POSITION into pos
    from teacher;
 
	if new.SAL < 4000 and pos = 'Instructor' then
		set new.SAL = 4000;
	elseif new.sal < 7000 and position_salary = 'Associate professor' then
        set new.sal = 7000;
    elseif new.sal < 10000 and position_salary = 'Professor' then
        set new.sal = 10000;
    elseif new.sal > 7000 and position_salary = 'Instructor' then
        set new.sal = 7000;
    elseif new.sal > 10000 and position_salary = 'Associate professor' then
        set new.sal = 10000;
    elseif new.sal > 13000 and position_salary = 'Professor' then
        set new.sal = 1300;
    end if;
end;
//
DELIMITER ;

-- 50
drop trigger insert_sal;
drop trigger update_sal;
drop trigger insert2_sal;
drop trigger insert2_sal;