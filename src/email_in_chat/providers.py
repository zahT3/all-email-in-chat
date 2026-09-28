"""Bundled provider presets. Domains match exactly; no remote discovery runs."""


def preset(zh, en, imap, smtp, *, domains=(), auth="app_password", source="", smtp_port=465):
    return {
        "name": {"zh": zh, "en": en},
        "imap": imap,
        "smtp": smtp,
        "imap_port": 993,
        "smtp_port": smtp_port,
        "domains": list(domains),
        "auth": auth,
        "source_url": source,
        "available": True,
    }


PROVIDERS = {
    "aliyun-enterprise": preset(
        "阿里企业邮箱",
        "Alibaba Mail (business)",
        "imap.qiye.aliyun.com",
        "smtp.qiye.aliyun.com",
        auth="enterprise",
        source="https://help.aliyun.com/zh/document_detail/36576.html",
    ),
    "aliyun-personal": preset(
        "阿里个人邮箱",
        "Aliyun Mail",
        "imap.aliyun.com",
        "smtp.aliyun.com",
        domains=("aliyun.com",),
        source="https://help.aliyun.com/zh/document_detail/465790.html",
    ),
    "qq": preset(
        "QQ 邮箱",
        "QQ Mail",
        "imap.qq.com",
        "smtp.qq.com",
        domains=("qq.com",),
        auth="authorization_code",
        source="https://service.mail.qq.com/detail/0/339",
    ),
    "netease-163": preset(
        "网易 163",
        "NetEase 163",
        "imap.163.com",
        "smtp.163.com",
        domains=("163.com",),
        auth="authorization_code",
        source="https://autoconfig.thunderbird.net/v1.1/163.com",
    ),
    "netease-126": preset(
        "网易 126",
        "NetEase 126",
        "imap.126.com",
        "smtp.126.com",
        domains=("126.com",),
        auth="authorization_code",
        source="https://autoconfig.thunderbird.net/v1.1/126.com",
    ),
    "netease-yeah": preset(
        "网易 yeah.net",
        "NetEase yeah.net",
        "imap.yeah.net",
        "smtp.yeah.net",
        domains=("yeah.net",),
        auth="authorization_code",
        source="https://autoconfig.thunderbird.net/v1.1/yeah.net",
    ),
    "gmail": preset(
        "Gmail",
        "Gmail",
        "imap.gmail.com",
        "smtp.gmail.com",
        domains=("gmail.com",),
        auth="google_app_password",
        source="https://support.google.com/accounts/answer/185833",
    ),
    "icloud": preset(
        "iCloud 邮箱",
        "iCloud Mail",
        "imap.mail.me.com",
        "smtp.mail.me.com",
        domains=("icloud.com", "me.com", "mac.com"),
        auth="apple_app_password",
        smtp_port=587,
        source="https://support.apple.com/en-us/102525",
    ),
    "privateemail": preset(
        "PrivateEmail",
        "PrivateEmail",
        "mail.privateemail.com",
        "mail.privateemail.com",
        auth="password",
        source="https://www.namecheap.com/support/knowledgebase/article.aspx/1179/2175/general-private-email-configuration-for-mail-clients-and-mobile-devices/",
    ),
    "custom": preset("其他邮箱 / 手动设置", "Other / manual setup", "", "", auth="custom"),
}

# Recognition is separate from implemented authentication support.
PROVIDER_CATALOG = {
    **PROVIDERS,
    "outlook": {
        "name": {"zh": "Outlook / Microsoft 365", "en": "Outlook / Microsoft 365"},
        "domains": ["outlook.com", "hotmail.com", "live.com", "msn.com"],
        "available": False,
        "auth": "oauth_required",
        "source_url": "https://support.microsoft.com/en-gb/outlook/pop-imap-and-smtp-settings-for-outlook-com",
    },
}
