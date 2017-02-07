function getIconFromCategory(category, scale) {
	var icon;
	switch (category) {
			case "Museums":
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/blue.png"}
			break;
			case "Landmarks":
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/pink.png"}
			break;
			case "Activities":
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/yellow.png"}
			break;
			case "Nature":
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/green.png"}
			break;
			case "Restaurants":
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/red.png"}
			break;
			default:
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/purple.png"}
			break;
	}
	if (scale == true) {
		icon["scaledSize"] = new google.maps.Size(45, 45);
	} else {
		icon["url"] = icon["url"].replace(".png", "-dot.png");
	}
	return icon;
}
