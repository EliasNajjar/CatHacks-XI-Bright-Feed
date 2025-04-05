document.getElementById("actionButton").addEventListener("click", () => {
    chrome.runtime.sendMessage({ action: "performAction" }, (response) => {
      console.log(response.result);
    });
  });
  