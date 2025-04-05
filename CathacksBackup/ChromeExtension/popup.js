let ID;

function show_output() {
  const keyword = document.getElementById("to check for").value;
  const subreddit = document.getElementById("input").value;
  document.getElementById("AI Output").innerText =
    `Analyzing "${keyword}" from r/${subreddit}...`;
}

function getInput() {
  return document.getElementById("input").value;
}

function postSubreddit() {
  console.log("Posting to backend...");
  fetch("http://localhost:3000/subreddit", {
    method: "POST",
    body: getInput(),
  })
    .then(response => response.text())
    .then(id => {
      console.log("Received ID:", id);
      ID = id;
      show_output();
    })
    .catch(err => {
      console.error(err);
      document.getElementById("AI Output").innerText = "Error sending request.";
    });
}

function getState() {
  if (!ID) {
    alert("Please analyze first!");
    return;
  }

  fetch(`http://localhost:3000/state/${ID}`, {
    method: "GET",
  })
    .then(response => response.text())
    .then(state => {
      console.log("State:", state);
      document.getElementById("AI Output").innerText = "AI Result: " + state;
    })
    .catch(err => {
      console.error(err);
      document.getElementById("AI Output").innerText = "Error retrieving result.";
    });
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("post").addEventListener("click", postSubreddit);
  document.getElementById("check").addEventListener("click", getState);
});