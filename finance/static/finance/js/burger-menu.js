document.addEventListener('DOMContentLoaded', () => {
    const burgerMenu = document.querySelector('.burger-menu');
    const navMenu = document.querySelector('.nav-menu');

    burgerMenu.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        const isActive = navMenu.classList.contains('active');
        burgerMenu.setAttribute('aria-expanded', isActive);
        burgerMenu.querySelector('i').classList.toggle('fa-bars');
        burgerMenu.querySelector('i').classList.toggle('fa-times');
    });

    document.addEventListener('click', (event) => {
        if (!navMenu.contains(event.target) && !burgerMenu.contains(event.target)) {
            navMenu.classList.remove('active');
            burgerMenu.setAttribute('aria-expanded', 'false');
            burgerMenu.querySelector('i').classList.add('fa-bars');
            burgerMenu.querySelector('i').classList.remove('fa-times');
        }
    });
});