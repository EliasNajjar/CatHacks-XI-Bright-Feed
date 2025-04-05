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
  while ((!latestResponse.includes("close") && !latestResponse.includes("error") && !latestResponseFinished))
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
  const response = await fetch(`${HOSTNAME}/post`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      site: getInput(),
      detectionType: document.getElementById("to-check-for").value,
    }),
  });

  ID = await response.text();
}


async function getLatestResponse() {
  try {
    const response = await fetch(`${HOSTNAME}/state/${ID}`);

    if (response.status === 200) {
      // Get file content on a 200 status
      const fileContent = await response.text();
      latestResponse = fileContent;
      latestResponseFinished = true;
    } else if (response.status === 202) {
      // Get the state as a string on a 202 status
      const responseText = await response.text();
      latestResponse = responseText;
    } else {
      console.error(`Unexpected status: ${response.status}`);
    }
  } catch (error) {
    console.error("Error fetching state:", error);
  }

}
