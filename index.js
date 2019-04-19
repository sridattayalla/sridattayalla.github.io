
function changeMenuSheetPosition(){
	if(getComputedStyle(document.getElementById('menu_sheet'), null).display === "none"){
		document.getElementById('menu_sheet').style.display = "block";
	}else{
		document.getElementById('menu_sheet').style.display = "none";
	}
}

function hover(element){
	console.log("datta");
	document.getElementById('github_img').setAttribute('src', 'icons/github-logo-white.svg');
}

function unhover(element){
	document.getElementById('github_img').setAttribute('src', 'icons/github-logo.svg');
}

function moveToTop(){
	document.body.scrollTop = 0;
  	document.documentElement.scrollTop = 0;
}
