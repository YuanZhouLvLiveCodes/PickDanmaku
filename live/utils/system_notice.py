import pathlib

import winotify
from win11toast import toast as win11toast


class SystemNotice:
    title: str
    content: str
    app_id: str
    icon: str

    def __init__(self, content, title="", app_id="圆周率弹幕系统", icon=""):  # 初始化系统通知的标题、内容和时间
        self.title = title
        self.content = content
        self.app_id = app_id

    def show_notice(self):  # 显示系统通知
        # 根据系统通知的标题、内容和时间，显示系统通知
        print(self.__dict__)
        pass


class WinNotify(SystemNotice):
    def __init__(self,
                 app_id: str = "圆周率弹幕系统",
                 title: str = "",
                 msg: str = "",
                 icon: str = "",
                 duration: str = 'short',
                 launch: str = ''):
        super().__init__(content=msg, title=title, app_id=app_id, icon=icon)
        self.notify = winotify.Notification(app_id=app_id,
                                            title=title,
                                            msg=msg,
                                            duration=duration,
                                            icon=icon,
                                            launch=launch)

    def show_notice(self):
        super().show_notice()
        self.notify.show()


class Win11Notice(SystemNotice):
    def __init__(self, title=None, body=None, on_click=print, icon=None, image=None, progress=None, audio=None,
                 dialogue=None, duration=None, input=None, inputs=None, selection=None, selections=None, button=None,
                 buttons=None, xml="""
<toast activationType="protocol" launch="http:" scenario="{scenario}">
    <visual>
        <binding template='ToastGeneric'></binding>
    </visual>
</toast>
""", app_id="圆周率弹幕系统",
                 ocr=None, on_dismissed=print, on_failed=print, scenario=None, tag=None, group=None):
        super().__init__(content=body, title=title, app_id=app_id, icon=icon)
        if buttons is None:
            buttons = []
        if selections is None:
            selections = []
        if inputs is None:
            inputs = []
        self.on_click = on_click
        self.image = image
        self.icon = icon
        self.progress = progress
        self.audio = audio
        self.dialogue = dialogue
        self.duration = duration
        self.input = input
        self.inputs = inputs
        self.selection = selection
        self.selections = selections
        self.button = button
        self.buttons = buttons
        self.xml = xml
        self.ocr = ocr
        self.on_dismissed = on_dismissed
        self.on_failed = on_failed
        self.scenario = scenario
        self.tag = tag
        self.group = group

    def show_notice(self):
        super().show_notice()
        # win11toast(title=title, body=body, on_click=on_click, icon=icon, image=image, progress=progress,
        #                         audio=audio, dialogue=dialogue, duration=duration, input=input, inputs=inputs,
        #                         selection=selection, selections=selections, button=button, buttons=buttons, xml=xml,
        #                         app_id=app_id, ocr=ocr, on_dismissed=on_dismissed, on_failed=on_failed,
        #                         scenario=scenario, tag=tag, group=group)
        win11toast(title=self.title, body=self.content, on_click=self.on_click, image=self.image,
                   progress=self.progress, audio=self.audio, dialogue=self.dialogue, duration=self.duration,
                   input=self.input, inputs=self.inputs, selection=self.selection, selections=self.selections,
                   button=self.button, buttons=self.buttons, xml=self.xml, app_id=self.app_id, ocr=self.ocr,
                   on_dismissed=self.on_dismissed, on_failed=self.on_failed, scenario=self.scenario, tag=self.tag,
                   group=self.group)


if __name__ == '__main__':
    notice = Win11Notice("圆周率弹幕系统", "这是一条测试通知")
    notice.show_notice()
