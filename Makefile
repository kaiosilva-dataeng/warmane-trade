# Makefile for Actioneer HTML Processor
# Uses UV as package manager and script executor

# Configuration
PYTHON := python
UV := uv
SCRIPT := src/trade/actioneer_raw_csv_cli.py
DATA_DIR := data
RAW_DIR := $(DATA_DIR)/raw
PROCESSED_DIR := $(DATA_DIR)/processed
DEFAULT_OUTPUT := $(PROCESSED_DIR)/actioneer_listings.csv

# Ensure directories exist
$(RAW_DIR):
	mkdir -p $(RAW_DIR)

$(PROCESSED_DIR):
	mkdir -p $(PROCESSED_DIR)

# Help target
.PHONY: help
help:
	@echo "Actioneer HTML Processor Makefile"
	@echo "=================================="
	@echo ""
	@echo "Available targets:"
	@echo "  help           - Show this help message"
	@echo "  setup          - Set up the Python environment with UV"
	@echo "  process        - Process the latest HTML file"
	@echo "  process-file   - Process a specific HTML file (use FILE=path/to/file.html)"
	@echo "  process-all    - Process all HTML files in the raw directory"
	@echo "  clean          - Remove all processed data"
	@echo "  clean-all      - Remove all data (raw and processed)"
	@echo ""
	@echo "Examples:"
	@echo "  make process"
	@echo "  make process-file FILE=$(RAW_DIR)/actioneer-2025-03-04T120000.html OUTPUT=$(PROCESSED_DIR)/actioneer-2025-03-04T120000.html.csv"
	@echo ""

# Setup target
.PHONY: setup
setup:

	$(UV) sync

# Process the latest HTML file (using Python script's --latest flag)
.PHONY: process
process: $(PROCESSED_DIR)
	$(UV) run $(SCRIPT) --latest --output $(DEFAULT_OUTPUT)
	@echo "Latest file processed and saved to $(DEFAULT_OUTPUT)"

# Process a specific HTML file
.PHONY: process-file
process-file: $(PROCESSED_DIR)
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify the input file with FILE=path/to/file.html"; \
		exit 1; \
	fi
	@if [ -z "$(OUTPUT)" ]; then \
		OUTPUT=$(PROCESSED_DIR)/output_$$(basename $(FILE) .html).csv; \
		echo "No OUTPUT specified. Using $$OUTPUT"; \
		$(UV) run $(SCRIPT) --input $(FILE) --output $$OUTPUT; \
	else \
		$(UV) run $(SCRIPT) --input $(FILE) --output $(OUTPUT); \
	fi
	@echo "File processed successfully"

# Process multiple files
.PHONY: process-all
process-all: $(PROCESSED_DIR)
	@echo "Processing all HTML files in $(RAW_DIR)..."
	@for file in $(RAW_DIR)/*.html; do \
		if [ -f "$$file" ]; then \
			output=$(PROCESSED_DIR)/$$(basename $$file .html).csv; \
			echo "Processing $$file -> $$output"; \
			$(UV) run $(SCRIPT) --input $$file --output $$output --silent; \
		fi; \
	done
	@echo "All files processed"

# Clean processed data
.PHONY: clean
clean:
	rm -f $(PROCESSED_DIR)/*.csv
	@echo "Removed all processed data"

# Clean all data
.PHONY: clean-all
clean-all: clean
	rm -f $(RAW_DIR)/*.html
	@echo "Removed all data files"

# Default target
.DEFAULT_GOAL := help
