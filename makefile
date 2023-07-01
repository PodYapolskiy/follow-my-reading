standalone:
	@echo building docker image
	docker build -f deploy/standalone.dockerfile -t follow-my-reading-standalone-image .
	@echo stopping and removing previous containers
	docker stop follow-my-reading-standalone || true && docker rm follow-my-reading-standalone || true
	@echo starting docker container
	docker run -d --name follow-my-reading-standalone -p 80:80 follow-my-reading-standalone-image