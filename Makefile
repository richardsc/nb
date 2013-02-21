create: force
	rm -f na.db
	sqlite3 na.db < make_database.sql
	./na add --keywords 'R,lecture' --title="John Cook lecture on R" --content="http://channel9.msdn.com/Events/Lang-NEXT/Lang-NEXT-2012/Why-and-How-People-Use-R"
	./na add --keywords 'lecture,physics,MIT' --title="Walter Lewin physics lectures" --content="http://ocw.mit.edu/courses/physics/8-01-physics-i-classical-mechanics-fall-1999/index.htm"
	./na add --json note.json

test:
	./na find --keywords "python"

force:

