SHELL=/bin/bash

all: solr-instance

solr.tgz:
	wget ${SOLR_TGZ_URL} -O solr.tgz

solr-content: solr.tgz
	mkdir -p solr-content
	tar -xvf $< --strip-components=1 -C solr-content/

webapps:
	mkdir -p webapps

webapps/solr.war: webapps solr-content
	cp solr-content/dist/solr-*.war $@

solr-instance: solr-content webapps/solr.war
	cp -r solr-content/example/{contexts,etc,resources,lib,start.jar} .
	mkdir -p contrib dist
	# copying files for ExtractingRequestHandler
	cp -r solr-content/contrib/extraction contrib/
	cp solr-content/dist/solr-cell-*.jar dist/

run-solr:
	java -Djetty.host="${IP}" -Djetty.port="${PORT}" -jar start.jar

clean:
	rm -rf solr.tgz solr-content

mrproper: clean
	rm -rf contexts etc lib webapps start.jar solr-webapp contrib dist
	rm -rf solr/${CORENAME}/data

.PHONY: solr-instance clean mrproper run-solr
