SOURCE_FILE := runs/heartwall.txt
DEST_FILE := jsons/heartwall.json

experiment:
	python3 heuristic_sim.py $(SOURCE_FILE) $(DEST_FILE)

plot:
	python3 plot.py $(DEST_FILE)

clean_images:
	@rm plots/*.png

clean_data:
	@rm *.json

clean_all:
	@make clean_data
	@make clean_images