// const { exec } = import('child_process');
// const { curly } = import('node-libcurl');

let ID
let latestResponse

async function check() {
  let input = getInput();
  if (!input || input == "") {
    document.getElementById("AI Output").innerText = "Valid Input Required";
    return;
  }
  await postSubreddit();

  while (latestResponse != "SENDING DATA") {
    await getLatestResponse();
    await sleep(15);
    console.log(latestResponse)
    document.getElementById("AI Output").innerText = latestResponse;
  }
    //`AI Output for ${document.getElementById("to check for").value} from ${document.getElementById("input").value} : \n`
};

function getInput() {
    return document.getElementById("input").value;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms)); // Helper function to add a delay
}

async function postSubreddit() {
  const response = await fetch("http://localhost:3000/subreddit", {
      method: "POST",
      body: getInput()
  });
  ID = await response.text();
}


async function getLatestResponse() {
  await fetch(`http://localhost:3000/state/${ID}`, {
      method: "GET",
  }).then(response => {
      return response.text();
  }).then(text => {
      latestResponse = text;
      return text;
  });
}