/*
SCRIPT TO REMOTELY ACCESS TO ROCHEFORT DAS

Must be launched on the server
node rochefort.js

Requirements(on the server):
- Node.js
- socket.io

Access from the client:
10.107.10.41:8000

A Settings file must be created !!!
*/

var http = require('http');
var fs = require('fs');
var net = require('net');
var settings = require('./settings').settings;

console.log(settings.remoteHost);

var client = net.connect({port: settings.remotePort, host: settings.remoteHost},
    function() { //'connect' listener
        console.log('client connected');
    });


var webserver = http.createServer(function(request, response){
    fs.readFile("client.html", 'utf-8', function(error, data){
        response.writeHead(200, {'Content-Type':'text/html'});
        response.write(data);
        response.end();
    });
}).listen(settings.localPort, settings.localHost);

var io = require('socket.io').listen(webserver);

var readData = '';
io.sockets.on('connection', function(socket){
    console.log("Socket connected");
    socket.on('messaqe_to_server', function(command){
        // show command sent by the client
        client.write(command+'\r');
        console.log(command);
    });

    client.on('data', function(data) {
        console.log(data.toString());
        readData = data.toString();
        io.sockets.emit("message_to_client",{ response: data});
        //client.end();
    });

    client.on('end', function() {
        console.log('client disconnected');
    });
});

