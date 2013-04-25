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

solr-instance: solr-content webapps/solr.war run_solr.sh
	cp solr-content/example/{contexts,etc,lib,start.jar} -r .

clean:
	rm -rf solr.tgz solr-content

mrproper: clean
	rm -rf contexts etc lib webapps start.jar solr-webapp run_solr.sh
	rm -rf solr/${CORENAME}/data

run_solr.sh:
	echo '#!/bin/sh -e' > $@
	echo 'java -Djetty.host="${IP}" -Djetty.port="${PORT}" start.jar' >> $@
	chmod a+x $@

.PHONY: solr-instance clean mrproper
