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

        if (readData.indexOf('*') >= 0 && readData.indexOf('\n\r') >= 0) {
            readData = readData .substring(readData .indexOf('*'), readData.indexOf('\n')-1);
            console.log("log - readdata :" + readData);
            var parse_data = /^([*])(\d{4})\s(\d{2})\s(\d{2})\s(\d{2})\s(\d{2})\s(\d{2})\s(\d{6}\.\d{4})\s(\d{6}\.\d{4})\s(\d{6}\.\d{4}\s)(\d{6}\.\d{4})$/;
            var result = parse_data.exec(readData);
            if(result) {
                console.log("log - string has been parsed");
                var fields = ['data', 'star', 'year', 'month', 'day', 'hour', 'minute', 'second', 'sensor1',
                    'sensor2', 'sensor3', 'sensor4'];
                var realtime_data = {};
                var i;
                for (i = 0; i < fields.length; i++){
                    realtime_data[fields[i]] = result[i];
                }
                var sendData;
                sendData = "sensor 1 value :" + realtime_data.sensor1;
            }
            io.sockets.emit("message_to_client",{ response: sendData});
            console.log(sendData);
            readData = '';
        }
    });

    client.on('end', function () {
        console.log('client disconnected');
    });
});


