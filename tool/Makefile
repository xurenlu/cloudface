all:
	tdoc > api_search.t2t
	sed -i 's/General Title/Help/i' ./api_search.t2t
	./pythondoc.py ../server/api_search.py >> api_search.t2t
	txt2tags ./api_search.t2t
