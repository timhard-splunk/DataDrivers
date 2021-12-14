
document.getElementById("get-started").addEventListener("click", set_driver_details);

function set_driver_details(){
    console.log("Clicked!");
    var driver_name = document.getElementById("driver-name").value;
    var driver_team = document.getElementById("driver-team").value;
    var splunk_token = document.getElementById("token").value;
    console.log("Driver Name: " + driver_name);
    console.log("Team Name: " + driver_team);
    console.log("Token: " + token);
    eel.set_racing_parameters(driver_name, driver_team, splunk_token);

}
