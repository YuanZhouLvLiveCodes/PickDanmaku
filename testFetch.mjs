const fetchPromise = import("node-fetch")
fetchPromise.then(fetchModule => {
  const { default: fetch } = fetchModule

  fetch("https://api.mineserv.cn/db_manage.php", {
  "headers": {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "cookie": "buvid3=B2EB28D2-44E5-738A-13E1-25FFF7EA9F4371454infoc; b_nut=1726453971; _uuid=CB94FE45-CFF4-66310-46DA-6C135711099DA70424infoc; enable_web_push=DISABLE; buvid4=4D7DA686-67FF-AEC3-D204-3B59992113B972237-024091602-SHZMx60u9947eXxsMdPIKJ%2BLFJSV8ifIpcJjd9kR5fj6obMop1dAJhZdhBPyWdnT; rpdid=0zbfAHOWpU|gITEKc17|3HB|3w1SQ1AG; header_theme_version=CLOSE; buvid_fp_plain=undefined; LIVE_BUVID=AUTO8417264673414292; hit-dyn-v2=1; CURRENT_BLACKGAP=0; SESSDATA=22a46844%2C1743675378%2C21dbf%2Aa1CjDxAChqrj10x0hzjhyWMNgzi5MKCUPv2SwwB3VSXHupRQ7WxJbJxcvhCYbsq5m820wSVmpVSGdIbERpTnhvcjBteWZXYW42Wnl3eHE0RUtJQ3YyeF9lNnhKN09GV3lqYko2b3daN3F2WWplV0Jjb3lGVmFTZHAzUUNHVV91NmQ3aVUwQng1TFh3IIEC; bili_jct=2ca1409683f47c622c5406cd26250e40; DedeUserID=269755531; DedeUserID__ckMd5=dbf9600a3a0d2377; sid=67ec25l6; balh_server_inner=__custom__; balh_is_closed=; fingerprint=276963493bc68fc340ae064c30de1034; CURRENT_QUALITY=112; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1733646576,1733700192,1733720940,1733809256; HMACCOUNT=7E050522F3706417; _ga=GA1.1.819198803.1733868286; home_feed_column=4; Hm_lpvt_8a6e55dbd2870f0f5bc9194cddf32a02=1733872234; _ga_HE7QWR90TV=GS1.1.1733872650.2.0.1733872650.0.0.0; buvid_fp=276963493bc68fc340ae064c30de1034; share_source_origin=COPY; bsource=share_source_copy_link; bp_t_offset_269755531=1009472062231674880; CURRENT_FNVAL=2000; browser_resolution=639-362; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQxMzgyODYsImlhdCI6MTczMzg3OTAyNiwicGx0IjotMX0.TSoCTSnAw1p9WKkc9L1m06tOAukul7ij7qdpX6LgLuA; bili_ticket_expires=1734138226; b_lsid=B63FB10AA_193B33F568B; PVID=50",
    "Referer": "https://link.bilibili.com/p/center/index",
    "Referrer-Policy": "no-referrer-when-downgrade"
  },
  "body": "debug=1&room_id=8487238&platform=pc&csrf_token=2ca1409683f47c622c5406cd26250e40&csrf=2ca1409683f47c622c5406cd26250e40",
  "method": "POST"
}).then(res => res.text()).then(data => {
    console.log(data)
  })
})

