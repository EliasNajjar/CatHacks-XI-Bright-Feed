const { spawn } = require('child_process');

const express = require('express');
const app = express();

const path = require("path");
const fs = require("fs");

app.use(express.text());
app.use(express.json());

const REDDIT_FILE = "redditscrapper.py";
const YOUTUBE_FILE = "Booptube.py";

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

function createPythonProcess(scriptPath, args) { //arguments: url, username, password

  const Process = spawn('python', ['-u',scriptPath, args.site, args.detectionType]);

  const Session = {
    spawn: Process,
    state: "started",
    id: Process.pid
  }

  Process.stdout.on('data', (data) => {
    Session.state = data.toString();
    console.log(data.toString());
  });

  Process.stderr.on('data', (data) => {
    console.log(`ERROR: ${data}`);
    Session.state = "An Error Occurred";
  });

  Process.on('close', (code) => {
    Session.state = `close: ${code}`;
  });

  sessions.push(Session);

  return Process.pid;
}

function getSession(id) {
    return sessions.find(session => session.id === id);
}

function closeOutputFile(id) {
  const filePath = path.join(__dirname, `response-${id}`);
  fs.unlink(filePath, (err) => {
    if (err) {
      console.error(`Error deleting file: ${err}`);
    }
  });
  sessions = sessions.filter(session => session.id !== id);
}

//default response
app.get('/', (req, res) => {
    res.send("Hello World!");
});


app.post('/post', function (req, res) {
  let site = req.body.site;
  let id = -1
    if (site.includes("youtube.com") || site.includes("youtu.be")) {
      id = createPythonProcess(YOUTUBE_FILE, req.body);
    } else {
      id = createPythonProcess(REDDIT_FILE, req.body);
    }

    res.send(id.toString());
})

app.post('/close/:id', function (req, res) {
  let ID = parseInt(req.params.id);

  closeOutputFile(ID);

  res.send(200);
})

app.get('/state/:id', function (req, res) {
    let ID = parseInt(req.params.id)
    let session = getSession(ID);

    if (session.state.includes('close: 0')) {
        res.status(200).sendFile(path.join(__dirname, `response-${ID}`));
    }
    else{
        res.status(202).send(session.state);
    }
  })
  

 
