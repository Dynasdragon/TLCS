const { app, BrowserWindow, ipcMain } = require('electron/main')
const path = require('node:path')
const electron = require('electron')
const querystring = require('querystring')
const ipcRenderer = require('electron').ipcRenderer;

var win
function createWindow() {
    win = new BrowserWindow({
        title: "TLCS",
        frame: false,
        width: 1920,
        height: 1080,
        minHeight: 1080,
        minWidth: 1920,
        maxHeight: 1080,
        maxWidth: 1920,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true,
            plugins: true
        }
    })
    startArduino()
    win.loadFile('./src/pages/Login.html')
    win.maximize()
    win.setAutoHideMenuBar(true)
    console.log('size:', win.getSize());
    console.log('bounds:', win.getBounds());

}

app.whenReady().then(() => {
    createWindow()
    //require('./backend/servicesSQL.js');

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow()
        }
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        fetch("http://127.0.0.1:5000/closePort",
            {
                method: 'GET',
                headers: {
                    'Content-type': 'application/json',
                    'Accept': 'application/json'
                }
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
        app.quit()
    }
})

ipcMain.on("loginClk", function (event, arg) {
    // Create a new window
    win.loadFile('./src/pages/violationPage.html')
    event.sender.send("loginBtn-task-finished", "yes");

});

ipcMain.on("paramClk", function (event, arg) {
    // Create a new window
    win.loadFile('./src/pages/paramPage.html', { query: { "data": JSON.stringify(arg) } })
});
ipcMain.on("violateClk", function (event, arg) {
    // Create a new window
    win.loadFile('./src/pages/violationPage.html', { query: { "data": JSON.stringify(arg) }})
});

ipcMain.on("logoutClk", function (event, arg) {
    // Create a new window
    win.loadFile('./src/pages/Login.html')
});

ipcMain.on("settingClk", function (event, arg) {
    // Create a new window
    win.loadFile('./src/pages/settingsAdmin-user.html')
});
ipcMain.on("intersectionClk", function (event, arg) {
    // Create a new window
    win.loadFile('./src/pages/settingsAdmin-street.html', { query: { "data": JSON.stringify(arg) } })
});

ipcMain.on("settingsUserClk", function (event, arg) {
    // Create a new window
    win.loadFile('./src/pages/settingsUser.html')
});

const startArduino = () => {

    const { spawn } = require('child_process');
    const codeDir = path.join(__dirname, 'src', 'backend', 'trafficlight.py')
    console.log(codeDir)
    const pythonProcess = spawn('py', ['-u', codeDir], { shell: true });
    const serverDir = path.join(__dirname, 'src', 'backend', 'receiveImage.py')
    console.log(serverDir)
    //const server = spawn('py', ['-u', serverDir], { shell: true });
    const violationDir = path.join(__dirname, 'src', 'backend', 'violations.py')
    console.log(violationDir)
    //const violations = spawn('py', ['-u', violationDir], { shell: true });
    pythonProcess.stderr.pipe(process.stdout)
    pythonProcess.on('spawn', () => {
        console.log(`child process started`);
    });

    //server.stdout.on('data', (data) => {
    //    console.log("Received Data from sever")
    //    console.log(String.fromCharCode.apply(null, data))
    //});

    //server.stderr.on('data', (data) => {
    //    console.log("Received error from server")
    //    console.log(String.fromCharCode.apply(null, data))
    //});

    //server.on('close', () => {
    //    console.log(`child process closed`);

    //});

    //violations.stdout.on('data', (data) => {
    //    console.log("Received Data from violations")
    //    console.log(String.fromCharCode.apply(null, data))
    //});

    //violations.stderr.on('data', (data) => {
    //    console.log("Received error from violations")
    //    console.log(String.fromCharCode.apply(null, data))
    //});

    //violations.on('close', () => {
    //    console.log(`child process closed`);

    //});

    pythonProcess.stdout.on('data', (data) => {
        console.log("Received Data")
        console.log(String.fromCharCode.apply(null, data))
    });

    pythonProcess.stderr.on('data', (data) => {
        console.log("Received error")
        console.log(String.fromCharCode.apply(null, data))
    });

    pythonProcess.on('close', () => {
        console.log(`child process closed`);

    });
}