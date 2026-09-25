const products = []

// Selected products array
let selectedProducts = [];

// DOM elements
const selectTriggers = document.querySelectorAll('.select-header');
const productSearchs = document.querySelectorAll('.productSearch');

// Initialize the application
function init() {
    selectTriggers.forEach(selectTrigger => {
        let dropdownContent = selectTrigger.parentElement.querySelector(".dropdown-content")

        selectTrigger.addEventListener('click', () => toggleDropdown(dropdownContent));
        // Close dropdown when clicking outside

        document.addEventListener('click', function(event) {
            if (!selectTrigger.contains(event.target) && !dropdownContent.contains(event.target)) {
                dropdownContent.classList.remove('active');
            }
        });
    })

    productSearchs.forEach(productSearch => {
        productSearch.addEventListener('input', filterProducts);

    })


}


// Toggle dropdown visibility
function toggleDropdown(dropdownContent) {
    dropdownContent.classList.toggle('active');
}

// Filter products based on search input
function filterProducts() {

    let productRows = event.target.parentElement.parentElement.querySelectorAll(".product-row")

    let searchTerm = event.target.value.toLowerCase().trim();


    if (searchTerm === '') {
        // renderProductList();
        return;
    }
    let products = []

    productRows.forEach(product => {
        product.style.display = "none"
        let titleDiv = product.querySelector(".product-name");
        let productCategory = product.querySelector(".product-category");
        let productUpc = product.querySelector(".product-upc");

        let search = titleDiv.innerText.toLowerCase().includes(searchTerm) ||
            productCategory.innerText.toLowerCase().includes(searchTerm) ||
            productUpc.innerText.toLowerCase().includes(searchTerm);

        if (search == true) {
            product.style.display = "flex"
        }
    })



}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
