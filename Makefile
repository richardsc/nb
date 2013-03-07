create: force
	rm -f ~/Dropbox/na.db
	./nb add --keywords 'R,lecture' --title="John Cook lecture on R" --content="http://channel9.msdn.com/Events/Lang-NEXT/Lang-NEXT-2012/Why-and-How-People-Use-R"
	./nb add --keywords 'lecture,physics,MIT' --title="Walter Lewin physics lectures" --content="http://ocw.mit.edu/courses/physics/8-01-physics-i-classical-mechanics-fall-1999/index.htm"
	./nb add --mode json --file development/note.json

test:
	./nb find --keywords "python"

force:

