function parseElements()  {
        const content = document.getElementsByClassName("yt-simple-endpoint inline-block style-scope ytd-thumbnail");
        for (var i = 0; i < content.length; i++){
            var url = content[i].getAttribute("href");
            if (url !== null && !url.includes("shorts"))
                console.log("https://youtu.be/"+url.split("=")[1].split('&')[0]);
        }
};


window.onload = () =>{
    setInterval(parseElements, 1000);
}