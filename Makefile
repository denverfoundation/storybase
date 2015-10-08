# TODO: Replace this with a custom staticfiles storage that defines
# a post_process() method that does the building and compression.
# See https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
LESS_DIR=static/less
CSS_DIR=static/css
JS_DIR=static/js
LESSC=lessc
LESSCFLAGS=--compress
CLOSURE_COMPILE=scripts/closure_compile

all: styles

styles: global_styles widget_styles

global_styles: $(LESS_DIR)/base.less
	$(LESSC) $(LESSCFLAGS) $(LESS_DIR)/base.less > $(CSS_DIR)/style.css

widget_styles: $(LESS_DIR)/widget.less
	$(LESSC) $(LESSCFLAGS) $(LESS_DIR)/widget.less > $(CSS_DIR)/widget.css

scripts: widget_script jquery_plugins

widget_script: $(JS_DIR)/widgets.js
	$(CLOSURE_COMPILE) $(JS_DIR)/widgets.js > $(JS_DIR)/widgets.min.js

jquery_plugins: apps/cmsplugin_storybase/$(JS_DIR)/jquery.storybase.activityguide.js
	$(CLOSURE_COMPILE) apps/cmsplugin_storybase/$(JS_DIR)/jquery.storybase.activityguide.js > apps/cmsplugin_storybase/$(JS_DIR)/jquery.storybase.activityguide.min.js

include Makefile.solr
