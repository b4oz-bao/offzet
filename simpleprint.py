import requests, json, base64, re, time, os, sys, random, asyncio, signal, ctypes
from datetime import datetime, timezone
from typing import Optional

API = "https://discord.com/api/v9"

SUPPORTED_TASKS = [
    "WATCH_VIDEO", "PLAY_ON_DESKTOP", "STREAM_ON_DESKTOP",
    "PLAY_ACTIVITY", "WATCH_VIDEO_ON_MOBILE",
]

def fetch_build() -> str:
    FALLBACK = "504649"
    try:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        r = requests.get("https://discord.com/app", headers={"User-Agent": ua}, timeout=15)
        if r.status_code != 200:
            return FALLBACK
        scripts = re.findall(r'/assets/([a-f0-9]+)\.js', r.text)
        if not scripts:
            scripts = re.findall(r'src="(/assets/[^"]+\.js)"', r.text)
            scripts = [s.split('/')[-1].replace('.js', '') for s in scripts]
        for asset_hash in scripts[-5:]:
            try:
                ar = requests.get(f"https://discord.com/assets/{asset_hash}.js", headers={"User-Agent": ua}, timeout=15)
                m = re.search(r'buildNumber["\s:]+["\s]*(\d{5,7})', ar.text)
                if m:
                    return m.group(1)
            except:
                continue
    except:
        pass
    return FALLBACK

def make_super_properties(bn: int, mobile: bool = False) -> str:
    if mobile:
        return base64.b64encode(json.dumps({
            "os": "iOS", "browser": "Discord iOS",
            "release_channel": "stable", "client_version": "251.0",
            "os_version": "18.0", "os_arch": "arm64", "app_arch": "arm64",
            "system_locale": "en-US", "client_build_number": bn,
            "native_build_number": 59498, "client_event_source": None,
            "browser_user_agent": "Discord/251.0 iOS/18.0",
            "browser_version": "251.0",
        }).encode()).decode()
    return base64.b64encode(json.dumps({
        "os": "Windows", "browser": "Discord Client",
        "release_channel": "stable", "client_version": "1.0.9175",
        "os_version": "10.0.26100", "os_arch": "x64", "app_arch": "x64",
        "system_locale": "en-US", "client_build_number": bn,
        "native_build_number": 59498, "client_event_source": None,
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9175 Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36",
        "browser_version": "32.2.7",
    }).encode()).decode()

class DiscordAPI:
    def __init__(self, token: str):
        self.session = requests.Session()
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9175 Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36"
        sp = make_super_properties(int(fetch_build()))
        self.session.headers.update({
            "Authorization": token, "Content-Type": "application/json",
            "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": ua, "X-Super-Properties": sp,
            "X-Discord-Locale": "en-US", "X-Discord-Timezone": "Asia/Ho_Chi_Minh",
            "Origin": "https://discord.com", "Referer": "https://discord.com/channels/@me",
        })
    def get(self, path: str):
        return self.session.get(f"{API}{path}")

    def post(self, path: str, payload: Optional[dict] = None):
        return self.session.post(f"{API}{path}", json=payload or {})

def _get(d: Optional[dict], *keys):
    if d is None: return None
    for k in keys:
        if k in d: return d[k]
    return None

def get_name(q):
    cfg = q.get("config", {})
    msgs = cfg.get("messages", {})
    name = _get(msgs, "questName", "quest_name")
    if name: return name.strip()
    game = _get(msgs, "gameTitle", "game_title")
    if game: return game.strip()
    return _get(cfg.get("application", {}), "name") or q.get("id", "?")[:8]

def get_task_config(q):
    return _get(q.get("config", {}), "taskConfig", "task_config", "taskConfigV2", "task_config_v2")

def get_task_type(q):
    tc = get_task_config(q)
    if not tc: return None
    tasks = tc.get("tasks", {})
    for t in SUPPORTED_TASKS:
        if tasks.get(t): return t
    return None

def is_expired(q):
    expires = _get(q.get("config", {}), "expiresAt", "expires_at")
    if expires:
        try:
            return datetime.fromisoformat(expires.replace("Z", "+00:00")) <= datetime.now(timezone.utc)
        except: pass
    return False

def get_user_status(q):
    return _get(q, "userStatus", "user_status") or {}

def complete_video(api: DiscordAPI, q, log=print):
    name, qid = get_name(q), q["id"]
    tc = get_task_config(q)
    tt = get_task_type(q)
    if not tc or not tt: return
    target = tc["tasks"][tt].get("target", 0)
    us = get_user_status(q)
    p = us.get("progress", {}).get(tt, {}).get("value", 0)
    enrolled_at_str = _get(us, "enrolledAt", "enrolled_at")
    enrolled_ts = datetime.fromisoformat(enrolled_at_str.replace("Z", "+00:00")).timestamp() if enrolled_at_str else time.time()

    mobile = tt == "WATCH_VIDEO_ON_MOBILE"
    old_headers = {}
    if mobile:
        old_headers["User-Agent"] = api.session.headers.get("User-Agent")
        old_headers["X-Super-Properties"] = api.session.headers.get("X-Super-Properties")
        api.session.headers.update({
            "User-Agent": "Discord/251.0 iOS/18.0",
            "X-Super-Properties": make_super_properties(int(fetch_build()), mobile=True),
        })

    log(f"[{tt}] {name}")
    try:
        while p < target:
            max_allowed = (time.time() - enrolled_ts) + 10
            ts = p + 7
            if max_allowed - ts >= -3:
                r = api.post(f"/quests/{qid}/video-progress", {"timestamp": min(target, ts + random.random())})
                if r.status_code == 200:
                    body = r.json()
                    if body.get("completed_at"):
                        log(f"  -> done!")
                        return
                    p = min(target, ts)
                elif r.status_code == 429:
                    wait = r.json().get("retry_after", 5) + 1
                    log(f"  rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    log(f"  error ({r.status_code})")
                    break
            if ts >= target: break
            time.sleep(1)
        api.post(f"/quests/{qid}/video-progress", {"timestamp": target})
        log(f"  -> done!")
    finally:
        if mobile:
            api.session.headers.update(old_headers)

def complete_heartbeat(api: DiscordAPI, q, is_activity=False, log=print):
    name, qid = get_name(q), q["id"]
    tc = get_task_config(q)
    tt = get_task_type(q)
    if not tc or not tt: return
    target = tc["tasks"][tt].get("target", 0)
    app_id = tc["tasks"][tt].get("application_id")
    us = get_user_status(q)
    p = us.get("progress", {}).get(tt, {}).get("value", 0)

    log(f"[{tt}] {name} (~{max(0,target-p)//60}min)")
    pid = 1 if is_activity else (int(time.time()) % 30000 + 1000)

    while p < target:
        payload = {"stream_key": f"call:0:{pid}", "terminal": False}
        if app_id: payload["application_id"] = app_id
        r = api.post(f"/quests/{qid}/heartbeat", payload)
        if r.status_code == 200:
            body = r.json()
            if body.get("completed_at"):
                log(f"  -> done!")
                api.post(f"/quests/{qid}/heartbeat", {"stream_key": f"call:0:{pid}", "terminal": True})
                return
            v = body.get("progress", {}).get(tt, {}).get("value", 0)
            if v >= target:
                api.post(f"/quests/{qid}/heartbeat", {"stream_key": f"call:0:{pid}", "terminal": True})
                log(f"  -> done!")
                return
            p = v
        elif r.status_code == 429:
            wait = r.json().get("retry_after", 10) + 1
            log(f"  rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        else:
            log(f"  error ({r.status_code})")
            break
        time.sleep(20)

def enroll_quest(api: DiscordAPI, q, log=print) -> Optional[dict]:
    name, qid = get_name(q), q["id"]
    tt = get_task_type(q)
    mobile = tt == "WATCH_VIDEO_ON_MOBILE"
    payload = {
        "location": 11, "is_targeted": False,
        "metadata_raw": q.get("metadata_raw"),
        "metadata_sealed": q.get("metadata_sealed"),
        "traffic_metadata_raw": q.get("traffic_metadata_raw"),
        "traffic_metadata_sealed": q.get("traffic_metadata_sealed"),
    }
    old_headers = {}
    if mobile:
        old_headers["User-Agent"] = api.session.headers.get("User-Agent")
        old_headers["X-Super-Properties"] = api.session.headers.get("X-Super-Properties")
        api.session.headers.update({
            "User-Agent": "Discord/251.0 iOS/18.0",
            "X-Super-Properties": make_super_properties(int(fetch_build()), mobile=True),
        })
    try:
        for attempt in range(5):
            r = api.post(f"/quests/{qid}/enroll", payload)
            if r.status_code == 429:
                wait = r.json().get("retry_after", 5) + 1
                log(f"  rate limited, waiting {wait:.0f}s...")
                time.sleep(wait)
                continue
            if r.status_code in (200, 201, 204):
                log(f"Enrolled: {name}")
                r2 = api.get("/quests/@me")
                if r2.status_code == 200:
                    for rq2 in r2.json().get("quests", []):
                        if rq2["id"] == qid:
                            return rq2
                return q
            log(f"Enroll failed {name} ({r.status_code}): {r.text[:200]}")
            return None
        log(f"Enroll {name} failed")
        return None
    finally:
        if mobile:
            api.session.headers.update(old_headers)

def process_quest(api: DiscordAPI, q, log=print) -> bool:
    name = get_name(q)
    tt = get_task_type(q)
    if not tt:
        log(f"Skipped {name} - unsupported task")
        return False
    if is_expired(q):
        log(f"Skipped {name} - expired")
        return False

    us = get_user_status(q)
    if _get(us, "completedAt", "completed_at"):
        return True

    if not _get(us, "enrolledAt", "enrolled_at"):
        q = enroll_quest(api, q, log)
        if not q:
            return False
        time.sleep(2)

    if "VIDEO" in tt:
        complete_video(api, q, log)
    elif tt in ("PLAY_ON_DESKTOP", "STREAM_ON_DESKTOP"):
        complete_heartbeat(api, q, False, log)
    elif tt == "PLAY_ACTIVITY":
        complete_heartbeat(api, q, True, log)
    return True

# ── CLI mode ─────────────────────────────────────────────────────────────────

def console_handler(ctrl_type):
    os._exit(0)
    return True
ctypes.windll.kernel32.SetConsoleCtrlHandler(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)(console_handler), True)

def ts(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def load_token():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        return sys.argv[1].strip().strip('"').strip("'")
    token_file = ".token"
    if os.path.exists(token_file):
        with open(token_file) as f:
            token = f.read().strip().strip('"').strip("'")
        if token:
            ts(f"Loaded token from {token_file}")
            return token
    return input("Enter Discord token: ").strip().strip('"').strip("'")

def cli_main():
    token = load_token()
    if not token:
        ts("Token is empty")
        sys.exit(1)

    api = DiscordAPI(token)
    r = api.get("/users/@me")
    if r.status_code != 200:
        ts(f"Invalid token ({r.status_code})")
        sys.exit(1)
    user = r.json()
    ts(f"Logged in as {user['username']}")

    r = api.get("/quests/@me")
    if r.status_code != 200:
        ts(f"Failed to fetch quests ({r.status_code})")
        sys.exit(1)
    data = r.json()
    all_quests = data.get("quests", [])
    excluded = {e.get("id") if isinstance(e, dict) else e for e in data.get("excluded_quests", [])}

    quests = [q for q in all_quests if q["id"] not in excluded]
    total = len(quests)
    enrolled = sum(1 for q in quests if _get(get_user_status(q), "enrolledAt", "enrolled_at"))
    completed = sum(1 for q in quests if _get(get_user_status(q), "completedAt", "completed_at"))
    completable = sum(1 for q in quests if get_task_type(q) and not is_expired(q))
    ts(f"Total: {total} quest | Enrolled: {enrolled} | Completed: {completed} | Completable: {completable}")

    for q in quests:
        us = get_user_status(q)
        tt = get_task_type(q) or "?"
        name = get_name(q)
        if _get(us, "completedAt", "completed_at"):
            icon = "done"
        elif _get(us, "enrolledAt", "enrolled_at"):
            icon = "enrolled"
        else:
            icon = "available"
        ts(f"  [{icon}] {name} [{tt}]")

    unaccepted = [
        q for q in quests
        if not _get(get_user_status(q), "enrolledAt", "enrolled_at")
        and not _get(get_user_status(q), "completedAt", "completed_at")
        and get_task_type(q)
    ]
    if unaccepted:
        ts(f"\nEnrolling {len(unaccepted)} quest(s)...")
        for q in unaccepted:
            new_q = enroll_quest(api, q, ts)
            if new_q:
                for i, old_q in enumerate(quests):
                    if old_q["id"] == q["id"]:
                        quests[i] = new_q
                        break
            time.sleep(2)

    actionable = [
        q for q in quests
        if _get(get_user_status(q), "enrolledAt", "enrolled_at")
        and not _get(get_user_status(q), "completedAt", "completed_at")
        and get_task_type(q)
    ]
    if not actionable:
        ts("Nothing to do")
        return

    ts(f"Processing {len(actionable)} quest(s)")
    done = 0
    for q in actionable:
        if process_quest(api, q, ts):
            done += 1
    ts(f"Done ({done}/{len(actionable)} completed)")

# ── Bot mode ─────────────────────────────────────────────────────────────────

running = {}

async def do_quests_bot(user_token, user_id, channel, username):
    api = DiscordAPI(user_token)
    done_quests = []

    r = await asyncio.to_thread(api.get, "/users/@me")
    if r.status_code != 200:
        await channel.send("Invalid token")
        running[user_id]["done"] = True
        return

    r = await asyncio.to_thread(api.get, "/quests/@me")
    if r.status_code != 200:
        await channel.send(f"Failed to fetch quests ({r.status_code})")
        running[user_id]["done"] = True
        return
    data = r.json()
    raw_quests = data.get("quests", [])
    excluded = {e.get("id") if isinstance(e, dict) else e for e in data.get("excluded_quests", [])}

    quests = [q for q in raw_quests if q["id"] not in excluded]



    for q in quests:
        if _get(get_user_status(q), "completedAt", "completed_at") and get_task_type(q):
            done_quests.append(f"\u2705 {get_name(q)} \u2014 Xong r\u1ed3i! V\u00e0o Settings \u279c Gifts nh\u1eadn th\u01b0\u1edfng!")

    actionable = [
        q for q in quests
        if _get(get_user_status(q), "enrolledAt", "enrolled_at")
        and not _get(get_user_status(q), "completedAt", "completed_at")
        and get_task_type(q)
    ]
    unaccepted = [
        q for q in quests
        if not _get(get_user_status(q), "enrolledAt", "enrolled_at")
        and not _get(get_user_status(q), "completedAt", "completed_at")
        and get_task_type(q)
    ]

    unaccepted_ids = {q["id"] for q in unaccepted}

    if not actionable and not unaccepted:
        running[user_id]["done"] = True
        return

    for q in actionable + unaccepted:
        if not running.get(user_id, {}).get("active"):
            running[user_id]["done"] = True
            return

        name = get_name(q)
        tt = get_task_type(q)

        if q["id"] in unaccepted_ids:
            new_q = await asyncio.to_thread(lambda: enroll_quest(api, q, lambda m: print(f"[ENROLL] {m}")))
            if not new_q:
                print(f"[ENROLL] Failed for {get_name(q)}")
                continue
            q = new_q
            await asyncio.sleep(2)

        msg = await channel.send(f"\u231b {name}...")
        if "VIDEO" in tt:
            await asyncio.to_thread(complete_video, api, q, lambda m: print(f"[VIDEO] {m}"))
        else:
            await asyncio.to_thread(complete_heartbeat, api, q, tt == "PLAY_ACTIVITY", lambda m: print(f"[HB] {m}"))
        await msg.edit(content=f"\u2705 {name} \u2014 Ho\u00e0n th\u00e0nh!")

    for q in done_quests:
        await channel.send(q)
    if done_quests:
        await channel.send(f"\U0001f389 V\u00e0o Settings \u279c Gifts \u0111\u1ec3 nh\u1eadn th\u01b0\u1edfng!")
    ts = datetime.now().strftime('%H:%M:%S')
    await channel.send(f"**AutoQuest** \u2022 {username} \u2022 {ts}\n<@{user_id}> Quest xong r\u1ed3i! \U0001f389")
    running[user_id]["done"] = True

def bot_main():
    import discord
    from discord import app_commands
    from dotenv import load_dotenv

    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("BOT_TOKEN not found in .env")
        sys.exit(1)

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @tree.command(name="autoquest", description="Auto-complete Discord quests using your user token")
    @app_commands.describe(token="Your Discord user token")
    async def autoquest(interaction: discord.Interaction, token: str):
        uid = interaction.user.id
        if uid in running and running[uid].get("active"):
            await interaction.response.send_message("Already running! Use /stop first.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)

        token = token.strip().strip('"').strip("'")
        running[uid] = {"active": True, "done": False}
        channel = interaction.channel
        username = interaction.user.name

        ts = datetime.now().strftime('%H:%M:%S')
        await interaction.followup.send(f"**AutoQuest** \u2022 {username} \u2022 {ts}\n\u23f3 \u0110ang l\u1ea5y danh s\u00e1ch quest...")
        await do_quests_bot(token, uid, channel, username)

        if uid in running:
            del running[uid]

    @tree.command(name="stop", description="Stop your running quest farming")
    async def stop(interaction: discord.Interaction):
        uid = interaction.user.id
        if uid not in running or not running[uid].get("active"):
            await interaction.response.send_message("Nothing is running.", ephemeral=True)
            return
        running[uid]["active"] = False
        await interaction.response.send_message("Stopping...", ephemeral=True)

    @client.event
    async def on_ready():
        await tree.sync()
        print(f"Bot ready: {client.user}")

    def cleanup(sig, frame):
        print("\nShutting down...")
        os._exit(0)
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    try:
        client.run(bot_token)
    except:
        pass

# ── Entry ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--bot":
        bot_main()
    else:
        has_user_token = False
        if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
            has_user_token = True
        elif os.path.exists(".token"):
            with open(".token") as f:
                if f.read().strip():
                    has_user_token = True
        elif os.getenv("BOT_TOKEN"):
            pass
        else:
            has_user_token = True

        if has_user_token:
            cli_main()
        else:
            bot_main()
