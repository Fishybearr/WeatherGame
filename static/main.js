const tempDiv = document.getElementById("temp");

    const xhr = new XMLHttpRequest();

    xhr.open('GET','/weather');

    xhr.onload = function()
    {
        if(xhr.status >= 200 && xhr.status < 300 )
        {
            tempDiv.innerText = xhr.responseText;
        }
        else //request failed
        {
            tempDiv.innerText = 'Failed to load: ' +xhr.status;
        }
    };

    xhr.onerror = function()
    {
        tempDiv.innerText = 'Failed to Load: ' + xhr.status;
    }

    xhr.send(); //closes here


    //have another xhr for reading the button names from server
    //also set the button ids to the names read from server
    //Those ids can be sent to server and verified against correct answer in the DB
    

