IMAGE=follow-my-reading-standalone-image
NAME=follow-my-reading-standalone
# TEMP_DIR=/tmp/temp_data
# REDIS_FILE=/redis/fmr/dump.rdb
TEMP_DIR=$(shell pwd)/shared/temp
REDIS_FILE=$(shell pwd)/shared/redis/dump.rdb
RUN_OPTIONS=--detach --name $(NAME) --publish 80:80 \
	--volume $(TEMP_DIR):/app/temp_data \
	#--mount type=bind,source=$(REDIS_FILE),target=/app/dump.rdb


standalone:
	@echo building docker image
	docker build -f deploy/standalone.dockerfile -t $(IMAGE) .
	
	@echo stopping and removing previous containers
	docker stop $(NAME) || true && docker rm $(NAME) || true
	
	@echo starting docker container
	docker run $(RUN_OPTIONS) $(IMAGE)

format:
	isort .
	black .