const { app, BrowserWindow } = require('electron/main')
const path = require('node:path')
const electron = require('electron')

function createWindow() {
    const win = new BrowserWindow({
        width: 1920,
        height: 1080,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            preload: path.join(__dirname, './preload.js')
        }
    })
    win.loadFile('./src/pages/violationPage.html')
    win.maximize()
    win.setAutoHideMenuBar(true)
    console.log('size:', win.getSize());
    console.log('bounds:', win.getBounds());

}

app.whenReady().then(() => {
    createWindow()


    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow()
        }
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})
