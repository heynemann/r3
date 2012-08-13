# %%%%%%%%%%%%%% SERVICE %%%%%%%%%%%%%%
run:
	@PYTHONPATH=$$PYTHONPATH:.:./test python r3/app/server.py --redis-port=7778 --redis-pass=r3 --config-file="./test/app_config.py" --debug


# %%%%%%%%%%%%%% WORKER %%%%%%%%%%%%%%
worker:
	@PYTHONPATH=$$PYTHONPATH:. python r3/worker/mapper.py --mapper-key="${KEY}" --mapper-class="test.count_words_mapper.CountWordsMapper" --redis-port=7778 --redis-pass=r3


# %%%%%%%%%%%%%% WEB %%%%%%%%%%%%%%
web:
	@PYTHONPATH=$$PYTHONPATH:.:./test python r3/web/server.py --redis-port=7778 --redis-pass=r3 --config-file=./r3/web/config.py --debug


# %%%%%%%%%%%%%% REDIS %%%%%%%%%%%%%%
kill_redis:
	@ps aux | awk '(/redis-server/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'

redis: kill_redis
	@mkdir -p /tmp/r3/db
	@redis-server redis.conf &
