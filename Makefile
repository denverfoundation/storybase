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

scripts: widget_script

widget_script: $(JS_DIR)/widgets.js
	$(CLOSURE_COMPILE) $(JS_DIR)/widgets.js > $(JS_DIR)/widgets.min.js
	
