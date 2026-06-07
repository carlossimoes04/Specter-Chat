const { app, BrowserWindow } = require('electron')
const path = require('path')

function createWindow () {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    title: "SPECTER | Your Local AI Assistant",
    icon: path.join(__dirname, '../public/iconSpecterApp.ico'),
    autoHideMenuBar: true, // Esconde as abas "File", "Edit", etc
    backgroundColor: '#030712', // Match tailwind dark theme
    webPreferences: {
      nodeIntegration: true
    }
  })

  // Carrega o localhost servido pelo Vite
  win.loadURL('http://localhost:5173')
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
