SOURCE_FILE := runs/bfs_small.txt
DEST_FILE := jsons/bfs_small.json
PLOTS_SUB_DIR := plots/bfs_small

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