const sql = require("mssql");
const ipcRenderer = require('electron').ipcRenderer;
const querystring = require('querystring');
const module = require('../backend/config.js')

var config = module.config;

const loadParams = (values) => {
    let query = querystring.parse(global.location.search);
    let data = query['?data'] || "";
    data = data === "" ? "" : JSON.parse(query['?data']);
    if (data === "")
        return
    console.log(data);
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
    console.log(street1);
    console.log(street2);
    console.log(sDate);
    console.log(eDate);
    console.log(pl);
    console.log(rBox);
    console.log(sBox);
    console.log(query);

    sql.connect(config, function (err) {
        if (err) console.log(err);

        // create Request object
        var request = new sql.Request();

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
                console.log(result.recordset);
                console.log(result.recordset.length);
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
    sql.connect(config, function (err) {
        if (err) console.log(err);

        // create Request object
        var request = new sql.Request();
        var dropdown = document.getElementById(street);

        // query to the database and get the records
        request.query('SELECT distinct '+street+' as street FROM Intersection', function (err, recordset) {
            if (err) {
                console.log("Something went wrong")
            }
            else {
                
                //Conver Return Data Object to string
                var result = JSON.parse(JSON.stringify(recordset));
                //console.log(result.recordset);

                result.recordset.forEach((street) => {
                    var option = document.createElement("option");
                    option.text = street.street;
                    option.value = street.street;
                    //console.log(option)
                    dropdown.appendChild(option);
                }); 
                return dropdown;
            }
        });

     
    });
}

function updateSelection(ID) {
    console.log(ID);
    if (ID === "")
        return;

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

    var info = JSON.parse(ID);
    lp.innerHTML = info.licensePlate;
    vTime.innerHTML = info.date_str.split('-')[1];
    vDate.innerHTML = info.date_str.split('-')[0];
    image.src = '../images/' + info.ImagePath;

    if ((info.speed !== 0 && info.speed !== null) && info.timeElapsed !== 0 && info.timeElapsed !== null) {
        vType.innerHTML = "Speeding and Red Light Violation";
        relatedAttribute.innerHTML = "Speed Limit: ";
        relatedValue.innerHTML = info.speedLimit + " km/h";
        violationAttribute.innerHTML = "Current Speed: ";
        violationValue.innerHTML = info.speed + " km/h";
        extraAttribute.innerHTML = "Time Elasped: ";
        extraValue.innerHTML = info.timeElapsed + "s";
    }
    else if (info.speed !== 0 && info.speed !== null) {
        vType.innerHTML = "Speeding Violation";
        relatedAttribute.innerHTML = "Speed Limit: ";
        relatedValue.innerHTML = info.speedLimit + " km/h";
        violationAttribute.innerHTML = "Current Speed: ";
        violationValue.innerHTML = info.speed + " km/h";
        extraAttribute.innerHTML = "";
        extraValue.innerHTML = "";
    }
    else {
        vType.innerHTML = "Red Light Violation";
        relatedAttribute.innerHTML = "Time Elapsed: ";
        relatedValue.innerHTML = info.timeElapsed + " s";
        violationAttribute.innerHTML = "";
        violationValue.innerHTML = "";
        extraAttribute.innerHTML = "";
        extraValue.innerHTML = "";
    }

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

const logout = () => {
    var arg = "secondparam";
    // Send the info to the main process. We can pass any arguments as the second parameter.
    ipcRenderer.send("logoutClk", arg); // ipcRenderer.send will pass the information to the main process
}

const goToParams = (parameters) => {
    // Send the info to the main process. We can pass any arguments as the second parameter.
    ipcRenderer.send("paramClk", parameters); // ipcRenderer.send will pass the information to the main process
}

const goToSettings = () => {
    var arg = "secondparam";
    // Send the info to the main process. We can pass any arguments as the second parameter.
    ipcRenderer.send("settingClk", arg); // ipcRenderer.send will pass the information to the main process
}
 