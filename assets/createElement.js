


function createSimpleElement(uid, uname, msg) {
    let element = document.createElement("div")
    element.classList.add("selectedDanmaku")
    let left = document.createElement("div")
    left.classList.add("left")
    let right = document.createElement("div")
    right.classList.add("right")
    let face = document.createElement("div")
    face.classList.add("face")
    let img = document.createElement("img")
    img.src = `/face/${uid}`
    img.alt = "头像"
    let username = document.createElement("span")
    username.classList.add("uname")
    username.textContent = uname
    let content = document.createElement("div")
    content.classList.add("content")
    content.textContent = msg
    face.appendChild(img)
    left.appendChild(face)
    right.appendChild(username)
    right.appendChild(content)
    element.appendChild(left)
    element.appendChild(right)
    return element
}

function createNoticeListWithColorElement(contentSegments) {
    const element = document.createElement("div")
    element.classList.add("selectedDanmaku")
    for (const segment of contentSegments) {
        const span = document.createElement("span")
        span.textContent = segment.text
        span.style.color = segment.font_color
        element.append(span)
    }
    return element
}
function createNoticeSingleElement(msg) {
    const element = document.createElement("div")
    element.classList.add("selectedDanmaku")
    const span = document.createElement("span")
    span.textContent = msg
    element.append(span)
    return element
}
function createNoticeSingleLinkElement(msg, url) {
    const element = document.createElement("div")
    element.classList.add("selectedDanmaku")
    const a = document.createElement("a")
    a.textContent = msg
    a.href = url
    element.append(a)
    return element
}

function createDanmakuElement(data) {
    const {uid, uname, msg} = data
    return createSimpleElement(uid, uname, msg)
}

function createGiftElement(data) {
    const {uid, uname, gift_name, num} = data
    const msg = `送出 ${gift_name} x ${num}`
    return createSimpleElement(uid, uname, msg)
}
function createSuperchatElement(data) {
    const {uid, uname, price, msg} = data
    const message = `发送 ${price} 电池留言：${msg}`;
    return createSimpleElement(uid, uname, message)
}
function createGuardElement(data) {
    const {uid, uname, num, guard_level} = data
    let guard_name
    switch (guard_level) {
    case 1:
        guard_name = "总督"
        break;
    case 2:
        guard_name = "提督"
        break;
    case 3:
        guard_name = "舰长"
        break;
    default:
        guard_name = "非舰队"
    }
    const message = `成为 ${guard_name} x ${num}`;
    return createSimpleElement(uid, uname, message)
}


function appendElementLast(rootElement, data) {
    let newElement = document.createElement("div")
    if (data.type === "danmaku") {
        // 弹幕
        newElement = createDanmakuElement(data)
    } else if (data.type === "gift") {
        // 礼物
        newElement = createGiftElement(data)
    } else if (data.type === "superchat") {
        // 醒目留言
        newElement = createSuperchatElement(data)
    } else if (data.type === "buy_guard") {
        // 舰队
        newElement = createGuardElement(data)
    } else if (data.type === "command") {
        switch (data.cmd) {
            case "NOTICE_MSG":
                const currentRoomId = data["room_id"]
                const noticeRoomId = data["original_data"]["roomid"]
                const noticeRealRoomId = data["original_data"]["real_roomid"]
                let isSelf =
                    currentRoomId === noticeRoomId ||
                    currentRoomId === noticeRealRoomId;
                let noticeContent = ""
                if (isSelf) {
                    noticeContent = data["original_data"]["msg_self"]
                } else {
                    noticeContent = data["original_data"]["msg_common"]
                }
                const linkUrl = data["original_data"]["link_url"]
                newElement = createNoticeSingleElement(noticeContent)
                // newElement = createNoticeSingleLinkElement(noticeContent, linkUrl)
                break;
            case "COMMON_NOTICE_DANMAKU":
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            case "ENTRY_EFFECT": // 进入直播间
                newElement = createNoticeSingleElement(
                    formatString(data.data["copy_writing"], "<%", "%>", data.data["uinfo"])
                )
                break;
            case "PK_BATTLE_END": // 对战结束
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            case "PK_BATTLE_PRE_NEW": // 新对战准备
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            case "PK_BATTLE_PRE": // 上一个对战
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            case "PK_BATTLE_START_NEW": // 新对战开始
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            case "PK_BATTLE_START": // 新对战开始
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            case "ONLINE_RANK_COUNT": // 榜单
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            case "ONLINE_RANK_V2": // 在线榜单
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            case "WATCHED_CHANGE": // 监测改变
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            case "PK_BATTLE_FINAL_PROCESS": // 对战结束
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            case "PK_BATTLE_PROCESS_NEW": // 对战结束
                newElement = createNoticeListWithColorElement(data["original_data"]["data"]["content_segments"])
                break;
            default:
                newElement = createNoticeSingleElement(JSON.stringify(data["original_data"]))
                break;
        }
    }
    show(newElement)
    console.log(rootElement, newElement)
    rootElement.append(newElement)
}