var less = require('less');
var fs = require('fs');
var pathToLessFiles = '../static/less/';
var pathToCompiledCSS = '../static/css/style.css';

var lessData = '';
var dirContents = [];
try {
	dirContents = fs.readdirSync(pathToLessFiles);
}
catch (error) {
	console.error('Could not read less directory: ' + error);
}

for (var i = 0; i < dirContents.length; i++) {
	if (dirContents[i].indexOf('base.less') != -1) {
		try {
			lessData += fs.readFileSync(pathToLessFiles + dirContents[i], 'utf8');
		}
		catch (error) {
			console.error('Could not read less file ' + pathToLessFiles + dirContents[i] + ': ' + error);
		}
	}
}

var parser = new(less.Parser)({
	paths: [pathToLessFiles], // Specify search paths for @import directives
});

parser.parse(lessData, function (error, tree) {
	if (error) {
		console.error(e);
	}
	try {
		fs.writeFileSync(pathToCompiledCSS, tree.toCSS({ compress: true }));
	}
	catch (error) {
		console.error('Could not write css: ' + error);
	}
});