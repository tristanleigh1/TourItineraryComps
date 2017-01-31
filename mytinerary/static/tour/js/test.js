function test() {
	console.log(document.getElementById("mytour"));
	document.getElementById("mytour").innerHTML = '{{origin.address}}';
}
