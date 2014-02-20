/*
SCRIPT TO REMOTELY ACCESS TO DAS

Must be launched on the server
node server.js

Requirements(on the server):
- Node.js
- serialport
- socket.io

Access from the client:
10.107.10.41:8000

*/

var http = require('http');
var fs = require('fs');
var serialport = require("serialport");


//create new SerialPort object
var sp = new  serialport.SerialPort("/dev/ttyUSB0", {
    baudrate: 9600,
    //parser: serialport.parsers.readline("\r")
    parser: serialport.parsers.readline("\r")
});

readData = '';


var webserver = http.createServer(function(request, response){
    fs.readFile("client.html", 'utf-8', function(error, data){
        response.writeHead(200, {'Content-Type':'text/html'});
        response.write(data);
        response.end();
    });
}).listen(8000, '10.107.10.41');


var io = require('socket.io').listen(webserver);

io.sockets.on('connection', function(socket){
    console.log("Socket connected");
    socket.on('messaqe_to_server', function(command){
        // show command sent by the client
        sp.write(command+'\r');
        console.log(command);
    });

    sp.on("data", function(data){
        readData += data.toString();
         console.log(data);
        if(readData.indexOf("\n") != -1 ){
            //console.log(readData);

        }
        io.sockets.emit("message_to_client",{ response: data});
    });

    sp.on("open", function()
    {
        console.log('port opened…');
    });

    sp.on("error", function(msg){
        console.log("error" + msg);
    });

    sp.on("close", function(err){
        console.log('port closed');
    });
});