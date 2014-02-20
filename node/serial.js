/*

SCRIPT TO INTERFACE LOCAL DAS
Requirements :
- Node.js
- serialport

Launch:
node serial.js

*/

var readline = require("readline");
// Import serialport constructor
var serialport = require("serialport");
var SerialPort = require("serialport").SerialPort;

//create new SerialPort object
var sp = new SerialPort("/dev/ttyUSB0", {
    baudrate: 9600,
    parser: serialport.parsers.readline("\r")
    //parser: serialport.parsers.raw
});

readData = '';
sp.on("open", function()
{
    sp.on("data", function(data){
        readData += data.toString();
         console.log(data);
        if(readData.indexOf("\r") != -1 ){
            console.log(readData);
            sp.close();
            process.exit(code=0);
        }

    });

    sp.on("error", function(msg){
        console.log("error" + msg);
    });

    sp.on("end", function(){
        sp.close();
    });
});

var rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.question("Enter your command ", function(command) {
    sp.write(command+"\r");
    console.log(typeof(command));
    console.log("Your command has been sent", command);

    rl.close();
});



