window.addEventListener('DOMContentLoaded', function() {
    var alertBox = document.getElementById('alert');
    if (alertBox) {
        setTimeout(function() {
            alertBox.classList.add('show');
        }, 100);
        setTimeout(function() {
            alertBox.classList.remove('show');
        }, 5100);
    }
});