chrome.runtime.onInstalled.addListener(() => {
    console.log("Text Analyzer Extension Installed");
  });
  
  // Example: Listening for a message from the popup or content script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "performAction") {
      // Integrate functionality from the CatHacks project here
      sendResponse({ result: "Action performed" });
    }
  });
  