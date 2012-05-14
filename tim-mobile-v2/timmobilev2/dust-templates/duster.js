// duster.js  
// Watch directory of dust.js templates and automatically compile them
// by Dan McGrady http://dmix.ca

var src_path = "./templates"; // directory of dust templates are stored with .dust file extension
//var public_path = "/Users/klenga/Projects/thisisme/thisis.me-MVP/tim-mobile-v2/timmobilev2/assets/default/"; // directory where the compiled .js files should be saved to
var public_path = "../assets/default/"; // directory where the compiled .js files should be saved to

var fs = require('fs');                                                                        
var dust = require('dustjs-linkedin');
var watcher = require('watch-tree-maintained').watchTree(src_path, {'sample-rate': 30}); // polls folder every 30ms

watcher.on('fileModified', function(path, stats) {
  fs.readFile(path, 'ascii', function (err, data) {
    if (err) {
			throw err;
		}

    var filename = path.split("/").reverse()[0].replace(".dust","");
    var filepath = public_path + filename + ".dust.js";
    var compiled = dust.compile(data, filename);

    fs.writeFile(filepath, compiled, function (err) {
      if (err) throw err;
      console.log('Saved ' + filepath);
    });
  });
});