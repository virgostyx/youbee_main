function openMenu() {
    
    if (document.getElementById("left-menu").style.display == "") {
        document.getElementById("left-menu").style.display = "inline-flex";
    } else {
        document.getElementById("left-menu").style.display = "";
    };
  }
  
function showMessages() {
  // Get the snackbar DIV
  var x = document.getElementById("snackbar");

  // Add the "show" class to DIV
  x.className = "show";

  // After 3 seconds, remove the show class from DIV
  setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
}
