// const { exec } = import('child_process');
// const { curly } = import('node-libcurl');

function show_output() {
    document.getElementById("AI Output").innerText = "AI Output for " + document.getElementById("to check for").value + " from " + document.getElementById("URL").value;
};

function getUrl() {
    return document.getElementById("URL").value;
}


// function post() {
//     curly.post('localhost:3000/post', "EXAMPLEURL");
// }

function post() {
    fetch("http://localhost:3000/url", {
        method: "POST",
        body: getUrl(),
      });
}