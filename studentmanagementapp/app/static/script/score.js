const form = document.getElementById('filter-form');
const submitButton = form.querySelector('button[class="sidebar-btn"]');

submitButton.addEventListener('click', (event) => {
    event.preventDefault();
    form.action = '/scores';
    form.submit();
});