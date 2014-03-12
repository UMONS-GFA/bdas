/*
SCRIPT TO REMOTELY ACCESS TO ROCHEFORT DAS

Must be launched on the server
node rochefort.js

Requirements(on the server):
- Node.js
- socket.io
*/

var http = require('http');                     // used for webserver
var fs = require('fs');                         // used to read file
var net = require('net');                       // used to access serialport
var settings = require('./settings').settings;

var client = net.connect({port: settings.remotePort, host: settings.remoteHost},
    function () {
        console.log('client connected');
    });
client.setEncoding('utf-8');

var webserver = http.createServer(function (request, response) {
    fs.readFile("rochefort.html", 'utf-8', function (error, data) {
        response.writeHead(200, {'Content-Type':'text/html'});
        response.write(data);
        response.end();
    });
}).listen(settings.localPort, settings.localHost);

var io = require('socket.io').listen(webserver);

var readData = '';
io.sockets.on('connection', function (socket) {
    console.log("Socket connected");
    socket.on('messaqe_to_server', function (command) {
        client.write(command + settings.EOL);
        if (command == 'exit') {
            process.exit(code=0);
        }
        console.log(command);
    });

    client.on('data', function (data) {
        readData += data.toString();
        console.log("Readdata :" + readData);
        if (readData.indexOf('*') >= 0 && readData.indexOf('\r') >= 0) {
            sendData = readData .substring(readData .indexOf('*'), readData.indexOf('\r'));
            io.sockets.emit("message_to_client",{ response: sendData});
            console.log(sendData);
            readData = '';
        }
    });

    client.on('end', function () {
        console.log('client disconnected');
    });
});


