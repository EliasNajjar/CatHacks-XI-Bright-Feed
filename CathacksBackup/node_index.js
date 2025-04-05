const { spawn } = require('child_process');

const express = require('express');
const app = express();

app.use(express.text());
const cors = require("cors");

const PYTHON_FILE = "index.py";

const port = parseInt(process.env.PORT) || 3000;
app.listen(port, () => {
  console.log(`helloworld: listening on port ${port}`);
});

function runPythonScript(scriptPath, args) { //arguments: url,
  const pythonProcess = spawn('python', [scriptPath, ...args]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });
}



//default response
app.get('/', (req, res) => {
    res.send("Hello World!");
});


app.post('/url', function (req, res) {
    console.log("URL Received!")
  
    console.log(req.body)

    res.send("received!")

    runPythonScript(PYTHON_FILE, [req.body]);
})
