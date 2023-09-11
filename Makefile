.PHONEY: help start clean

help:
	@echo "---------------COMMANDS-----------------"
	@echo -e "make help\nmake start\nmake format\nmake sort\nmake clean- removes all messages stored in topic"
	@echo "----------------------------------------"

start: 
	@python yak/zoo_keeper.py

format:
	@python -m black --version
	@echo -e "Formatting using black..."
	@black .

sort:
	@python -m isort --version
	@echo -e "Formatting using isort..."
	@isort .

clean:
	@echo "removing all messages stored"
	@rm -rf ./yak/topics/*
