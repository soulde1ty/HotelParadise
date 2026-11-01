document.querySelectorAll('.toggle-description').forEach(function(button) {
    button.addEventListener('click', function() {
        var shortDescription = this.parentNode.querySelector('.short-description');
        var longDescription = this.parentNode.querySelector('.long-description');
        
        // Перевіряємо, чи розгорнутий текст
        var isExpanded = longDescription.style.display !== 'none';

        // Згортаємо або розгортаємо текст в залежності від поточного стану
        if (isExpanded) {
            shortDescription.style.display = 'inline';
            longDescription.style.display = 'none';
            this.innerText = 'Read more';
        } else {
            shortDescription.style.display = 'none';
            longDescription.style.display = 'inline';
            this.innerText = 'Read less';
        }
    });
});


// // Згортаємо всі тексти перед розгортанням поточного
// document.querySelectorAll('.long-description').forEach(function(description) {
//     description.style.display = 'none';
// });
// document.querySelectorAll('.short-description').forEach(function(description) {
//     description.style.display = 'inline';
// });