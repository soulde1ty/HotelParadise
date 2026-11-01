document.querySelectorAll('.btn-play').forEach(button => {
    button.addEventListener('click', () => {
        const video = document.getElementById('video');
        if (video) video.src = button.dataset.src;
    });
});
document.getElementById('videoModal')?.addEventListener('hidden.bs.modal', () => {
    document.getElementById('video')?.setAttribute('src', '');
});
const backToTop = document.querySelector('.back-to-top');
if (backToTop) {
    window.addEventListener('scroll', () => {
        backToTop.style.display = window.scrollY > 300 ? 'inline-flex' : 'none';
    });
    backToTop.addEventListener('click', event => {
        event.preventDefault();
        window.scrollTo({top: 0, behavior: 'smooth'});
    });
}
