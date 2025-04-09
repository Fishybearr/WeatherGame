const tempDiv = document.getElementById("temp");


//get the buttons
const b1 = document.getElementById("b1");
const b2 = document.getElementById("b2");
const b3 = document.getElementById("b3");



    const xhr = new XMLHttpRequest();

    xhr.open('GET','/weather');

    xhr.onload = function()
    {
        if(xhr.status >= 200 && xhr.status < 300 )
        {
            let wethData = String(xhr.responseText);
            let w = wethData.split("\n");
            tempDiv.innerText = w[0];
            
            //pick an image based on w[1]
            GetWeatherIcon(w[1]);
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



    function GetWeatherIcon(weatherCode)
    {
        const wIcon = document.getElementById("weatherIcon");

        if(weatherCode === "clear")
            {
                wIcon.src = 'static/weatherIcons/clear-day.svg';
            }
        else if(weatherCode === "cloudy")
            {
                wIcon.src = 'static/weatherIcons/cloudy.svg';
            }
    }


    //have another xhr for reading the button names from server
    //also set the button ids to the names read from server
    //Those ids can be sent to server and verified against correct answer in the DB
function GetCitiesFromServer()
{
   

    const xhr2 = new XMLHttpRequest
    xhr2.open('GET','/cityNames');
    xhr2.onload = function()
    {
        if(xhr2.status >= 200 && xhr2.status < 300)
            {
                let output = String(xhr2.responseText);
                let names = output.split("\n")
                //console.log(names[0]);
                //console.log(names[1]);
                //console.log(names[2]);

                //Sets the buttons text values to read names
                b1.textContent = names[0];
                b2.textContent = names[1];
                b3.textContent = names[2];
                      
            }


        else
        {
            //error
            console.log("could not read");
        }
    }
    

    xhr2.onerror = function()
    {
        console.log("Error")
    }

    xhr2.send();

}

/**
 * Validate an answer against the server
 * @param {string} answer to be validated on server 
 */
function SendAnswer(ans,btnID)
{
    console.log(ans);

    sender = new XMLHttpRequest;

    sender.open('POST','/validate');
    sender.onload = function()
    {
        if(sender.status >= 200 && sender.status < 300)
            {
                //Take this response and use it to determine what
                //happens next
                console.log(sender.responseText);
                let output = String(sender.responseText); //this is hackable on client side so actual score would have to be saved serverSide
                
                b1.disabled = true;
                b2.disabled = true;
                b3.disabled = true;


                if(output === "yes")
                {
                    btnID.textContent = "Correct";
                    btnID.className = 'correct';
                    
                }
                else
                {
                    btnID.textContent = "Wrong";
                    btnID.className = 'wrong';
                    
                }

                document.getElementById("endMessage").className = 'endMessage';
                
            }
        else
        {
            console.error("Error");
        }
    }

    sender.onerror = function()
    {
        console.error("Error");
    }

    sender.send(String(ans));
}


GetCitiesFromServer();


    

