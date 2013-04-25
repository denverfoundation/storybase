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
	cp solr-content/example/{contexts,etc,lib,start.jar} -r .

run-solr:
	java -Djetty.host="${IP}" -Djetty.port="${PORT}" -jar start.jar

clean:
	rm -rf solr.tgz solr-content

mrproper: clean
	rm -rf contexts etc lib webapps start.jar solr-webapp
	rm -rf solr/${CORENAME}/data

.PHONY: solr-instance clean mrproper run-solr
