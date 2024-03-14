
const sql = require("mssql");


    // Database Configuration
var config = {
    user: 'TLCS',
    password: 'trafficlight',
    server: 'Eddys-Laptop\\SQLEXPRESS',
    database: 'TLCS',
    pool: {
        max: 10,
        min: 0,
        idleTimeoutMillis: 30000
    },
    options: {
        instanceName: 'SQLEXPRESS',
        enableArithAbort: true,
        trustServerCertificate: true
    }
};

function connectToDatabase(ID) {
    

    // connect to your database
    sql.connect(config, function (err) {
        if (err) console.log(err);
        // create Request object
        var request = new sql.Request();

        // query to the database and get the records
        request.query('SELECT * FROM Violations', function (err, recordset) {
            if (err) {
                console.log("Something went wrong")
            }
            else {

                //Conver Return Data Object to string
                var result = JSON.stringify(recordset);
                console.log(result);

            }
        });
    });
}

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

                //Conver Return Data Object to string
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