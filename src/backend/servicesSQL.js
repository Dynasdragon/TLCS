const querystring = require('querystring')
const sql = require("mssql");
const ipcRenderer = require('electron').ipcRenderer;
const path = require('node:path');
const module = require('../backend/config.js')
const config = module.config;

const authLogin = (username, password) => {

    sql.connect(config, function (err) {
        if (err) console.log(err);
        // create Request object
        var request = new sql.Request();

        // query to the database and get the records
        request.query('SELECT * FROM Users where username = \'' + username + '\' and password = \'' + password+'\'', function (err, recordset) {
            if (err) {
                console.log("Something went wrong")
                console.log(err)
                return false
            }
            else {

                //Convert Return Data Object to string
                var result = JSON.parse(JSON.stringify(recordset));

                const ipcRenderer = require('electron').ipcRenderer;
                try {
                    console.log(result.recordset[0].username);
                    console.log(result.recordset[0].username === username)
                    if (result.recordset[0].username === username)

                        var arg = "";
                        console.log("Returning true")
                        ipcRenderer.send("loginClk", arg); // ipcRenderer.send will pass the information to the main process

                } catch (e){
                    console.log("No account found")
                    return false;
                }                 

            }
        });
    });

}