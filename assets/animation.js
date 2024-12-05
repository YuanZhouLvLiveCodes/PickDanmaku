function show(element) {
    console.log("ShowElement", element)
    element.classList.remove("fadeOut")
    element.classList.add("fadeIn")
}
function hide(element) {
    if (element === null) {
        return
    }
    console.log("hideElement", element)
    element.classList.remove("fadeIn")
    element.classList.add("fadeOut")
    if (root.children.length !== 2) {
        return
    }
    setTimeout(() => {
        element.remove()
    }, 500)
}

function deleteElementFirst(rootElement) {
    hide(rootElement.firstElementChild)
    setTimeout(function () {
        rootElement.removeChild(rootElement.firstChild)
    }, 500)
}

function showNext(rootElement, data) {
    deleteElementFirst(rootElement)
    appendElementLast(rootElement, data)
}