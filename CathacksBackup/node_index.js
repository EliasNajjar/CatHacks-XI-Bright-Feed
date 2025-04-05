const { spawn } = require('child_process');

const express = require('express');
const app = express();

app.use(express.text());

const PYTHON_FILE = "jsnodecommunicationtesting.py";

const port = parseInt(process.env.PORT) || 3000;
app.listen(port, () => {
  console.log(`helloworld: listening on port ${port}`);
});

//cors allowed origins
const cors = require('cors');
app.use(cors({
    origin: "*"
}));


let sessions = [];

function runPythonScript(scriptPath, subReddit) { //arguments: url, username, password

  const Process = spawn('python', [scriptPath, subReddit]);

  const Session = {
    spawn: Process,
    state: "started",
    id: Process.pid
  }

  sessions.push(Session);

  Process.stdout.on('data', (data) => {
    Session.state = data.toString();
  });

  Process.stderr.on('data', (data) => {
    Session.state = `error: ${data}`;
  });

  Process.on('close', (code) => {
    Session.state = `close: ${code}`;
  });

  return Process.pid;
}

function getSession(id) {
    return sessions.find(session => session.id === id);
}

//default response
app.get('/', (req, res) => {
    res.send("Hello World!");
});


app.post('/subreddit', function (req, res) {
    let id = runPythonScript(PYTHON_FILE, req.body);

    res.send(id.toString());
})

app.get('/state/:id', function (req, res) {
    let ID = parseInt(req.params.id)
    let session = getSession(ID);

    if (session.state.includes('close: 0')) {
        res.status(200).send("SENDING DATA");
    }
    else{
        res.status(200).send(session.state);
    }
  })
