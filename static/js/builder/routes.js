Namespace('storybase.builder.routers');
storybase.builder.routers.Router = Backbone.Router.extend({
  routes: {
    ":id/": "selectStage",
    ":id/:stage/": "selectStage"
  },

  initialize: function(options) {
    this.dispatcher = options.dispatcher;
    this.dispatcher.on("navigate", this.navigate, this);
  },

  selectStage: function(id, stage) {
    if (_.isUndefined(stage)) {
      stage = 'build';
    }
    this.dispatcher.trigger('select:workflowstage', stage);
  }
   
});
