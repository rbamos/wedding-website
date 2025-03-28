/* Load photo data from the embedded JSON */
const photos = JSON.parse(document.getElementById("photo-data").textContent);

/* Modal State */
let currentPhotoIndex = null;

/* Open the Modal */
function openGalleryModal(index) {
    const modal = document.getElementById("gallery_modal");
    const modalImg = document.getElementById("gallery_modalImage");
    const modalDescription = document.getElementById("gallery_modalDescription");

    // Validate index and update modal content
    if (photos[index]) {
        modalImg.src = photos[index].url;
        modalDescription.textContent = photos[index].description;

        // Show the modal
        modal.style.display = "block";

        // Set the current photo index
        currentPhotoIndex = index;

        // Add keydown listener
        document.addEventListener("keydown", handleGalleryKeydown);
    } else {
        console.error(`Invalid index ${index}. Photo not found.`);
    }
}

/* Close the Modal */
function closeGalleryModal() {
    const modal = document.getElementById("gallery_modal");
    modal.style.display = "none";

    // Reset the current photo index
    currentPhotoIndex = null;

    // Remove keydown listener
    document.removeEventListener("keydown", handleGalleryKeydown);
}

/* Handle Keydown Events */
function handleGalleryKeydown(event) {
    if (event.key === "Escape") {
        closeGalleryModal();
    } else if (event.key === "ArrowLeft") {
        showPreviousImage();
    } else if (event.key === "ArrowRight") {
        showNextImage();
    }
}

/* Show Previous Image */
function showPreviousImage() {
    if (currentPhotoIndex > 0) {
        openGalleryModal(currentPhotoIndex - 1);
    }
}

/* Show Next Image */
function showNextImage() {
    if (currentPhotoIndex < photos.length - 1) {
        openGalleryModal(currentPhotoIndex + 1);
    }
}

/* Close Modal on Outside Click */
window.onclick = function (event) {
    const modal = document.getElementById("gallery_modal");
    if (event.target === modal) {
        closeGalleryModal();
    }
};
