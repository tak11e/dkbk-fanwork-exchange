let allTags = []

async function loadAndSetupSearch() {
    try {
        const response = await fetch('tags.json')
        alltags = await response.json()

        const searchInput = document.getElementById('tagSearch')
        const listElement = document.getElementById('list_for_freeform_0')

        if (!searchInput || !listElement) {
            console.error("Could not find search bar or list element in HTML");
            return;
        }

        const renderTags = (filterText = '') => {
            const filtered = allTags.filter(tag => 
                tag.toLowerCase().includes(filterText.toLowerCase())
            )
            listElement.innerHTML = filtered
            .map(tag => `<li>${tag}</li>`)
            .join('')
        }

        renderTags();

        searchInput.addEventListener('input', (e) => {
            renderTags(e.target.value)
        })
    } catch (err) {
        console.error("Error loading tags:", err)
    }
}

loadAndSetupSearch();