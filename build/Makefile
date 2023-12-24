build:
	docker compose build

up:
	docker compose up consumer -d
	docker compose up weather -d
	docker compose up webscraper -d

get_logs:
	docker compose logs -t --no-log-prefix consumer > ../logs/consumer.log
	docker compose logs -t --no-log-prefix weather > ../logs/weather.log
	docker compose logs -t --no-log-prefix kafka > ../logs/kafka.log
	docker compose logs -t --no-log-prefix zookeeper > ../logs/zookeeper.log
	docker compose logs -t --no-log-prefix postgres > ../logs/postgres.log
	docker compose logs -t --no-log-prefix webscraper > ../logs/webscraper.log
down:	
	docker compose down

clean:
	docker compose down --volumes
	
full_clean:
	docker compose down --volumes --rmi all

prune:
	docker system prune -a