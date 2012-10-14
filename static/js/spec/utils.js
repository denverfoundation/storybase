describe('getRoot function', function() {
  it("Should include the i18n prefix", function() {
    expect(storybase.utils.getRoot(["build"], "/en/build/")).toEqual("/en/build/");
  });

  it("Should exclude parts of the path after the search term", function() {
    expect(storybase.utils.getRoot(["build"], "/en/build/f81eca996d754a549ae48cf8ef9622dc/")).toEqual("/en/build/");
  });

  it("Should accept multiple base arguments ", function() {
    expect(storybase.utils.getRoot(["build", "build-connected"], "/en/stories/f81eca996d754a549ae48cf8ef9622dc/build-connected/")).toEqual("/en/stories/f81eca996d754a549ae48cf8ef9622dc/build-connected/");
  });
});
