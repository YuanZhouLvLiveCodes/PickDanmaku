

PLATFORM_NAME = {
    "bilibili": "哔哩哔哩",
    "douyu": "斗鱼",
    "huya": "虎牙",
    "douyin": "抖音",
    "tiktok": "TikTok",
    "twitch": "Twitch",
    "youtube": "Youtube",
}
COMMAND_NAME = {
    "bilibili": {
        # 参数来源 https://github.com/iwxyi/Bilibili-MagicalDanmaku/blob/master/README.md
        "LIVE": "开播",
        "PREPARING": "下播",
        "ROOM_CHANGE": "房间信息改变",
        "ROOM_RANK": "房间排行榜",
        "DANMU_MSG": "弹幕",
        "SEND_GIFT": "礼物",
        "WELCOME_GUARD": "舰长进入",
        "ENTRY_EFFECT": "舰长、高能榜、老爷进入",
        "WELCOME": "老爷进入",
        "INTERACT_WORD": "用户进入",
        "ATTENTION": "用户关注",
        "SHARE": "用户分享直播间",
        "SPECIAL_ATTENTION": "特别关注直播间",  # special
        "ROOM_REAL_TIME_MESSAGE_UPDATE": "粉丝数量改变",
        "SUPER_CHAT_MESSAGE": "醒目留言",
        "SUPER_CHAT_MESSAGE_JPN": "醒目留言日文翻译",
        "SUPER_CHAT_MESSAGE_DELETE": "删除醒目留言",
        # "SPECIAL_GIFT": "节奏风暴",
        "ROOM_BLOCK_MSG": "用户被禁言",  # uname
        "GUARD_BUY": "有人上船",
        "FIRST_GUARD": "用户初次上船",
        "NEW_GUARD_COUNT": "船员数量改变",  # uname num room_info
        "USER_TOAST_MSG": "上船附带的通知",
        "HOT_RANK_CHANGED": "限时热门榜排名",
        "HOT_RANK_CHANGED_V2": "限时热门榜排名V2",
        "HOT_RANK_SETTLEMENT": "限时热门榜排名通知",
        "HOT_RANK_SETTLEMENT_V2": "限时热门榜排名通知V2",
        "HOT_RANK": "热门榜xx榜topX",  # text
        "ONLINE_RANK_V2": "礼物榜（高能榜）刷新",
        "ONLINE_RANK_TOP3": "高能榜TOP3改变",
        "ONLINE_RANK_COUNT": "高能榜改变",
        "NOTICE_MSG": "通知",
        "COMBO_SEND": "礼物连击",
        "SPECIAL_GIFT": "定制的专属礼物、节奏风暴类礼物等特殊礼物",
        "ANCHOR_LOT_CHECKSTATUS": "天选时刻前的审核",
        "ANCHOR_LOT_START": "开启天选",
        "ANCHOR_LOT_END": "天选结束",
        "ANCHOR_LOT_AWARD": "天选结果推送",
        "VOICE_JOIN_ROOM_COUNT_INFO": "申请连麦队列变化",
        "VOICE_JOIN_LIST": "连麦申请、取消连麦申请",
        "VOICE_JOIN_STATUS": "开始连麦、结束连麦",
        "WARNING": "被警告",  # text
        "CUT_OFF": "被超管切断",
        "CUT_OFF_V2": "被超管切断",
        "room_admin_entrance": "设置房管",
        "ROOM_ADMINS": "房管数量改变",
        "MEDAL_UPGRADE": "勋章升级",  # medal_level
        "WATCHED_CHANGE": "观看人数改变",
        "ROOM_SILENT_ON": "开启直播间禁言",
        "ROOM_SILENT_OFF": "关闭直播间禁言",
        # PK
        "PK_BATTLE_PRE": "大乱斗准备，10秒后开始",
        "PK_BATTLE_SETTLE": "",
        "PK_BATTLE_START": "大乱斗开始",
        "PK_BATTLE_PROCESS": "大乱斗双方送礼",
        "PK_ENDING": "大乱斗尾声，最后几秒",
        "PK_BATTLE_END": "大乱斗结束",
        "PK_END": "PK结束",  # %level%判断胜负，-1输，0平，1赢，可用来计算连胜
        "PK_BATTLE_SETTLE_USER": "",
        "PK_BATTLE_SETTLE_V2": "",
        "PK_LOTTERY_START": "大乱斗胜利后的抽奖",
        "PK_BEST_UNAME": "PK最佳助攻",  # %uname%昵称；%level%:1赢,0平,-1输；%gift_coin%总积分(=金瓜子/100)
        "CALL_ON_OPPOSITE": "PK本直播间的观众跑去对面串门",
        "ATTENTION_OPPOSITE": "PK本直播间观众关注了对面主播",
        "SHARE_OPPOSITE": "本直播间观众分享了PK对面直播间",
        "ATTENTION_ON_OPPOSITE": "PK对面观众关注了本直播间",
        "PK_MATCH_INFO": "获取PK对面直播间信息",  # 详见“大乱斗匹配信息”示例，%gift_coin%获取高能榜总积分(=金瓜子数/100)，%number%获取高能榜人数
        "PK_MATCH_ONLINE_GUARD": "获取对面直播间舰长在线人数",  # 详见“对面在线舰长播报”示例
        "PK_WINNING_STREAK": "大乱斗连胜事件",  # %number%获取次数，至少为2
        # 参数来源
        "COMMON_NOTICE_DANMAKU": "通用通知",  # 含红包礼物涨粉、直播活动信息等
        "DANMU_AGGREGATION": "抽奖弹幕",  # 包含天选抽奖弹幕、红包抽奖弹幕等
        "LIKE_INFO_V3_CLICK": "用户点赞",
        "LIKE_INFO_V3_UPDATE": "点赞总数量更新",
        "POPULARITY_RED_POCKET_NEW": "红包礼物",
        "POPULARITY_RED_POCKET_START": "红包开抢",
        "POPULARITY_RED_POCKET_WINNER_LIST": "红包中奖",
        "STOP_LIVE_ROOM_LIST": "停播房间列表",
        "VERIFICATION_SUCCESSFUL": "成功连接",
        "VIEW": "人气更新",
        "WIDGET_BANNER": "小部件横幅",
        # 参数来源，自行检测
        "AREA_RANK_CHANGED": "分区榜更新",  # 分区变化
        "PLAYTOGETHER_ICON_CHANGE": "联动图标更新",
        "SUPER_CHAT_ENTRANCE": "醒目留言入口",
        "REVENUE_RANK_CHANGED": "礼物榜更新",
        "CHG_RANK_REFRESH": "礼物榜刷新",
        "POPULARITY_RANK_TAB_CHG": "礼物榜刷新",
        "ROOM_LOCK": "房间封禁",
        "DM_INTERACTION": "他们都在说",
        "ROOM_CONTENT_AUDIT_REPORT": "房间内容审核",
        "MESSAGEBOX_USER_MEDAL_CHANGE": "勋章变动",  # 点亮粉丝牌、切换粉丝牌
        "ENTRY_EFFECT_MUST_RECEIVE": "舰长进入",
        "ANCHOR_LOT_NOTICE": "天选通知",
        "RANK_CHANGED": "榜单变动",
        "GOTO_BUY_FLOW": "购买提示",  # XX正在购买
        "RECOMMEND_CARD": "推荐卡片",
        "GUARD_HONOR_THOUSAND": "千舰变化"  # add为达成，del为掉舰
    }
}
"""
`POPULARITY_RANK_TAB_CHG`:           nil,
`POPULAR_RANK_GUIDE_CARD`:           nil, //投喂一个人气票帮助主播打榜
`PK_BATTLE_SETTLE_NEW`:              nil,
`LIKE_GUIDE_USER`:                   nil,              //主播@你：点点赞支持一下我吧
`ROOM_LOCK`:                         replyF.room_lock, //房间封禁提示
`DM_INTERACTION`:                    nil,              //他们都在说
`BENEFIT_CARD_CLEAN`:                nil,
`WEALTH_NOTIFY`:                     replyF.wealth_notify, //荣耀等级提示
`LOG_IN_NOTICE`:                     replyF.log_in_notice, //登录提示
`HOT_BUY_NUM`:                       nil,
`VOICE_JOIN_ROOM_COUNT_INFO`:        replyF.voice_join_room_count_info, //连麦等待
`VOICE_JOIN_LIST`:                   nil,
`VOICE_JOIN_STATUS`:                 replyF.voice_join_status,     //连麦人状态
`STOP_LIVE_ROOM_LIST`:               nil,                          //停止直播的直播间
`PK_LOTTERY_START`:                  replyF.pk_lottery_start,      //大乱斗pk
`PK_BATTLE_PRE_NEW`:                 nil,                          //pk准备
`PK_BATTLE_START_NEW`:               nil,                          //pk开始
`PK_BATTLE_PROCESS_NEW`:             replyF.pk_battle_process_new, //pk进行中
`VTR_GIFT_LOTTERY`:                  replyF.vtr_gift_lottery,      //特别礼物
`ENTRY_EFFECT_MUST_RECEIVE`:         nil,                          //高能榜前三进入
`GIFT_BAG_DOT`:                      nil,
`LITTLE_MESSAGE_BOX`:                replyF.little_message_box,           //小消息
`MESSAGEBOX_USER_MEDAL_CHANGE`:      replyF.messagebox_user_medal_change, //粉丝牌切换
`HOT_RANK_SETTLEMENT`:               nil,                                 //replyF.hot_rank_settlement, 热门榜获得
`HOT_RANK_SETTLEMENT_V2`:            replyF.hot_rank_settlement_v2,       //热门榜获得v2
`HOT_RANK_CHANGED`:                  nil,                                 //replyF.hot_rank_changed, 热门榜变动
`HOT_RANK_CHANGED_V2`:               nil,                                 //replyF.hot_rank_changed_v2, 热门榜变动v2
`CARD_MSG`:                          nil,                                 //提示关注
`WIDGET_BANNER`:                     nil,                                 //每日任务
`ROOM_ADMINS`:                       nil,                                 //房管列表
`ONLINE_RANK_TOP3`:                  nil,
`ONLINE_RANK_COUNT`:                 nil,
`ONLINE_RANK_V2`:                    nil,
"TRADING_SCORE":                     nil, //每日任务
"MATCH_ROOM_CONF":                   nil, //赛事房间配置
"HOT_ROOM_NOTIFY":                   nil, //热点房间
"MATCH_TEAM_GIFT_RANK":              nil, //赛事人气比拼
"ACTIVITY_MATCH_GIFT":               nil, //赛事礼物
"PK_BATTLE_PRE":                     nil, //人气pk
"PK_BATTLE_START":                   nil, //人气pk
"PK_BATTLE_PROCESS":                 nil, //人气pk
"PK_BATTLE_END":                     nil, //人气pk
"PK_BATTLE_RANK_CHANGE":             nil, //人气pk
"PK_BATTLE_SETTLE_USER":             nil, //人气pk
"PK_BATTLE_SETTLE_V2":               nil, //人气pk
"PK_BATTLE_SETTLE":                  nil, //人气pk
"SYS_MSG":                           nil, //系统消息
"ROOM_SKIN_MSG":                     nil,
"GUARD_ACHIEVEMENT_ROOM":            nil,
"ANCHOR_LOT_START":                  replyF.anchor_lot_start,   //天选之人开始
"ANCHOR_LOT_CHECKSTATUS":            nil,
"ANCHOR_LOT_END":                    nil,                       //天选之人结束
"ANCHOR_LOT_AWARD":                  replyF.anchor_lot_award,   //天选之人获奖
"COMBO_SEND":                        nil,
"INTERACT_WORD":                     replyF.interact_word,      //进入信息，包含直播间关注提示
"ACTIVITY_BANNER_UPDATE_V2":         nil,
"NOTICE_MSG":                        nil,
"ROOM_BANNER":                       nil,
"ONLINERANK":                        nil,
"WELCOME":                           nil,
"HOUR_RANK_AWARDS":                  nil,
"ROOM_RANK":                         nil,
"ROOM_SHIELD":                       nil,
"USER_TOAST_MSG":                    replyF.user_toast_msg,     //大航海购买信息
"WIN_ACTIVITY":                      replyF.win_activity,       //活动
"SPECIAL_GIFT":                      replyF.special_gift,       //节奏风暴
"GUARD_BUY":                         nil,                       //replyF.guard_buy,//大航海购买
"WELCOME_GUARD":                     nil,                       //replyF.welcome_guard,//大航海进入 ？已废弃？
"DANMU_MSG":                         replyF.danmu,              //弹幕
"DANMU_MSG:4:0:2:2:2:0":             replyF.danmu,              //弹幕
"DANMU_MSG:3:7:1:1:1:1":             nil,                       //弹幕
"ROOM_CHANGE":                       replyF.room_change,        //房间信息分区改变
"ROOM_SILENT_OFF":                   replyF.roomsilent,         //禁言结束
"ROOM_SILENT_ON":                    replyF.roomsilent,         //禁言开始
"SEND_GIFT":                         replyF.send_gift,          //礼物
"ROOM_BLOCK_MSG":                    replyF.room_block_msg,     //封禁
"PREPARING":                         replyF.preparing,          //下播
"LIVE":                              replyF.live,               //开播
"SUPER_CHAT_ENTRANCE":               nil,                       //SC入口
"SUPER_CHAT_MESSAGE_DELETE":         nil,                       //SC删除
"SUPER_CHAT_MESSAGE":                replyF.super_chat_message, //SC
"SUPER_CHAT_MESSAGE_JPN":            nil,                       //replyF.super_chat_message, //SC
"PANEL":                             nil,                       //replyF.panel,//排行榜 被HOT_RANK_CHANGED替代
"ENTRY_EFFECT":                      replyF.entry_effect,       //进入特效
"ROOM_REAL_TIME_MESSAGE_UPDATE":     nil,                       //replyF.roominfo,//粉丝数
"WATCHED_CHANGE":                    replyF.watched_change,     //Msg-观看人数
"FULL_SCREEN_SPECIAL_EFFECT":        nil,
"GIFT_BOARD_RED_DOT":                nil,
"USER_PANEL_RED_ALARM":              nil,
"POPULARITY_RED_POCKET_NEW":         replyF.popularity_red_pocket_new,   //老板打赏新礼物红包
"POPULARITY_RED_POCKET_START":       replyF.popularity_red_pocket_start, //老板打赏礼物红包开始
"POPULARITY_RED_POCKET_WINNER_LIST": nil,                                //老板打赏礼物红包的得奖名单
"COMMON_NOTICE_DANMAKU":             nil,                                //replyF.common_notice_danmaku,       //元气赏连抽
"ACTIVITY_BANNER_CHANGE":            nil,                                //活动标题改变
"ACTIVITY_BANNER_CHANGE_V2":         replyF.activity_banner_change_v2,   //活动标题改变v2
"VIDEO_CONNECTION_JOIN_START":       replyF.video_connection_join_start, //开始了与某人的视频连线
"VIDEO_CONNECTION_JOIN_END":         replyF.video_connection_join_end,   //结束了与某人的视频连线
"VIDEO_CONNECTION_MSG":              replyF.video_connection_msg,        //视频连线状态改变
"WARNING":                           replyF.warning,                     //超管警告
"DANMU_AGGREGATION":                 nil,                                //聚合弹幕
"GUARD_HONOR_THOUSAND":              nil,
"LIKE_INFO_V3_CLICK":                replyF.like_info_v3_click, //为主播点赞了
"LIKE_INFO_V3_UPDATE":               nil,                       //为主播点赞了总个数
"USER_TASK_PROGRESS":                nil,
"LITTLE_TIPS":                       replyF.little_tips, //小提示窗口
"LIKE_INFO_V3_NOTICE":               nil,
"LIVE_INTERACTIVE_GAME":             nil,
"LIVE_MULTI_VIEW_CHANGE":            nil,
"POPULAR_RANK_CHANGED":              nil, //replyF.popular_rank_changed, // Msg-人气排名
"AREA_RANK_CHANGED":                 nil,
"GIFT_STAR_PROCESS":                 nil,
"RECOMMEND_CARD":                    nil, //主播商品营销
"GOTO_BUY_FLOW":                     nil,
"CUT_OFF":                           replyF.cut_off, // 超管切直播
"SHOPPING_CART_SHOW":                nil,
"WIDGET_GIFT_STAR_PROCESS":          nil,
 """



