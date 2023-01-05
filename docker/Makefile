build:
	docker compose build

up:
	docker compose up zookeeper -d
	docker compose up postgres -d
	docker compose up kafka -d
	docker compose up consumer -d
	docker compose up producer -d
	
down:	
	docker compose down

clean:
	docker compose down --volumes
	
full_clean:
	docker compose down --volumes --rmi all