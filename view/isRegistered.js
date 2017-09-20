function isname(){
	var p = document.getElementById("name").value
	if(p.length < 3){
		alert("名子需輸入3~10個字元");
		document.getElementById("name").value = "";
	}
	if(p.length >10){
		alert("名子需輸入3~10個字元");
		document.getElementById("name").value = "";
	}
}
function isuser(){
	var p = document.getElementById("user").value
	if(p.length < 6){
		alert("帳號需輸入6~10個字元");
		document.getElementById("user").value = "";
	}
	if(p.length >10){
		alert("帳號需輸入6~10個字元");
		document.getElementById("user").value = "";
	}
}
function ispw1(){
	var p = document.getElementById("pw1").value
	if(p.length < 6){
		alert("密碼需輸入6~10個字元");
		document.getElementById("pw1").value = "";
	}
	if(p.length >10){
		alert("名子需輸入6~10個字元");
		document.getElementById("pw1").value = "";
	}
}
function ispw2(){
	var p1 = document.getElementById("pw1").value
	var p2 = document.getElementById("pw2").value
	if(p1 != p2){
		alert("密碼不合");
		document.getElementById("pw2").value = "";
	}
}