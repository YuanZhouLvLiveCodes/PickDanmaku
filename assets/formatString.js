
function formatString(str, left, right, data) {
    let reg = new RegExp(`${left}(.*?)${right}`, "g")
    str = str.replace(reg, (match, p1) => {
        return data[p1]
    })
    return str
}

function removeFormatFlags(str, left, right) {
    return str.replaceAll(left, "").replaceAll(right, "")
}