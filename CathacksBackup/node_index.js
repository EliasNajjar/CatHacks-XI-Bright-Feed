const { spawn } = require('child_process');

const express = require('express');
const app = express();

app.use(express.text());

const PYTHON_FILE = "redditscrapper.py";

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

  const Process = spawn('python', [scriptPath, subReddit, process.pid]);

  const Session = {
    spawn: Process,
    state: "started",
    id: Process.pid
  }

  sessions.push(Session);

  Process.stdout.on('data', (data) => {
    console.log(data.toString())
    //Session.state = output;
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
    console.log("URL Received!")
  
    let id = runPythonScript(PYTHON_FILE, req.body);

    console.log(`Session id: ${id}`);

    res.send(id.toString());
})

app.get('/state/:id', function (req, res) {
    let ID = parseInt(req.params.id)
    let session = getSession(ID);

    if (session.state.includes('started')) {
        res.status(202).send("started");
    }
    else if (session.state.includes('scraping')) {
        res.status(202).send("scraping");
    }
    else if (session.state.includes('analyzing')) {
        res.status(202).send("analyzing");
    }
    else if (session.state.includes('done')) {
        res.status(200).send("done");
    }
    else{
        res.status(200).send(session.state);
    }
  })
