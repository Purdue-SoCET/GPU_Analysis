SOURCE_FILE := runs/heartwall.txt
DEST_FILE := jsons/heartwall.json
PLOTS_SUB_DIR := plots/heartwall

experiment:
	python3 heuristic_sim.py $(SOURCE_FILE) $(DEST_FILE)

plot:
	mkdir -p $(PLOTS_SUB_DIR)
	python3 plot.py $(DEST_FILE) $(PLOTS_SUB_DIR)

clean_images:
	@rm -rf plots/*

clean_data:
	@rm *.json

clean_all:
	@make clean_data
	@make clean_images