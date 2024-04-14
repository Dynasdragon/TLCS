const querystring = require('querystring')
const sql = require("mssql");
const ipcRenderer = require('electron').ipcRenderer;
const path = require('node:path'); 
const module = require('../backend/config.js')

var ranOnce = false;
var config = module.config;


const loadParams = (values) => {
    let query = querystring.parse(global.location.search);
    try {
        let data = JSON.parse(query['?data']);
        //console.log(data);
        const selectStreet1 = document.getElementById('street1');
        const selectStreet2 = document.getElementById('street2');
        const startDate = document.getElementById('startDate');
        const endDate = document.getElementById('endDate');
        const redBox = document.getElementById('redBox');
        const speedBox = document.getElementById('speedBox');
        for (var i = 0; i < selectStreet1.options.length; i++) {
            if (selectStreet1.options[i].innerHTML === data.street1) {
                selectStreet1.selectedIndex = i;
                break;
            }
        }


        for (var i = 0; i < selectStreet2.options.length; i++) {
            if (selectStreet2.options[i].innerHTML === data.street2) {
                selectStreet2.selectedIndex = i;
                break;
            }
        }

        startDate.value = data.startDate;
        endDate.value = data.endDate;
        redBox.checked = data.rBox === "false" ? false : true;
        speedBox.checked = data.sBox === "false" ? false : true;
    }
    catch (e) {
        console.log("No Data")
        return
    }

}

const getViolations = () => {

    const selectStreet1 = document.getElementById('street1');
    const selectStreet2 = document.getElementById('street2');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const plate = document.getElementById('plate');
    const redBox = document.getElementById('redBox');
    const speedBox = document.getElementById('speedBox');

    const street1 = selectStreet1.value;
    const street2 = selectStreet2.value;
    const sDate = startDate.value;
    const eDate = endDate.value;
    const pl = plate.value;
    const rBox = redBox.checked;
    const sBox = speedBox.checked;

    var interQuery = 'Select * from Intersection where street1 = \'' + street1 + '\' and street2 = \'' + street2 + '\'';

    var queryCol = 'Violations.*, FORMAT(date, \'MMMM, dd, yyyy-HH:mm:ss\') as date_str, image.ImagePath, Intersection.speedLimit,(CASE WHEN redLight.timeElapsed IS NOT NULL THEN \'True\' else \'False\' end) as violateRed,(CASE WHEN speed.speed IS NOT NULL THEN \'True\' else \'False\' end) as violateSpeed';
    var joins = 'inner join Intersection on Violations.intersectionID = Intersection.IntersectionID right join image on image.ImageID = Violations.imageID';
    var conds = ' where street1 = \'' + street1 + '\' and street2 = \'' + street2 + '\'';

    if (!(!sDate) && !(!eDate)) {
        conds += ' and date between \'' + sDate.replace('T', ' ') + '\' and \'' + eDate.replace('T', ' ') + '\'';
    }

    if (pl !== "")
        conds += ' and Violations.licensePlate = \'' + pl + '\'';

        queryCol += ', redLight.timeElapsed';
        joins += ' full outer join redLight on redLight.redLightID = Violations.violationID';
        queryCol += ', speed.speed';
        joins += ' full outer join speed on speed.speedID = Violations.violationID';

    if (rBox === false && sBox === false) {
        var table = document.getElementById('table');
        var rowCount = table.rows.length;
        for (var j = rowCount - 1; j > 0; j--) {
            table.deleteRow(j);
        }
        return
    }

    var query = 'Select ' + queryCol + ' from Violations ' + joins + conds;
    //console.log(street1);
    //console.log(street2);
    //console.log(sDate);
    //console.log(eDate);
    //console.log(pl);
    //console.log(rBox);
    //console.log(sBox);
    //console.log(query);
    //console.log(interQuery);

    sql.connect(config, function (err) {
        if (err) console.log(err);

        // create Request object
        var request = new sql.Request();

        //query to the database to get Intersection info
        request.query(interQuery, function (err, recordset) {
            const defaultTimer = document.getElementById('defaultTimer');
            const pedestrianOverride = document.getElementById('pedestrianOverride');
            const speedLimit = document.getElementById('speedLimit');
            const yesRadio = document.getElementById('yesRadio');
            const noRadio = document.getElementById('noRadio');
            const nightMode = document.getElementById('nightMode');

            var result = JSON.parse(JSON.stringify(recordset));
            //console.log(result.recordset);
            //console.log(result.recordset.length);
            defaultTimer.value = result.recordset[0].trafficTimer;
            pedestrianOverride.value = result.recordset[0].overrideTimer;
            speedLimit.value = result.recordset[0].speedLimit;
            nightMode.value = result.recordset[0].NightModeTimer;
            if (result.recordset[0].hasNightMode) {
                yesRadio.checked = 'checked';
                nightMode.disabled = false;
            }
            else {
                noRadio.checked = 'checked';
                nightMode.disabled = true;
            }

        });

        // query to the database and get the records
        request.query(query, function (err, recordset) {
            var table = document.getElementById('table');
            var rowCount = table.rows.length;
            for (var j = rowCount - 1; j > 0; j--) {
                table.deleteRow(j);
            }
            if (err) {
                var row = table.insertRow(i);
                var cell = row.insertCell(0);
                cell.colSpan = "4";
                cell.innerHTML = "No Data"
                emptyFields();
                console.log("Something went wrong")
            }
            else {

                //Conver Return Data Object to string
                var result = JSON.parse(JSON.stringify(recordset));
                //console.log(result.recordset);
                //console.log(result.recordset.length);
                if (result.recordset.length === 0) {
                    row = table.insertRow(i);
                    cell = row.insertCell(0);
                    cell.colSpan = "4";
                    cell.innerHTML = "No Data";
                    emptyFields();

                }



                var i = 1;

                result.recordset.forEach((violation) => {
                    var violationType = "Speeding";
                    if (violation.violateRed === "True" && violation.violateSpeed === "True") {
                        violationType = "Red Light, Speeding";
                    }
                    else if (violation.violateRed === "True") {
                        violationType = "Red Light";
                    }

                    if ((sBox === true && violationType.includes("Speeding")) || (rBox === true && violationType.includes("Red Light"))) {
                        var row = table.insertRow(i);
                        var date = row.insertCell(0);
                        var time = row.insertCell(1);
                        var lp = row.insertCell(2);
                        var vt = row.insertCell(3);
                        row.setAttribute('id', JSON.stringify(violation));

                        date.innerHTML = violation.date_str.split('-')[0];
                        time.innerHTML = violation.date_str.split('-')[1];
                        lp.innerHTML = violation.licensePlate;
                        vt.innerHTML = violationType;
                        i++;
                    }

                });

                return table;

            }
        });


    });
}

const getStreets = (street) => {
    return new Promise((resolve, reject) => {
        var options = []

        sql.connect(config, function (err) {
            if (err) console.log(err);

            // create Request object
            var request = new sql.Request();
            var dropdown = document.getElementById(street);

            // query to the database and get the records
            request.query('SELECT distinct ' + street + ' as street FROM Intersection', function (err, recordset) {
                if (err) {
                    console.log("Something went wrong")
                }
                else {

                    //Conver Return Data Object to string
                    var result = JSON.parse(JSON.stringify(recordset));
                    //console.log(result.recordset);

                    result.recordset.forEach((street) => {
                        var option = document.createElement("option");
                        options.push(street.street)
                        option.text = street.street;
                        option.value = street.street;
                        //console.log(option)
                        dropdown.appendChild(option);
                    });
                }
            });


        });
        resolve(options)
    });
}

const emptyFields = () => {
    const relatedValue = document.getElementById('relatedValue');
    const relatedAttribute = document.getElementById('relatedAttribute');
    const violationAttribute = document.getElementById('violationAttribute');
    const violationValue = document.getElementById('violationValue');
    const extraAttribute = document.getElementById('extraAttribute');
    const extraValue = document.getElementById('extraValue');
    const lp = document.getElementById('lp');
    const image = document.getElementById('image');
    const vType = document.getElementById('vType');
    const vDate = document.getElementById('vDate');
    const vTime = document.getElementById('vTime');
    const exportBtn = document.getElementById('export');
    const deleteBtn = document.getElementById('delete');


    vType.innerHTML = "";
    relatedAttribute.innerHTML = "";
    relatedValue.innerHTML = "Select a violation for more info";
    violationAttribute.innerHTML = "";
    violationValue.innerHTML = "";
    extraAttribute.innerHTML = "";
    extraValue.innerHTML = "";
    image.src = '../assets/placeholder.png';
    lp.innerHTML = "";
    vTime.innerHTML = "";
    vDate.innerHTML = "";
    exportBtn.style.visibility = 'hidden';
    deleteBtn.style.visibility = 'hidden';
}

const updateIntersection = () => {
    const defaultTimer = document.getElementById('defaultTimer').value;
    const pedestrianOverride = document.getElementById('pedestrianOverride').value;
    const speedLimit = document.getElementById('speedLimit').value;
    const yesRadio = document.getElementById('yesRadio');
    const nightMode = document.getElementById('nightMode').value;
    const street1 = document.getElementById('street1').value;
    const street2 = document.getElementById('street2').value;

    if (document.getElementById('street1').selectedIndex === 0 || document.getElementById('street2').selectedIndex === 0)
        return false

    var query = 'Update Intersection set overrideTimer = ' + pedestrianOverride + ', trafficTimer = ' + defaultTimer + ', speedLimit = ' + speedLimit + ', NightModeTimer = '+ nightMode;
    if (yesRadio.checked === 'checked') {
        query += ', hasNightMode = 1'
    }
    else {
        query += ', hasNightMode = 0'
    }

    query += ' where street1 = \'' + street1 + '\' and street2 = \'' + street2 + '\''

    var request = new sql.Request();
    var status = true
    request.query(query, function (err) {
        if (err) {
            console.log("Error " + err)
            status = false;
        }
        else {
            console.log("Updated Successfully");
        }

    })
    return status
}

const loadArduino = () => {
    const defaultTimer = document.getElementById('defaultTimer').value;
    const pedestrianOverride = document.getElementById('pedestrianOverride').value;

    const params = {
        defaultTimer: parseInt(defaultTimer),
        //pedestrianOverride: parseInt(pedestrianOverride)
        
    }

    //console.log(ranOnce)
    //if (ranOnce) {
    //    fetch("http://127.0.0.1:5000/closePort",
    //        {
    //            method: 'GET',
    //            headers: {
    //                'Content-type': 'application/json',
    //                'Accept': 'application/json'
    //            }
    //        }).then(res => {
    //            if (res.ok) {
    //                return res.json();
    //            } else {
    //                alert("something is wrong");
    //            }
    //        }).then(jsonResponse => {
    //            // Log the response data in the console
    //            console.log(jsonResponse);
    //        }).catch((err) => console.error(err));
    //}


        fetch("http://127.0.0.1:5000/receiver",
            {
                method: 'POST',
                headers: {
                    'Content-type': 'application/json',
                    'Accept': 'application/json'
                },// Strigify the payload into JSON:
                body: JSON.stringify(params)
            }).then(res => {
                if (res.ok) {
                    return res.json();
                } else {
                    alert("something is wrong");
                }
            }).then(jsonResponse => {
                // Log the response data in the console
                console.log(jsonResponse);
            }).catch((err) => console.error(err));


}

const logout = () => {
    // Send the info to the main process. We can pass any arguments as the second parameter.
    ipcRenderer.send("logoutClk", ""); // ipcRenderer.send will pass the information to the main process
}

const goToViolate = (parameters) => {
    var arg = "secondparam";
    // Send the info to the main process. We can pass any arguments as the second parameter.
    ipcRenderer.send("violateClk", parameters); // ipcRenderer.send will pass the information to the main process
}

const goToSettings = () => {
    // Send the info to the main process. We can pass any arguments as the second parameter.
    ipcRenderer.send("settingClk", ""); // ipcRenderer.send will pass the information to the main process
}
