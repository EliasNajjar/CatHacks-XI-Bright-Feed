const HOSTNAME = "http://localhost:3000"
let ID
let latestResponse = ""


async function check() {
  let input = getInput();
  if (!input || input == "") {
    document.getElementById("AI Output").innerText = "Valid Input Required";
    return;
  }
  await postSubreddit();

  do {
    await getLatestResponse();
    document.getElementById("AI Output").innerText = latestResponse;
    await sleep(100);
  }
  while (latestResponse != "SENDING DATA" && !latestResponse.includes("close") && !latestResponse.includes("error"))
};

function getInput() {
    return document.getElementById("input").value;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms)); // Helper function to add a delay
}

async function postSubreddit() {
  const response = await fetch(`${HOSTNAME}/subreddit`, {
      method: "POST",
      body: getInput()
  });
  ID = await response.text();
}


async function getLatestResponse() {
  await fetch(`${HOSTNAME}/state/${ID}`, {
      method: "GET",
  }).then(response => {
      return response.text();
  }).then(text => {
      latestResponse = text;
      return text;
  });
}