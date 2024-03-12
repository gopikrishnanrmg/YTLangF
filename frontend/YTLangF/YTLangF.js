var categorized = [];

/**
 * The function picks all the videos and its URL and requests the backend code for the result
 * This request is sent periodically as new videos may be populated on the user's view.
 */

async function parseElements() {
  vids = document.querySelectorAll('[id="dismissible"]')

  for (var i = 0; i < vids.length; i++) {
    content = vids[i].getElementsByClassName("yt-simple-endpoint inline-block style-scope ytd-thumbnail");
    content_box = vids[i].getElementsByClassName("text-wrapper style-scope ytd-video-renderer");
    
    var url = content[0].getAttribute("href");
    if (categorized.includes(url)) continue;

    if (url !== null && !url.includes("shorts")) {
      var urlReq = "https://youtu.be/" + url.split("=")[1].split("&")[0];
      const response = await fetch("http://localhost:8000/video/" + urlReq);
      const data = await response.json();
      console.log(urlReq.toString() + " " + JSON.stringify(data));

      if (data["status"] === "success") {
        categorized.push(url);
        langElement = document.createElement("div"); 
        langElement.textContent = "Languages: " + JSON.parse(data["message"])["langs"].toString().replace(/"/g, ""); 
        content_box[0].appendChild(langElement);
      }
    }
  }
}

window.onload = () => {
  setInterval(parseElements, 15000);
};
