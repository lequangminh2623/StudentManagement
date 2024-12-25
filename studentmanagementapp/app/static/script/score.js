const selectElements = document.querySelectorAll('.sidebar-nav select');
const selectButton = document.querySelector('.sidebar-btn');

selectButton.addEventListener('click', () => {
  const selectedFilters = {};

  selectElements.forEach(selectElement => {
    const filterId = selectElement.id;
    const selectedValue = selectElement.value;

    selectedFilters[filterId] = selectedValue;
  });

  let queryString = '';
  const hasFilters = Object.keys(selectedFilters).length > 0;


});