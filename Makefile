SOURCE_FILE := runs/new_gaussian.txt
DEST_FILE := jsons/new_gaussian.json
PLOTS_SUB_DIR := plots/new_gaussian

experiment:
	python3 heuristic_sim.py $(SOURCE_FILE) $(DEST_FILE)

plot:
	mkdir -p $(PLOTS_SUB_DIR)
	python3 plot.py $(DEST_FILE) $(PLOTS_SUB_DIR)

clean_images:
	@rm -rf $(PLOTS_SUB_DIR)/*

clean_data:
	@rm *.json

clean_all:
	@make clean_data
	@make clean_images