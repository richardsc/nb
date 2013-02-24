select * from note where noteid IN (select noteid from (select * from notetag where tagid in (1,2)) s group by noteid having count(distinct s.tagid) = 2);
