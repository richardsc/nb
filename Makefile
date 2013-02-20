create: force
	rm -f na.db
	sqlite3 na.db < make_database.sql
	./na --action add --keyword 'R,lecture' --title="John Cook lecture on R" --content="http://channel9.msdn.com/Events/Lang-NEXT/Lang-NEXT-2012/Why-and-How-People-Use-R"
	./na --action add --keyword 'lecture,physics,MIT' --title="Walter Lewin physics lectures" --content="http://ocw.mit.edu/courses/physics/8-01-physics-i-classical-mechanics-fall-1999/index.htm"
	./na --action add --keyword 'SQL,stackoverflow' --title="Q on SQL" --content="http://stackoverflow.com/questions/14836568/sql-join-with-boolean-on-where"
	./na --action add --title "oceanpython lecture" --keyword "lecture,python" --content "Diego gave a great talk"

test:
	./na --action find --keyword "lecture"

force:

