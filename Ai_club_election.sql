create database Ai_Club_Election
use Ai_club_election
----------------------Tables creation-------------------------------------------------------------
create table Candidates
(
candidateId char(5) primary key,
fname varchar(15) not null,
mname varchar(15) not null,
lname varchar(15) not null,
campaignSlogan varchar(250),
gender char(1) default('M') check(gender='M' or gender='F'),
dateOfBirth date not null,
advisorId char(5),
campaignId char(5)
);

create table Voters
(
voterId char(5) primary key,
fname varchar(15) not null,
mname varchar(15) not null,
lname varchar(15) not null,
gender char(1) default('M') check(gender='M' or gender='F'),
dateOfBirth date not null
);

create table Advisors
(
advisorId char(5) primary key,
fname varchar(15) not null,
mname varchar(15) not null,
lname varchar(15) not null,
academicDegree char(1) default('B') check(academicDegree in ('B','M','D'))
);

create table CampaignTeams
(
campaignId char(5) primary key,
campaignName varchar(30) not null unique,
numberOfMembers int not null
);

create table CandidatesLocations
(
candidateId char(5),
city varchar(15),
street varchar(15),
building varchar(5),
constraint candidate_location_primary primary key(candidateId,city,street,building)
);

create table Votes
(
voterId char(5),
candidateId char(5),
date date not null,
time time not null,
constraint candidate_voter_primary primary key(voterId,candidateId)
);

-------------------Foreign keys------------------------------------------------------------------------
alter table Candidates
add constraint candidate_advisor_fk foreign key(advisorId) references Advisors(advisorId) 
on delete no action on update cascade

alter table Candidates
add constraint candidate_campaign_fk foreign key(campaignId) references CampaignTeams(campaignId)
on delete no action on update cascade

alter table CandidatesLocations
add constraint canLoc_candidate_fk foreign key(candidateId)	references Candidates(candidateId)
on delete cascade on update cascade

alter table Votes
add constraint votes_candidate_fk foreign key(candidateId) references Candidates(candidateId)
on delete cascade on update cascade

alter table Votes
add constraint votes_voter_fk foreign key(voterId) references Voters(voterId)
on delete cascade on update cascade
------------------droping foregin keys because of a mistake in delete and update cascade------------
alter table Candidates
drop constraint candidate_advisor_fk

alter table Candidates
drop constraint candidate_campaign_fk

alter table CandidatesLocations
drop constraint canLoc_candidate_fk

alter table Votes
drop constraint votes_candidate_fk

alter table Votes
drop constraint votes_voter_fk
------------------------------------------------------------------
select * from candidates
select * from advisors
select * from CampaignTeams
select * from CandidatesLocations
select * from Votes
select * from Voters
------------------------------Insertion--------------------------------------
insert into Advisors (advisorId, fname, mname, lname, academicDegree) values 
('20005','Ali','Abdo','Imad','D'),
('20001','Khaled','Ahmed','Suleiman','D'),
('20002','Noura','Fatima','Jaber','M'),
('20003','Yousef','Hassan','Ali','B'),
('20004','Hana','Layla','Othman','M')

insert into CampaignTeams (campaignId,campaignName, numberOfMembers) values 
('30001','Team Future',10),
('30002','Team Change',8),
('30003','Team Unity',12),
('30004','Team Progress',9)

insert into Candidates (candidateId,fname, mname, lname,campaignSlogan, gender, dateOfBirth,advisorId,campaignId) values
('10005','Zaid','Abdullah','Aldous','The unity','M','2005-3-28','20005','30001'),
('10001', 'Ahmed', 'Khaled', 'Al-Masri', 'For a Bright Future', 'M', '1990-01-01', '20001', '30001'),
('10002', 'Fatima', 'Ali', 'Hassan', 'Change We Need', 'F', '1992-02-02', '20002', '30002'),
('10003', 'Omar', 'Yousef', 'Nasser', 'Together We Can', 'M', '1991-03-03','20003', '30003'),
('10004', 'Layla', 'Hana', 'Salem', 'A New Dawn', 'F','1993-04-04', '20004', '30004')

insert into Voters (voterId, fname, mname, lname, gender, dateOfBirth) values 
('40001', 'Ali', 'Mohammed', 'Abdullah', 'M', '1985-03-03'),
('40002', 'Sara', 'Nadia', 'Ibrahim', 'F', '1987-04-04'),
('40003', 'Hassan', 'Omar', 'Khalil', 'M', '1986-05-05'),
('40004', 'Mona', 'Laila', 'Zaid', 'F', '1988-06-06')

insert into CandidatesLocations (candidateId, city, street, building) values
('10001','Irbid','University','203'),
('10001', 'Amman', 'Rainbow', '101'),
('10002', 'Irbid', 'University', '202'),
('10003', 'Zarqa', 'King Hussein', '303'),
('10004', 'Aqaba', 'Corniche', '404')

insert into Votes (voterId, candidateId, date, time) values 
('40001', '10002', '2024-08-21', '11:00:00'),
('40001', '10001', '2024-08-21', '10:00:00'),
('40002', '10002', '2024-08-21', '11:00:00'),
('40003', '10003', '2024-08-21', '12:00:00'),
('40004', '10004', '2024-08-21', '13:00:00')
------------------------Views---------------------------------------
create view candidatesNames_view			-------1
as
select candidateId,fname,mname,lname,campaignSlogan,year(convert(date,GETDATE()))-year(dateOfBirth) "Age" 
from Candidates

create view NumberOfVotes_view			---------------2
as
select v.candidateId,c.fname,c.mname,c.lname,count(v.candidateId) "votes"
from Votes v
join Candidates c
on c.candidateId=v.candidateId
group by v.candidateId,c.fname,c.mname,c.lname

create view TheWinner_view ----------3
as
select 'The presedent of the club is '+fname+' '+
mname+' '+lname "The winner",max(votes) "Number Of votes"
from NumberOfVotes_view
where votes=(select max(votes) from NumberOfVotes_view)
group by candidateId,fname,mname,lname
----------------------------------------procedures-------------------------------
create procedure voter_votes	-----1
@voterId varchar(5)
as
begin
select
v.candidateId "Candidate Id",
c.fname "Candidate first name",
c.lname "Candidate last name",
v.date "Voting date",
v.time "Voting time"
from votes v
join candidates c
on c.candidateId=v.candidateId
where v.voterId=@voterId
end;

create procedure CandidateInfo	-----2
@candidateId varchar(5)
as
begin
select c.fname+' '+c.mname+' '+c.lname "Candidate name",
STRING_AGG(cl.building+' '+cl.city+' '+cl.street,', ') "Living location",
a.fname "Advisor name",
camp.campaignName "Campaign name"
from candidates c
join Advisors a
on a.advisorId=c.advisorId
join CampaignTeams camp
on camp.campaignId=c.campaignId
join CandidatesLocations cl
on c.candidateId=cl.candidateId
where c.candidateId=@candidateId
group by c.fname,c.mname,c.lname,a.fname,camp.campaignName
end;

create procedure vote		--3
@voterId varchar(5),
@candidateId varchar(5)
as
begin
insert into votes values(@voterId,@candidateId,convert(date,GETDATE()),convert(time,getdate()))
end;

create procedure deleteVote		--4
@voterId varchar(5),
@candidateId varchar(5)
as
begin
delete from votes where voterId=@voterId and candidateId=@candidateId
end;

create procedure updateVote		--5
@voterId varchar(5),
@oldcandidateId varchar(5),
@newcandidateId varchar(5)
as
begin
update votes set candidateId=@newcandidateId
where voterId=@voterId and candidateId=@oldcandidateId
end;
-----------------------------------------------------------Users and privilages---------------
create login voter1_Ali			--1
with password='Ali1234'

create user voter1_Ali for login voter1_Ali

grant exec on voter_votes to voter1_Ali
grant exec on vote to voter1_Ali
grant exec on deleteVote to voter1_ALi
grant exec on updateVote to voter1_Ali
grant select on candidatesNames_view to voter1_Ali

create login candidate1_Ahmed			--2
with password='Ahmed1234'
create user candidate1_Ahmed for login candidate1_Ahmed
grant insert,select,update,delete on candidates to candidate1_Ahmed
grant select on candidatesNames_view to candidate1_Ahmed
grant exec on CandidateInfo to candidate1_Ahmed

create login advisor1_Khaled                      ----3
with password='Khaled1234'
create user advisor1_Khaled for login advisor1_Khaled
grant select(candidateId,fname,mname,lname,campaignSlogan) on candidates to advisor1_khaled
grant select,insert,update,delete on Advisors to advisor1_Khaled
grant select on candidatesNames_view to advisor1_Khaled
grant exec on CandidateInfo to advisor1_Khaled


create login campaignTeam1_Future            ----4
with password='Future1234'

create user campaignTeam1_Future for login campaignTeam1_Future

grant select,update,insert,delete on Candidates to campaignTeam1_Future
grant select,update,insert,delete on Voters to campaignTeam1_Future
grant select,update,insert,delete on Advisors to campaignTeam1_Future
grant select,update,insert,delete on CampaignTeams to campaignTeam1_Future
grant select,update,insert,delete on CandidatesLocations to campaignTeam1_Future
grant select on candidatesNames_view to campaignTeam1_Future
grant select on NumberOfVotes_view	 to campaignTeam1_Future
grant select on TheWinner_view  to campaignTeam1_Future
grant exec on voter_votes to campaignTeam1_Future
grant exec on CandidateInfo to campaignTeam1_Future
grant exec on vote to campaignTeam1_Future
grant exec on deleteVote to campaignTeam1_Future
grant exec on updateVote to campaignTeam1_Future
-----------------------------------------------------------Backups---------------

backup database Ai_club_election
to disk='aiClub.bak'
with init,
name='Ai_club_election_BackUp';

insert into CampaignTeams values('30005','Team Help','10')

backup database Ai_club_election
to disk='aiClub.bak'
with differential

insert into CampaignTeams values('30006','Team Top','10')

backup log Ai_club_election
to disk='aiClub.bak'
with name= 'Ai_club_election log backup'

insert into CampaignTeams values('30007','Team Go','10')

backup database Ai_club_election
to disk='aiClub.bak'
with noinit,
name='Ai_club_election_BackUp';

restore database Ai_club_election
from disk='aiClub.bak'
with file=4, norecovery

insert into CampaignTeams values('30008','Team lead','10')

backup database Ai_club_election
to disk='aiClub.bak'
with differential

restore database Ai_club_election
from disk='aiClub.bak'
with file=5

restore headeronly			--to restore the headers of the backup
from disk='aiClub.bak'
-----------------------------------------------Validation----------------------------------------------
insert into voters values('40005','Abood','Abood','Abood','M','2005-3-28')

select * from candidates

insert into votes values('40001','10004','2024-9-1','11:00:00:00')
update votes set candidateId='10003'where voterId='40001' and candidateId='10004'

delete from votes where voterId='40001' and candidateId='10004'
select voterId,candidateId,date,time from  votes

exec CandidateInfo '10001'

select * from advisors

insert into Advisors values ('20006','Abood','Mahmoud','Aldous','D')