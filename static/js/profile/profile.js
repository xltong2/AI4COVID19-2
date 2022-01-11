function Init() {
    menuDrawer = document.querySelector(".menu-drawer-container");
    btnDrawer = document.getElementById("btnDrawer");
    btnDrawerInside = document.getElementById("btnDrawerInside");

    btnDrawer.addEventListener("click", function() {menuDrawer.style.display = "block"});
    btnDrawerInside.addEventListener("click", function() {menuDrawer.style.display = "none"});

    btnBack = document.getElementById("btnBack");
    btnSignOut = document.getElementById("btnSignOut");
    popupWindow = document.querySelector(".popup-container");
    btnPopupCancel = document.getElementById("btnPopupCancel");

    btnBack.addEventListener("click", function() {location.href = '../dashboard'});
    btnSignOut.addEventListener("click", function() {popupWindow.style.display = "flex"});
    btnPopupCancel.addEventListener("click", function() {popupWindow.style.display = "none"});
}