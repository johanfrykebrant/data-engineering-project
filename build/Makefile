build:
	docker compose build

up:
	docker compose up zookeeper -d
	docker compose up postgres -d
	docker compose up kafka -d
	docker compose up selenium -d
	docker compose up consumer -d
	docker compose up producer -d

get_logs:
	docker-compose logs -t --no-log-prefix consumer > ../logs/consumer.log
	docker-compose logs -t --no-log-prefix producer > ../logs/producer.log
	docker-compose logs -t --no-log-prefix kafka > ../logs/kafka.log
	docker-compose logs -t --no-log-prefix zookeeper > ../logs/zookeeper.log
	docker-compose logs -t --no-log-prefix postgres > ../logs/postgres.log
	docker-compose logs -t --no-log-prefix selenium > ../logs/selenium.log 

down:	
	docker compose down

clean:
	docker compose down --volumes
	
full_clean:
	docker compose down --volumes --rmi all

prune:
	docker system prune -a