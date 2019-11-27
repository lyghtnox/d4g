window.onscroll = function() {stickfunc();};
window.onload = function() {apply_theme();};


function apply_theme(){
	//var zoom = getCookie("zoom");
	mode(0);
	magnification(0);
	//document.body.style.transitionDuration = "0.3s";
	//document.body.style.WebkitTransitionDuration = "0.3s";
	
}

function magnification(multiplier) {
	var zoom = parseInt(getCookie("zoom"));
	if(isNaN(zoom))zoom = 0;
	zoom += multiplier;
	
	if(zoom > 5) zoom = 5;
	if(zoom < -3) zoom = -3;
	setCookie("zoom", zoom, 30);
	if (document.body.style.fontSize == "") {
		document.body.style.fontSize = "14px";
	}
	document.body.style.fontSize = 14 + (zoom * 2) + "px";
	try {
		document.getElementById('data_table').style.fontSize = 14 + (zoom * 2) + "px";
	}
	catch(error) {
		console.error(error);
	}
	try {
		document.getElementById('info_table').style.fontSize = 14 + (zoom * 2) + "px";
	}
	catch(error) {
		console.error(error);
	}
	try {
		var elems = document.getElementsByClassName('btn'), i;
		for (i =0 ; i<elems.length ; i++) {
			elems[i].style.fontSize = 18 + (zoom * 2) + "px";
		}
	}
	catch(error) {
		console.error(error);
	}
	try {
		var elems = document.getElementsByClassName('input_form'), i;
		for (i =0 ; i<elems.length ; i++) {
			elems[i].style.fontSize = 14+ (zoom * 2) + "px";
		}
	}
	catch(error) {
		console.error(error);
	}
	try {
		var elems = document.getElementsByClassName('login_form'), i;
		for (i =0 ; i<elems.length ; i++) {
			elems[i].style.fontSize = 18 + (zoom * 2) + "px";
		}
	}
	catch(error) {
		console.error(error);
	}
	try {
		myimg = document.getElementById('mag_img').style.fontSize = 20 + (zoom * 2) + "px";
	}
	catch(error) {
		console.error(error);
	}
	try {
		myimg2 = document.getElementById('logo');
		if(myimg2 && myimg2.style) {
			myimg2.style.height = 76 + (zoom * 5) + "px";
			myimg2.style.width = 73 + (zoom * 5) + "px";
		}
	}
	catch(error) {
		console.error(error);
	}
}

function setCookie(cname,cvalue,exdays) {
	var d = new Date();
	d.setTime(d.getTime() + (exdays*24*60*60*1000));
	var expires = "expires=" + d.toGMTString();
	document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
	var name = cname + "=";
	var decodedCookie = decodeURIComponent(document.cookie);
	var ca = decodedCookie.split(';');
	for(var i = 0; i < ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0) == ' ') {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		}
	}
	return "";
}

function checkCookie() {
	var user=getCookie("zoom");
	if (user != "") {
		alert("Welcome again " + user);
	} else {
		user = prompt("Please enter your name:","");
		if (user != "" && user != null) {
			setCookie("username", user, 30);
		}
	}
}

function mode(a){
	var mode = parseInt(getCookie("mode"));
	if(isNaN(mode))mode = 0;
	mode += a;
	if(mode == 2)mode = 0;
	setCookie("mode", mode, 30);
	if (mode == 1)
	{
		document.body.classList.add('dark-mode');
		document.getElementById("myHeader_").classList.add('dark-mode');
		document.getElementById("myHeader").classList.add('dark-mode');
		document.getElementById("footer").classList.add('dark-mode');
		document.getElementById("logo").src = "/static/img/Logo.png";
		var elems = document.getElementsByClassName('menu'), i;
		for (i =0 ; i<elems.length ; i++) {
			elems[i].classList.add('dark-mode');
		}

	}
	else
	{
		document.body.classList.remove('dark-mode');
		document.getElementById("myHeader_").classList.remove('dark-mode');
		document.getElementById("myHeader").classList.remove('dark-mode');
		document.getElementById("footer").classList.remove('dark-mode');
		document.getElementById("logo").src = "/static/img/Logo.png";

		var elems = document.getElementsByClassName('menu'), i;
		for (i =0 ; i<elems.length ; i++) {
			elems[i].classList.remove('dark-mode');
		}
	}
}

function listeLogement(logements){
	var logmt = new Array();
	for(var i=0;i<logements.length;i++){
		logmt.push([logements[i], logements[i] + ' Logement ']);
	}
	var select = document.createElement("SELECT");
	select.id = "data_select";
	select.classList = "box"
	var option;
	for (const i of logmt) {
		option = document.createElement('option');
		option.value = i[0];
		option.textContent =i[1];
		select.appendChild(option);
	}
	//data_select_div.innerHTML = "";
	data_select_div.insertBefore(select,data_select_div.childNodes[0]);
}

function request_logmt(){
	var e = document.getElementById("data_select").value;
	alert(e);
}



function updateTable(labels,dataset){

    //Build an array containing Customer records.
    var conso = new Array();
    conso.push(["Jour", "Consommation (kWh)"]);
    for(var i=0;i<labels.length;i++){
    	conso.push([labels[i], dataset[i]]);
    }

    //Create a HTML Table element.
    var table = document.createElement("TABLE");

    table.id = "data_table";

    //Get the count of columns.
    var columnCount = conso[0].length;

    //Add the header row.
    var row = table.insertRow(-1);
    for (var i = 0; i < columnCount; i++) {
    	var headerCell = document.createElement("TH");
    	headerCell.innerHTML = conso[0][i];
    	row.appendChild(headerCell);
    }

    //Add the data rows.
    for (var i = 1; i < conso.length; i++) {
    	row = table.insertRow(-1);
    	for (var j = 0; j < columnCount; j++) {
    		var cell = row.insertCell(-1);
    		cell.innerHTML = conso[i][j];
    	}
    }

    data_table_div.innerHTML = "";
    data_table_div.appendChild(table);
}


function updateGraph(){
	var e = parseInt(document.getElementById("DaysSelector").value);
	const new_data = dataset.slice(dataset.length-e, dataset.length);
	const new_label = labelset.slice(labelset.length-e ,labelset.length);
	updateTable(new_label,new_data);
	removeData(theChart);
	theChart.options.animationEnabled = false;
	for(var i = 0; i<new_label.length;i++){
		addData(theChart,new_label[i] , new_data[i]);
	}

}

function printGraph(){
	updateTable(labelset,dataset);
	removeData(theChart);
	theChart.options.animationEnabled = false;
	for(var i = 0; i<labelset.length;i++){
		addData(theChart,labelset[i] , dataset[i]);
	}
}

var options = {
	maintainAspectRatio: false,
	animationEnabled: false,
	animationDuration: 1000,
	legend: {
		labels: {
			fontColor: "rgba(128,208,208,1)"
		}
	},
	scales: {
		yAxes: [{
			stacked: true,
			gridLines: {
				display: true,
				color: "rgba(128,208,208,0.2)"
			},
			ticks: {
				beginAtZero:true,
				fontColor: "rgba(128,208,208,1)"
			}
		}],
		xAxes: [{
			gridLines: {
				display: false
			},
			ticks: {
				beginAtZero:true,
				fontColor: "rgba(128,208,208,1)"
			}
		}]
	}
};

var data = {
	labels: [],
	datasets: [{
		label: "Consomation (en kWh)",
		backgroundColor: "rgba(128,208,208,0.2)",
		borderColor: "rgba(128,208,208,1)",
		borderWidth: 2,
		hoverBackgroundColor: "rgba(128,208,208,0.4)",
		hoverBorderColor: "rgba(128,208,208,1)",
		data: [],
	}]
};

function removeData(chart) {
	var j =chart.data.labels.length
	for(var i=0;i<j;i++){
		chart.data.labels.pop();
		chart.data.datasets.forEach((dataset) => {
			dataset.data.pop();
		});
	}
	chart.update();
}

function addData(chart, label, data) {
	chart.data.labels.push(label);
	chart.data.datasets.forEach((dataset) => {
		dataset.data.push(data);
	});
	chart.update();
}










































