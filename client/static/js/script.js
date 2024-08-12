// script.js

document.addEventListener("DOMContentLoaded", function() {
    const navLinks = document.querySelectorAll("nav ul li a");
    const backgroundImages = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg"
        // Add more image filenames as needed
    ];
    let currentIndex = 0;

    function changeBackground() {
        const imageUrl = `/static/images/${backgroundImages[currentIndex]}`;
        document.body.style.backgroundImage = `url(${imageUrl})`;
        currentIndex = (currentIndex + 1) % backgroundImages.length;
    }

    setInterval(changeBackground, 5000);

    navLinks.forEach(function(link) {
        link.addEventListener("click", function(event) {
            navLinks.forEach(function(navLink) {
                navLink.classList.remove("active");
            });
            link.classList.add("active");
        });
    });
});
