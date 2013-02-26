describe('Error handler', function() {

  beforeEach(function() {
    var spec = this;
    delete window._sbJsErrs;
    this.mockErrorUrl = '/errors/';
    window.jsLogUrl = this.mockErrorUrl;
    this.xhr = sinon.useFakeXMLHttpRequest(); 
    this.requests = [];
    this.xhr.onCreate = function(req) {
      spec.requests.push(req);
    }
  });

  afterEach(function() {
    this.xhr.restore();
  });

  it('should log an error to the server', function() {
    window.onerror("http://floodlightproject.org/en/build/61b3768161184a21a43f4853826e38bd/", "Uncaught SyntaxError: Unexpected token ILLEGAL", 681);
    expect(this.requests.length).toEqual(1);
  });

  it('should log the same error to the server only once', function() {
    for(var i=0; i <= 10; i++) {
      window.onerror("http://floodlightproject.org/en/build/61b3768161184a21a43f4853826e38bd/", "Uncaught SyntaxError: Unexpected token ILLEGAL", 681);
      expect(this.requests.length).toEqual(1);
    }
  });
});
