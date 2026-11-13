import re
import winreg as wr

import tweaks as T
import v4
from tweaks import run, reg, HKLM, HKCU

GUID = r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}"
SZ = wr.REG_SZ


def _active_scheme():
    out = run("powercfg /getactivescheme")
    m = re.search(GUID, out, re.I)
    return m.group(0) if m else None


def v5_power():
    g = _active_scheme()
    if not g:
        return "güç planı bulunamadı, atlandı"
    rows = [
        ("2a737441-1930-4402-8d77-b2bebba308a3", "0853a681-27c8-4100-a2fd-82013e970683", 0),
        ("2a737441-1930-4402-8d77-b2bebba308a3", "d4e98f31-5ffe-4ce1-be31-1b38b384c009", 0),
        ("19cbb8fa-5279-450e-9fac-8a3d5fedd0c1", "12bbebe6-58d6-4636-95bb-3217ef867c1a", 0),
        ("501a4d13-42af-4429-9fd1-a8218c268e20", "ee12f906-d277-404b-b6da-e5fa1a576df5", 0),
        ("0012ee47-9041-4b5d-9b77-535fba8b1442", "0b2d69d7-a2a1-449c-9680-f91c70521c60", 0),
        ("0012ee47-9041-4b5d-9b77-535fba8b1442", "51dea550-bb38-4bc4-991b-eacf37be5ec8", 100),
        ("2e601130-5351-4d9d-8e04-252966bad054", "d502f7ee-1dc7-4efd-a55d-f04b6f5c0545", 0),
        ("54533251-82be-4824-96c1-47b60b740d00", "3b04d4fd-1cc7-4f23-ab1c-d1337819c4bb", 0),
    ]
    for sub, st, val in rows:
        run("powercfg -setacvalueindex %s %s %s %d" % (g, sub, st, val))
        run("powercfg -setdcvalueindex %s %s %s %d" % (g, sub, st, val))
    run("powercfg -setactive " + g)
    return "USB, PCIe, SATA ve C-state derin uyku kapatıldı"


def v5_gpu():
    reg(HKLM, r"SYSTEM\CurrentControlSet\Services\amdkmdap\Parameters", "ThreadPriority", 0x1F)
    reg(HKLM, r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Parameters", "ThreadPriority", 0x1F)
    for sub in (r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Power",
                r"SYSTEM\CurrentControlSet\Services\nvlddmkm",
                r"SYSTEM\CurrentControlSet\Services\nvlddmkm\NVAPI",
                r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak"):
        reg(HKLM, sub, "RmGpsPsEnablePerCpuCoreDpc", 1)
    seen = []
    for sub, d in v4.gpu_classes():
        if "nvidia" in d:
            seen.append("NVIDIA")
        elif "amd" in d or "radeon" in d:
            seen.append("AMD")
    return (", ".join(sorted(set(seen))) + " sürücü önceliği ayarlandı") if seen else "sürücü anahtarları eklendi"


def v5_latency():
    p = r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\75b0ae3f-bce0-45a7-8c89-c9611c25e100"
    reg(HKLM, p, "Attributes", 2)
    d = r"SYSTEM\CurrentControlSet\Services\DXGKrnl"
    reg(HKLM, d, "MonitorLatencyTolerance", 0)
    reg(HKLM, d, "MonitorRefreshLatencyTolerance", 0)
    reg(HKLM, r"SYSTEM\CurrentControlSet\Control\PriorityControl", "ConvertibleSlateMode", 0)
    return "maksimum işlemci frekansı seçeneği açıldı, monitör gecikme toleransı sıfırlandı"


def v5_memcompress():
    v4.ps("Disable-MMAgent -mc -ErrorAction SilentlyContinue")
    return "bellek sıkıştırma kapatıldı"


def v5_services():
    run('sc config "GraphicsPerfSvc" start= disabled')
    run('sc stop "GraphicsPerfSvc"')
    reg(HKLM, r"SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR", "value", 0)
    return "GraphicsPerfSvc ve ek Game DVR politikası kapatıldı"


ITEMS = [
    ("v5_power", "Güç", "Ek güç tasarrufu", "USB, PCIe, SATA derin uyku ve C-state kapatılır", v5_power, None),
    ("v5_gpu", "Grafik", "GPU sürücü önceliği", "NVIDIA/AMD sürücü thread önceliği ve DPC ayarı", v5_gpu, None),
    ("v5_latency", "Gecikme", "Ek gecikme ayarları",
     "Maksimum işlemci frekansı seçeneği açılır, monitör gecikme toleransı sıfırlanır", v5_latency, None),
    ("v5_memcompress", "Bellek", "Bellek sıkıştırmayı kapat", "CPU'yu bellek sıkıştırmasından kurtarır", v5_memcompress, None),
    ("v5_services", "CPU", "Ek servisler", "GraphicsPerfSvc ve ek Game DVR politikası kapalı", v5_services, None),
]


def register():
    for i, grp, name, desc, fn, chk in ITEMS:
        T.ALL[i] = (grp, name, desc, fn)
    T.TIERS["V5"] = list(T.TIERS["V4"]) + [x[0] for x in ITEMS]
    T.GAMES4.update(v4.GAMES4)
    T.TIER_GAMES["V5"] = list(v4.GAMES4)
    T.TIER_TITLES["V5"] = "Nexa Premium Tweak"
    T.TIER_SCAN["V5"] = True
    T.CHECKBOX_TIERS.add("V5")
