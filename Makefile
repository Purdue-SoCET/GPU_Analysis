SOURCE_FILE := presentation/counting_sort/count_4.txt
DEST_FILE := presentation/counting_sort/count_4.json
PLOTS_SUB_DIR := presentation/counting_sort/plots_4

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