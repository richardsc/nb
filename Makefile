create: force
	rm -f na.db
	sqlite3 na.db < make_database.sql
	./na --action add --title "oceanpython lecture" --keyword "lecture,python" --content "Diego gave a great talk"

test:
	./na --action find --keyword "lecture,R"
	echo "NB. the above is wrong; no logic is being done on combining keywords"

force:

