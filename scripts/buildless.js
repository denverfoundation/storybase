#!/usr/bin/env node

var less = require('less');
var fs = require('fs');
var path = require('path');

var argv = process.argv.splice(2);
// Assume we're running this from the scripts directory
var searchDir = '..';
var lessDir = 'static/less';
var cssDir = 'static/css';
var compiledCSSFilename = 'style.css';
// Build some paths to the LESS files and the output file
// or get them as command line arguments
var pathToLessFiles;
var pathToCompiledCSS;
if (argv.length >= 1) {
  pathToLessFiles = argv[0];
}
else {
  pathToLessFiles = path.join(searchDir, lessDir);
}
if (argv.length >= 2) {
  pathToCompiledCSS = argv[1];
}
else {
  pathToCompiledCSS = path.join(searchDir, cssDir, compiledCSSFilename);
}

var lessData = '';
var dirContents = [];
try {
	dirContents = fs.readdirSync(pathToLessFiles);
}
catch (error) {
  try {
    // Try relative to the current directory 
    pathToLessFiles = path.join(process.cwd(), lessDir); 
    dirContents = fs.readdirSync(pathToLessFiles);
  }
  catch (error) {
    console.error('Could not read less directory: ' + error);
  }
}

for (var i = 0; i < dirContents.length; i++) {
	if (dirContents[i].indexOf('base.less') != -1) {
		try {
			lessData += fs.readFileSync(path.join(pathToLessFiles, dirContents[i]), 'utf8');
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
		console.error(error);
	}
	try {
		fs.writeFileSync(pathToCompiledCSS, tree.toCSS({ compress: true }));
	}
	catch (error) {
    try {
      pathToCompiledCSS = path.join(process.cwd(), cssDir, compiledCSSFilename); 
      fs.writeFileSync(pathToCompiledCSS, tree.toCSS({ compress: true }));
    }
    catch (error) {
      console.error('Could not write css: ' + error);
    }
	}
});
