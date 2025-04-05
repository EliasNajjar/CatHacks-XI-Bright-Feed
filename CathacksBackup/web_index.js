// const { exec } = import('child_process');
// const { curly } = import('node-libcurl');

let ID

function show_output() {
    document.getElementById("AI Output").innerText = "AI Output for " + document.getElementById("to check for").value + " from " + document.getElementById("URL").value;
};

function getInput() {
    return document.getElementById("input").value;
}


function postSubreddit() {
    console.log("post")
    fetch("http://localhost:3000/subreddit", {
        method: "POST",
        body: getInput(),
      }).then(response => {
        return response.text();
      }).then(id => {
        ID = id;
      })
}

function getState() {
    fetch(`http://localhost:3000/state/${ID}`, {
        method: "GET",
      }).then(response => {
        console.log(response.text())
      })
}