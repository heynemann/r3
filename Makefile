# %%%%%%%%%%%%%% SERVICE %%%%%%%%%%%%%%
run:
	@PYTHONPATH=$$PYTHONPATH:.:./test python r3/app/server.py 0.0.0.0 9999 localhost 7778


# %%%%%%%%%%%%%% WORKER %%%%%%%%%%%%%%
worker:
	@cd test && PYTHONPATH=$$PYTHONPATH:.:.. python count_words_mapper.py localhost 7778 ${KEY}


# %%%%%%%%%%%%%% WEB %%%%%%%%%%%%%%
web:
	@PYTHONPATH=$$PYTHONPATH:.:./test python r3/web/app.py 0.0.0.0 8888 localhost 7778


# %%%%%%%%%%%%%% REDIS %%%%%%%%%%%%%%
kill_redis:
	@ps aux | awk '(/redis-server/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'

redis: kill_redis
	@mkdir -p /tmp/r3/db
	@redis-server redis.conf &
