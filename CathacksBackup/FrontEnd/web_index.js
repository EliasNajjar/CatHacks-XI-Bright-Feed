const HOSTNAME = "http://localhost:3000"
let ID
let latestResponse = ""
latestResponseFinished = false;


document.addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    check();
    event.preventDefault()
  }
});



async function check() {
  let input = getInput();
  if (!input || input == "") {
    document.getElementById("AI Output").innerText = "Valid Input Required";
    return;
  }
  await startSession();

  do {
    await getLatestResponse();
    document.getElementById("AI Output").innerText = latestResponse;
    await sleep(100);
  }
  while ((latestResponse != "SENDING DATA" && !latestResponse.includes("close") && !latestResponse.includes("error") && !latestResponseFinished))
  endSession();
};

function getInput() {
    return document.getElementById("input").value;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms)); // Helper function to add a delay
}

function endSession() {
  fetch(`${HOSTNAME}/close/${ID}`, {
    method: "POST",
  });
}

async function startSession() {
  latestResponseFinished = false;
  const response = await fetch(`${HOSTNAME}/subreddit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      subReddit: getInput(),
      detectionType: document.getElementById("to-check-for").value,
    }),
  });

  ID = await response.text();
}


async function getLatestResponse() {
  await fetch(`${HOSTNAME}/state/${ID}`, {
      method: "GET",
  })    .then(response => {
    if (response.status === 200) {
      // If status is 200, return the file as text
      latestResponseFinished = true;
      return response.text();
    } else {
      // Handle non-200 status codes (optional)
      throw new Error(`Request failed with status ${response.status}`);
    }
  })
  .then(text => {
    // Set latestResponse if the status is 200
    latestResponse = text;
    return text;
  })
  .catch(error => {
    console.error("Error fetching the latest response:", error);
  });

}

