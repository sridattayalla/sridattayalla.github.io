
function changeMenuSheetPosition(){
	if(getComputedStyle(document.getElementById('menu_sheet'), null).display === "none"){
		document.getElementById('menu_sheet').style.display = "block";
	}else{
		document.getElementById('menu_sheet').style.display = "none";
	}
}
