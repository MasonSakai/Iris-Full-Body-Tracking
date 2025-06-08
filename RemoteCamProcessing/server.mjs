import { Console } from 'console';
import http from 'http';
import fs from 'fs';
import open, { apps } from 'open';

let config = JSON.parse(fs.readFileSync("config.json"));
let openBrowsers = config.autostart;
let connectedCount = 0;

let hostname = config.hostname;
let port = config.port;

const ContentTypes = {
	"html": "text/html",
	"js": "application/javascript",
	"css": "text/css",
	"json": "application/json"
}

async function readRequest(req) {
	return new Promise((resolve, reject) => {
		var body = "";
		req.on("data", function (chunk) {
			body += chunk;
		});

		req.on("end", function () {
			resolve(body);
		});
	})
}

function serverGet(req, res) {
	try {
		var url = req.url;
		if (url == "/config.json") {
			let doc = "";
			try {
				doc = fs.readFileSync("config.json");
			} catch (err) {
				console.log(err);
				res.statusCode = 404;
				res.end();
				return;
			}
			let data = {};
			try {
				data = JSON.parse(doc);
				data.status = "ok";
			} catch (err) {
				data = {
					id: connectedCount,
					status: "no-config"
				};
			}
			res.statusCode = 200;
			res.setHeader('Content-Type', ContentTypes.json);
			res.end(JSON.stringify(data));
			return;
		}

		if (url == "/") url = "dist/index.html";
		else url = "dist" + url;
		var data = fs.readFileSync(url, 'utf8');

		var splits = url.split('.');
		var contentType = ContentTypes[splits[splits.length - 1]];

		res.statusCode = 200;
		res.setHeader('Content-Type', contentType);
		res.end(data);
	} catch (err) {
		console.log(err)
		res.statusCode = 404;
		res.setHeader('Content-Type', 'text/plain');
		res.end("File Not Found");
	}
}
function serverPUT(req, res) {
	var url = req.url;
	try {
		if (url == "/connect" ||
			url == "/poseData" ||
			url == "/cameraSize" ||
			url == "/start") {
			res.statusCode = 200;
			res.end();
			return;
		}


		res.statusCode = 405;
		res.setHeader('Content-Type', 'text/plain');
		res.end(`Action Not Allowed (cannot edit ${url})`);
	} catch (err) {
		console.log(err)
		res.statusCode = 404;
		res.setHeader('Content-Type', 'text/plain');
		res.end("File Not Found");
	}
}

async function configHandler(req, res) {
	var index = -1
	switch (req.method) {
		case 'PUT':
			var body = await readRequest(req)
			var data = JSON.parse(body)

			let id = data.id;
			try {
				data.id = undefined;
				data.status = undefined;
				config.windowConfigs[id] = data;
				fs.writeFile("config.json", JSON.stringify(config, null, '\t'), (err) => {
					if (err) {
						console.log(err);
						res.statusCode = 400;
						res.setHeader('Content-Type', 'text/plain');
						res.end(`error (is ID ${id} invalid?)`);
					} else {
						res.statusCode = 200;
						res.end();
					}
				});
			} catch (err) {
				console.log(err);
				res.statusCode = 400;
				res.setHeader('Content-Type', 'text/plain');
				res.end(`error (is ID ${id} invalid?)`);
			}
			break;
	}
}

const server = http.createServer((req, res) => {
	switch (req.url) {
		case "/config":
			configHandler(req, res);
			return;
		default:
			switch (req.method) {
				case "GET":
					serverGet(req, res);
					break;
				case "PUT":
					serverPUT(req, res);
					break;
				default:
					console.log("Defaulted on http method: " + req.method);
					break
			}
		break;
	}
});

server.listen(port, hostname, () => {
	console.log(`Server running at http://${hostname}:${port}/`);
});


/*
 * Server Startup:
 *	Start Server
 *	Open config.json
 *	if(open sites on startup)
 *		open 1 instance of site
 *		site startup:
 *			normal site stuff
 *			open config.json (server gives personal section)
 *			checks:
 *			startup complete conditions
 *				has started up
 *				has gotten camera*
 *				has started AI*
 *				has connected to host*
 *			once complete send message to Server
 *		repeat for all sites
 *		
 *		if no responce from site during startup, fall back and exit
 *			timeout of 1min
 *	Figure out shutdown, may require client to close browser windows
 *	
 *	
 * Site to Host (main computer) communication
 *	Send to Host:
 *		AI results
 *		status
 *		camera snapshot (on request)
 *	Receive from Host:
 *		config changes
 *	
 *	incorperate playspace mover into main (or figure out compatability)
 *	in calibration get camera position first, and maybe calculate a general percentage between controller (tracking) and wrist (ai tracking) positions in t-pose
 */