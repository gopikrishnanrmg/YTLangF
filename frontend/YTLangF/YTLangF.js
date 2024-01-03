async function parseElements() {
  const content = document.getElementsByClassName(
    "yt-simple-endpoint inline-block style-scope ytd-thumbnail"
  );
  for (var i = 0; i < content.length; i++) {
    var url = content[i].getAttribute("href");
    if (url !== null && !url.includes("shorts")) {
      var urlReq = "https://youtu.be/" + url.split("=")[1].split("&")[0];
      const response = await fetch("http://localhost:8000/video/" + urlReq);
      const data = await response.json();
      console.log(urlReq.toString() + " " + JSON.stringify(data));
    }
  }
}

window.onload = () => {
  setInterval(parseElements, 15000);
};