// User data (this could come from a database or API)
const user = {
    name: document.getElementById("user-name").textContent, // Example name
    profilePic: "" // Set to empty string if no picture, or a URL like "https://example.com/profile.jpg"
};


// Function to get initials from a name
function getInitials(name) {
    const nameParts = name.trim().split(" ");
    if (nameParts.length === 1) {
        return nameParts[0].charAt(0).toUpperCase();
    }
    return nameParts[0].charAt(0).toUpperCase() + nameParts[nameParts.length - 1].charAt(0).toUpperCase();
}

// Function to update user profile display
function updateUserProfile() {
    const profileContainer = document.getElementById("user-profile");
    const userNameElement = document.getElementById("user-name");

    // Update the user name
    userNameElement.textContent = user.name;

    // Check if profile picture exists
    if (user.profilePic && user.profilePic.trim() !== "") {
        // Display profile picture
        profileContainer.innerHTML = `<img src="${user.profilePic}" alt="${user.name}'s profile picture">`;
    } else {
        // Display initials
        profileContainer.textContent = getInitials(user.name);
    }
}



// Call the function to initialize
updateUserProfile();