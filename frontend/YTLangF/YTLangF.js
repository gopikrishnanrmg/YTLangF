var categorized = [];

/**
 * The function picks all the videos and its URL and requests the backend code for the result
 * This request is sent periodically as new videos may be populated on the user's view.
 */

async function parseElements() {
  const content = document.getElementsByClassName(
    "yt-simple-endpoint inline-block style-scope ytd-thumbnail"
  );
  const content_box = document.getElementsByClassName(
    "metadata-snippet-text style-scope ytd-video-renderer"
  );
  for (var i = 0; i < content.length; i++) {
    var url = content[i].getAttribute("href");
    if (categorized.includes(url)) continue;

    if (url !== null && !url.includes("shorts")) {
      var urlReq = "https://youtu.be/" + url.split("=")[1].split("&")[0];
      const response = await fetch("http://localhost:8000/video/" + urlReq);
      const data = await response.json();
      console.log(urlReq.toString() + " " + JSON.stringify(data));

      if (data["status"] === "success") {
        categorized.push(url);
        content_box[i].innerHTML += "<br> <b>Languages:</b> " + JSON.parse(data["message"])["langs"].toString().replace(/"/g, "");
      }
    }
  }
}

window.onload = () => {
  setInterval(parseElements, 15000);
};
