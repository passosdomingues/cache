.PHONY: all venv build instances plot report apresentacao clean

all: build venv plot report apresentacao

build:
	$(MAKE) -C "codigo base"

venv:
	@if [ ! -d "venv" ]; then \
		echo "Criando virtual environment e instalando dependencias..."; \
		python3 -m venv venv; \
		./venv/bin/pip install -r "gerador de instancias/requirements.txt" matplotlib; \
	fi

instances: build venv
	# Instancias sao geradas dinamicamente dentro do runner_and_plot.py

plot: build venv
	# Executa o codigo gerando instancias e plotando o grafico na pasta de relatorio
	chmod +x runner_and_plot.py
	./venv/bin/python3 runner_and_plot.py

report: plot
	# Compila o PDF no diretorio do relatorio
	cd relatorio_tp03 && pdflatex -interaction=nonstopmode sbc-template.tex
	cd relatorio_tp03 && bibtex sbc-template || true
	cd relatorio_tp03 && pdflatex -interaction=nonstopmode sbc-template.tex
	cd relatorio_tp03 && pdflatex -interaction=nonstopmode sbc-template.tex

apresentacao:
	# Compila a apresentacao Beamer
	mkdir -p apresentacao
	cd apresentacao && pdflatex -interaction=nonstopmode apresentacao.tex
	cd apresentacao && pdflatex -interaction=nonstopmode apresentacao.tex

clean:
	$(MAKE) -C "codigo base" clean
	rm -f temp.dat
	rm -rf venv
	cd relatorio_tp03 && rm -f *.aux *.bbl *.blg *.log *.synctex.gz
	cd apresentacao && rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb *.synctex.gz
