function displayFilename() {
    const fileInput = document.getElementById('file');
    const filenameLabel = document.getElementById('filename');

    if (fileInput.files.length > 0) {
        let fileName = fileInput.files[0].name;
        const maxLength = 20; // Set the maximum length for the displayed file name

        // Shorten the file name if it exceeds the maximum length
        if (fileName.length > maxLength) {
            const start = fileName.substring(0, 10);  // First 10 characters
            const end = fileName.substring(fileName.length - 7);  // Last 7 characters
            fileName = `${start}...${end}`;  // Combine the start and end with ellipsis
        }

        // Update the label with the shortened file name
        filenameLabel.textContent = fileName;
    }
}


(function() {
    const form = document.querySelector('#sectionForm');
    const checkboxes = form.querySelectorAll('input[type=checkbox]');
    const checkboxLength = checkboxes.length;
    const firstCheckbox = checkboxLength > 0 ? checkboxes[0] : null;

    function init() {
        if (firstCheckbox) {
            for (let i = 0; i < checkboxLength; i++) {
                checkboxes[i].addEventListener('change', checkValidity);
            }

            checkValidity();
        }
    }

    function isChecked() {
        for (let i = 0; i < checkboxLength; i++) {
            if (checkboxes[i].checked) return true;
        }

        return false;
    }

    function checkValidity() {
        const errorMessage = !isChecked() ? 'กรุณาเลือกอย่างน้อย 1 อาการ' : '';
        firstCheckbox.setCustomValidity(errorMessage);
    }

    init();
})();

document.addEventListener("DOMContentLoaded", function() {
    // Check if the server-side variable image_output exists
    const imageOutput = window.imageOutput;
    
    // If image_output is not empty, trigger the modal
    if (imageOutput) {
        var myModal = new bootstrap.Modal(document.getElementById('outputModal'));
        myModal.show();
    }
});

function validateFileType() {
    const fileInput = document.getElementById('file');
    const filePath = fileInput.value;
    // Remove .gif from allowed extensions
    const allowedExtensions = /(\.jpg|\.jpeg|\.png|\.bmp)$/i;
    
    if (!allowedExtensions.exec(filePath)) {
        alert('Please upload a valid image file (JPG, JPEG, PNG, BMP).');
        fileInput.value = ''; // Clear the invalid file
        return false;
    }
    return true;
}
