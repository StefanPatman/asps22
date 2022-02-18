all: generator processor aggregator

generator:
	docker build -t generator src/generator

processor:
	docker build -t processor src/processor

aggregator:
	docker build -t aggregator src/aggregator
