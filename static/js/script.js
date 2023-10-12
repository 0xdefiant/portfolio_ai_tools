async function getSuggestion() {
    try {
        document.getElementById("loader").style.display = "block";

        const network = document.getElementById("network").value;
        const tokensList = Array.from(document.getElementById("tokens").selectedOptions).map(option => option.value);
        const tokens = tokensList.join(',');

        // Fetch the AI portfolio suggestion directly
        const response = await fetch('/get-token-suggestion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ network: network }) // Ensure you have the right body parameters here.
        });

        const data = await response.json();

        // Hide the loader
        document.getElementById("loader").style.display = "none";

        // Display the suggestion from the AI
        document.getElementById("suggestion").innerText = data.portfolio;

    } catch (error) {
        console.error("Error occurred:", error);
        document.getElementById("suggestion").innerText = "An error occurred. Please check the console for details.";

        // Also hide the loader in case of error
        document.getElementById("loader").style.display = "none";
    }
}

document.getElementById("tokenSuggestionForm").addEventListener("submit", function(event) {
    event.preventDefault();
    
    getSuggestion(); // Call the async function to get the suggestion and handle the loader.
});
