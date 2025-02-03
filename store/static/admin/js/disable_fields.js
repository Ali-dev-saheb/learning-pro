function toggleField(changedField, otherFieldId) {
    var otherField = document.getElementById(otherFieldId);
    
    if (changedField.value) {
        otherField.disabled = true;
    } else {
        otherField.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", function() {
    var imageFields = document.querySelectorAll('input[type="file"]');
    var urlFields = document.querySelectorAll('input[type="url"]');

    imageFields.forEach(function(imageField) {
        var urlFieldId = imageField.id.replace('image', 'image_url');
        imageField.addEventListener('change', function() {
            toggleField(imageField, urlFieldId);
        });
    });

    urlFields.forEach(function(urlField) {
        var imageFieldId = urlField.id.replace('image_url', 'image');
        urlField.addEventListener('input', function() {
            toggleField(urlField, imageFieldId);
        });
    });
});
