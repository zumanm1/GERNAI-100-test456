// Automation page specific JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Activate Bootstrap tabs
    var triggerTabList = [].slice.call(document.querySelectorAll('#automationTabs button'))
    triggerTabList.forEach(function (triggerEl) {
        var tabTrigger = new bootstrap.Tab(triggerEl)

        triggerEl.addEventListener('click', function (event) {
            event.preventDefault()
            tabTrigger.show()
        })
    })
});

