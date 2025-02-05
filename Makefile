SOURCE_FILE := ../bfs_run.log

expirement:
	python3 heuristic_sim.py $(SOURCE_FILE)

plot:
	python3 plot.py

clean_images:
	@rm plots/*.png

clean_data:
	@rm *.json

clean_all:
	@make clean_data
	@make clean_images