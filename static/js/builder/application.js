;(function(_, Backbone, storybase) {
  var Builder;

  if (_.isUndefined(storybase.builder)) {
    storybase.builder = {};
  }
  Builder = storybase.builder;

  if (_.isUndefined(Builder.globals)) {
    Builder.globals = {};
  }
  // TODO: Just use Backbone for this
  Builder.globals.dispatcher =  _.clone(Backbone.Events);
})(_, Backbone, storybase);
