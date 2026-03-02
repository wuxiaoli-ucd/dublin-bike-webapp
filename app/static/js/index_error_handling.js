// Declare a global variable `my_map` to store the map instance.
// Declaring it globally allows it to be accessed outside the `initMap` function if needed.
var my_map; 

// Define the `initMap` function which will initialize the Google Map
function initMap() {
    console.log("initMap function called."); // Log when the function is called

    // Create an object representing Dublin's latitude and longitude coordinates.
    const dublin = { lat: 53.350140, lng: -6.266155 };
    console.log("Dublin coordinates set:", dublin); // Log the Dublin coordinates

    // Get the DOM element where the map will be rendered.
    const mapElement = document.getElementById("map");
    if (!mapElement) {
        console.error("Element with ID 'map' not found in the DOM!"); // Log an error if the element is missing
        return; // Exit the function to avoid further errors
    }
    console.log("Map element found:", mapElement); // Log the element reference

    // Create a new map instance centered at Dublin.
    try {
        my_map = new google.maps.Map(mapElement, {
            zoom: 12, // Zoom level of the map
            center: dublin, // Center the map at Dublin's coordinates
        });
        console.log("Map instance created successfully."); // Log success
    } catch (error) {
        console.error("Error creating map instance:", error); // Log any errors
        return;
    }

    // Add a marker to the map, positioned at Dublin's coordinates.
    try {
        const marker = new google.maps.Marker({
            position: dublin, // Position the marker at Dublin
            map: my_map,      // Add the marker to the map instance
        });
        console.log("Marker added to the map at:", dublin); // Log marker creation
    } catch (error) {
        console.error("Error adding marker to the map:", error); // Log any errors
    }
}

// Expose the `initMap` function as a global function.
// This step is necessary because Google Maps API needs to call `initMap`
// when the `callback` parameter is specified in the script URL.
// Without this, Google Maps would not know where to find the function.
window.initMap = initMap;

// Log that the script loaded successfully.
console.log("Script loaded. Waiting for Google Maps API to call `initMap`...");
